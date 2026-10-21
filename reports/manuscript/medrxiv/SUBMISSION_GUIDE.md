# medRxiv submission guide (prepared 2026-10-21)

## Files in this folder

| File | Use |
|---|---|
| `MANUSCRIPT_medRxiv_v1.pdf` | **The upload file.** The typeset manuscript (A4, 8 figures and 3 tables placed in the text, page numbers). |
| `MANUSCRIPT_medRxiv_v1.docx` | The same manuscript as a Word file, for reading, commenting or small edits. |
| `MANUSCRIPT_medRxiv_v1.md` | Source text. Edit this file if you change wording, then rebuild both files with `bash reports/manuscript/medrxiv/build_manuscript.sh` from the project root. |
| `figures/Figure1–8.png` / `.pdf` | Figures at 300 dpi, in case medRxiv asks for separate figure files. Drawn from the accepted outputs by `R/manuscript_figures_design.R`, `R/manuscript_figures.R` and `R/manuscript_figures_results.R`. |
| `ABSTRACT_for_web_form.txt` | Plain-text abstract to paste into the submission form. |
| `BEFORE_POSTING.md` | The remaining steps that need you, practice questions to defend the paper, and a reader-request email. |
| `check_numbers.py` | Checks the manuscript's key numbers against the accepted outputs (run after any wording change). |
| `make_reference_docx.py`, `manuscript_print.css`, `build_manuscript.sh` | The Word style template, the PDF layout and the build script. |

## Before you submit (checklist)

1. **Read the whole manuscript once.** Every claim should be one you can explain. Ask me about anything that's unclear.
2. Your email is on the title page (done).
3. **Make the public code repository visible** before you submit: github.com/sadgaselime/BIO-MB-001-public → Settings →
   Change visibility → Public. It is a clean copy of the project (current files only, no history and no private
   correspondence). The working repository `BIO-MB-001` stays private.
4. Optional but recommended: ask one researcher to read it first. A posted preprint **cannot be deleted**, only marked
   "withdrawn".
5. Open `MANUSCRIPT_medRxiv_v1.pdf` and check every page, including the figures and tables.

## Submitting

1. Go to **https://www.medrxiv.org** → **Submit a manuscript**, and create an account (free).
2. **Title:** copy it from the manuscript.
3. **Authors:** Sadga Selime; affiliation **Independent researcher**; you are the corresponding author.
4. **Abstract:** paste `ABSTRACT_for_web_form.txt`.
5. **Subject area:** choose **Neurology**. Genetic and Genomic Medicine is an alternative.
6. **Article type:** original research (a secondary analysis of public data with full methods; medRxiv accepts these).
7. **Declarations in the form:**
   - **Ethics:** secondary analysis of openly available, de-identified data; no ethics approval required. The original
     studies' approvals are cited.
   - **Clinical trial:** not applicable.
   - **Funding:** none.
   - **Competing interests:** none.
   - **Data availability:** public GEO data (GSE63060, GSE63061, GSE140829, GSE99039); code and derived outputs in the
     GitHub repository.
   - **Co-author consent:** sole author.
   - **AI use:** described in Methods 2.10, as medRxiv requires; AI is not listed as an author.
8. **Licence:** **CC BY 4.0** is recommended. It's the most open option and allows others to reuse the work with
   attribution.
9. Upload `MANUSCRIPT_medRxiv_v1.pdf`, then submit.

## After submitting

- Screening usually takes **2–4 days**. medRxiv may decline any submission. If it does, we can revise, or post on bioRxiv
  instead (Bioinformatics or Genomics).
- Once it's posted, you get a DOI. Add it to the README and share the preprint with the researchers you cite, for example
  as part of a mentor request.
- The D9 data-owner query is still pending. The manuscript states this, so posting doesn't need to wait for a reply. If a
  reply changes anything, you can post a revised version.
