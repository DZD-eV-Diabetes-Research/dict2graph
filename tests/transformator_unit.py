import os, sys
from neo4j import GraphDatabase, Driver, Result, Transaction
import json

if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(
        os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
    )
    MODULE_ROOT_DIR = os.path.join(SCRIPT_DIR, "..")
    sys.path.insert(0, os.path.normpath(MODULE_ROOT_DIR))
from dict2graph import Dict2graph, Transformer, NodeTrans, RelTrans

DRIVER = GraphDatabase.driver("neo4j://localhost")


def get_all_neo4j_data(driver: Driver) -> Result:
    def run_read(driver: Driver):
        with driver.session() as session:
            return session.execute_read(read_data)

    def read_data(tx: Transaction):
        query = "MATCH (n) OPTIONAL MATCH (n)-[r]-(m) RETURN labels(n) as labels, n as props, type(r) as relation, labels(m) as neighbour_labels;"
        result = tx.run(query)
        return result.data()

    return run_read(driver)


def wipe_all_neo4j_data(driver: Driver):
    def run_delete(driver: Driver):
        with driver.session() as session:
            return session.execute_write(read_data)

    def read_data(tx: Transaction):
        query = "MATCH (n) detach delete n"
        result = tx.run(query)

    run_delete(driver)


# NodeTrans.CapitalizeLabels
def CapitalizeLabels():
    wipe_all_neo4j_data(DRIVER)
    data = {
        "article": {
            "title": "Science Behind The Cyberpunks-Genre Awesomeness",
        }
    }
    d2g = Dict2graph()
    d2g.add_node_transformation(
        Transformer.match_node().do(NodeTrans.CapitalizeLabels())
    )
    d2g.parse(data, "est")
    d2g.create(DRIVER)
    result = get_all_neo4j_data(DRIVER)
    # mind the uppercase "A" in article. thats what we are going here for.
    expected_res: dict = [
        {
            "labels": ["Article"],
            "props": {"title": "Science Behind The Cyberpunks-Genre Awesomeness"},
            "relations": None,
            "neighbour_labels": None,
        }
    ]
    assert expected_res == result


# you are here:
# todo: maybe switch to self geenrated josn object like `MATCH (n) OPTIONAL MATCH (n)-[r]-() RETURN {labels:labels(n) ,propeties:n, rels:r} as d`
d = [
    {
        "labels": ["Article"],
        "props": {"title": "Science Behind The Cyberpunks-Genre Awesomeness"},
        "relations": (
            {},
            "Est_HAS_Article",
            {"title": "Science Behind The Cyberpunks-Genre Awesomeness"},
        ),
        "neighbour_labels": ["Est"],
    },
    {
        "labels": ["Est"],
        "props": {"id": "8937743809b504bf824bd50989cc6ce3"},
        "relations": (
            {"id": "8937743809b504bf824bd50989cc6ce3"},
            "Est_HAS_Article",
            {"title": "Science Behind The Cyberpunks-Genre Awesomeness"},
        ),
        "neighbour_labels": ["Article"],
    },
]

CapitalizeLabels()
