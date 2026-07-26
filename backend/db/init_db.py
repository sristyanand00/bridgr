import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import Base, engine
from db.models import Analysis, Roadmap, User

logger = logging.getLogger(__name__)


def init_db():
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()
