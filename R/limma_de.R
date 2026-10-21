# BIO-MB-001 D8 limma runner (approved method: lmFit + eBayes(trend = TRUE, robust = FALSE)).
#
# Invoked by src/biomarker_project/limma_backend.py with the project root as working directory, so
# the project .Rprofile activates the renv library. Refuses to run unless R, Bioconductor, limma,
# renv, BiocManager and statmod match the pins passed on the command line (exit status 3).
#
# Usage:
#   Rscript R/limma_de.R --check  <pins>  --info OUT.tsv
#   Rscript R/limma_de.R --fit    <pins>  --info OUT.tsv --expression E.tsv --design X.tsv
#                                          --coef NAME --confint 0.95 --out RESULTS.tsv
# <pins> = --R 4.6.1 --bioc 3.23 --limma 3.68.5 --renv 1.3.1 --BiocManager 1.30.27 --statmod 1.5.2
#
# Inputs: E.tsv = feature_id + one column per sample; X.tsv = sample_id + one column per design
# column, rows in the same sample order as E.tsv's columns. Numbers are written with 17
# significant digits. The confidence interval is topTable(confint = 0.95): coefficient
# +/- qt(0.975, df.total) * sqrt(s2.post) * stdev.unscaled (moderated SE and moderated df).

args <- commandArgs(trailingOnly = TRUE)
opt <- function(name, default = NULL) {
  i <- match(paste0("--", name), args)
  if (is.na(i)) default else args[i + 1]
}
mode <- if ("--check" %in% args) "check" else if ("--fit" %in% args) "fit" else stop("need --check or --fit")
pin_names <- c("R", "bioc", "limma", "renv", "BiocManager", "statmod")
pins <- vapply(pin_names, function(n) { v <- opt(n); if (is.null(v) || is.na(v)) NA_character_ else v }, character(1))
if (anyNA(pins)) {
  message("MISSING VERSION PINS: ", paste(pin_names[is.na(pins)], collapse = ", "))
  quit(status = 3)
}

pkg_version <- function(p) tryCatch(as.character(utils::packageVersion(p)), error = function(e) NA_character_)
limma_desc <- tryCatch(utils::packageDescription("limma"), error = function(e) NULL)
# Bioconductor release of the installed limma build: DESCRIPTION "Repository: Bioconductor 3.23".
bioc_repo <- if (is.null(limma_desc) || is.null(limma_desc$Repository)) NA_character_ else limma_desc$Repository
bioc_from_branch <- sub("^Bioconductor ", "", bioc_repo)
renv_bioc <- tryCatch(as.character(renv::settings$bioconductor.version()), error = function(e) NA_character_)

found <- c(R = paste(R.version$major, R.version$minor, sep = "."),
           bioc = if (identical(bioc_from_branch, renv_bioc)) renv_bioc else
             paste0("inconsistent(limma Repository ", bioc_repo, "; renv setting ", renv_bioc, ")"),
           limma = pkg_version("limma"), renv = pkg_version("renv"),
           BiocManager = pkg_version("BiocManager"), statmod = pkg_version("statmod"))
limma_path <- tryCatch(find.package("limma"), error = function(e) NA_character_)

info <- c(sprintf("found_%s\t%s", names(found), found),
          sprintf("pinned_%s\t%s", names(pins), pins),
          sprintf("R_home\t%s", R.home()),
          sprintf("Rscript\t%s", file.path(R.home("bin"), "Rscript")),
          sprintf("limma_path\t%s", limma_path),
          sprintf("lib_paths\t%s", paste(.libPaths(), collapse = ";")),
          sprintf("platform\t%s", R.version$platform))
info_path <- opt("info")
if (!is.null(info_path)) writeLines(info, info_path)

mismatch <- names(pins)[is.na(found[names(pins)]) | found[names(pins)] != pins]
if (length(mismatch)) {
  message("VERSION MISMATCH: ", paste(sprintf("%s found %s, pinned %s", mismatch, found[mismatch], pins[mismatch]),
                                      collapse = "; "))
  quit(status = 3)
}
if (mode == "check") quit(status = 0)

suppressPackageStartupMessages(library(limma))
E <- utils::read.delim(opt("expression"), check.names = FALSE, row.names = 1, colClasses = c("character"))
E <- as.matrix(data.frame(lapply(E, as.numeric), check.names = FALSE, row.names = rownames(E)))
X <- utils::read.delim(opt("design"), check.names = FALSE, row.names = 1)
X <- as.matrix(X)
stopifnot(identical(colnames(E), rownames(X)), all(is.finite(E)), all(is.finite(X)))
coef <- opt("coef")
confint <- as.numeric(opt("confint", "0.95"))
stopifnot(coef %in% colnames(X), confint > 0, confint < 1)

fit <- lmFit(E, X)
eb <- eBayes(fit, trend = TRUE, robust = FALSE)
tt <- topTable(eb, coef = coef, number = Inf, sort.by = "none", adjust.method = "BH", confint = confint)
stopifnot(identical(rownames(tt), rownames(E)))
se <- sqrt(eb$s2.post) * eb$stdev.unscaled[, coef]
s2_prior <- if (length(eb$s2.prior) == 1) rep(eb$s2.prior, nrow(E)) else eb$s2.prior
df_prior <- if (length(eb$df.prior) == 1) rep(eb$df.prior, nrow(E)) else eb$df.prior
out <- data.frame(feature_id = rownames(E), estimate = tt$logFC, std_error = se, ci_low = tt$CI.L, ci_high = tt$CI.R,
                  t_statistic = tt$t, df_total = eb$df.total, p_value = tt$P.Value, q_value_bh = tt$adj.P.Val,
                  ave_expr = tt$AveExpr, sigma = eb$sigma, df_residual = eb$df.residual, df_prior = df_prior,
                  s2_prior = s2_prior, s2_post = eb$s2.post, stdev_unscaled = eb$stdev.unscaled[, coef],
                  check.names = FALSE)
num <- vapply(out, is.numeric, logical(1))
out[num] <- lapply(out[num], function(v) sprintf("%.17g", v))
utils::write.table(out, opt("out"), sep = "\t", quote = FALSE, row.names = FALSE)
if (!is.null(info_path)) {
  si <- utils::capture.output(print(utils::sessionInfo()))
  writeLines(c(info, sprintf("method\tlmFit + eBayes(trend = TRUE, robust = FALSE); topTable(confint = %s, adjust.method = 'BH')", confint),
               paste0("sessionInfo\t", si)), info_path)
}
