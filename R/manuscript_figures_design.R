# BIO-MB-001 manuscript design figures (base R only): study design and model anatomy.
# Descriptive drawings of accepted outputs; no statistics are computed.
# Usage (project root): Rscript R/manuscript_figures_design.R <outdir>
args <- commandArgs(trailingOnly = TRUE)
out <- if (length(args)) args[1] else "reports/manuscript/medrxiv/figures"
dir.create(out, showWarnings = FALSE, recursive = TRUE)
both <- function(name, w, h, f) {
  grDevices::png(file.path(out, paste0(name, ".png")), width = w, height = h, units = "in", res = 300); f(); grDevices::dev.off()
  grDevices::pdf(file.path(out, paste0(name, ".pdf")), width = w, height = h); f(); grDevices::dev.off()
}
q <- function(c, key) { s <- utils::read.delim(sprintf("reports/qc_stage_b/%s/v1/summary.tsv", c), stringsAsFactors = FALSE)
  as.integer(s$n[startsWith(s$quantity, key)][1]) }
js <- paste(readLines("reports/discovery/GSE63060/fit_v1/discovery_summary.json", warn = FALSE), collapse = "")
gene_sig <- as.integer(sub('.*"gene_level": *\\{[^}]*"n_q_lt_0.05": *([0-9]+).*', "\\1", js))
genes <- utils::read.csv("reports/ml/GSE63060/v1_readable_model_genes.csv", stringsAsFactors = FALSE)
st <- utils::read.delim("reports/ml/GSE63060/v1/final_model_settings.tsv")
n_in <- st$n_genes_input[1]; thr <- st$threshold[1]; k <- st$k[1]

ink <- "#1d2733"; sub <- "#5b6675"; line <- "#9aa5b1"
pal <- list(disc = c("#e6eef8", "#2b5b8f"), rel = c("#eef1f4", "#5b6675"), rep = c("#e7f3ee", "#2d7a57"),
            spec = c("#f1ecf7", "#6a4c93"), ml = c("#fbf1e4", "#a3601a"))
rbox <- function(x0, y0, x1, y1, col, r = 1.6) {
  t <- seq(0, pi / 2, length.out = 12)
  xs <- c(x1 - r + r * cos(t), x0 + r - r * sin(t), x0 + r - r * cos(t), x1 - r + r * sin(t))
  ys <- c(y1 - r + r * sin(t), y1 - r + r * cos(t), y0 + r - r * sin(t), y0 + r - r * cos(t))
  graphics::polygon(xs, ys, col = col[1], border = col[2], lwd = 1.4)
}
arrow <- function(x0, y0, x1, y1, col = line, lty = 1) graphics::arrows(x0, y0, x1, y1, length = 0.08, angle = 22, col = col, lwd = 1.6, lty = lty)
txt <- function(x, y, s, cex = 0.8, col = ink, font = 1, adj = 0.5) graphics::text(x, y, s, cex = cex, col = col, font = font, adj = adj)

# ---- Study design
both("Figure1_study_design", 11, 7, function() {
  graphics::par(mar = c(0.4, 0.4, 0.4, 0.4), family = "sans"); graphics::plot.new(); graphics::plot.window(c(0, 100), c(0, 100))
  cohorts <- list(
    list("GSE63060", "Discovery", "AddNeuroMed batch 1, Illumina HT-12 v3", q("GSE63060", "R1 universe"),
         sprintf("%d AD, %d CTL", q("GSE63060", "primary population AD"), q("GSE63060", "primary population CTL")),
         sprintf("%d sex-discordant controls removed", q("GSE63060", "Q1 among")), pal$disc),
    list("GSE63061", "Related cohort", "AddNeuroMed batch 2, possible overlap", q("GSE63061", "R1 universe"),
         sprintf("%d AD, %d CTL", q("GSE63061", "primary population AD"), q("GSE63061", "primary population CTL")), "consistency, not replication", pal$rel),
    list("GSE140829", "Replication", "HT-12 v4 (nuID), independence unverified", q("GSE140829", "R1 universe"),
         sprintf("%d AD, %d CTL", q("GSE140829", "primary population AD"), q("GSE140829", "primary population CTL")), "4 unpartnered replicates set aside", pal$rep),
    list("GSE99039", "Specificity", "Parkinson's disease, Affymetrix U133+2", q("GSE99039", "R1 universe"),
         sprintf("IPD %d / GPD %d / GU %d / CTL %d", q("GSE99039", "primary population IPD"), q("GSE99039", "primary population GPD"),
                 q("GSE99039", "primary population GENETIC_UNAFFECTED"), q("GSE99039", "primary population CONTROL")), "two-sided, Holm across 3 contrasts", pal$spec))
  xs <- c(2, 27, 52, 77); w <- 21
  txt(50, 97.5, "Pre-specified eligibility and quality control in every cohort (rule-applied exclusion lists approved before modelling)", cex = 0.78, col = sub)
  for (i in seq_along(cohorts)) {
    c <- cohorts[[i]]; x0 <- xs[i]; rbox(x0, 72, x0 + w, 94, c[[7]])
    txt(x0 + w / 2, 90.5, c[[1]], cex = 1.05, font = 2, col = c[[7]][2]); txt(x0 + w / 2, 87, c[[2]], cex = 0.82, font = 2)
    txt(x0 + w / 2, 83.8, c[[3]], cex = 0.58, col = sub)
    txt(x0 + w / 2, 80.3, sprintf("%d arrays deposited", c[[4]]), cex = 0.66, col = sub); txt(x0 + w / 2, 77.3, c[[5]], cex = if (nchar(c[[5]]) > 22) 0.62 else 0.74, font = 2)
    txt(x0 + w / 2, 74.4, c[[6]], cex = 0.6, col = sub)
  }
  # discovery chain
  rbox(2, 44, 23, 66, pal$disc)
  txt(12.5, 62.5, "Differential expression", cex = 0.82, font = 2, col = pal$disc[2])
  txt(12.5, 58.5, "limma, age, sex, chip", cex = 0.66, col = sub)
  txt(12.5, 54.5, sprintf("%s genes at FDR < 0.05", format(gene_sig, big.mark = ",")), cex = 0.72, font = 2)
  txt(12.5, 50.5, "14 sensitivity analyses", cex = 0.62, col = sub)
  txt(12.5, 46.8, "Signature locked: 200 genes", cex = 0.72, font = 2, col = pal$disc[2])
  arrow(12.5, 72, 12.5, 66.3, pal$disc[2])
  # tests of the locked signature
  tests <- list(c(37.5, "Consistency test", "composite score, per gene", pal$rel), c(62.5, "Replication test", "composite score, per gene", pal$rep),
                c(87.5, "Specificity test", "two-sided score test", pal$spec))
  for (t in tests) { x <- as.numeric(t[1]); col <- t[4:5]
    rbox(x - 10, 48, x + 10, 62, col); txt(x, 57.6, t[2], cex = 0.76, font = 2, col = t[5]); txt(x, 52.8, t[3], cex = 0.62, col = sub)
    arrow(x, 72, x, 62.3, t[5]) }
  graphics::segments(23.2, 47, 89, 47, col = pal$disc[2], lwd = 1.6)
  for (x in c(37.5, 62.5, 87.5)) arrow(x, 47, x, 48, pal$disc[2])
  txt(55, 45.2, "the same locked signature, unchanged", cex = 0.6, col = pal$disc[2])
  # classifier chain
  rbox(2, 16, 23, 38, pal$ml)
  txt(12.5, 34.5, "Classifier", cex = 0.85, font = 2, col = pal$ml[2])
  txt(12.5, 30.5, "ridge, genes chosen inside folds", cex = 0.62, col = sub)
  txt(12.5, 27, "nested, chip-grouped CV", cex = 0.66, col = sub)
  txt(12.5, 23.3, "200-permutation null", cex = 0.62, col = sub)
  txt(12.5, 19.3, "Model frozen", cex = 0.74, font = 2, col = pal$ml[2])
  graphics::segments(12.5, 44, 12.5, 38.3, col = pal$ml[2], lwd = 1.6, lty = 3)
  rbox(27.5, 20, 47.5, 32, pal$ml); txt(37.5, 28.2, "Applied once", cex = 0.74, font = 2, col = pal$ml[2]); txt(37.5, 23.8, "to GSE63061", cex = 0.66, col = sub)
  rbox(52.5, 20, 72.5, 32, pal$ml); txt(62.5, 28.2, "Applied once", cex = 0.74, font = 2, col = pal$ml[2]); txt(62.5, 23.8, "to GSE140829", cex = 0.66, col = sub)
  arrow(23.2, 26, 27.3, 26, pal$ml[2]); graphics::segments(47.7, 26, 52.3, 26, col = pal$ml[2], lwd = 1.6); arrow(51, 26, 52.3, 26, pal$ml[2])
  txt(37.5, 17.6, "no re-fitting, no tuning", cex = 0.58, col = sub)
  # composition band
  rbox(2, 2, 98, 11, list("#f6f6f4", line)[[1]] |> c(line))
  txt(50, 8, "Leukocyte-composition sensitivity: five MCP-counter marker indices added as covariates", cex = 0.72, font = 2)
  txt(50, 4.6, "discovery cohort (S11; method chosen after primary results), replication and specificity cohorts (S11-ext; post hoc)", cex = 0.62, col = sub)
})

# ---- Model anatomy
both("Figure8_model_anatomy", 10, 6.2, function() {
  graphics::layout(matrix(1:2, ncol = 2), widths = c(1, 1.25))
  graphics::par(mar = c(0.5, 0.5, 2.2, 0.5), family = "sans"); graphics::plot.new(); graphics::plot.window(c(0, 100), c(0, 100))
  graphics::title("How a prediction is made", adj = 0, cex.main = 0.95, col.main = ink, font.main = 2, line = 0.6)
  steps <- list(
    c("Blood expression", sprintf("%s genes (sex-chromosome genes removed)", format(n_in, big.mark = ","))),
    c("Centre within chip, standardise", "removes batch shifts; no diagnosis used"),
    c(sprintf("%d genes x learned weights", k), "chosen and weighted inside training folds"),
    c("Add up, convert to probability", "logistic function, 0 to 1"),
    c(sprintf("Probability at least %.3f", thr), "output: AD-like pattern"))
  ys <- seq(90, 10, length.out = length(steps))
  for (i in seq_along(steps)) {
    rbox(6, ys[i] - 7, 94, ys[i] + 7, if (i == 3) pal$ml else if (i == 5) pal$disc else list("#f6f7f9", line)[[1]] |> c(line))
    txt(50, ys[i] + 2.2, steps[[i]][1], cex = 0.82, font = 2); txt(50, ys[i] - 3, steps[[i]][2], cex = 0.64, col = sub)
    if (i < length(steps)) arrow(50, ys[i] - 7.2, 50, ys[i + 1] + 7.2)
  }
  top <- head(genes[order(-abs(genes$weight)), ], 20); top <- top[order(abs(top$weight)), ]
  graphics::par(mar = c(4, 6.2, 2.2, 1))
  cols <- ifelse(top$weight > 0, pal$ml[2], pal$disc[2])
  b <- graphics::barplot(top$weight, horiz = TRUE, names.arg = top$gene_symbol, las = 1, col = cols, border = NA,
                         xlim = range(c(0, top$weight)) * 1.15, cex.names = 0.68, cex.axis = 0.7, col.axis = sub, xlab = "")
  graphics::abline(v = 0, col = line)
  graphics::title("Top 20 of 200 genes by influence", adj = 0, cex.main = 0.95, col.main = ink, font.main = 2, line = 0.6)
  graphics::mtext("weight per standard deviation of expression", side = 1, line = 2.4, cex = 0.62, col = sub)
  graphics::legend("bottomright", bty = "n", fill = c(pal$ml[2], pal$disc[2]), border = NA, cex = 0.62, text.col = ink,
                   legend = c("higher expression: more AD-like", "lower expression: more AD-like"))
})
cat("design figures written to", out, "\n")
