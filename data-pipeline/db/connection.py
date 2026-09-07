import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

def get_engine():
    db_url=os.getenv("DATABASE_URL")

    if not db_url:
        raise RuntimeError(
            "DATABASE_URL not found "
        )

    return create_engine(db_url)


if __name__=="__main__":
    engine=get_engine()

    with engine.connect() as conn:
        print("connected succesfully to :",engine.url.database)
