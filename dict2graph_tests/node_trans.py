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
    result = get_all_neo4j_data(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_res: dict = [
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
    result = get_all_neo4j_data(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_res: dict = [
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
        Transformer.match_node(["books", "CollectionItem"]).do(
            NodeTrans.SetMergeProperties(props=["title"])
        )
    )
    d2g.parse(data)
    d2g.merge(DRIVER)
    result = get_all_neo4j_data(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_res: dict = [
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
    assert_result(result, expected_res)


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
    result = get_all_neo4j_data(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_res: dict = [
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
    assert_result(result, expected_res)


def test_BlankListHubNodes():
    wipe_all_neo4j_data(DRIVER)
    data = ["Amos", "Avasarala", "Holden", "Nagata"]
    d2g = Dict2graph()

    d2g.add_node_transformation(
        Transformer.match_node().do(NodeTrans.BlankListHubNodes())
    )

    d2g.parse(data)
    d2g.merge(DRIVER)
    result = get_all_neo4j_data(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_res: dict = [
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
    assert_result(result, expected_res)


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
    result = get_all_neo4j_data(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_res: dict = [
        {
            "labels": ["Dict2GraphRoot"],
            "props": {"name": "Julie Mao", "dead": True, "age": 22},
            "outgoing_rels": [],
        }
    ]
    assert_result(result, expected_res)


def test_PopListHubNodes():
    wipe_all_neo4j_data(DRIVER)
    data = {"space": {"ship": ["Agatha King", "Okimbo"]}}
    d2g = Dict2graph()

    d2g.add_node_transformation(
        Transformer.match_node().do(NodeTrans.PopListHubNodes()),
    )

    d2g.parse(data)
    d2g.merge(DRIVER)
    result = get_all_neo4j_data(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_res: dict = [
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
    assert_result(result, expected_res)


def test_CreateHubbing():
    wipe_all_neo4j_data(DRIVER)
    data = {"space": {"ship": ["Agatha King", "Okimbo"]}}
    d2g = Dict2graph()

    d2g.add_node_transformation(
        Transformer.match_node().do(NodeTrans.CreateHubbing()),
    )

    d2g.parse(data)
    d2g.merge(DRIVER)
    result = get_all_neo4j_data(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_res: dict = [
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
    assert_result(result, expected_res)


def test_RemoveListItemLabels():
    print("TODO test_RemoveListItemLabels", test_RemoveListItemLabels)


test_OverrideLabel()
test_RemoveLabel()
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
