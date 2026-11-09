"""POST HOC / DEVIATION analysis (declared in SUPPLEMENT_QWEN.md before the supplement ran).

Combines the usable pre-registered held-out rows (claude, gpt) with the Qwen supplement rows and
applies the frozen analyze_v03.analyse() and markdown() unchanged.
Writes results/posthoc-heldout-combined.{json,md}.
"""
import json

import analyze_v03 as A

rows = A.load("heldout") + A.load("heldout_qwen_supplement")
res = A.analyse(rows)
md = A.markdown("heldout + Qwen supplement (POST HOC / DEVIATION, see SUPPLEMENT_QWEN.md)", res)
(A.BASE / "results" / "posthoc-heldout-combined.json").write_text(json.dumps(res, indent=2))
(A.BASE / "results" / "posthoc-heldout-combined.md").write_text(md)
print(md)
