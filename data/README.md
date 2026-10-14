# Dataset

The project uses the public source file `Hawaii_RegimesPredictors.txt` maintained in the research repository:

- https://github.com/JBjouffray/Hawaii_RegimesPredictors/blob/master/Data/Hawaii_RegimesPredictors.txt
- Direct download used by the code: https://raw.githubusercontent.com/JBjouffray/Hawaii_RegimesPredictors/master/Data/Hawaii_RegimesPredictors.txt

On the first run, `run_project.py` downloads the original tab-delimited file to this folder. Decimal commas are parsed as numeric decimal separators. The code validates that the expected 620 rows and regime labels [1, 2, 3, 5] are present. Do not replace it with the separate 1,027-row ecological-regime table; that is a different dataset.
