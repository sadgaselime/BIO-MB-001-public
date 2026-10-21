# BIO-MB-001 exploratory ML engine (approved ML protocol, 2026-10-19; v7:603; environment v7:611).
#
# Invoked by scripts/ml_gse63060.py / scripts/ml_apply_gse63061.py with the project root as working directory, so
# the project .Rprofile activates the renv library. Refuses to run unless R, limma and glmnet match the pins
# passed on the command line (exit status 3).
#
# Modes:
#   --cv     nested, chip-grouped cross-validation in the discovery cohort (outer: n_outer folds x n_repeats;
#            inner: n_inner folds), plus an optional within-chip label-permutation null (--n_perm)
#   --final  refit on all arrays with the inner-loop procedure; writes the frozen model
#   --apply  applies a frozen model once to another cohort (per-chip centring, within-cohort standardization)
#
# Protocol elements implemented (reports/planning/ML_PROTOCOL_DRAFT_2026-10-19.md, M1):
#   - per-chip, diagnosis-blind centring of every gene (chips are wholly in training or test, so this equals
#     centring test chips on their own means);
#   - gene scaling learned on training arrays only;
#   - selection inside each training set: limma (age scaled, recorded sex, chip, AD; trend = TRUE), top k by
#     p (ties: |t| desc, gene id asc), k tuned in the inner loop over --kgrid;
#   - primary model: ridge logistic (alpha = 0) on the k selected genes; secondary: elastic net (--alpha_en) on
#     all genes; inverse-frequency class weights; no resampling;
#   - inner-loop choice: minimum class-weighted binomial deviance over pooled inner out-of-fold predictions
#     (ties: larger lambda, then smaller k); classification threshold: Youden-optimal on the same predictions;
#   - baselines per outer fold: B0 training prevalence; B1 logistic on age; B2 equal-weight score of the top
#     --b2_genes training genes (signed by limma t; training z-scale);
#   - metrics on pooled out-of-fold predictions per repeat: AUROC, AUPRC, Brier, calibration intercept/slope,
#     sensitivity, specificity, PPV and balanced accuracy at the fold threshold; DeLong CIs on per-array predictions averaged over repeats.
# All randomness is seeded per task (set.seed(seed + task)), so results do not depend on scheduling.

args <- commandArgs(trailingOnly = TRUE)
opt <- function(name, default = NULL) {
  i <- match(paste0("--", name), args)
  if (is.na(i)) default else args[i + 1]
}
num <- function(name, default) as.numeric(opt(name, default))
mode <- if ("--cv" %in% args) "cv" else if ("--final" %in% args) "final" else if ("--apply" %in% args) "apply" else
  stop("need --cv, --final or --apply")
pv <- function(p) tryCatch(as.character(utils::packageVersion(p)), error = function(e) NA_character_)
found <- c(R = paste(R.version$major, R.version$minor, sep = "."), limma = pv("limma"), glmnet = pv("glmnet"))
pins <- c(R = opt("R", NA), limma = opt("limma", NA), glmnet = opt("glmnet", NA))
if (anyNA(pins) || any(is.na(found)) || any(found != pins)) {
  message("VERSION MISMATCH: ", paste(sprintf("%s found %s, pinned %s", names(found), found, pins), collapse = "; "))
  quit(status = 3)
}
suppressPackageStartupMessages({ library(limma); library(glmnet); library(parallel) })
glmnet.control(fdev = 0, devmax = 1)   # full lambda path, no early stopping
outdir <- opt("outdir")
dir.create(outdir, showWarnings = FALSE, recursive = TRUE)
fmt <- function(df) { n <- vapply(df, is.numeric, logical(1)); df[n] <- lapply(df[n], function(v) sprintf("%.17g", v)); df }
put <- function(df, name) utils::write.table(fmt(df), file.path(outdir, name), sep = "\t", quote = FALSE, row.names = FALSE)

read_E <- function(p) {
  E <- utils::read.delim(p, check.names = FALSE, row.names = 1, colClasses = "character")
  as.matrix(data.frame(lapply(E, as.numeric), check.names = FALSE, row.names = rownames(E)))
}
chip_centre <- function(E, chip) {
  for (c in unique(chip)) { j <- chip == c; E[, j] <- E[, j, drop = FALSE] - rowMeans(E[, j, drop = FALSE]) }
  E
}
LAMBDA <- exp(seq(log(100), log(1e-3), length.out = as.integer(num("n_lambda", 60))))
KGRID <- as.integer(strsplit(opt("kgrid", "50,100,200"), ",")[[1]])
ALPHA_EN <- num("alpha_en", 0.5)
B2_GENES <- as.integer(num("b2_genes", 200))
USE_SEX <- opt("use_sex", "true") == "true"
clamp <- function(p) pmin(pmax(p, 1e-15), 1 - 1e-15)
cw <- function(y) { n <- length(y); ifelse(y == 1, n / (2 * sum(y == 1)), n / (2 * sum(y == 0))) }

group_folds <- function(chip, y, K, seed) {
  set.seed(seed)
  ch <- unique(chip); ch <- ch[sample.int(length(ch))]
  frac <- vapply(ch, function(c) mean(y[chip == c]), numeric(1))
  ch <- ch[order(frac, method = "radix")]
  f <- stats::setNames(rep(c(seq_len(K), rev(seq_len(K))), length.out = length(ch)), ch)
  unname(f[chip])
}
rank_genes <- function(E, P, idx) {
  p <- P[idx, ]
  X <- cbind(intercept = 1, age = as.numeric(scale(p$age)))
  if (USE_SEX) X <- cbind(X, sex = p$sex_male)
  ch <- factor(p$chip)
  if (nlevels(ch) > 1) { M <- stats::model.matrix(~ch)[, -1, drop = FALSE]; X <- cbind(X, M) }
  X <- cbind(X, AD = p$y)
  q <- qr(X)
  keep <- sort(q$pivot[seq_len(q$rank)])
  if (!(ncol(X) %in% keep)) stop("AD column aliased in a training design")
  X <- X[, keep, drop = FALSE]
  fit <- eBayes(lmFit(E[, idx, drop = FALSE], X), trend = TRUE)
  t <- fit$t[, "AD"]; pval <- fit$p.value[, "AD"]
  list(order = order(pval, -abs(t), rownames(E)), sign = sign(t))
}
scale_tr <- function(Etr) { mu <- rowMeans(Etr); s <- apply(Etr, 1, stats::sd); s[!is.finite(s) | s == 0] <- 1; list(mu = mu, sd = s) }
zmat <- function(E, g, idx, s) t((E[g, idx, drop = FALSE] - s$mu) / s$sd)
fit_path <- function(X, y, alpha) glmnet(X, y, family = "binomial", alpha = alpha, lambda = LAMBDA, weights = cw(y),
                                         standardize = FALSE)
wdev <- function(y, p, w) -mean(w * (y * log(clamp(p)) + (1 - y) * log(1 - clamp(p))))
youden <- function(y, p) {
  th <- sort(unique(p)); J <- vapply(th, function(t) mean(p[y == 1] >= t) + mean(p[y == 0] < t) - 1, numeric(1))
  th[which.max(J)]
}
auc <- function(y, s) { r <- rank(s); n1 <- sum(y == 1); n0 <- sum(y == 0); (sum(r[y == 1]) - n1 * (n1 + 1) / 2) / (n1 * n0) }
auprc <- function(y, s) {
  o <- order(-s); y <- y[o]; s <- s[o]
  # ties share the precision of their block end
  ends <- c(which(diff(s) != 0), length(s)); tp <- cumsum(y)[ends]; n <- ends
  prec <- tp / n; dtp <- diff(c(0, tp))
  sum(prec * dtp) / sum(y)
}
calib <- function(y, p) {
  lp <- stats::qlogis(clamp(p))
  sl <- suppressWarnings(stats::coef(stats::glm(y ~ lp, family = stats::binomial()))[2])
  ic <- suppressWarnings(stats::coef(stats::glm(y ~ 1, offset = lp, family = stats::binomial()))[1])
  c(calibration_intercept = unname(ic), calibration_slope = unname(sl))
}
delong_parts <- function(y, s) {
  X <- s[y == 1]; Y <- s[y == 0]
  psi <- function(a, b) (a > b) + 0.5 * (a == b)
  list(V10 = vapply(X, function(x) mean(psi(x, Y)), numeric(1)), V01 = vapply(Y, function(v) mean(psi(X, v)), numeric(1)))
}
delong <- function(y, s) {
  d <- delong_parts(y, s); a <- mean(d$V10); se <- sqrt(stats::var(d$V10) / length(d$V10) + stats::var(d$V01) / length(d$V01))
  c(auc = a, se = se, ci_low = a - stats::qnorm(0.975) * se, ci_high = a + stats::qnorm(0.975) * se)
}
delong_diff <- function(y, s1, s2) {
  a <- delong_parts(y, s1); b <- delong_parts(y, s2)
  S10 <- stats::cov(cbind(a$V10, b$V10)); S01 <- stats::cov(cbind(a$V01, b$V01))
  d <- mean(a$V10) - mean(b$V10)
  se <- sqrt((S10[1, 1] + S10[2, 2] - 2 * S10[1, 2]) / length(a$V10) + (S01[1, 1] + S01[2, 2] - 2 * S01[1, 2]) / length(a$V01))
  c(auc_difference = d, se = se, ci_low = d - stats::qnorm(0.975) * se, ci_high = d + stats::qnorm(0.975) * se,
    p_two_sided = 2 * stats::pnorm(-abs(d / se)))
}

# Inner loop on training indices tr: returns the chosen k, lambda index, threshold (primary) and EN lambda index.
inner <- function(E, P, tr, K, seed, with_en) {
  f <- group_folds(P$chip[tr], P$y[tr], K, seed)
  pred <- array(NA_real_, c(length(tr), length(KGRID), length(LAMBDA)))
  pen <- matrix(NA_real_, length(tr), length(LAMBDA))
  for (v in seq_len(K)) {
    itr <- tr[f != v]; ite <- tr[f == v]
    if (!length(ite)) next
    rk <- rank_genes(E, P, itr)
    for (a in seq_along(KGRID)) {
      g <- rk$order[seq_len(KGRID[a])]; s <- scale_tr(E[g, itr, drop = FALSE])
      m <- fit_path(zmat(E, g, itr, s), P$y[itr], 0)
      pred[f == v, a, ] <- stats::predict(m, zmat(E, g, ite, s), type = "response")
    }
    if (with_en) {
      g <- seq_len(nrow(E)); s <- scale_tr(E[, itr, drop = FALSE])
      m <- fit_path(zmat(E, g, itr, s), P$y[itr], ALPHA_EN)
      pen[f == v, ] <- stats::predict(m, zmat(E, g, ite, s), type = "response")
    }
  }
  y <- P$y[tr]; w <- cw(y)
  D <- apply(pred, c(2, 3), function(p) wdev(y, p, w))           # k x lambda
  cand <- which(D == min(D), arr.ind = TRUE)
  cand <- cand[order(cand[, 2], cand[, 1]), , drop = FALSE]      # larger lambda (smaller index) first, then smaller k
  a <- cand[1, 1]; l <- cand[1, 2]
  out <- list(k = KGRID[a], k_index = a, lambda_index = l, lambda = LAMBDA[l], threshold = youden(y, pred[, a, l]),
              inner_deviance = D[a, l])
  if (with_en) {
    De <- apply(pen, 2, function(p) wdev(y, p, w)); le <- which(De == min(De))[1]
    out$en_lambda_index <- le; out$en_threshold <- youden(y, pen[, le])
  }
  out
}

# One repeat of the outer loop; returns per-array out-of-fold predictions and per-fold choices.
one_repeat <- function(E, P, r, seed, n_outer, n_inner, with_baselines) {
  fo <- group_folds(P$chip, P$y, n_outer, seed + 1000 * r)
  preds <- list(); choices <- list()
  for (v in seq_len(n_outer)) {
    tr <- which(fo != v); te <- which(fo == v)
    if (!length(te)) next
    ch <- inner(E, P, tr, n_inner, seed + 1000 * r + v, with_baselines)
    rk <- rank_genes(E, P, tr)
    g <- rk$order[seq_len(ch$k)]; s <- scale_tr(E[g, tr, drop = FALSE])
    m <- fit_path(zmat(E, g, tr, s), P$y[tr], 0)
    p_main <- stats::predict(m, zmat(E, g, te, s), type = "response")[, ch$lambda_index]
    d <- data.frame(array = P$array[te], repeat_id = r, fold = v, y = P$y[te], ridge = p_main,
                    ridge_class = as.integer(p_main >= ch$threshold))
    if (with_baselines) {
      d$B0_prevalence <- mean(P$y[tr])
      b1 <- suppressWarnings(stats::glm(y ~ age, data = P[tr, ], family = stats::binomial(), weights = cw(P$y[tr])))
      d$B1_age <- stats::predict(b1, P[te, ], type = "response")
      gb <- rk$order[seq_len(min(B2_GENES, nrow(E)))]; sb <- scale_tr(E[gb, tr, drop = FALSE]); z <- zmat(E, gb, te, sb)
      up <- rk$sign[gb] > 0
      d$B2_equal_weight <- (if (any(up)) rowMeans(z[, up, drop = FALSE]) else 0) - (if (any(!up)) rowMeans(z[, !up, drop = FALSE]) else 0)
      ga <- seq_len(nrow(E)); sa <- scale_tr(E[, tr, drop = FALSE])
      me <- fit_path(zmat(E, ga, tr, sa), P$y[tr], ALPHA_EN)
      d$elastic_net <- stats::predict(me, zmat(E, ga, te, sa), type = "response")[, ch$en_lambda_index]
      d$elastic_net_class <- as.integer(d$elastic_net >= ch$en_threshold)
    }
    preds[[v]] <- d
    choices[[v]] <- data.frame(repeat_id = r, fold = v, n_train = length(tr), n_test = length(te),
                               test_chips = paste(sort(unique(P$chip[te])), collapse = ";"), k = ch$k,
                               lambda = ch$lambda, threshold = ch$threshold, inner_deviance = ch$inner_deviance,
                               en_lambda = if (with_baselines) LAMBDA[ch$en_lambda_index] else NA_real_)
  }
  list(pred = do.call(rbind, preds), choices = do.call(rbind, choices))
}
threshold_metrics <- function(y, cls) {
  if (is.null(cls)) return(data.frame(sensitivity = NA_real_, specificity = NA_real_, ppv = NA_real_, balanced_accuracy = NA_real_))
  se <- mean(cls[y == 1] == 1); sp <- mean(cls[y == 0] == 0)
  data.frame(sensitivity = se, specificity = sp, ppv = if (any(cls == 1)) mean(y[cls == 1] == 1) else NA_real_,
             balanced_accuracy = (se + sp) / 2)
}
repeat_metrics <- function(d) {
  y <- d$y
  row <- function(model, p, cls = NULL, prob = TRUE) {
    # B0 is constant within each fold: its pooled AUROC/AUPRC reflect between-fold prevalence only (not reported)
    m <- data.frame(repeat_id = d$repeat_id[1], model = model, auroc = if (model == "B0_prevalence") NA_real_ else auc(y, p),
                    auprc = if (model == "B0_prevalence") NA_real_ else auprc(y, p))
    if (prob) { m$brier <- mean((p - y)^2); cb <- calib(y, p); m$calibration_intercept <- cb[1]; m$calibration_slope <- cb[2] }
    else { m$brier <- NA_real_; m$calibration_intercept <- NA_real_; m$calibration_slope <- NA_real_ }
    m <- cbind(m, threshold_metrics(y, cls))
    m
  }
  out <- list(row("ridge", d$ridge, d$ridge_class))
  if ("B1_age" %in% names(d)) {
    out <- c(out, list(row("B0_prevalence", d$B0_prevalence), row("B1_age", d$B1_age),
                       row("B2_equal_weight", d$B2_equal_weight, prob = FALSE),
                       row("elastic_net", d$elastic_net, d$elastic_net_class)))
  }
  do.call(rbind, out)
}
permute_within_chip <- function(y, chip, seed) {
  set.seed(seed)
  for (c in unique(chip)) { j <- which(chip == c); if (length(j) > 1) y[j] <- y[j][sample.int(length(j))] }
  y
}

E <- read_E(opt("expression"))
P <- utils::read.delim(opt("pheno"), colClasses = c(array = "character", chip = "character"))
stopifnot(identical(colnames(E), P$array), all(P$y %in% c(0, 1)), all(is.finite(E)))
E <- chip_centre(E, P$chip)
cores <- as.integer(num("cores", 1)); seed <- as.integer(num("seed", 20261019))
n_outer <- as.integer(num("n_outer", 5)); n_inner <- as.integer(num("n_inner", 5)); n_rep <- as.integer(num("n_repeats", 20))

if (mode == "cv") {
  reps <- parallel::mclapply(seq_len(n_rep), function(r) one_repeat(E, P, r, seed, n_outer, n_inner, TRUE),
                             mc.cores = cores, mc.preschedule = FALSE)
  if (any(vapply(reps, inherits, logical(1), "try-error"))) stop("a repeat failed: ", paste(reps[vapply(reps, inherits, logical(1), "try-error")], collapse = "; "))
  pred <- do.call(rbind, lapply(reps, `[[`, "pred")); choices <- do.call(rbind, lapply(reps, `[[`, "choices"))
  met <- do.call(rbind, lapply(split(pred, pred$repeat_id), repeat_metrics))
  put(pred, "oof_predictions.tsv"); put(choices, "fold_choices.tsv"); put(met, "repeat_metrics.tsv")
  models <- c("ridge", "B0_prevalence", "B1_age", "B2_equal_weight", "elastic_net")
  avg <- stats::aggregate(pred[, models], by = list(array = pred$array), FUN = mean)
  avg$y <- P$y[match(avg$array, P$array)]
  put(avg, "oof_predictions_averaged.tsv")
  dl <- do.call(rbind, lapply(setdiff(models, "B0_prevalence"), function(m) data.frame(model = m, t(delong(avg$y, avg[[m]])))))
  put(dl, "delong_auc_averaged.tsv")
  dd <- do.call(rbind, lapply(c("B1_age", "B2_equal_weight", "elastic_net"), function(m)
    data.frame(comparison = paste0("ridge - ", m), t(delong_diff(avg$y, avg$ridge, avg[[m]])))))
  put(dd, "delong_auc_differences_averaged.tsv")
  n_perm <- as.integer(num("n_perm", 0)); perm_from <- as.integer(num("perm_from", 1))
  if (n_perm > 0) {
    ids <- seq(perm_from, length.out = n_perm)
    perm <- parallel::mclapply(ids, function(i) {
      Pp <- P; Pp$y <- permute_within_chip(P$y, P$chip, seed + 7919 * i)
      a <- vapply(seq_len(n_rep), function(r) { d <- one_repeat(E, Pp, r, seed + 100000 * i, n_outer, n_inner, FALSE)$pred; auc(d$y, d$ridge) }, numeric(1))
      data.frame(permutation = i, mean_auroc = mean(a))
    }, mc.cores = cores, mc.preschedule = FALSE)
    if (any(vapply(perm, inherits, logical(1), "try-error"))) stop("a permutation failed")
    put(do.call(rbind, perm), "permutation_null.tsv")
  }
} else if (mode == "final") {
  all <- seq_len(ncol(E))
  ch <- inner(E, P, all, n_inner, seed + 999999, FALSE)
  rk <- rank_genes(E, P, all); g <- rk$order[seq_len(ch$k)]; s <- scale_tr(E[g, all, drop = FALSE])
  m <- fit_path(zmat(E, g, all, s), P$y, 0)
  b <- as.numeric(stats::coef(m)[, ch$lambda_index])
  put(data.frame(feature_id = c("(Intercept)", rownames(E)[g]), coefficient = b,
                 train_mean = c(NA, s$mu), train_sd = c(NA, s$sd)), "final_model_coefficients.tsv")
  b1 <- suppressWarnings(stats::glm(y ~ age, data = P, family = stats::binomial(), weights = cw(P$y)))
  put(data.frame(k = ch$k, lambda = ch$lambda, threshold = ch$threshold, inner_deviance = ch$inner_deviance,
                 n_arrays = ncol(E), n_genes_input = nrow(E), B1_intercept = stats::coef(b1)[1], B1_age = stats::coef(b1)[2]),
      "final_model_settings.tsv")
} else {
  M <- utils::read.delim(opt("model"), colClasses = c(feature_id = "character"))
  S <- utils::read.delim(opt("settings"))
  genes <- M$feature_id[-1]; beta <- M$coefficient[-1]
  present <- genes %in% rownames(E)
  Z <- matrix(0, ncol(E), length(genes))                          # missing genes stay at the cohort mean (z = 0)
  if (any(present)) {
    G <- E[genes[present], , drop = FALSE]
    sd_g <- apply(G, 1, stats::sd); sd_g[!is.finite(sd_g) | sd_g == 0] <- 1
    Z[, present] <- t((G - rowMeans(G)) / sd_g)
  }
  p <- stats::plogis(M$coefficient[1] + as.numeric(Z %*% beta))
  pb1 <- stats::plogis(S$B1_intercept + S$B1_age * P$age)
  d <- data.frame(array = P$array, y = P$y, ridge = p, ridge_class = as.integer(p >= S$threshold), B1_age = pb1)
  put(d, "external_predictions.tsv")
  cb <- calib(d$y, d$ridge); cb1 <- calib(d$y, d$B1_age)
  met <- rbind(data.frame(model = "ridge", t(delong(d$y, d$ridge)), auprc = auprc(d$y, d$ridge), brier = mean((d$ridge - d$y)^2),
                          calibration_intercept = cb[1], calibration_slope = cb[2], threshold_metrics(d$y, d$ridge_class)),
               data.frame(model = "B1_age", t(delong(d$y, d$B1_age)), auprc = auprc(d$y, d$B1_age), brier = mean((d$B1_age - d$y)^2),
                          calibration_intercept = cb1[1], calibration_slope = cb1[2], threshold_metrics(d$y, NULL)))
  put(met, "external_metrics.tsv")
  put(data.frame(t(delong_diff(d$y, d$ridge, d$B1_age))), "external_auc_difference_vs_B1.tsv")
  put(data.frame(n_model_genes = length(genes), n_present = sum(present), n_missing = sum(!present)), "external_gene_coverage.tsv")
}
