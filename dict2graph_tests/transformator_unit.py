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
from dict2graph_tests._test_tools import (
    wipe_all_neo4j_data,
    DRIVER,
    get_all_neo4j_data,
    assert_result,
)


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
    assert_result(result, expected_res)


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

    expected_res: dict = [
        {"labels": ["authors"], "props": {"name": "Urho"}, "outgoing_rels": []},
        {
            "labels": ["article"],
            "props": {"topic": "Science Behind The Cyberpunks-Genre Awesomeness"},
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "article_HAS_CollectionHub_CollectionHubauthors",
                    "rel_target_node": {
                        "labels": ["CollectionHub", "CollectionHubauthors"],
                        "props": {"id": "03217453e0f378672a54ae6ba365b2ed"},
                    },
                }
            ],
        },
        {
            "labels": ["CollectionHub", "CollectionHubauthors"],
            "props": {"id": "03217453e0f378672a54ae6ba365b2ed"},
            "outgoing_rels": [
                {
                    "rel_props": {"_index": 1},
                    "rel_type": "CollectionHub_CollectionHubauthors_HAS_authors",
                    "rel_target_node": {
                        "labels": ["authors"],
                        "props": {"name": "Urho"},
                    },
                },
                {
                    "rel_props": {"_index": 0},
                    "rel_type": "CollectionHub_CollectionHubauthors_HAS_authors",
                    "rel_target_node": {
                        "labels": ["authors"],
                        "props": {"name": "Amina"},
                    },
                },
            ],
        },
        {"labels": ["authors"], "props": {"name": "Amina"}, "outgoing_rels": []},
    ]
    # print("DIFF:", DeepDiff(expected_res, result, ignore_order=True))
    assert_result(result, expected_res)


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

    expected_res: dict = [
        {
            "labels": ["book"],
            "props": {"title": "Science Behind The Cyberpunks-Genre Awesomeness"},
            "outgoing_rels": [],
        }
    ]
    assert_result(result, expected_res)


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
        Transformer.match_node("books").do(
            NodeTrans.SetMergeProperties(props=["title"])
        )
    )
    d2g.parse(data)
    d2g.merge(DRIVER)
    result = get_all_neo4j_data(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_res: dict = [
        {
            "labels": ["CollectionHub", "CollectionHubbooks"],
            "props": {"id": "c4a300f8cf40fff66920094208ab5386"},
            "outgoing_rels": [
                {
                    "rel_props": {"_index": 2},
                    "rel_type": "CollectionHub_CollectionHubbooks_HAS_books",
                    "rel_target_node": {
                        "labels": ["books"],
                        "props": {
                            "condition": "good",
                            "title": "Science Behind The Cyberpunks-Genre Awesomeness",
                        },
                    },
                }
            ],
        },
        {
            "labels": ["books"],
            "props": {
                "condition": "good",
                "title": "Science Behind The Cyberpunks-Genre Awesomeness",
            },
            "outgoing_rels": [],
        },
    ]
    assert_result(result, expected_res)


def test_TypeCastProperty():
    wipe_all_neo4j_data(DRIVER)
    data = {"article": {"good": "yes", "relevant": "No", "in_stock_no": "23"}}
    d2g = Dict2graph()
    d2g.add_node_transformation(
        [
            Transformer.match_node("article").do(
                NodeTrans.TypeCastProperty("good", bool)
            ),
            Transformer.match_node("article").do(
                NodeTrans.TypeCastProperty("in_stock_no", int)
            ),
        ]
    )
    d2g.parse(data)
    d2g.create(DRIVER)
    result = get_all_neo4j_data(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_res: dict = [
        {
            "labels": ["article"],
            "props": {"relevant": "No", "good": True, "in_stock_no": 23},
            "outgoing_rels": [],
        }
    ]
    assert_result(result, expected_res)


def test_CreateNewMergePropertyFromHash_simple():
    wipe_all_neo4j_data(DRIVER)
    data = [
        {"person": {"firstname": "Wolfgang", "lastname": "Pauli", "age": 34}},
        {"person": {"firstname": "Wolfgang", "lastname": "Pauli", "age": 123}},
    ]
    d2g = Dict2graph()

    d2g.add_node_transformation(
        Transformer.match_node("person").do(
            NodeTrans.CreateNewMergePropertyFromHash(
                hash_includes_properties=["firstname", "lastname"],
                hash_includes_existing_merge_props=False,
                hash_includes_existing_other_props=False,
            )
        )
    )
    d2g.parse(data)
    d2g.merge(DRIVER)
    result = get_all_neo4j_data(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_res: dict = [
        {
            "labels": ["CollectionHub", "CollectionHubDict2GraphRoot"],
            "props": {"id": "5cf48f5b18ab1bf7f29a9e98aa753a19"},
            "outgoing_rels": [
                {
                    "rel_props": {"_index": 1},
                    "rel_type": "CollectionHub_CollectionHubDict2GraphRoot_HAS_person",
                    "rel_target_node": {
                        "labels": ["person"],
                        "props": {
                            "firstname": "Wolfgang",
                            "_id": "03e008fb38d6c6b337602b6d22f5bd5d",
                            "age": 123,
                            "lastname": "Pauli",
                        },
                    },
                }
            ],
        },
        {
            "labels": ["person"],
            "props": {
                "firstname": "Wolfgang",
                "_id": "03e008fb38d6c6b337602b6d22f5bd5d",
                "age": 123,
                "lastname": "Pauli",
            },
            "outgoing_rels": [],
        },
    ]
    assert_result(result, expected_res)


def test_CreateNewMergePropertyFromHash_advanced():
    wipe_all_neo4j_data(DRIVER)
    data = [
        {"person": {"firstname": "Wolfgang", "lastname": "Pauli", "children": []}},
        {
            "person": {
                "firstname": "Wolfgang",
                "lastname": "Pauli",
                "children": [{"name": "Elfride"}],
            }
        },
    ]
    d2g = Dict2graph()

    d2g.add_node_transformation(
        Transformer.match_node("person").do(
            NodeTrans.CreateNewMergePropertyFromHash(
                hash_includes_properties=["firstname", "lastname"],
                hash_includes_existing_merge_props=False,
                hash_includes_existing_other_props=False,
                hash_includes_children_nodes_merge_data=True,
            )
        )
    )

    d2g.parse(data)
    d2g.merge(DRIVER)
    result = get_all_neo4j_data(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_res: dict = [
        {
            "labels": ["CollectionHub", "CollectionHubDict2GraphRoot"],
            "props": {"id": "70250fe04440555565cf29422be7cf19"},
            "outgoing_rels": [
                {
                    "rel_props": {"_index": 0},
                    "rel_type": "CollectionHub_CollectionHubDict2GraphRoot_HAS_person",
                    "rel_target_node": {
                        "labels": ["person"],
                        "props": {
                            "firstname": "Wolfgang",
                            "_id": "3fd35b0354104b98b46ec13b8003c033",
                            "lastname": "Pauli",
                        },
                    },
                },
                {
                    "rel_props": {"_index": 1},
                    "rel_type": "CollectionHub_CollectionHubDict2GraphRoot_HAS_person",
                    "rel_target_node": {
                        "labels": ["person"],
                        "props": {
                            "firstname": "Wolfgang",
                            "_id": "0f4e57ef332dd2f42783f08f0554d17e",
                            "lastname": "Pauli",
                        },
                    },
                },
            ],
        },
        {
            "labels": ["CollectionHub", "CollectionHubchildren"],
            "props": {"id": "d751713988987e9331980363e24189ce"},
            "outgoing_rels": [],
        },
        {
            "labels": ["CollectionHub", "CollectionHubchildren"],
            "props": {"id": "7f5335ca59326bfed3612f0d997c1c39"},
            "outgoing_rels": [
                {
                    "rel_props": {"_index": 0},
                    "rel_type": "CollectionHub_CollectionHubchildren_HAS_children",
                    "rel_target_node": {
                        "labels": ["children"],
                        "props": {"name": "Elfride"},
                    },
                }
            ],
        },
        {
            "labels": ["person"],
            "props": {
                "firstname": "Wolfgang",
                "_id": "3fd35b0354104b98b46ec13b8003c033",
                "lastname": "Pauli",
            },
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "person_HAS_CollectionHub_CollectionHubchildren",
                    "rel_target_node": {
                        "labels": ["CollectionHub", "CollectionHubchildren"],
                        "props": {"id": "d751713988987e9331980363e24189ce"},
                    },
                }
            ],
        },
        {
            "labels": ["person"],
            "props": {
                "firstname": "Wolfgang",
                "_id": "0f4e57ef332dd2f42783f08f0554d17e",
                "lastname": "Pauli",
            },
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "person_HAS_CollectionHub_CollectionHubchildren",
                    "rel_target_node": {
                        "labels": ["CollectionHub", "CollectionHubchildren"],
                        "props": {"id": "7f5335ca59326bfed3612f0d997c1c39"},
                    },
                }
            ],
        },
        {"labels": ["children"], "props": {"name": "Elfride"}, "outgoing_rels": []},
    ]
    assert_result(result, expected_res)


test_OverrideLabel()
test_CapitalizeLabels()
test_OverridePropertyName()
test_SetMergeProperties()
test_TypeCastProperty()
test_CreateNewMergePropertyFromHash_simple()
test_CreateNewMergePropertyFromHash_advanced()
