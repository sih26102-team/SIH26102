import pandas as pd
from pathlib import Path

RAW_DATA_DIR = Path(__file__).parent.parent / "raw_data"
OUT_PATH = RAW_DATA_DIR / "ingested_combined.csv"

SOURCE_REGISTRY = {
    "sample_projects_synthetic.csv": "synthetic"
}

EXPECTED_COLUMNS = [
    "project_id", "constituency", "district", "state", "sanctioned_amount", "released_amount", "expenditure",
    "project_status", "project_start_date","expected_completion_date", "actual_completion_date",
    "implementing_agency", "project_category", "progress_percent",
]

def ingest() -> pd.DataFrame:
    frames = []

    for filename , source_lable in SOURCE_REGISTRY.items():
        Path = RAW_DATA_DIR / filename

        if not Path.exists():
            print(f"Warning: {filename} is listed in SOURCE_REGISTERY but not found in raw/data, skiping")

        df = pd.read_csv(Path, dtype=str)

        missing_cols = set(EXPECTED_COLUMNS) - set(df.columns)
        if missing_cols:
            print(f"Warning: {filename} is missing expected columns: {missing_cols}")

        df["data_source"] = source_lable 
        df["source_file"] = filename
        frames.append(df)
        print(f"Ingested {len(df)} rows from {filename} (source: {source_lable})")

    if not frames:
        raise RuntimeError("no raw files were ingested -- check SOURCE_REGISRTY and raw_data")

    combined = pd.concat(frames, ignore_index=True)
    combined.to_csv(OUT_PATH)
    print(f"Total ingested: {len(combined)} rows from {len(frames)} files -> {OUT_PATH}")
    return combined

if __name__ == "__main__":
    df = ingest()

