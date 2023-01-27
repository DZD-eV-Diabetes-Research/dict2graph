import os, sys

from neo4j import GraphDatabase

if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(
        os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
    )
    MODULE_ROOT_DIR = os.path.join(SCRIPT_DIR, "..")
    sys.path.insert(0, os.path.normpath(MODULE_ROOT_DIR))
from dict2graph_tests._test_tools import wipe_all_neo4j_data

wipe_all_neo4j_data(GraphDatabase.driver("neo4j://localhost"))

from neo4j import GraphDatabase
from dict2graph import Dict2graph, Transformer, NodeTrans

data = {"bookshelf": {"Genre": "Explaining the world"}}
d2g = Dict2graph()
d2g.add_transformation(
    [
        Transformer.match_nodes("bookshelf").do(NodeTrans.AddProperty({"mtr": "wood"})),
        Transformer.match_nodes("bookshelf").do(
            NodeTrans.OverridePropertyName("mtr", "material")
        ),
    ]
)
d2g.parse(data)
NEO4J_DRIVER = GraphDatabase.driver("neo4j://localhost")
d2g.create(NEO4J_DRIVER)
