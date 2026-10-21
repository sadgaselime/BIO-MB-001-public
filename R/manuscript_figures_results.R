# BIO-MB-001 manuscript result figures (base R only): discovery, score distributions, per-gene agreement,
# leukocyte composition and classifier discrimination. Descriptive plots of accepted outputs; the only quantities
# computed are ROC curve coordinates and their AUC, which are checked against the accepted AUROC values.
# Usage (project root): Rscript R/manuscript_figures_results.R <outdir>
args <- commandArgs(trailingOnly = TRUE)
out <- if (length(args)) args[1] else "reports/manuscript/medrxiv/figures"
dir.create(out, showWarnings = FALSE, recursive = TRUE)
both <- function(name, w, h, f) {
  grDevices::png(file.path(out, paste0(name, ".png")), width = w, height = h, units = "in", res = 300); f(); grDevices::dev.off()
  grDevices::pdf(file.path(out, paste0(name, ".pdf")), width = w, height = h); f(); grDevices::dev.off()
}
tsv <- function(p) utils::read.delim(p, check.names = FALSE, stringsAsFactors = FALSE)
txt <- function(p) paste(readLines(p, warn = FALSE), collapse = "\n")

ink <- "#1d2733"; sub <- "#5b6675"; grid_ <- "#e3e7ec"
blue <- "#2b5b8f"; orange <- "#c0602a"; green <- "#2d7a57"; purple <- "#6a4c93"; grey_ <- "#b8c0c9"
alpha <- function(col, a) grDevices::adjustcolor(col, alpha.f = a)
panel_tag <- function(s) graphics::mtext(s, side = 3, adj = 0, line = 1.1, font = 2, cex = 0.95, col = ink,
                                         at = graphics::grconvertX(0.03, "nfc", "user"))
frame_ <- function() { graphics::box(bty = "l", col = sub) }
setpar <- function(mar = c(4.2, 4.4, 3, 1)) graphics::par(mar = mar, family = "sans", col.axis = sub, col.lab = ink,
                                                      cex = 0.9, cex.axis = 0.78, cex.lab = 0.85, las = 1, tcl = -0.25, mgp = c(2.6, 0.5, 0))

# ---- Figure 2: discovery
gl <- tsv("reports/discovery/GSE63060/fit_v1/gene_level_results.tsv")
sig <- tsv("reports/lock/GSE63060/v1/signature.tsv")
sens <- txt("reports/discovery/GSE63060/sensitivity_v1/sensitivity_summary.json")
sens_lab <- c("S1a" = "Age 65 or older", "S1b" = "Age 61 to 88", "S3a" = "Site added", "S3b" = "Site instead of chip",
              "S4" = "Exclude M-coded AD", "S5a" = "Exclude R9 outliers", "S5e" = "Exclude R8 ambiguous",
              "S5f" = "Re-include sex-discordant", "S5g" = "Exclude all QC flags", "S7_p25" = "Expression filter, 25th pct",
              "S7_p50" = "Expression filter, 50th pct", "S8" = "Highest-mean probe per gene",
              "S12" = "Case-control subset", "S-R8m" = "Remove Y-marker discordant")
sval <- function(k, key) { s <- substring(sens, regexpr(paste0('"', k, '": {'), sens, fixed = TRUE))
  as.numeric(sub('.*: *', '', regmatches(s, regexpr(paste0('"', key, '": *[0-9.]+'), s)))) }
sdat <- data.frame(k = names(sens_lab), lab = unname(sens_lab),
                   rho = sapply(names(sens_lab), sval, key = "spearman_t_vs_primary"),
                   n = sapply(names(sens_lab), sval, key = "n"),
                   same = sapply(names(sens_lab), sval, key = "of_which_same_sign"))
sdat <- sdat[order(sdat$rho), ]
both("Figure2_discovery", 10.5, 4.8, function() {
  graphics::layout(matrix(1:2, ncol = 2), widths = c(1.05, 1))
  setpar(c(4.2, 4.4, 3, 1))
  y <- -log10(gl$p_value); locked <- gl$feature_id %in% sig$entrez_gene_id; sigq <- gl$q_value_bh < 0.05
  col <- ifelse(locked, ifelse(gl$estimate < 0, blue, orange), ifelse(sigq, alpha(grey_, 0.9), alpha("#d5dade", 0.6)))
  o <- order(locked, sigq)
  graphics::plot(gl$estimate[o], y[o], pch = 16, cex = ifelse(locked[o], 0.55, 0.35), col = col[o], axes = FALSE,
                 xlab = expression("Effect, AD minus control (log"[2]*" expression)"), ylab = expression(-log[10]~italic(p)))
  graphics::abline(v = 0, col = grid_); qline <- max(gl$p_value[sigq]); graphics::abline(h = -log10(qline), lty = 2, col = sub)
  graphics::axis(1); graphics::axis(2); frame_()
  top <- head(sig[order(sig$p_value), ], 6)[-3, ]
  idx <- match(top$entrez_gene_id, gl$feature_id)
  graphics::text(gl$estimate[idx], y[idx], top$symbol, pos = 4, cex = 0.6, col = ink, offset = 0.3)
  graphics::text(par("usr")[2], -log10(qline), "FDR 0.05", adj = c(1, -0.4), cex = 0.6, col = sub)
  graphics::legend("topright", bty = "n", pch = 16, cex = 0.66, col = c(blue, orange, grey_), text.col = ink,
                   legend = c("Locked gene, lower in AD (172)", "Locked gene, higher in AD (28)", "Other gene at FDR < 0.05"))
  panel_tag("a   Discovery cohort GSE63060: 1,401 of 17,425 genes at FDR < 0.05")
  setpar(c(4.2, 10.5, 3, 4))
  yy <- seq_len(nrow(sdat))
  graphics::plot(sdat$rho, yy, xlim = c(0.7, 1), ylim = c(0.5, nrow(sdat) + 0.5), pch = 19, col = blue, axes = FALSE,
                 xlab = "Spearman correlation of t statistics with primary", ylab = "")
  graphics::abline(v = seq(0.7, 1, 0.05), col = grid_); graphics::segments(0.7, yy, sdat$rho, yy, col = alpha(blue, 0.35), lwd = 2)
  graphics::points(sdat$rho, yy, pch = 19, col = blue)
  graphics::axis(1); graphics::axis(2, at = yy, labels = sdat$lab, tick = FALSE, cex.axis = 0.72); frame_()
  graphics::mtext(sprintf("n=%d", sdat$n), side = 4, at = yy, las = 1, line = 0.3, cex = 0.55, col = sub)
  panel_tag("b   Robustness across 14 sensitivity analyses")
})

# ---- Figure 3: score distributions by group
sc <- list(
  list(t = "a   GSE63061 (related cohort)", d = tsv("reports/validation/GSE63061/v1/score_W1.tsv"), g = c("CTL", "AD"), lab = c("Control", "AD"), col = c(grey_, blue)),
  list(t = "b   GSE140829 (replication)", d = tsv("reports/validation/GSE140829/v1/score_W1.tsv"), g = c("CTL", "AD"), lab = c("Control", "AD"), col = c(grey_, green)),
  list(t = "c   GSE99039 (Parkinson's disease)", d = tsv("reports/specificity/GSE99039/v1/IPD__score_W1.tsv"), g = c("CONTROL", "IPD"),
       lab = c("Control", "Idiopathic PD"), col = c(grey_, purple)))
both("Figure3_score_distributions", 10.5, 4.2, function() {
  graphics::layout(matrix(1:3, ncol = 3), widths = c(1, 1, 1))
  set.seed(1)
  for (p in sc) {
    setpar(c(4.2, 4.4, 3, 0.8))
    d <- unique(p$d[p$d$group %in% p$g, ]); f <- factor(d$group, levels = p$g)
    graphics::boxplot(d$S ~ f, names = p$lab, outline = FALSE, col = alpha(p$col, 0.35), border = sub, axes = FALSE,
                      xlab = "", ylab = if (identical(p, sc[[1]])) "Signature score (higher = more AD-like)" else "", boxwex = 0.6,
                      ylim = range(d$S))
    graphics::points(jitter(as.integer(f), 0.55), d$S, pch = 16, cex = 0.35, col = alpha(p$col[as.integer(f)], 0.75))
    graphics::axis(2); graphics::axis(1, at = seq_along(p$g), labels = p$lab, tick = FALSE, padj = 0.6, cex.axis = 0.72)
    graphics::mtext(sprintf("n=%d", as.integer(table(f))), side = 1, at = seq_along(p$g), line = 2.9, cex = 0.55, col = sub)
    frame_(); panel_tag(p$t)
  }
})

# ---- Figure 5: per-gene agreement in GSE63061 and GSE140829
ca61 <- tsv("reports/validation/GSE63061/v1/c_a_per_gene.tsv"); ca140 <- tsv("reports/validation/GSE140829/v1/c_a_per_gene.tsv")
both("Figure5_gene_agreement", 10, 4.8, function() {
  graphics::layout(matrix(1:2, ncol = 2))
  for (p in list(list(ca61, "beta_GSE63061", "consistent_q_lt_0.05", "a   GSE63061 (related cohort)", blue, "consistent"),
                 list(ca140, "beta_GSE140829", "replicated_q_lt_0.05", "b   GSE140829 (replication)", green, "replicated"))) {
    setpar(); m <- merge(sig[, c("entrez_gene_id", "beta_AD_minus_CTL")], p[[1]], by = "entrez_gene_id")
    hit <- m[[p[[3]]]] %in% c(TRUE, "True")
    graphics::plot(m$beta_AD_minus_CTL, m[[p[[2]]]], type = "n", axes = FALSE,
                   xlab = expression("Discovery effect, GSE63060 (log"[2]*")"), ylab = "Effect in this cohort (AD minus control)")
    graphics::abline(h = 0, v = 0, col = grid_)
    graphics::points(m$beta_AD_minus_CTL, m[[p[[2]]]], pch = 16, cex = 0.7, col = ifelse(hit, p[[5]], alpha(grey_, 0.9)))
    graphics::axis(1); graphics::axis(2); frame_()
    graphics::legend("topleft", bty = "n", pch = 16, col = c(p[[5]], grey_), cex = 0.7, text.col = ink,
                     legend = c(sprintf("%s at q < 0.05 (%d of 200)", p[[6]], sum(hit)), "not significant"))
    panel_tag(p[[4]])
  }
})

# ---- Figure 6: leukocyte composition
cs <- tsv("reports/discovery/GSE63060/s11_v1/cell_scores.tsv")
oof <- tsv("reports/ml/GSE63060/v1/oof_predictions_averaged.tsv")
cs$grp <- factor(ifelse(oof$y[match(cs$gsm, oof$array)] == 1, "AD", "Control"), levels = c("Control", "AD"))
s11 <- tsv("reports/discovery/GSE63060/s11_v1/gene_level_results_S11.tsv")
ext140 <- tsv("reports/s11_ext/v1/GSE140829__c_a_per_gene.tsv")
cells <- c(T_cells = "T cells", B_lineage = "B lineage", NK_cells = "NK cells", Monocytic_lineage = "Monocytic", Neutrophils = "Neutrophils")
both("Figure6_leukocyte_composition", 11, 4.3, function() {
  graphics::layout(matrix(1:3, ncol = 3), widths = c(1.3, 1, 1))
  setpar(c(4.2, 4.4, 3, 0.8))
  at <- rep(seq_along(cells) * 3, each = 2) + c(-0.55, 0.55)
  vals <- unlist(lapply(names(cells), function(k) split(cs[[k]], cs$grp)), recursive = FALSE)
  graphics::boxplot(vals, at = at, outline = FALSE, col = alpha(c(grey_, orange), 0.45), border = sub, axes = FALSE, boxwex = 0.9,
                    xlim = c(1.5, length(cells) * 3 + 1.5), ylim = c(-2, 2.6), ylab = "Marker index (z-score)", xlab = "")
  graphics::axis(2); graphics::axis(1, at = seq_along(cells) * 3, labels = cells, tick = FALSE, cex.axis = 0.72); frame_()
  graphics::legend("top", horiz = TRUE, bty = "n", fill = alpha(c(grey_, orange), 0.45), border = sub, cex = 0.7, text.col = ink,
                   legend = c(sprintf("Control (n=%d)", sum(cs$grp == "Control")), sprintf("AD (n=%d)", sum(cs$grp == "AD"))))
  panel_tag("a   Leukocyte indices, GSE63060")
  sc_ <- function(x, y, xl, yl, col, tag, note) {
    setpar(); lim <- range(c(x, y), na.rm = TRUE)
    graphics::plot(x, y, type = "n", xlim = lim, ylim = lim, axes = FALSE, xlab = xl, ylab = yl)
    graphics::abline(h = 0, v = 0, col = grid_); graphics::abline(0, 1, lty = 2, col = sub)
    graphics::points(x, y, pch = 16, cex = 0.65, col = alpha(col, 0.8)); graphics::axis(1); graphics::axis(2); frame_()
    graphics::text(lim[1], lim[2], note, adj = c(0, 1), cex = 0.68, col = ink); panel_tag(tag)
  }
  m <- merge(sig[, c("entrez_gene_id", "beta_AD_minus_CTL")], s11[, c("feature_id", "estimate")], by.x = "entrez_gene_id", by.y = "feature_id")
  m <- m[m$entrez_gene_id != 915, ]
  sc_(m$beta_AD_minus_CTL, m$estimate, "Effect, primary model", "Effect, composition-adjusted", blue,
      "b   Discovery: signature survives", "199 of 199 genes still\nsignificant, same direction")
  m2 <- merge(ca140[, c("entrez_gene_id", "beta_GSE140829")], ext140[, c("entrez_gene_id", "beta_GSE140829")], by = "entrez_gene_id",
              suffixes = c("_primary", "_adj"))
  sc_(m2$beta_GSE140829_primary, m2$beta_GSE140829_adj, "Effect, primary model", "Effect, composition-adjusted", green,
      "c   GSE140829: signal shrinks", "replicated genes: 43 to 1\n(post hoc analysis)")
})

# ---- Figure 7: classifier discrimination
rm_ <- tsv("reports/ml/GSE63060/v1/repeat_metrics.tsv"); perm <- tsv("reports/ml/GSE63060/v1/permutation_null.tsv")
e61 <- tsv("reports/ml/GSE63061_external/v1/external_metrics.tsv"); e140 <- tsv("reports/ml/GSE140829_external/v1/external_metrics.tsv")
p61 <- tsv("reports/ml/GSE63061_external/v1/external_predictions.tsv"); p140 <- tsv("reports/ml/GSE140829_external/v1/external_predictions.tsv")
dav <- tsv("reports/ml/GSE63060/v1/delong_auc_averaged.tsv")
roc <- function(s, y) { o <- order(-s); y <- y[o]; s <- s[o]; keep <- c(diff(s) != 0, TRUE)
  tpr <- c(0, cumsum(y)[keep] / sum(y)); fpr <- c(0, cumsum(1 - y)[keep] / sum(1 - y))
  list(fpr = fpr, tpr = tpr, auc = sum(diff(fpr) * (head(tpr, -1) + tail(tpr, -1)) / 2)) }
curves <- list(list(roc(oof$ridge, oof$y), dav$auc[dav$model == "ridge"], "GSE63060, cross-validated", blue, 1),
               list(roc(p61$ridge, p61$y), e61$auc[e61$model == "ridge"], "GSE63061, frozen model", purple, 1),
               list(roc(p140$ridge, p140$y), e140$auc[e140$model == "ridge"], "GSE140829, frozen model", green, 1))
for (cv in curves) if (abs(cv[[1]]$auc - cv[[2]]) > 1e-6) stop("ROC AUC does not match accepted AUROC: ", cv[[3]])
obs <- mean(rm_$auroc[rm_$model == "ridge"])
both("Figure7_classifier", 11.5, 4.2, function() {
  graphics::layout(matrix(1:3, ncol = 3), widths = c(1.15, 1, 1))
  setpar(c(4.6, 4.4, 3, 0.8))
  mods <- c("ridge", "elastic_net", "B2_equal_weight", "B1_age"); labs <- c("Ridge", "Elastic net", "Equal-weight", "Age only")
  dat <- lapply(mods, function(k) rm_$auroc[rm_$model == k])
  graphics::boxplot(dat, ylim = c(0.4, 1), axes = FALSE, col = alpha(c(blue, blue, grey_, grey_), 0.4), border = sub,
                    ylab = "AUROC (20 repeats of nested CV)", boxwex = 0.55)
  graphics::abline(h = 0.5, lty = 2, col = sub); graphics::axis(2)
  graphics::axis(1, at = 1:4, labels = labs, tick = FALSE, cex.axis = 0.72); frame_()
  panel_tag("a   Discovery cohort GSE63060")
  setpar(c(4.6, 4.4, 3, 0.8))
  graphics::hist(perm$mean_auroc, breaks = seq(0.3, 0.9, 0.02), col = alpha(grey_, 0.8), border = "white", xlim = c(0.3, 0.9),
                 main = "", xlab = "AUROC under shuffled labels", ylab = "Permutations", axes = FALSE)
  graphics::axis(1); graphics::axis(2); frame_()
  graphics::abline(v = obs, col = blue, lwd = 2.5)
  graphics::text(obs, par("usr")[4] * 0.9, sprintf("observed\n%.3f", obs), pos = 2, cex = 0.7, col = blue)
  panel_tag("b   Permutation null (200 shuffles)")
  setpar(c(4.6, 4.4, 3, 0.8))
  graphics::plot(0:1, 0:1, type = "n", axes = FALSE, xlab = "1 - specificity", ylab = "Sensitivity", xaxs = "i", yaxs = "i")
  graphics::abline(0, 1, lty = 2, col = sub)
  for (cv in curves) graphics::lines(cv[[1]]$fpr, cv[[1]]$tpr, col = cv[[4]], lwd = 2, type = "s")
  graphics::axis(1); graphics::axis(2); frame_()
  graphics::legend("bottomright", bty = "n", lwd = 2, col = sapply(curves, `[[`, 4), cex = 0.66, text.col = ink,
                   legend = sapply(curves, function(cv) sprintf("%s (AUROC %.2f)", cv[[3]], cv[[2]])))
  panel_tag("c   ROC curves")
})
cat("result figures written to", out, "\n")
