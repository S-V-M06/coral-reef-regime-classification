# Submission validation checklist (team-owned)

## Automated work included in this bundle
- [x] Runnable command-line pipeline and dependency list.
- [x] Official data URL and row/label schema validation.
- [x] Target/input boundary prevents target-derived regime dummy columns from entering features.
- [x] Missing-value imputation is kept inside the model pipeline.
- [x] Stratified 80/20 split with fixed seed.
- [x] Five-fold stratified CV on training data only.
- [x] Macro-F1 model selection and micro-F1/weighted-F1/accuracy reporting.
- [x] One held-out test evaluation for the CV-selected model.
- [x] Per-class classification report, confusion matrix and permutation-importance artifacts.
- [x] Script-generated PDF write-up and slide deck populated from measured run outputs.
- [x] Unit tests for feature boundaries and model pipeline fit/predict.

## You and your teammate must complete before submission
- [x] Dependencies were installed in the Windows environment; the pipeline completed successfully in the provided terminal screenshot.
- [x] Run `python run_project.py`; the seven-stage pipeline completed and generated the listed outputs.
- [x] Dataset audit confirms 620 observations and regime labels 1, 2, 3 and 5.
- [x] Results bundle was reviewed; model metrics, class counts and confusion matrix were checked for consistency. Team should still review the figures before presenting.
- [x] Package review test run in the validation environment: `python -m pytest -q` -> 3 passed. Run again in the team's Windows environment before submission if not already recorded.
- [x] PDF numbers match the CSV/JSON results reviewed in the results bundle.
- [x] Updated `TEAM_MEMBERS.txt` with the names present in the supplied documents, regenerated the polished PDF/PPTX without retraining, and visually checked layout/rendering. [ ] Confirm both entries are the official full names and correct the file if needed.
- [ ] Add both members' actual contributions; do not claim work no one performed.
- [ ] Create/push the extracted project contents to a **private** GitHub repository and grant access to faculty/assigned TAs; do not commit `.venv`, caches, or secrets.
- [ ] Verify the README works from a clean clone/new environment; never commit private tokens.
- [ ] Rehearse the live demo and each teammate's Q&A segment.
- [ ] Ask the faculty whether the write-up should be one page or two pages: the brief heading says “One-Page Write-up”, while its body says “two-page summary”.
- [ ] Confirm whether a late submission/review is accepted; the listed deadline was 10 October 2026 at 11:59 PM.
