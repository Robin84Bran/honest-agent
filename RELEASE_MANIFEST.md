# Release manifest

Unpublished staging copy built 9 Nov 2026 from the private project folder. Originals are unchanged.

## Redacted files

| File | Original SHA-256 | Release SHA-256 | Frozen? |
|---|---|---|---|
| `v0.3/README.md` | `f827acd5cd0186d0e7208e13587ad2d7e419af2205dbefdb75e45fccf5a25f96` | `beeda9b3a1163f42f6dc2b0194a6485a30003d8a72c1b15f42ffd0a68541aa83` | no |
| `v0.3/providers_api.py` | `726c7ecc83f0975cd09af04eede3248739e046c6060771d65257e1ed998abef9` | `7778e862a08d54ecc9b0ba15325687401ed5b749620d8e00e21a2d29a12010c3` | yes |
| `v0.3/results/ollama.log` | `6c93f395db8784fbc221971827720f20a68571ba922592ac051c0011e6c4d726` | `7389e9ebd68d6ea44e6857c1c3aa8d17cc58d27cb941118f690e397dc2e42663` | no |

| `v0.2/action-budget/runs/model.json` | `b7e15e896c3cbbc2f14300d0276d3b9936a8d548e5639e889cca2c045fd79ac9` | `a3ac28f71951da51ce4ef851c0bfdc62a772921f4e08666d27d3f2bf4bed0779` | yes (hashed in `runs/manifest.json`) |
| `appendix/obedient-rebel/README.md` | `82ec999e24502e2587d810e3db72e1fe9c773a85d3ea50ba5d9a4f771fa26468` | `c11eebaa1e4caf512fa1131471eefdae6453ccfdadb4e653b2d8c56624ab0103` | no (listed in its own `MANIFEST.sha256`) |

For `providers_api.py` the original hash equals the one in `freeze.json`; only the two CLI path constants differ.

For `v0.2/action-budget/runs/model.json`, the original hash equals the one in `v0.2/action-budget/runs/manifest.json`. The only change is in the Modelfile line `FROM …/blobs/sha256-1837…`: the local Ollama store path before `/blobs/` was replaced with `<local-ollama-store>`. Because of this, the unchanged `v0.2/action-budget/analyze.py` stops at its hash check on this copy by design. `v0.2/verify_release.py` runs that unchanged analysis, accepting this one file only if it has the redacted hash above, and confirms the regenerated statistics equal `analysis.json`.

## Added for release

- `v0.2/` was added on 9 Nov 2026, after the v0.3 release was first staged. It was copied from the private project folder, where v0.2 lives at the project root; the project's `README.md` became `v0.2/README.md`. Links inside v0.2 are relative, so they still resolve. Apart from the redaction above, no v0.2 file changed.
- `v0.2/verify_release.py` is a release-only helper, not part of v0.2's evidence.
- `appendix/` was added on 10 Nov 2026. It holds the release files of two sister projects, The Obedient Rebel and The Swarm Illusion, copied from their private project folders without the Codex working folders (`codex-workspace-2026-11-08/`). Only one file changed: in `appendix/obedient-rebel/README.md`, a local folder name was replaced by its path in this repository. As a result, that one line of `appendix/obedient-rebel/MANIFEST.sha256` doesn't match on this copy; the frozen files in its `freeze.sha256` are unaffected, and `experiment.py --verify` passes.
- `index.html` at the repository root is a landing page for the whole package, added on 10 Nov 2026.

## Left out

- `v0.3/HANDOFF.md` (internal agent prompt)
- `v0.3/results/EXECUTIVE_SUMMARY.md` (internal briefing; superseded by `WRITEUP.md`)
- `__pycache__/`, `.DS_Store`
- The project's `PROJECT_STATE.md`, a stale internal status note
- `models/` (local Ollama store, ~940 MB; pull `qwen2.5:1.5b`, digest `65ec0654…`, instead)

## Checksums

`SHA256SUMS` covers every file in this folder except itself and this manifest.
