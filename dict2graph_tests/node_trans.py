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
    get_all_neo4j_nodes_with_rels,
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
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))
    # mind the uppercase "A" in article. thats what we are going here for.
    expected_result_nodes: dict = [
        {
            "labels": ["Article"],
            "props": {"title": "Science Behind The Cyberpunks-Genre Awesomeness"},
            "outgoing_rels": [],
        }
    ]
    assert_result(result, expected_result_nodes)


# NodeTrans.CapitalizeLabels
def test_OverridePropertyName():
    wipe_all_neo4j_data(DRIVER)
    data = {
        "article": {
            "title": "Science Behind The Cyberpunks-Genre Awesomeness",
            "author": [{"name": "Amina"}, {"name": "Urho"}],
        }
    }
    d2g = Dict2graph()
    d2g.add_node_transformation(
        Transformer.match_node("article").do(
            NodeTrans.OverridePropertyName("title", "topic")
        )
    )
    d2g.add_relation_transformation(
        Transformer.match_rel("article_HAS_author").do(
            NodeTrans.OverridePropertyName("_list_item_index", "rank")
        )
    )
    d2g.parse(data)
    d2g.create(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_result_nodes: dict = [
        {
            "labels": ["CollectionHub", "author"],
            "props": {"id": "03217453e0f378672a54ae6ba365b2ed"},
            "outgoing_rels": [
                {
                    "rel_props": {"rank": 1},
                    "rel_type": "article_HAS_author",
                    "rel_target_node": {
                        "labels": ["CollectionItem", "author"],
                        "props": {"name": "Urho"},
                    },
                },
                {
                    "rel_props": {"rank": 0},
                    "rel_type": "article_HAS_author",
                    "rel_target_node": {
                        "labels": ["CollectionItem", "author"],
                        "props": {"name": "Amina"},
                    },
                },
            ],
        },
        {
            "labels": ["CollectionItem", "author"],
            "props": {"name": "Amina"},
            "outgoing_rels": [],
        },
        {
            "labels": ["CollectionItem", "author"],
            "props": {"name": "Urho"},
            "outgoing_rels": [],
        },
        {
            "labels": ["article"],
            "props": {"topic": "Science Behind The Cyberpunks-Genre Awesomeness"},
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "article_HAS_author",
                    "rel_target_node": {
                        "labels": ["CollectionHub", "author"],
                        "props": {"id": "03217453e0f378672a54ae6ba365b2ed"},
                    },
                }
            ],
        },
    ]
    # print("DIFF:", DeepDiff(expected_result_nodes, result, ignore_order=True))
    assert_result(result, expected_result_nodes)


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
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_result_nodes: dict = [
        {
            "labels": ["book"],
            "props": {"title": "Science Behind The Cyberpunks-Genre Awesomeness"},
            "outgoing_rels": [],
        }
    ]
    assert_result(result, expected_result_nodes)


def test_RemoveLabel():
    wipe_all_neo4j_data(DRIVER)
    data = {
        "Ship": {
            "name": "Agatha King",
            "souls": ["Souther", "Nguyễn", "Ghazi"],
        }
    }

    d2g = Dict2graph()
    d2g.add_node_transformation(
        Transformer.match_node(["CollectionHub", "souls"]).do(
            NodeTrans.RemoveLabel("souls")
        )
    )
    d2g.parse(data)
    d2g.create(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_result_nodes: dict = [
        {
            "labels": ["CollectionHub"],
            "props": {"id": "bb43cd7a2e84200db2862749cda5aa68"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "Ship_HAS_souls",
                    "rel_target_node": {
                        "labels": ["CollectionItem", "souls"],
                        "props": {"_list_item_data": "Souther"},
                    },
                },
                {
                    "rel_props": {"_list_item_index": 1},
                    "rel_type": "Ship_HAS_souls",
                    "rel_target_node": {
                        "labels": ["CollectionItem", "souls"],
                        "props": {"_list_item_data": "Nguyễn"},
                    },
                },
                {
                    "rel_props": {"_list_item_index": 2},
                    "rel_type": "Ship_HAS_souls",
                    "rel_target_node": {
                        "labels": ["CollectionItem", "souls"],
                        "props": {"_list_item_data": "Ghazi"},
                    },
                },
            ],
        },
        {
            "labels": ["CollectionItem", "souls"],
            "props": {"_list_item_data": "Souther"},
            "outgoing_rels": [],
        },
        {
            "labels": ["CollectionItem", "souls"],
            "props": {"_list_item_data": "Nguyễn"},
            "outgoing_rels": [],
        },
        {
            "labels": ["CollectionItem", "souls"],
            "props": {"_list_item_data": "Ghazi"},
            "outgoing_rels": [],
        },
        {
            "labels": ["Ship"],
            "props": {"name": "Agatha King"},
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "Ship_HAS_CollectionHub",
                    "rel_target_node": {
                        "labels": ["CollectionHub"],
                        "props": {"id": "bb43cd7a2e84200db2862749cda5aa68"},
                    },
                }
            ],
        },
    ]
    assert_result(result, expected_result_nodes)


def test_RemoveProperty():
    wipe_all_neo4j_data(DRIVER)
    data = {
        "Ship": {
            "name": "Agatha King",
            "souls": 3,
            "class": "Truman-class",
            "note": "asdadfsdfwfe",
        },
        "Body": {"name": "Mars", "souls": "9billion", "class": "Planet"},
    }

    d2g = Dict2graph()
    d2g.add_node_transformation(
        [
            Transformer.match_node(["Ship"]).do(
                NodeTrans.RemoveProperty(["souls", "note"])
            ),
            Transformer.match_node("Body").do(
                NodeTrans.RemoveProperty(["souls", "nonexists"])
            ),
        ]
    )
    d2g.parse(data)
    d2g.create(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_result_nodes: dict = [
        {
            "labels": ["Ship"],
            "props": {"name": "Agatha King", "class": "Truman-class"},
            "outgoing_rels": [],
        },
        {
            "labels": ["Body"],
            "props": {"name": "Mars", "class": "Planet"},
            "outgoing_rels": [],
        },
        {
            "labels": ["Dict2GraphRoot"],
            "props": {"id": "4c7eebf9de1843dbde015f1091a6a0bb"},
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "Dict2GraphRoot_HAS_Body",
                    "rel_target_node": {
                        "labels": ["Body"],
                        "props": {"name": "Mars", "class": "Planet"},
                    },
                },
                {
                    "rel_props": {},
                    "rel_type": "Dict2GraphRoot_HAS_Ship",
                    "rel_target_node": {
                        "labels": ["Ship"],
                        "props": {"name": "Agatha King", "class": "Truman-class"},
                    },
                },
            ],
        },
    ]
    assert_result(result, expected_result_nodes)


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
        Transformer.match_node(["books", "CollectionItem"]).do(
            NodeTrans.SetMergeProperties(props=["title"])
        )
    )
    d2g.parse(data)
    d2g.merge(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_result_nodes: dict = [
        {
            "labels": ["CollectionHub", "books"],
            "props": {"id": "c4a300f8cf40fff66920094208ab5386"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 2},
                    "rel_type": "books_HAS_books",
                    "rel_target_node": {
                        "labels": ["books", "CollectionItem"],
                        "props": {
                            "condition": "good",
                            "title": "Science Behind The Cyberpunks-Genre Awesomeness",
                        },
                    },
                }
            ],
        },
        {
            "labels": ["books", "CollectionItem"],
            "props": {
                "condition": "good",
                "title": "Science Behind The Cyberpunks-Genre Awesomeness",
            },
            "outgoing_rels": [],
        },
    ]
    assert_result(result, expected_result_nodes)


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
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_result_nodes: dict = [
        {
            "labels": ["article"],
            "props": {"relevant": "No", "good": True, "in_stock_no": 23},
            "outgoing_rels": [],
        }
    ]
    assert_result(result, expected_result_nodes)


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
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_result_nodes: dict = [
        {
            "labels": ["CollectionHub", "Dict2GraphRoot"],
            "props": {"id": "5cf48f5b18ab1bf7f29a9e98aa753a19"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 1},
                    "rel_type": "Dict2GraphRoot_HAS_person",
                    "rel_target_node": {
                        "labels": ["person", "CollectionItem"],
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
            "labels": ["person", "CollectionItem"],
            "props": {
                "firstname": "Wolfgang",
                "_id": "03e008fb38d6c6b337602b6d22f5bd5d",
                "age": 123,
                "lastname": "Pauli",
            },
            "outgoing_rels": [],
        },
    ]
    assert_result(result, expected_result_nodes)


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
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_result_nodes: dict = [
        {
            "labels": ["CollectionHub", "Dict2GraphRoot"],
            "props": {"id": "70250fe04440555565cf29422be7cf19"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "Dict2GraphRoot_HAS_person",
                    "rel_target_node": {
                        "labels": ["person", "CollectionItem"],
                        "props": {
                            "firstname": "Wolfgang",
                            "_id": "3fd35b0354104b98b46ec13b8003c033",
                            "lastname": "Pauli",
                        },
                    },
                },
                {
                    "rel_props": {"_list_item_index": 1},
                    "rel_type": "Dict2GraphRoot_HAS_person",
                    "rel_target_node": {
                        "labels": ["person", "CollectionItem"],
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
            "labels": ["CollectionHub", "children"],
            "props": {"id": "d751713988987e9331980363e24189ce"},
            "outgoing_rels": [],
        },
        {
            "labels": ["CollectionHub", "children"],
            "props": {"id": "7f5335ca59326bfed3612f0d997c1c39"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "person_HAS_children",
                    "rel_target_node": {
                        "labels": ["children", "CollectionItem"],
                        "props": {"name": "Elfride"},
                    },
                }
            ],
        },
        {
            "labels": ["person", "CollectionItem"],
            "props": {
                "firstname": "Wolfgang",
                "_id": "3fd35b0354104b98b46ec13b8003c033",
                "lastname": "Pauli",
            },
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "person_HAS_children",
                    "rel_target_node": {
                        "labels": ["CollectionHub", "children"],
                        "props": {"id": "d751713988987e9331980363e24189ce"},
                    },
                }
            ],
        },
        {
            "labels": ["person", "CollectionItem"],
            "props": {
                "firstname": "Wolfgang",
                "_id": "0f4e57ef332dd2f42783f08f0554d17e",
                "lastname": "Pauli",
            },
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "person_HAS_children",
                    "rel_target_node": {
                        "labels": ["CollectionHub", "children"],
                        "props": {"id": "7f5335ca59326bfed3612f0d997c1c39"},
                    },
                }
            ],
        },
        {
            "labels": ["children", "CollectionItem"],
            "props": {"name": "Elfride"},
            "outgoing_rels": [],
        },
    ]
    assert_result(result, expected_result_nodes)


def test_RemoveEmptyListRootNodes():
    wipe_all_neo4j_data(DRIVER)
    data = [
        {
            "person": {
                "firstname": "Walther",
                "children": [],
            }
        },
        {
            "person": {
                "firstname": "Wolfgang",
                "children": [{"name": "Elfride"}, {"name": "Kid2"}],
            }
        },
    ]
    d2g = Dict2graph()

    d2g.add_node_transformation(
        Transformer.match_node().do(NodeTrans.RemoveEmptyListRootNodes())
    )

    d2g.parse(data)
    d2g.merge(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_result_nodes: dict = [
        {
            "labels": ["CollectionHub", "Dict2GraphRoot"],
            "props": {"id": "5597176a73757989202a3cfca96bc8c7"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "Dict2GraphRoot_HAS_person",
                    "rel_target_node": {
                        "labels": ["person", "CollectionItem"],
                        "props": {"firstname": "Walther"},
                    },
                },
                {
                    "rel_props": {"_list_item_index": 1},
                    "rel_type": "Dict2GraphRoot_HAS_person",
                    "rel_target_node": {
                        "labels": ["person", "CollectionItem"],
                        "props": {"firstname": "Wolfgang"},
                    },
                },
            ],
        },
        {
            "labels": ["person", "CollectionItem"],
            "props": {"firstname": "Walther"},
            "outgoing_rels": [],
        },
        {
            "labels": ["person", "CollectionItem"],
            "props": {"firstname": "Wolfgang"},
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "person_HAS_children",
                    "rel_target_node": {
                        "labels": ["CollectionHub", "children"],
                        "props": {"id": "b6e98eb4e995daa53f19cfda9a916e17"},
                    },
                }
            ],
        },
        {
            "labels": ["CollectionHub", "children"],
            "props": {"id": "b6e98eb4e995daa53f19cfda9a916e17"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 1},
                    "rel_type": "person_HAS_children",
                    "rel_target_node": {
                        "labels": ["children", "CollectionItem"],
                        "props": {"name": "Kid2"},
                    },
                },
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "person_HAS_children",
                    "rel_target_node": {
                        "labels": ["children", "CollectionItem"],
                        "props": {"name": "Elfride"},
                    },
                },
            ],
        },
        {
            "labels": ["children", "CollectionItem"],
            "props": {"name": "Elfride"},
            "outgoing_rels": [],
        },
        {
            "labels": ["children", "CollectionItem"],
            "props": {"name": "Kid2"},
            "outgoing_rels": [],
        },
    ]
    assert_result(result, expected_result_nodes)


def test_BlankListHubNodes():
    wipe_all_neo4j_data(DRIVER)
    data = ["Amos", "Avasarala", "Holden", "Nagata"]
    d2g = Dict2graph()

    d2g.add_node_transformation(
        Transformer.match_node().do(NodeTrans.BlankListHubNodes())
    )

    d2g.parse(data)
    d2g.merge(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_result_nodes: dict = [
        {
            "labels": ["CollectionHub", "Dict2GraphRoot"],
            "props": {"id": "5597176a73757989202a3cfca96bc8c7"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "Dict2GraphRoot_HAS_person",
                    "rel_target_node": {
                        "labels": ["person", "CollectionItem"],
                        "props": {"firstname": "Walther"},
                    },
                },
                {
                    "rel_props": {"_list_item_index": 1},
                    "rel_type": "Dict2GraphRoot_HAS_person",
                    "rel_target_node": {
                        "labels": ["person", "CollectionItem"],
                        "props": {"firstname": "Wolfgang"},
                    },
                },
            ],
        },
        {
            "labels": ["person", "CollectionItem"],
            "props": {"firstname": "Walther"},
            "outgoing_rels": [],
        },
        {
            "labels": ["person", "CollectionItem"],
            "props": {"firstname": "Wolfgang"},
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "person_HAS_children",
                    "rel_target_node": {
                        "labels": ["CollectionHub", "children"],
                        "props": {"id": "b6e98eb4e995daa53f19cfda9a916e17"},
                    },
                }
            ],
        },
        {
            "labels": ["CollectionHub", "children"],
            "props": {"id": "b6e98eb4e995daa53f19cfda9a916e17"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 1},
                    "rel_type": "person_HAS_children",
                    "rel_target_node": {
                        "labels": ["children", "CollectionItem"],
                        "props": {"name": "Kid2"},
                    },
                },
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "person_HAS_children",
                    "rel_target_node": {
                        "labels": ["children", "CollectionItem"],
                        "props": {"name": "Elfride"},
                    },
                },
            ],
        },
        {
            "labels": ["children", "CollectionItem"],
            "props": {"name": "Elfride"},
            "outgoing_rels": [],
        },
        {
            "labels": ["children", "CollectionItem"],
            "props": {"name": "Kid2"},
            "outgoing_rels": [],
        },
    ]
    assert_result(result, expected_result_nodes)


def test_TypeCastProperty():
    wipe_all_neo4j_data(DRIVER)
    data = {"name": "Julie Mao", "dead": "yes", "age": "22"}
    d2g = Dict2graph()

    d2g.add_node_transformation(
        [
            Transformer.match_node().do(NodeTrans.TypeCastProperty("dead", bool)),
            Transformer.match_node().do(NodeTrans.TypeCastProperty("age", int)),
        ]
    )

    d2g.parse(data)
    d2g.merge(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_result_nodes: dict = [
        {
            "labels": ["Dict2GraphRoot"],
            "props": {"name": "Julie Mao", "dead": True, "age": 22},
            "outgoing_rels": [],
        }
    ]
    assert_result(result, expected_result_nodes)


def test_PopListHubNodes():
    wipe_all_neo4j_data(DRIVER)
    data = {"space": {"ship": ["Agatha King", "Okimbo"]}}
    d2g = Dict2graph()

    d2g.add_node_transformation(
        Transformer.match_node().do(NodeTrans.PopListHubNodes()),
    )

    d2g.parse(data)
    d2g.merge(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_result_nodes: dict = [
        {
            "labels": ["CollectionItem", "ship"],
            "props": {"_list_item_data": "Agatha King"},
            "outgoing_rels": [],
        },
        {
            "labels": ["CollectionItem", "ship"],
            "props": {"_list_item_data": "Okimbo"},
            "outgoing_rels": [],
        },
        {
            "labels": ["space"],
            "props": {"id": "ad342afd0fac115aeafa89c68d89f1be"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "space_HAS_ship",
                    "rel_target_node": {
                        "labels": ["CollectionItem", "ship"],
                        "props": {"_list_item_data": "Agatha King"},
                    },
                },
                {
                    "rel_props": {"_list_item_index": 1},
                    "rel_type": "space_HAS_ship",
                    "rel_target_node": {
                        "labels": ["CollectionItem", "ship"],
                        "props": {"_list_item_data": "Okimbo"},
                    },
                },
            ],
        },
    ]
    assert_result(result, expected_result_nodes)


def test_CreateHubbing():
    wipe_all_neo4j_data(DRIVER)
    data = {"space": {"ship": ["Agatha King", "Okimbo"]}}
    d2g = Dict2graph()

    d2g.add_node_transformation(
        Transformer.match_node().do(NodeTrans.CreateHubbing()),
    )

    d2g.parse(data)
    d2g.merge(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_result_nodes: dict = [
        {
            "labels": ["CollectionItem", "ship"],
            "props": {"_list_item_data": "Agatha King"},
            "outgoing_rels": [],
        },
        {
            "labels": ["CollectionItem", "ship"],
            "props": {"_list_item_data": "Okimbo"},
            "outgoing_rels": [],
        },
        {
            "labels": ["space"],
            "props": {"id": "ad342afd0fac115aeafa89c68d89f1be"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "space_HAS_ship",
                    "rel_target_node": {
                        "labels": ["CollectionItem", "ship"],
                        "props": {"_list_item_data": "Agatha King"},
                    },
                },
                {
                    "rel_props": {"_list_item_index": 1},
                    "rel_type": "space_HAS_ship",
                    "rel_target_node": {
                        "labels": ["CollectionItem", "ship"],
                        "props": {"_list_item_data": "Okimbo"},
                    },
                },
            ],
        },
    ]
    assert_result(result, expected_result_nodes)


def test_RemoveListItemLabels():
    wipe_all_neo4j_data(DRIVER)
    data = {"space": ["Agatha King", "Okimbo"]}
    d2g = Dict2graph()

    d2g.add_node_transformation(
        Transformer.match_node().do(NodeTrans.RemoveListItemLabels()),
    )

    d2g.parse(data)
    d2g.merge(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_result_nodes: dict = [
        {
            "labels": ["CollectionHub", "space"],
            "props": {"id": "57325cd8fe8c533ae589a42a18ea1f31"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 1},
                    "rel_type": "space_HAS_space",
                    "rel_target_node": {
                        "labels": ["space"],
                        "props": {"_list_item_data": "Okimbo"},
                    },
                },
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "space_HAS_space",
                    "rel_target_node": {
                        "labels": ["space"],
                        "props": {"_list_item_data": "Agatha King"},
                    },
                },
            ],
        },
        {
            "labels": ["space"],
            "props": {"_list_item_data": "Agatha King"},
            "outgoing_rels": [],
        },
        {
            "labels": ["space"],
            "props": {"_list_item_data": "Okimbo"},
            "outgoing_rels": [],
        },
    ]
    assert_result(result, expected_result_nodes)


def test_OutsourcePropertiesToNewNode():
    wipe_all_neo4j_data(DRIVER)
    data = {"ship": {"name": "Agatha King", "navy": "United Nations Navy"}}
    d2g = Dict2graph()

    d2g.add_node_transformation(
        Transformer.match_node("ship").do(
            NodeTrans.OutsourcePropertiesToNewNode(
                property_keys=["navy"],
                new_node_labels=["Party"],
                relation_type="MEMBERSHIP",
            )
        ),
    )

    d2g.parse(data)
    d2g.merge(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_result_nodes: dict = [
        {
            "labels": ["ship"],
            "props": {"name": "Agatha King"},
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "MEMBERSHIP",
                    "rel_target_node": {
                        "labels": ["Party"],
                        "props": {"navy": "United Nations Navy"},
                    },
                }
            ],
        },
        {
            "labels": ["Party"],
            "props": {"navy": "United Nations Navy"},
            "outgoing_rels": [],
        },
    ]
    assert_result(result, expected_result_nodes)


def test_RemoveNodesWithOnlyEmptyProps():
    wipe_all_neo4j_data(DRIVER)
    data = {
        "ship": [
            {"name": "Agatha King", "navy": "United Nations Navy"},
            {"name": "", "navy": None},
        ]
    }
    d2g = Dict2graph()

    d2g.add_node_transformation(
        Transformer.match_node().do(NodeTrans.RemoveNodesWithOnlyEmptyProps()),
    )

    d2g.parse(data)
    d2g.merge(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_result_nodes: dict = [
        {
            "labels": ["CollectionHub", "ship"],
            "props": {"id": "2061e61739236751d14ae01dfe54023a"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "ship_HAS_ship",
                    "rel_target_node": {
                        "labels": ["CollectionItem", "ship"],
                        "props": {"navy": "United Nations Navy", "name": "Agatha King"},
                    },
                }
            ],
        },
        {
            "labels": ["CollectionItem", "ship"],
            "props": {"navy": "United Nations Navy", "name": "Agatha King"},
            "outgoing_rels": [],
        },
    ]
    assert_result(result, expected_result_nodes)


def test_RemoveNodesWithNoProps():
    wipe_all_neo4j_data(DRIVER)
    data = {
        "ship": [
            {"name": "Agatha King", "navy": "United Nations Navy"},
            {},
        ]
    }
    d2g = Dict2graph()

    d2g.add_node_transformation(
        Transformer.match_node().do(NodeTrans.RemoveNodesWithNoProps()),
    )

    d2g.parse(data)
    d2g.create(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_result_nodes: dict = [
        {
            "labels": ["CollectionHub", "ship"],
            "props": {"id": "be18eceea6105854d14dab4ea36cbf41"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "ship_HAS_ship",
                    "rel_target_node": {
                        "labels": ["CollectionItem", "ship"],
                        "props": {"navy": "United Nations Navy", "name": "Agatha King"},
                    },
                }
            ],
        },
        {
            "labels": ["CollectionItem", "ship"],
            "props": {"navy": "United Nations Navy", "name": "Agatha King"},
            "outgoing_rels": [],
        },
    ]
    assert_result(result, expected_result_nodes)


def test_match_has_one_label_of():
    wipe_all_neo4j_data(DRIVER)
    data = {
        "ship": [
            {"name": "Agatha King", "navy": "United Nations Navy"},
        ]
    }
    d2g = Dict2graph()

    d2g.add_node_transformation(
        Transformer.match_node(has_one_label_of=["ship", "totalyOther"]).do(
            NodeTrans.AddLabel("Matched")
        ),
    )
    d2g.parse(data)
    d2g.create(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_result_nodes: dict = [
        {
            "labels": ["CollectionHub", "ship", "Matched"],
            "props": {"id": "aad38ebe6134bfcc251e86f8b70a0134"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "ship_HAS_ship",
                    "rel_target_node": {
                        "labels": ["CollectionItem", "ship", "Matched"],
                        "props": {"navy": "United Nations Navy", "name": "Agatha King"},
                    },
                }
            ],
        },
        {
            "labels": ["CollectionItem", "ship", "Matched"],
            "props": {"navy": "United Nations Navy", "name": "Agatha King"},
            "outgoing_rels": [],
        },
    ]
    assert_result(result, expected_result_nodes)


def test_match_has_not_one_label_of():
    wipe_all_neo4j_data(DRIVER)
    data = {
        "ship": [
            {"name": "Agatha King", "navy": "United Nations Navy"},
        ]
    }
    d2g = Dict2graph()

    d2g.add_node_transformation(
        Transformer.match_node(
            has_one_label_of=["ship", "totalyOther"],
            has_none_label_of=["CollectionHub"],
        ).do(NodeTrans.AddLabel("Matched")),
    )
    d2g.parse(data)
    d2g.create(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_result_nodes: dict = [
        {
            "labels": ["CollectionHub", "ship"],
            "props": {"id": "aad38ebe6134bfcc251e86f8b70a0134"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "ship_HAS_ship",
                    "rel_target_node": {
                        "labels": ["CollectionItem", "ship", "Matched"],
                        "props": {"navy": "United Nations Navy", "name": "Agatha King"},
                    },
                }
            ],
        },
        {
            "labels": ["CollectionItem", "ship", "Matched"],
            "props": {"navy": "United Nations Navy", "name": "Agatha King"},
            "outgoing_rels": [],
        },
    ]
    assert_result(result, expected_result_nodes)


test_OverrideLabel()
test_RemoveLabel()
test_RemoveProperty()
test_CapitalizeLabels()
test_OverridePropertyName()
test_SetMergeProperties()
test_TypeCastProperty()
test_CreateNewMergePropertyFromHash_simple()
test_CreateNewMergePropertyFromHash_advanced()
test_RemoveEmptyListRootNodes()
test_TypeCastProperty()
test_PopListHubNodes()
test_RemoveListItemLabels()
test_OutsourcePropertiesToNewNode()
test_RemoveNodesWithOnlyEmptyProps()
test_RemoveNodesWithNoProps()
test_match_has_one_label_of()
test_match_has_not_one_label_of()
