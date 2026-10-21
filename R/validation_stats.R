# BIO-MB-001 validation statistics (base R 'stats' only; D8 R 4.6.1).
#
# Invoked by scripts/validation_gse63061.py with the project root as working directory. Refuses to run
# unless the R version matches the pin passed on the command line (exit status 3).
#
# Usage:
#   Rscript R/validation_stats.R --R 4.6.1 --ols  --y Y.tsv --design X.tsv --coef NAME --out OUT.tsv
#   Rscript R/validation_stats.R --R 4.6.1 --tail --input T.tsv --out OUT.tsv
#   Rscript R/validation_stats.R --R 4.6.1 --cor  --input XY.tsv --out OUT.tsv
#
# --ols : lm(y ~ 0 + X); for coefficient NAME: estimate, SE, t, residual df, one-sided upper-tail p
#         (H1: coefficient > 0), one-sided 95% lower bound qt(0.95), two-sided 95% CI qt(0.975).
# --tail: input columns feature_id, t_signed (= d * t), df -> p_one_sided = pt(t_signed, df, lower = FALSE)
#         and q95 = qt(0.95, df).
# --cor : input columns x, y -> Pearson r with its two-sided 95% Fisher-z interval (cor.test); the caller labels
#         the interval nominal (it assumes independent pairs).
# Numbers are written with 17 significant digits.

args <- commandArgs(trailingOnly = TRUE)
opt <- function(name, default = NULL) {
  i <- match(paste0("--", name), args)
  if (is.na(i)) default else args[i + 1]
}
pinned <- opt("R")
found <- paste(R.version$major, R.version$minor, sep = ".")
if (is.null(pinned) || is.na(pinned) || found != pinned) {
  message("VERSION MISMATCH: R found ", found, ", pinned ", if (is.null(pinned)) "none" else pinned)
  quit(status = 3)
}
fmt <- function(df) {
  num <- vapply(df, is.numeric, logical(1))
  df[num] <- lapply(df[num], function(v) sprintf("%.17g", v))
  df
}
write_out <- function(df) utils::write.table(fmt(df), opt("out"), sep = "\t", quote = FALSE, row.names = FALSE)

if ("--ols" %in% args) {
  y <- utils::read.delim(opt("y"), check.names = FALSE, row.names = 1)
  X <- as.matrix(utils::read.delim(opt("design"), check.names = FALSE, row.names = 1))
  stopifnot(identical(rownames(y), rownames(X)), ncol(y) == 1, all(is.finite(y[[1]])), all(is.finite(X)))
  coef <- opt("coef")
  stopifnot(coef %in% colnames(X))
  fit <- stats::lm(y[[1]] ~ 0 + X)
  stopifnot(fit$rank == ncol(X))
  s <- summary(fit)$coefficients
  k <- match(paste0("X", coef), rownames(s))
  est <- s[k, 1]; se <- s[k, 2]; df <- fit$df.residual; t <- est / se
  write_out(data.frame(coefficient = coef, estimate = est, std_error = se, t_statistic = t, df = df,
                       p_one_sided = stats::pt(t, df, lower.tail = FALSE),
                       lower_bound_one_sided_95 = est - stats::qt(0.95, df) * se,
                       ci_low_two_sided_95 = est - stats::qt(0.975, df) * se,
                       ci_high_two_sided_95 = est + stats::qt(0.975, df) * se))
} else if ("--tail" %in% args) {
  d <- utils::read.delim(opt("input"), colClasses = c(feature_id = "character"))
  write_out(data.frame(feature_id = d$feature_id, p_one_sided = stats::pt(d$t_signed, d$df, lower.tail = FALSE),
                       q95 = stats::qt(0.95, d$df)))
} else if ("--cor" %in% args) {
  d <- utils::read.delim(opt("input"))
  ct <- stats::cor.test(d$x, d$y, method = "pearson", conf.level = 0.95)
  write_out(data.frame(n = nrow(d), pearson_r = unname(ct$estimate), ci_low = ct$conf.int[1], ci_high = ct$conf.int[2]))
} else {
  stop("need --ols, --tail or --cor")
}
