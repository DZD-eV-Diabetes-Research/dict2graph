import os, sys
from typing import Dict
from neo4j import GraphDatabase, Driver, Result, Transaction
from deepdiff import DeepDiff

if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(
        os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
    )
    MODULE_ROOT_DIR = os.path.join(SCRIPT_DIR, "..")
    sys.path.insert(0, os.path.normpath(MODULE_ROOT_DIR))
from dict2graph import Dict2graph, Transformer, NodeTrans, RelTrans

DRIVER = GraphDatabase.driver("neo4j://localhost")


def get_all_neo4j_nodes_with_rels(driver: Driver) -> Result:
    def run_read(driver: Driver):
        with driver.session() as session:
            return session.execute_read(read_data)

    def read_data(tx: Transaction):
        query = """
            MATCH (n) 
            with n
            OPTIONAL MATCH p=(n)-[r]->(m)
            with n, collect(p) as outgoing_rels
            return labels(n) as labels, properties(n) as props, [o_rel IN outgoing_rels | {rel_type:type(relationships(o_rel)[0]),rel_props:properties(relationships(o_rel)[0]),rel_target_node:{labels:labels(nodes(o_rel)[1]),props:properties(nodes(o_rel)[1])}}]  as outgoing_rels
            """
        result = tx.run(query)
        return result.data()

    return run_read(driver)


def wipe_all_neo4j_data(driver: Driver):
    def run_delete(driver: Driver):
        with driver.session() as session:
            return session.execute_write(read_data)

    def read_data(tx: Transaction):
        query = "MATCH (n) detach delete n"
        tx.run(query)

    run_delete(driver)


def assert_result(result: Dict, expected_result: Dict):
    diff = DeepDiff(expected_result, result, ignore_order=True)
    assert (
        diff == {}
    ), f"Difference from expected Result:\nRESULT:\n{result}\nDIFFERENCE TO EXPECTATIONS:{diff}"
