from sqlalchemy import create_engine

DATABASE_URL = (
    "postgresql://gopalakrishnagk53@localhost:5432/portfolio"
)

engine = create_engine(DATABASE_URL)