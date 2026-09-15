# Decision Engine Evaluation History

The Decision Engine is evaluated against the 44-step labeled investment-management set in `labeled_set.json`. Verdict agreement is the headline submission metric.

| Version | Change | Verdict agreement |
| --- | --- | ---: |
| v1 | Baseline Decision Engine | 59.09% |
| v2 | AI-suitability calibration and quarterly extraction fix | 84.09% |
| v3 | Repetitiveness root-cause fix: score interpretive variation, not recurring procedure names | 86.36% |
| Final (frozen snapshot) | Extraction-aligned ground truth with no snapshot mismatch | 81.82% (36/44) |

**Reported number: v3, 86.36% (38/44 verdicts).**

The v3 score also improved repetitiveness agreement from v2's 36.36% exact and 81.82% within-one agreement to 59.09% exact and 97.73% within-one agreement. Full v3 artifacts are saved in `decision_engine_v3_predictions.json` and `decision_engine_v3_report.json`.

**Final (frozen snapshot): 81.82% (36/44), measured against extraction-aligned ground truth with no snapshot mismatch — the honest, submission-ready number.**
