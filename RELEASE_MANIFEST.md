# Release manifest

Unpublished staging copy built 9 Nov 2026 from the private project folder. Originals are unchanged.

## Redacted files

| File | Original SHA-256 | Release SHA-256 | Frozen? |
|---|---|---|---|
| `v0.3/README.md` | `f827acd5cd0186d0e7208e13587ad2d7e419af2205dbefdb75e45fccf5a25f96` | `beeda9b3a1163f42f6dc2b0194a6485a30003d8a72c1b15f42ffd0a68541aa83` | no |
| `v0.3/providers_api.py` | `726c7ecc83f0975cd09af04eede3248739e046c6060771d65257e1ed998abef9` | `7778e862a08d54ecc9b0ba15325687401ed5b749620d8e00e21a2d29a12010c3` | yes |
| `v0.3/results/ollama.log` | `6c93f395db8784fbc221971827720f20a68571ba922592ac051c0011e6c4d726` | `7389e9ebd68d6ea44e6857c1c3aa8d17cc58d27cb941118f690e397dc2e42663` | no |

For `providers_api.py` the original hash equals the one in `freeze.json`; only the two CLI path constants differ.

## Left out

- `v0.3/HANDOFF.md` (internal agent prompt)
- `v0.3/results/EXECUTIVE_SUMMARY.md` (internal briefing; superseded by `WRITEUP.md`)
- `__pycache__/`, `.DS_Store`
- `models/` (local Ollama store, ~940 MB; pull `qwen2.5:1.5b`, digest `65ec0654…`, instead)

## Checksums

`SHA256SUMS` covers every file in this folder except itself and this manifest.
