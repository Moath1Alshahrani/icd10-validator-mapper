import pandas as pd

diag = pd.read_csv("local_diagnoses.csv")
# --- Clean ---
diag["Entered_ICD10"] = diag["Entered_ICD10"].str.strip().str.upper()

# --- Format check ---
pattern = r"^[A-Z][0-9]{2}(\.[0-9A-Z]{1,4})?$"
diag["Format_OK"] = diag["Entered_ICD10"].str.match(pattern, na=False)
mapping = pd.read_csv("mapping_table.csv")
valid = pd.read_csv("valid_icd10_sample.csv")

print("Format check:")
print(diag["Format_OK"].value_counts())

print("\nRecords with wrong format:")
print(diag[~diag["Format_OK"]][["Record_ID", "Local_Code", "Entered_ICD10"]])
# --- Fix missing dot (J459 -> J45.9) ---
diag["Code_Fixed"] = diag["Entered_ICD10"].str.replace(
    r"^([A-Z][0-9]{2})([0-9A-Z]{1,4})$", r"\1.\2", regex=True
)
diag["Was_Fixed"] = diag["Entered_ICD10"].notna() & (diag["Code_Fixed"] != diag["Entered_ICD10"])
diag["Format_OK_After"] = diag["Code_Fixed"].str.match(pattern, na=False)

print("\nCodes fixed automatically:", diag["Was_Fixed"].sum())
print("Format check after fix:")
print(diag["Format_OK_After"].value_counts())

print("\nStill wrong (need manual review):")
print(diag[~diag["Format_OK_After"]][["Record_ID", "Entered_ICD10"]])
# --- Map local code -> standard code ---
mapping = mapping.rename(columns={"ICD10_Code": "Mapped_ICD10"})
diag = diag.merge(mapping, on="Local_Code", how="left")
print("\nRows after merge:", len(diag))

unmapped = diag[diag["Mapped_ICD10"].isna()]
print("\nLocal codes without mapping:")
print(unmapped["Local_Code"].value_counts())

diag["Matches_Mapping"] = diag["Code_Fixed"] == diag["Mapped_ICD10"]
print("\nEntered code vs mapping table:")
print(diag[diag["Mapped_ICD10"].notna()]["Matches_Mapping"].value_counts())
import numpy as np

# --- Classify each record ---
conditions = [
    diag["Mapped_ICD10"].isna(),
    diag["Entered_ICD10"].isna(),
    ~diag["Format_OK_After"],
    ~diag["Matches_Mapping"],
]
labels = [
    "1 - Unmapped local code",
    "2 - Empty code",
    "3 - Invalid format",
    "4 - Differs from mapping table",
]
diag["Issue"] = np.select(conditions, labels, default="OK")

print("\nIssue summary:")
print(diag["Issue"].value_counts())

# --- Export exception report ---
summary = diag["Issue"].value_counts().reset_index()
summary.columns = ["Issue", "Count"]

exceptions = diag[diag["Issue"] != "OK"][
    ["Record_ID", "Local_Code", "Local_Description", "Entered_ICD10",
     "Code_Fixed", "Mapped_ICD10", "Issue", "Department"]
].sort_values("Issue")

with pd.ExcelWriter("icd_exception_report.xlsx") as writer:
    summary.to_excel(writer, sheet_name="Summary", index=False)
    exceptions.to_excel(writer, sheet_name="Exceptions", index=False)

print("Report saved: icd_exception_report.xlsx")
