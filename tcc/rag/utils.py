from django.conf import settings
from neo4j import GraphDatabase

def get_neo4j_driver():
    return GraphDatabase.driver(
        settings.NEO4J_DATABASE_URL,
        auth=(settings.NEOJ_USERNAME, settings.NEO4J_PASSWORD)
    )
