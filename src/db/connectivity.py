from sqlalchemy import create_engine, text


def check_db_connection(db_url: str) -> bool:
    engine = create_engine(db_url, pool_pre_ping=True)
    with engine.connect() as connection:
        value = connection.execute(text("SELECT 1")).scalar_one()
        return value == 1

