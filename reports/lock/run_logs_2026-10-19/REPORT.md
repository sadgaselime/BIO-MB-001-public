# Signature lock (Tier B step 11): GSE63060, 2026-10-19

**Authorization:** PI approvals of 2026-10-18 and 2026-10-19 (SAP v7 §11): D15, D16, D7, H1 specification, D12, D20 and D13
(conservative). This is the SAP §7 lock, written **before any validation or specificity expression is modelled against
diagnosis**. The SAP remains a proposed draft (not approved, not frozen).

## Code and tests

- **Runner:** `scripts/signature_lock_gse63060.py`.
- **Tests:** `tests/test_signature_lock.py` 5/5 (selection order and tie-breaks, cap, empty case, excerpt hashing, gate). Full suite **315/315** under the audit hook, with no guarded opens.

## Run

| Item | Value |
|---|---|
| Command | `.venv/bin/python -I scripts/signature_lock_gse63060.py --version v1` |
| Time (UTC) | 2026-10-18T20:56:27Z to 2026-10-18T20:56:30Z |
| Result | exit=0 |
| Output | `reports/lock/GSE63060/v1/` (accepted; executed code tracked; 4/4 checks) |

## Locked signature

- **Selection (D15; v6 §7.1):** gene level q < 0.05 (**1,401 eligible**). Ranked by q, then |β|, then |t|, then Entrez ID; cap 200.
- **Locked: 200 genes. 172 lower in AD, 28 higher in AD.**
- Every gene has a symbol (from the pinned org.Hs.eg.db 3.23.1) and constituent probes in T_GSE63060.
- Effects range from −1.08 to +0.36 (log₂, AD − CTL). The largest locked q is 4.2 × 10⁻⁵.

Top-ranked genes:

| Direction | Genes |
|---|---|
| Lower in AD | NDUFA1, MRPL51, CETN2, NDUFS5, RPL36AL, ATP6V1E1, SEM1, COX17, UFC1, TBCA, RPS23, RPF2, UQCRB, RPA3, ZMAT2 |
| Higher in AD | CREBRF, AKAP17A, LPP, APBB3, LCOR, TYK2, ATP2B1-AS1, TRAPPC14, TCIRG1, SMIM48 |

Several top down-regulated genes are mitochondrial respiratory-chain or ribosomal genes. Whether that reflects a coherent
pathway signal is **exploratory only** (D14, not approved); no pathway or biological claim is made.

## What the lock record contains (`lock_record.json`, v7 §7 items 1–7)

1. **Gene-level unit:** D6 G3, with S8 = G1. T_GSE63060 checksum.
2. **Annotation:** pin record SHA-256, mapping rules, validation feature rule (none). GSE140829 is unmapped until D19.
3. **Per-gene table:** `signature.tsv` (Entrez, symbol, direction, β with 95% CI, SE, moderated t, df, p, q, constituent probes).
4. **Counts.**
5. **Validation specification**, 22 exact SAP excerpts (`sap_excerpts.json`; file, line range and SHA-256 of each), covering:
   - measurability; W1 score and standardization; the coverage rule;
   - C-c (one-sided, L_c); C-a; C-b (descriptive); magnitude comparability;
   - the locked covariates; the claim families (O1 + X1); the GSE63061 correlation;
   - the D12, D15 and D20 register rows.
6. **Specificity specification** (D13 conservative: equivalence not used; no Q2; Holm across the three contrasts): v6 §9.1–9.6, v7 §8.1–8.2 and the D13 row.
7. **Precedence rule and sensitivity definitions:** v7 §5, v6 §10.1 (with a note on its v7 §0.1 status) and the D16 row.

Superseded text (v6 §8.6, §8.8) is excluded, with a note. The record also cites:
- the SHA-256 of the identity record of every contained output (v7:486);
- the D8 environment record hashes;
- the SAP v7 and v6 file hashes.

## Output hashes

| File | SHA-256 |
|---|---|
| `signature.tsv` | `9ca4310ce634b536f5acdfb942d89daa3fc319721d39812fc026af8c41242975` |
| `lock_record.json` | `70b9e4d3ce260778665bafeed491d77efd1ce2f227aa11599f4534980da8f3c9` |
| `sap_excerpts.json` | `89ad980967d9e9e4c20a8009c014b7462b5f494fc932c753a25f0888077bdb48` |
| `manifest.json` | `45ba91d0e44dcee9924d27f6c3dc0fbd20ac37ec502c85d14e39c62d20c612df` |
| `code_identity.json` | `f456cf073b35683cc1b922e88c6939d48e511a62531e5a6a807508bf04fc1239` |

## Next (gates)

**GSE63061 consistency (C-c "consistency", C-a, C-b, the v7 §4.5 correlation).** It needs:
- GSE63061 eligibility and label rules: D2 defines GSE63060 only, and GSE63061 has 6 R5-category labels;
- QC Stage A/B for GSE63061: the QC Stage A ruling covers GSE63060 only;
- a PI go-ahead to run QC on GSE63061.

Possible participant overlap with GSE63060 (H9) is labelled throughout.

**GSE140829 replication:** D11, D19 and its eligibility rules. **GSE99039 specificity:** its eligibility and QC under the locked D13 specification.
