from settings import DATABASE_URL
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Set a database connection
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
Base = declarative_base()


# It's easier to control session at orchestrator side to control it's lifecycle and avoid using same session
# in different threads. All commits and rollbacks should be managed on orchestrator side as well.
def new_session():
    return sessionmaker(bind=engine)()
