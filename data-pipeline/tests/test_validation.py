import pandas as pd
import pandera.pandas as pa
from pandera import Check
from pathlib import Path

CLEAN_PATH = Path(__file__).parent.parent / "processed_data" / "projects_clean.csv"

VALID_STATUSES = ["recommended", "sanctioned", "ongoing", "completed", "stalled"]

project_schema = pa.DataFrameSchema(
    {
        "project_id": pa.Column(str, nullable=False, unique=True),
        "constituency": pa.Column(str, nullable=False),
        "district": pa.Column(str, nullable=False),
        "state": pa.Column(str, nullable=False),
        "sanctioned_amount": pa.Column(float, Check.ge(0), nullable=False, coerce=True),
        "released_amount": pa.Column(float, Check.ge(0), nullable=False, coerce=True),
        "expenditure": pa.Column(float, Check.ge(0), nullable=False, coerce=True),
        "project_status": pa.Column(str, Check.isin(VALID_STATUSES), nullable=False),
        "project_start_date": pa.Column("datetime64[ns]", nullable=False, coerce=True),
        "expected_completion_date": pa.Column("datetime64[ns]", nullable=False, coerce=True),
        "actual_completion_date": pa.Column("datetime64[ns]", nullable=True, coerce=True),
        "implementing_agency": pa.Column(str, nullable=True),
        "project_category": pa.Column(str, nullable=False),
        "progress_percent": pa.Column(float, Check.in_range(0, 100), nullable=True, coerce=True),
        "released_amount_imputed": pa.Column(bool, nullable=False),
    },
    strict=False,  # allow extra columns we haven't opinionated on yet (like sanctioned_duration_days)
)


def load_clean_data() -> pd.DataFrame:
    df = pd.read_csv(CLEAN_PATH)
    date_cols = ["project_start_date", "expected_completion_date", "actual_completion_date"]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def test_real_clean_data_passes():
    df = load_clean_data()
    validated = project_schema.validate(df, lazy=True)
    print(f"PASSED: all {len(validated)} real clean rows satisfy the schema")


def test_broken_data_is_caught():
    df = load_clean_data().head(5).copy()

    df.loc[0, "expenditure"] = -50000                
    df.loc[1, "progress_percent"] = 150                
    df.loc[2, "project_status"] = "in progress"        
    df.loc[3, "project_id"] = df.loc[4, "project_id"]  

    try:
        project_schema.validate(df, lazy=True)
        print("FAILED: schema did not catch the broken rows -- this would be a real bug")
    except pa.errors.SchemaErrors as err:
        print(f"CAUGHT correctly -- {len(err.failure_cases)} separate problems found:")
        print(err.failure_cases[["column", "check", "failure_case"]].to_string(index=False))


if __name__ == "__main__":
    test_real_clean_data_passes()
    print()
    test_broken_data_is_caught()