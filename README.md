# ICD-10 Code Validator & Mapper

A Python (pandas) project that validates ICD-10 diagnosis codes, maps local hospital codes to standard codes, and produces an exception report for manual review.

> All data in this project is **synthetic**. No real patient information is used.

## What it does
- Cleans entered codes (extra spaces, lowercase letters)
- Checks the code format using a regular expression
- Automatically fixes a missing dot (for example `J459` becomes `J45.9`) while keeping the original value
- Maps local codes to standard ICD-10 codes with a mapping table (merge)
- Detects local codes that have no mapping
- Classifies each record: unmapped local code, empty code, invalid format, or differs from the mapping table
- Exports an Excel exception report

## Important limitations
- The format check only confirms that a code *looks* like an ICD-10 code. It does not confirm that the code exists in the official classification. A real project would validate against the official code list.
- The valid-code list and mapping table in this repository are small synthetic samples for demonstration.
- Records are classified in a fixed order, so a record with several problems appears under the first matching issue.

## Tools
Python, pandas, numpy, openpyxl

## How to run
1. Install the libraries: `python -m pip install pandas numpy openpyxl`
2. Run: `python validator.py`

## Outputs
- `icd_exception_report.xlsx`: issue summary and the list of records needing review