# D8 reference-data record — MCP-counter marker list (2026-10-21)

Authorization: explicit PI instruction 2026-10-21 ("approve MCP-counter download"), under D21 option K1 (v7:624).
- Source: https://github.com/ebecht/MCPcounter, commit 6b85a671cfa8385798cea6147b6613a172e47ff5 (2020-06-18).
- Files (curl over HTTPS, --max-filesize 1 MB; plain ASCII text; nothing executed or installed):
  - Signatures/genes.txt: 5,342 bytes, SHA-256 408f6c5d02c8f9bd2f1599c598367881853520934f8ce398a4886a8b296922bb (112 lines)
  - Signatures/License.txt: 6,488 bytes, SHA-256 a2a7150a5cc1cbe08d513b7bae7c45362e34e8bb2851b31434f527a16817e2f0 (CC0 1.0 Universal)
- Stored at reference/mcpcounter_6b85a67/ with download_manifest.json and SHA256SUMS. Never edited.
- No R package was installed; renv.lock is unchanged.
- Limitation: the MCP-counter markers were developed mainly for tissue and tumour samples, not whole blood. The scores are
  relative abundance indices, not proportions.
