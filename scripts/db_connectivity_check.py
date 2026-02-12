import os

from src.db.connectivity import check_db_connection


def main() -> int:
    db_url = os.getenv("DB_URL", "")
    if not db_url:
        print("ERROR: DB_URL is not set.")
        return 1

    is_connected = check_db_connection(db_url)
    if is_connected:
        print("Database connectivity check passed.")
        return 0

    print("Database connectivity check failed.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

