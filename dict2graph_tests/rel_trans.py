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


def test_OverridePropertyName():
    wipe_all_neo4j_data(DRIVER)
    data = [{"name": "Thomas Prince"}, {"name": "Zheng Fei"}, {"name": "Montenegro"}]
    d2g = Dict2graph()
    d2g.add_relation_transformation(
        Transformer.match_rel("Ship_HAS_Ship").do(
            RelTrans.OverridePropertyName("_list_item_index", "size_rank")
        )
    )
    d2g.parse(data, "Ship")
    d2g.create(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_result_nodes: dict = [
        {
            "labels": ["CollectionHub", "Ship"],
            "props": {"id": "04e92e89a48c92e734fb6008c4206a62"},
            "outgoing_rels": [
                {
                    "rel_props": {"size_rank": 2},
                    "rel_type": "Ship_HAS_Ship",
                    "rel_target_node": {
                        "labels": ["CollectionItem", "Ship"],
                        "props": {"name": "Montenegro"},
                    },
                },
                {
                    "rel_props": {"size_rank": 1},
                    "rel_type": "Ship_HAS_Ship",
                    "rel_target_node": {
                        "labels": ["CollectionItem", "Ship"],
                        "props": {"name": "Zheng Fei"},
                    },
                },
                {
                    "rel_props": {"size_rank": 0},
                    "rel_type": "Ship_HAS_Ship",
                    "rel_target_node": {
                        "labels": ["CollectionItem", "Ship"],
                        "props": {"name": "Thomas Prince"},
                    },
                },
            ],
        },
        {
            "labels": ["CollectionItem", "Ship"],
            "props": {"name": "Thomas Prince"},
            "outgoing_rels": [],
        },
        {
            "labels": ["CollectionItem", "Ship"],
            "props": {"name": "Zheng Fei"},
            "outgoing_rels": [],
        },
        {
            "labels": ["CollectionItem", "Ship"],
            "props": {"name": "Montenegro"},
            "outgoing_rels": [],
        },
    ]
    # print("DIFF:", DeepDiff(expected_result_nodes, result, ignore_order=True))
    assert_result(result, expected_result_nodes)


def test_OverrideReliationType():
    wipe_all_neo4j_data(DRIVER)
    data = {"name": "Holden", "stationed": {"ship": {"name": "Zheng Fei"}}}
    d2g = Dict2graph()
    d2g.add_relation_transformation(
        Transformer.match_rel("stationed").do(
            RelTrans.OverrideReliationType(value="IS_STATIONED_AT")
        )
    )
    d2g.parse(data, "Person")
    d2g.create(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_result_nodes: dict = [
        {"labels": ["ship"], "props": {"name": "Zheng Fei"}, "outgoing_rels": []},
        {
            "labels": ["Person"],
            "props": {"name": "Holden"},
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "IS_STATIONED_AT",
                    "rel_target_node": {
                        "labels": ["ship"],
                        "props": {"name": "Zheng Fei"},
                    },
                }
            ],
        },
    ]
    # print("DIFF:", DeepDiff(expected_result_nodes, result, ignore_order=True))
    assert_result(result, expected_result_nodes)


def test_UppercaseRelationType():
    wipe_all_neo4j_data(DRIVER)
    data = {"name": "Holden", "stationed": {"ship": {"name": "Zheng Fei"}}}
    d2g = Dict2graph()
    d2g.add_relation_transformation(
        Transformer.match_rel("stationed").do(RelTrans.UppercaseRelationType())
    )
    d2g.parse(data, "Person")
    d2g.create(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_result_nodes: dict = [
        {"labels": ["ship"], "props": {"name": "Zheng Fei"}, "outgoing_rels": []},
        {
            "labels": ["Person"],
            "props": {"name": "Holden"},
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "STATIONED",
                    "rel_target_node": {
                        "labels": ["ship"],
                        "props": {"name": "Zheng Fei"},
                    },
                }
            ],
        },
    ]
    # print("DIFF:", DeepDiff(expected_result_nodes, result, ignore_order=True))
    assert_result(result, expected_result_nodes)


def test_FlipNodes():
    wipe_all_neo4j_data(DRIVER)
    data = data = {
        "Article": {
            "title": "Surviving blackouts in space with soda lime",
            "Journal": {
                "name": "Space Ranger",
                "JournalIssue": {"year": 2056, "number": 23},
                "ISSN": {"type": "electronic", "id": "7.2973525693"},
            },
        }
    }
    d2g = Dict2graph()

    d2g.add_relation_transformation(
        Transformer.match_rel("Journal_HAS_JournalIssue").do(RelTrans.FlipNodes())
    )

    d2g.parse(data)
    d2g.create(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_result_nodes: dict = [
        {
            "labels": ["Journal"],
            "props": {"name": "Space Ranger"},
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "Journal_HAS_ISSN",
                    "rel_target_node": {
                        "labels": ["ISSN"],
                        "props": {"id": "7.2973525693", "type": "electronic"},
                    },
                }
            ],
        },
        {
            "labels": ["Article"],
            "props": {"title": "Surviving blackouts in space with soda lime"},
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "Article_HAS_JournalIssue",
                    "rel_target_node": {
                        "labels": ["JournalIssue"],
                        "props": {"number": 23, "year": 2056},
                    },
                }
            ],
        },
        {
            "labels": ["JournalIssue"],
            "props": {"number": 23, "year": 2056},
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "JournalIssue_HAS_Journal",
                    "rel_target_node": {
                        "labels": ["Journal"],
                        "props": {"name": "Space Ranger"},
                    },
                }
            ],
        },
        {
            "labels": ["ISSN"],
            "props": {"id": "7.2973525693", "type": "electronic"},
            "outgoing_rels": [],
        },
    ]
    # print("DIFF:", DeepDiff(expected_result_nodes, result, ignore_order=True))
    assert_result(result, expected_result_nodes)


test_OverridePropertyName()
test_OverrideReliationType()
# todo: test_TypeCastProperty()
test_UppercaseRelationType()
test_FlipNodes()


def test_TypeCastProperty():
    # TODO
    # we need node properties shifting to relation first
    wipe_all_neo4j_data(DRIVER)
    data = {"name": "Pallas", "inhabitans": {"species": "human"}}
    d2g = Dict2graph()
    d2g.add_relation_transformation(
        Transformer.match_rel("stationed").do(
            RelTrans.TypeCastProperty("is_active", bool)
        )
    )
    d2g.parse(data, "Asteroid")
    d2g.create(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_result_nodes: dict = [
        {"labels": ["ship"], "props": {"name": "Zheng Fei"}, "outgoing_rels": []},
        {
            "labels": ["Person"],
            "props": {"name": "Holden"},
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "IS_STATIONED_AT",
                    "rel_target_node": {
                        "labels": ["ship"],
                        "props": {"name": "Zheng Fei"},
                    },
                }
            ],
        },
    ]
    # print("DIFF:", DeepDiff(expected_result_nodes, result, ignore_order=True))
    assert_result(result, expected_result_nodes)
