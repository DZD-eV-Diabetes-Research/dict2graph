import os, sys
from neo4j import GraphDatabase, Driver, Result, Transaction
import json
from deepdiff import DeepDiff

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


# NodeTrans.CapitalizeLabels
def test_CapitalizeLabels():
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
    d2g.parse(data)
    d2g.create(DRIVER)
    result = get_all_neo4j_data(DRIVER)
    # print(json.dumps(result, indent=2))
    # mind the uppercase "A" in article. thats what we are going here for.
    expected_res: dict = [
        {
            "labels": ["Article"],
            "props": {"title": "Science Behind The Cyberpunks-Genre Awesomeness"},
            "outgoing_rels": [],
        }
    ]
    assert expected_res == result


# NodeTrans.CapitalizeLabels
def test_OverridePropertyName():
    wipe_all_neo4j_data(DRIVER)
    data = {
        "article": {
            "title": "Science Behind The Cyberpunks-Genre Awesomeness",
            "authors": [{"name": "Amina"}, {"name": "Urho"}],
        }
    }
    d2g = Dict2graph()
    d2g.add_node_transformation(
        Transformer.match_node("article").do(
            NodeTrans.OverridePropertyName("title", "topic")
        )
    )
    d2g.add_relation_transformation(
        Transformer.match_rel("CollectionHub_authors_HAS_authors").do(
            NodeTrans.OverridePropertyName("_index", "rank")
        )
    )
    d2g.parse(data)
    d2g.create(DRIVER)
    result = get_all_neo4j_data(DRIVER)
    # print(json.dumps(result, indent=2))
    # mind the uppercase "A" in article. thats what we are going here for.
    expected_res: dict = [
        {
            "labels": ["CollectionHub", "authors"],
            "props": {"id": "d751713988987e9331980363e24189ce"},
            "outgoing_rels": [
                {
                    "rel_props": {"rank": 1},
                    "rel_type": "CollectionHub_authors_HAS_authors",
                    "rel_target_node": {
                        "labels": ["authors"],
                        "props": {"name": "Urho"},
                    },
                },
                {
                    "rel_props": {"rank": 0},
                    "rel_type": "CollectionHub_authors_HAS_authors",
                    "rel_target_node": {
                        "labels": ["authors"],
                        "props": {"name": "Amina"},
                    },
                },
            ],
        },
        {"labels": ["authors"], "props": {"name": "Amina"}, "outgoing_rels": []},
        {"labels": ["authors"], "props": {"name": "Urho"}, "outgoing_rels": []},
        {
            "labels": ["article"],
            "props": {"topic": "Science Behind The Cyberpunks-Genre Awesomeness"},
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "article_HAS_CollectionHub_authors",
                    "rel_target_node": {
                        "labels": ["CollectionHub", "authors"],
                        "props": {"id": "d751713988987e9331980363e24189ce"},
                    },
                }
            ],
        },
    ]

    assert DeepDiff(expected_res, result, ignore_order=True) == {}


def test_OverrideLabel():
    wipe_all_neo4j_data(DRIVER)
    data = {
        "article": {
            "title": "Science Behind The Cyberpunks-Genre Awesomeness",
        }
    }
    d2g = Dict2graph()
    d2g.add_node_transformation(
        Transformer.match_node("article").do(NodeTrans.OverrideLabel("book"))
    )
    d2g.parse(data)
    d2g.create(DRIVER)
    result = get_all_neo4j_data(DRIVER)
    # print(json.dumps(result, indent=2))
    # mind the uppercase "A" in article. thats what we are going here for.
    expected_res: dict = [
        {
            "labels": ["book"],
            "props": {"title": "Science Behind The Cyberpunks-Genre Awesomeness"},
            "outgoing_rels": [],
        }
    ]
    assert expected_res == result


def test_SetMergeProperties():
    wipe_all_neo4j_data(DRIVER)
    data = {
        "books": [
            {
                "title": "Science Behind The Cyberpunks-Genre Awesomeness",
                "condition": "good",
            },
            {
                "title": "Science Behind The Cyberpunks-Genre Awesomeness",
                "condition": "bad",
            },
            {
                "title": "Science Behind The Cyberpunks-Genre Awesomeness",
                "condition": "good",
            },
        ]
    }
    d2g = Dict2graph()
    d2g.add_node_transformation(
        Transformer.match_node("article").do(
            NodeTrans.SetMergeProperties(props=["title"])
        )
    )
    d2g.parse(data)
    d2g.merge(DRIVER)
    result = get_all_neo4j_data(DRIVER)
    print(json.dumps(result, indent=2))
    # mind the uppercase "A" in article. thats what we are going here for.
    expected_res: dict = [
        {
            "labels": ["book"],
            "props": {"title": "Science Behind The Cyberpunks-Genre Awesomeness"},
            "outgoing_rels": [],
        }
    ]
    assert expected_res == result


test_OverrideLabel()
test_CapitalizeLabels()
test_OverridePropertyName()
test_SetMergeProperties()
