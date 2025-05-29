from models import Base
from sqlalchemy import create_engine

# Create SQLite DB
engine = create_engine('sqlite:///database/casedb.sqlite3')
Base.metadata.create_all(engine)
