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


def test_merge_two_dicts_and_remove_list_hubs():
    wipe_all_neo4j_data(DRIVER)
    dic1 = {
        "Article": {
            "title": "Science Behind The Cyberpunk-Genres Awesomeness",
            "Authors": [
                {
                    "firstName": "Mike",
                    "lastName": "Pondsmith",
                    "affiliation": [{"name": "University 1"}],
                },
            ],
        }
    }

    dic2 = {
        "Article": {
            "title": "Transhumanism in Computergames",
            "Authors": [
                {
                    "firstName": "Mike",
                    "lastName": "Pondsmith",
                    "affiliation": [{"name": "University 1"}, {"name": "University 2"}],
                },
            ],
        }
    }
    d2g = Dict2graph()
    d2g.add_node_transformation(
        Transformer.match_node().do(NodeTrans.PopListHubNodes())
    )
    d2g.parse(dic1)
    d2g.parse(dic2)
    d2g.merge(DRIVER)
    result = get_all_neo4j_data(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_res: dict = [
        {
            "labels": ["affiliation", "CollectionItem"],
            "props": {"name": "University 1"},
            "outgoing_rels": [],
        },
        {
            "labels": ["affiliation", "CollectionItem"],
            "props": {"name": "University 2"},
            "outgoing_rels": [],
        },
        {
            "labels": ["CollectionItem", "Authors"],
            "props": {"firstName": "Mike", "lastName": "Pondsmith"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "Authors_HAS_affiliation",
                    "rel_target_node": {
                        "labels": ["affiliation", "CollectionItem"],
                        "props": {"name": "University 1"},
                    },
                },
                {
                    "rel_props": {"_list_item_index": 1},
                    "rel_type": "Authors_HAS_affiliation",
                    "rel_target_node": {
                        "labels": ["affiliation", "CollectionItem"],
                        "props": {"name": "University 2"},
                    },
                },
            ],
        },
        {
            "labels": ["Article"],
            "props": {"title": "Science Behind The Cyberpunk-Genres Awesomeness"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "Article_HAS_Authors",
                    "rel_target_node": {
                        "labels": ["CollectionItem", "Authors"],
                        "props": {"firstName": "Mike", "lastName": "Pondsmith"},
                    },
                }
            ],
        },
        {
            "labels": ["Article"],
            "props": {"title": "Transhumanism in Computergames"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "Article_HAS_Authors",
                    "rel_target_node": {
                        "labels": ["CollectionItem", "Authors"],
                        "props": {"firstName": "Mike", "lastName": "Pondsmith"},
                    },
                }
            ],
        },
    ]
    # print("DIFF:", DeepDiff(expected_res, result, ignore_order=True))
    assert_result(result, expected_res)


def test_hubbing_edge():
    wipe_all_neo4j_data(DRIVER)
    dic1 = {
        "Article": {
            "title": "Science Behind The Cyberpunk-Genres Awesomeness",
            "Authors": [
                {
                    "firstName": "Mike",
                    "lastName": "Pondsmith",
                    "affiliation": [{"name": "University 1"}],
                },
            ],
        }
    }

    dic2 = {
        "Article": {
            "title": "Transhumanism in Computergames",
            "Authors": [
                {
                    "firstName": "Mike",
                    "lastName": "Pondsmith",
                    "affiliation": [{"name": "University 1"}, {"name": "University 2"}],
                },
            ],
        }
    }
    d2g = Dict2graph()
    d2g.add_node_transformation(
        [
            Transformer.match_node().do(NodeTrans.PopListHubNodes()),
            Transformer.match_node().do(NodeTrans.RemoveListItemLabels()),
            Transformer.match_node("Article").do(
                NodeTrans.CreateHubbing(
                    follow_nodes_labels=["Authors", "affiliation"],
                    merge_property_mode="edge",
                    hub_labels=["Contribution"],
                )
            ),
        ]
    )
    d2g.parse(dic1)
    d2g.parse(dic2)
    d2g.merge(DRIVER)
    result = get_all_neo4j_data(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_res: dict = [
        {
            "labels": ["affiliation"],
            "props": {"name": "University 1"},
            "outgoing_rels": [],
        },
        {
            "labels": ["affiliation"],
            "props": {"name": "University 2"},
            "outgoing_rels": [],
        },
        {
            "labels": ["Authors"],
            "props": {"firstName": "Mike", "lastName": "Pondsmith"},
            "outgoing_rels": [],
        },
        {
            "labels": ["Article"],
            "props": {"title": "Science Behind The Cyberpunk-Genres Awesomeness"},
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "Article_HAS_Contribution",
                    "rel_target_node": {
                        "labels": ["Contribution"],
                        "props": {"id": "7fcd494bd8e15df89a8c970efcb1beeb"},
                    },
                }
            ],
        },
        {
            "labels": ["Article"],
            "props": {"title": "Transhumanism in Computergames"},
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "Article_HAS_Contribution",
                    "rel_target_node": {
                        "labels": ["Contribution"],
                        "props": {"id": "d6d0f91b22b1aa33ccb4584344c07508"},
                    },
                }
            ],
        },
        {
            "labels": ["Contribution"],
            "props": {"id": "7fcd494bd8e15df89a8c970efcb1beeb"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "Contribution_HAS_Authors",
                    "rel_target_node": {
                        "labels": ["Authors"],
                        "props": {"firstName": "Mike", "lastName": "Pondsmith"},
                    },
                },
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "Contribution_HAS_affiliation",
                    "rel_target_node": {
                        "labels": ["affiliation"],
                        "props": {"name": "University 1"},
                    },
                },
            ],
        },
        {
            "labels": ["Contribution"],
            "props": {"id": "d6d0f91b22b1aa33ccb4584344c07508"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "Contribution_HAS_Authors",
                    "rel_target_node": {
                        "labels": ["Authors"],
                        "props": {"firstName": "Mike", "lastName": "Pondsmith"},
                    },
                },
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "Contribution_HAS_affiliation",
                    "rel_target_node": {
                        "labels": ["affiliation"],
                        "props": {"name": "University 1"},
                    },
                },
                {
                    "rel_props": {"_list_item_index": 1},
                    "rel_type": "Contribution_HAS_affiliation",
                    "rel_target_node": {
                        "labels": ["affiliation"],
                        "props": {"name": "University 2"},
                    },
                },
            ],
        },
    ]
    # print("DIFF:", DeepDiff(expected_res, result, ignore_order=True))
    assert_result(result, expected_res)


# test_merge_two_dicts_and_remove_list_hubs()
test_hubbing_edge()
