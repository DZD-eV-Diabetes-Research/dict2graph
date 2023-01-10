import os, sys
from neo4j import GraphDatabase

if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(
        os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
    )
    MODULE_ROOT_DIR = os.path.join(SCRIPT_DIR, "..")
    sys.path.insert(0, os.path.normpath(MODULE_ROOT_DIR))
from dict2graph import Dict2graph, Transformer, NodeTrans, RelTrans

# init-test
json = {
    "Article": {
        "title": "Science Behind The Cyberpunks-Genre Awesomeness",
        "Authors": [
            {
                "firstName": "Mike",
                "lastName": "Pondsmith",
                "affiliation": [{"name": "University 1"}],
            },
        ],
    }
}
json1 = [1, 2, 3, 4, 5]
json2 = {"Article": "dummes json"}
d2g = Dict2graph(create_hub_nodes_for_lists=True)
d2g.add_node_transformation(Transformer.match_node().do(NodeTrans.CapitalizeLabels()))
d2g.add_node_transformation(Transformer.match_node().do(NodeTrans.BlankListHubNodes()))
d2g.add_relation_transformation(
    Transformer.match_rel().do(RelTrans.UppercaseRelationType())
)
d2g.parse(json, "test")
d2g.create(GraphDatabase.driver("neo4j://localhost"))
