import pandas as pd
from pathlib import Path

RAW_PATH= Path(__file__).parent.parent / "raw_data" / "ingested_combined.csv"
OUT_PATH=Path(__file__).parent.parent / "processed_data" / "projects_clean.csv"
FLAGGED_PATH=Path(__file__).parent.parent / "processed_data" / "projects_flagged_for_review.csv"

REQUIRED_ID_FIELDS= ["project_id", "district", "state"]

# load the csv and tell object is path and tell return is dataframe
def load_raw(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str)
    return df

#same tell df object is dataframe and return tell return value is  dataframe 
#here we remove unwanted spaces
def strip_whitespace(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.columns:
        df[col]=df[col].str.strip()
    return df 

#here we convert all data into lower and remove unwanted spaces
def standardize_status(df: pd.DataFrame) ->pd.DataFrame:
    df["project_status"] = df["project_status"].str.lower().str.strip()
    return df

#here we convert different time format into single format ad day-month-year 
def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    date_cols = ["project_start_date", "expected_completion_date", "actual_completion_date"]
    for cols in date_cols:
        parsed_iso = pd.to_datetime(df[cols], format="%Y-%m-%d" , errors="coerce")
        parsed_dmy = pd.to_datetime(df[cols], format="%d-%m-%Y" , errors="coerce")
        df[cols] = parsed_iso.fillna(parsed_dmy)
    return df

#to conver numeric(str) -> numeric
def coerce_numeric(df: pd.DataFrame) -> pd.DataFrame:
    numeric_cols=["sanctioned_amount", "released_amount", "expenditure", "progress_percent"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

#find missing rows remove and clean them and they are stored for review
def drop_unidentifiable_rows(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    mask_bad = (df[REQUIRED_ID_FIELDS].isna().any(axis=1) | (df[REQUIRED_ID_FIELDS]=="").any(axis=1))
    dropped = df[mask_bad].copy()
    dropped["drop_reason"] = "missing requried identifying fields"
    return df[~mask_bad].copy(), dropped 

#filling relesed amount nan values with 0
def handle_missing_amounts(df: pd.DataFrame) -> pd.DataFrame:
    df["released_amount_imputed"] = df["released_amount"].isna()
    df["released_amount"] = df["released_amount"].fillna(0)
    return df

# remove duplicate records and seperate conflicts 
def resolve_duplicates(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    exact_dupe = df.duplicated(subset=["project_id", "expenditure"], keep="first")
    df =df[~exact_dupe].copy()

    conflict_mask= df.duplicated(subset=["project_id"], keep=False)
    conflicts = df[conflict_mask].copy()
    conflicts["flag_reason"] = "same project id , conflicting expenditure values"
    df = df[~conflict_mask].copy()
    return df , conflicts

def clean() -> None:
    df= load_raw(RAW_PATH)
    starting_rows = len(df)

    df = strip_whitespace(df)
    df = standardize_status(df)
    df = parse_dates(df)
    df = coerce_numeric(df)

    df, dropped_unidentifiable = drop_unidentifiable_rows(df)
    df = handle_missing_amounts(df)
    df , conflicts = resolve_duplicates(df)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATH, index=False)

    flagged = pd.concat([dropped_unidentifiable, conflicts], ignore_index=True)
    flagged.to_csv(FLAGGED_PATH, index=False)

    print(f"Started with {starting_rows} raw rows")
    print(f"  -> {len(dropped_unidentifiable)} dropped (missing required ID fields)")
    print(f"  -> {len(conflicts)} flagged for manual review (conflicting duplicates)")
    print(f"  -> {df['released_amount_imputed'].sum()} released_amount values imputed as 0")
    print(f"  -> {len(df)} clean rows written to {OUT_PATH}")
    print(f"  -> {len(flagged)} rows written to {FLAGGED_PATH} for review")

if __name__ == "__main__":
    clean()