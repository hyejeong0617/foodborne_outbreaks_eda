"""Stage 3 offline QA. No execution of notebooks, writes or network calls."""
import ast
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
for filename in ("NB1_Data_Cleaning.ipynb", "NB2_Entity_Normalisation.ipynb", "NB3_EDA.ipynb"):
    notebook = json.loads((ROOT / filename).read_text(encoding="utf-8"))
    for i, cell in enumerate(notebook["cells"], 1):
        if cell.get("cell_type") == "code":
            src = "".join(cell.get("source", []))
            try:
                ast.parse(src)
            except SyntaxError as exc:
                raise AssertionError(f"{filename}: cell {i}: {exc}") from exc

frame = pd.read_csv(ROOT / "data" / "cleaned_data_grouped.csv")
assert frame.shape == (18839, 12)
assert frame[["Hospitalizations", "Fatalities"]].isna().sum().to_dict() == {
    "Hospitalizations": 3560, "Fatalities": 3538
}
assert int(frame.Illnesses.sum()) == 372135
assert int(frame.Hospitalizations.sum()) == 14669
assert int(frame.Fatalities.sum()) == 336
h = frame.Hospitalizations.notna()
f = frame.Fatalities.notna()
assert int(frame.loc[h, "Illnesses"].sum()) == 303446
assert int(frame.loc[f, "Illnesses"].sum()) == 306342
assert round(100 * frame.loc[h, "Hospitalizations"].sum() / frame.loc[h, "Illnesses"].sum(), 3) == 4.834
assert round(100 * frame.loc[f, "Fatalities"].sum() / frame.loc[f, "Illnesses"].sum(), 3) == 0.110
norovirus = frame[frame.Species_grouped == "Norovirus"]
assert int(norovirus.Illnesses.sum()) == 137651
assert int(frame[(frame.Species_grouped == "Norovirus") &
                 (frame.Food_grouped == "Salad")].Illnesses.sum()) == 10835
assert frame["Food_grouped"].nunique() == 1366
assert frame["Species_grouped"].nunique() == 139
assert frame["primary_location"].nunique() == 21
print("PASS: NB1–NB3 source syntax and stage-3 data/outcome integrity.")
