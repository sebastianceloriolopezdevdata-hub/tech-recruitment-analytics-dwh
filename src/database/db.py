import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Load variables from .env file at project root
_current_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_current_dir)
load_dotenv(os.path.join(_project_root, ".env"))


def get_engine():
    """
    Creates and returns a SQLAlchemy engine connected to PostgreSQL.
    Credentials are read from environment variables (set in .env).
    """
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    dbname = os.getenv("POSTGRES_DB")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
    engine = create_engine(url)
    return engine