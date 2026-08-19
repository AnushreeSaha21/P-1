from functools import lru_cache

from neo4j import GraphDatabase

from backend.database.config import (
    NEO4J_URI,
    NEO4J_USER,
    NEO4J_PASSWORD,
    NEO4J_DATABASE
)


@lru_cache(maxsize=1)
def get_neo4j_driver():

    if not NEO4J_PASSWORD:
        raise RuntimeError(
            "NEO4J_PASSWORD is not configured."
        )

    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(
            NEO4J_USER,
            NEO4J_PASSWORD
        )
    )

    driver.verify_connectivity()

    return driver


def get_neo4j_database():
    return NEO4J_DATABASE