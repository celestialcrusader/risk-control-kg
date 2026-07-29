"""
Database Seeding Script for Pure RCKG Baseline Graph (v1.0.0).

Loads data/seed/nist_olir_export.xml into live PostgreSQL and Memgraph databases.
"""

import sys
import logging
from pathlib import Path

# Add repository root to Python path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.app.models import Base, FrameworkControlObjectiveNode
from backend.app.services.seed_ingestion import ComplianceSeedIngester
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed_database")

# Database URLs (supports test containers on port 5433 or default 5432)
POSTGRES_TEST_URL = "postgresql://rckg_user:rckg_password@localhost:5433/rckg_test"
POSTGRES_DEV_URL = "postgresql://postgres:postgres@localhost:5432/rckg"

def run_seeding():
    engine = None
    for url in [POSTGRES_TEST_URL, POSTGRES_DEV_URL]:
        try:
            test_engine = create_engine(url)
            conn = test_engine.connect()
            conn.close()
            engine = test_engine
            logger.info(f"Connected to database at {url}")
            break
        except Exception as e:
            logger.warning(f"Could not connect to {url}: {e}")

    if not engine:
        sqlite_file = REPO_ROOT / "rckg_seed_baseline.db"
        engine = create_engine(f"sqlite:///{sqlite_file}")
        logger.info(f"Using SQLite database fallback at {sqlite_file}")

    # Ensure all tables defined in Base metadata exist
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    seed_file = REPO_ROOT / "data" / "seed" / "nist_olir_export.xml"
    if not seed_file.exists():
        logger.error(f"Seed file not found: {seed_file}")
        return

    ingester = ComplianceSeedIngester(db_session=session)
    stats = ingester.ingest_file(source_type="NIST_OLIR", file_path=str(seed_file))

    logger.info("==================================================")
    logger.info("SEEDING SUCCESSFUL!")
    logger.info(f"Ingested Framework Nodes: {stats['nodes']}")
    logger.info(f"Ingested Seed Edges:      {stats['edges']}")
    logger.info("==================================================")

    # Print database node summary
    nodes = session.query(FrameworkControlObjectiveNode).all()
    for n in nodes:
        logger.info(f"  • [{n.framework_name} {n.framework_version}] {n.framework_obj_id}: {n.objective_name} - '{n.objective_text}'")

    session.close()

if __name__ == "__main__":
    run_seeding()
