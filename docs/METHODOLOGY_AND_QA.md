# Methodology and Q&A notes

## What this project asks
Predict the regime label (1, 2, 3, or 5) of each Hawaiian reef site from the 20 source predictors `Effluent` through `Depth`.

## Why the changes are defensible
1. Use a clean scikit-learn pipeline instead of fragile, cell-order-dependent notebooks.
2. Keep the source target (`Regime`) separate from inputs; drop the one-hot `Regime1`, `Regime2`, `Regime3`, and `Regime5` columns from predictors.
3. Perform imputation/scaling within the CV fold via pipelines.
4. Compare models on identical stratified folds, choosing by macro-F1 so all four classes matter more evenly.
5. Preserve a held-out stratified test set and use it only after cross-validation selects the model.
6. Save metrics and figures programmatically so the write-up and deck reflect the executed model run.

## Likely judge questions

**Why macro-F1?** It averages per-class F1 equally and is more informative than accuracy when class sizes differ. Micro-F1 is still reported for comparison; in single-label multiclass classification it equals accuracy.

**Why omit the ecological columns and regime one-hot columns?** The four regime indicator columns are direct encodings of the target, which would leak the answer. Other ecological response variables are not part of the stated 20-predictor task; using them would change the problem relative to the reference dataset's predictor subset.

**Why median imputation?** It is a robust baseline for missing numeric features and is fitted within each training fold. The original Stanford project explored a K-means-based imputation approach; this project makes a small methodological change to a simpler leakage-safe baseline. Performance may differ.

**Does an important feature cause a regime?** No. Permutation importance measures how much a fitted model relies on a feature for predictive performance. It does not establish causation.

**Can we generalize to reefs outside Hawaii?** Not from this dataset alone. External regions and independent data are needed to test transfer.

**Why are the classes 1, 2, 3, and 5?** They are nominal regime labels from the source classification. Regime 4 was excluded in the published high-confidence subset due to high variability; we do not infer a missing class 4.

## Source references
- Cheng, Murphy & Walecka, Stanford CS229 project report: https://cs229.stanford.edu/proj2019spr/report/56.pdf
- Stanford project poster: https://cs229.stanford.edu/proj2019spr/poster/56.pdf
- Jouffray et al. (2019), *Parsing human and biophysical drivers of coral reef regimes*: https://doi.org/10.1098/rspb.2018.2544
- Official dataset repository: https://github.com/JBjouffray/Hawaii_RegimesPredictors
