# BIO-MB-001 manuscript figure 4 (base R only): composite score shifts. Descriptive plot of accepted outputs; computes no new statistics.
# Figures 2, 3 and 5-7 are drawn by R/manuscript_figures_results.R; figures 1 and 8 by R/manuscript_figures_design.R.
# Usage (project root): Rscript R/manuscript_figures.R <outdir>
# Inputs: accepted outputs under reports/ (validation, specificity, s11_ext). Writes PNG (300 dpi) and PDF.
args <- commandArgs(trailingOnly = TRUE)
out <- if (length(args)) args[1] else "reports/manuscript/medrxiv/figures"
dir.create(out, showWarnings = FALSE, recursive = TRUE)
js <- function(p) jsonlite_free(p)
# minimal JSON reader for the few numeric fields needed (avoids extra packages)
jsonlite_free <- function(p) paste(readLines(p, warn = FALSE), collapse = "\n")
num <- function(txt, key, after = NULL) {
  if (!is.null(after)) txt <- substring(txt, regexpr(after, txt, fixed = TRUE))
  m <- regmatches(txt, regexpr(paste0('"', key, '": *-?[0-9.eE+-]+'), txt))
  as.numeric(sub('.*: *', '', m))
}
tsv <- function(p) utils::read.delim(p, check.names = FALSE, stringsAsFactors = FALSE)
both <- function(name, w, h, f) {
  grDevices::png(file.path(out, paste0(name, ".png")), width = w, height = h, units = "in", res = 300)
  f(); grDevices::dev.off()
  grDevices::pdf(file.path(out, paste0(name, ".pdf")), width = w, height = h)
  f(); grDevices::dev.off()
}
col_p <- "#2b5b8f"; col_a <- "#c0602a"; col_g <- "#5b6675"; grid_ <- "#e3e7ec"

# ---- Figure 4: composite score shifts with 95% CIs, per cohort (magnitudes not comparable across cohorts)
v61 <- js("reports/validation/GSE63061/v1/validation_summary.json")
v140 <- js("reports/validation/GSE140829/v1/validation_summary.json")
spec <- js("reports/specificity/GSE99039/v1/specificity_summary.json")
ext <- js("reports/s11_ext/v1/s11_ext_summary.json")
cc <- function(txt, after) c(num(txt, "estimate", after), num(txt, "ci_low_two_sided_95", after), num(txt, "ci_high_two_sided_95", after))
q1 <- function(txt, sect, k) { s <- substring(txt, regexpr(paste0('"', sect, '"'), txt, fixed = TRUE)); cc(s, paste0('"', k, '"')) }
lab99 <- list(IPD = "Idiopathic PD", GPD = "Genetic PD", GENETIC_UNAFFECTED = "Genetic unaffected")
panels <- list(
  list(t = "GSE63061 (related cohort)", rows = list(list("Primary", cc(v61, '"C-c"'), col_p))),
  list(t = "GSE140829 (replication)", rows = list(list("Primary", cc(v140, '"C-c"'), col_p),
                                                  list("Adjusted (post hoc)", cc(substring(ext, regexpr('"GSE140829"', ext)), '"C-c"'), col_a))),
  list(t = "GSE99039 (Parkinson's disease)", rows = unlist(lapply(c("IPD", "GPD", "GENETIC_UNAFFECTED"), function(k) {
    s <- substring(ext, regexpr('"GSE99039"', ext))
    list(list(paste(lab99[[k]], "- primary"), q1(spec, "primary", k), col_p),
         list(paste(lab99[[k]], "- adjusted"), cc(s, paste0('"', k, '"')), col_a)) }), recursive = FALSE)))
both("Figure4_score_shifts", 7, 8, function() {
  graphics::layout(matrix(1:3, ncol = 1), heights = c(1.3, 1.8, 3.6))
  graphics::par(mar = c(4, 14, 2.8, 1), oma = c(3.4, 0, 0, 0), cex = 0.85, family = "sans", col.axis = col_g, las = 1, tcl = -0.25,
                mgp = c(2.4, 0.5, 0))
  tags <- c("a", "b", "c")
  for (i in seq_along(panels)) { pn <- panels[[i]]
    n <- length(pn$rows); y <- rev(seq_len(n))
    est <- sapply(pn$rows, function(r) r[[2]][1]); lo <- sapply(pn$rows, function(r) r[[2]][2]); hi <- sapply(pn$rows, function(r) r[[2]][3])
    graphics::plot(est, y, xlim = range(c(lo, hi, 0)), ylim = c(0.5, n + 0.5), yaxt = "n", pch = 19,
                   col = sapply(pn$rows, `[[`, 3), xlab = "Score shift (disease - control), 95% CI", ylab = "", bty = "l", fg = col_g)
    graphics::abline(v = pretty(range(c(lo, hi, 0))), col = grid_)
    graphics::mtext(paste(tags[i], "  ", pn$t), side = 3, adj = 0, line = 1, font = 2, cex = 0.95,
                    at = graphics::grconvertX(0.02, "nfc", "user"))
    graphics::segments(lo, y, hi, y, col = sapply(pn$rows, `[[`, 3), lwd = 2.2)
    graphics::points(est, y, pch = 19, cex = 1.2, col = sapply(pn$rows, `[[`, 3))
    graphics::abline(v = 0, lty = 2, col = col_g)
    graphics::axis(2, at = y, labels = sapply(pn$rows, `[[`, 1), las = 1, tick = FALSE, cex.axis = 0.9)
  }
  graphics::par(xpd = NA)
  graphics::legend(x = graphics::grconvertX(0.5, "ndc", "user"), y = graphics::grconvertY(0.025, "ndc", "user"), xjust = 0.5, horiz = TRUE,
                   bty = "n", pch = 19, lwd = 2.2, col = c(col_p, col_a), cex = 0.8,
                   legend = c("Primary, pre-specified", "Adjusted for leukocyte indices (post hoc)"))
})

cat("figures written to", out, "\n")
