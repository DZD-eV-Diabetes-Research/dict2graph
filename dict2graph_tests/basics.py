import json
import os, sys

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


def test_create_simple_obj():
    wipe_all_neo4j_data(DRIVER)
    data = {"person": {"firstname": "Wolfgang", "lastname": "Pauli", "age": 34}}

    d2g = Dict2graph()
    d2g.parse(data)
    d2g.create(DRIVER)
    result = get_all_neo4j_data(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_res: dict = [
        {
            "labels": ["person"],
            "props": {"firstname": "Wolfgang", "age": 34, "lastname": "Pauli"},
            "outgoing_rels": [],
        }
    ]
    assert_result(result, expected_res)


def test_create_simple_graph():
    wipe_all_neo4j_data(DRIVER)
    data = {
        "person": {
            "firstname": "Wolfgang",
            "lastname": "Pauli",
            "age": 34,
            "affiliation": {"name": "CERN"},
        }
    }

    d2g = Dict2graph()
    d2g.parse(data)
    d2g.create(DRIVER)
    result = get_all_neo4j_data(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_res: dict = [
        {"labels": ["affiliation"], "props": {"name": "CERN"}, "outgoing_rels": []},
        {
            "labels": ["person"],
            "props": {"firstname": "Wolfgang", "age": 34, "lastname": "Pauli"},
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "person_HAS_affiliation",
                    "rel_target_node": {
                        "labels": ["affiliation"],
                        "props": {"name": "CERN"},
                    },
                }
            ],
        },
    ]
    assert_result(result, expected_res)


def test_create_wrapped_list_graph():
    wipe_all_neo4j_data(DRIVER)
    data = {
        "pupils": [
            {"firstname": "Wolfgang", "lastname": "Pauli", "age": 34},
            {"firstname": "Wolfgang", "lastname": "Pauli", "age": 123},
            {"firstname": "Wolfgang", "lastname": "Pauli", "age": 147},
        ]
    }
    d2g = Dict2graph()
    d2g.parse(data)
    d2g.create(DRIVER)
    result = get_all_neo4j_data(DRIVER)
    # print(json.dumps(result, indent=2))
    expected_res: dict = [
        {
            "labels": ["CollectionHub", "CollectionHubpupils"],
            "props": {"id": "15ae1bf7a577ae4c5e429418639cc81d"},
            "outgoing_rels": [
                {
                    "rel_props": {"_index": 2},
                    "rel_type": "CollectionHub_CollectionHubpupils_HAS_pupils",
                    "rel_target_node": {
                        "labels": ["pupils"],
                        "props": {
                            "firstname": "Wolfgang",
                            "age": 147,
                            "lastname": "Pauli",
                        },
                    },
                },
                {
                    "rel_props": {"_index": 1},
                    "rel_type": "CollectionHub_CollectionHubpupils_HAS_pupils",
                    "rel_target_node": {
                        "labels": ["pupils"],
                        "props": {
                            "firstname": "Wolfgang",
                            "age": 123,
                            "lastname": "Pauli",
                        },
                    },
                },
                {
                    "rel_props": {"_index": 0},
                    "rel_type": "CollectionHub_CollectionHubpupils_HAS_pupils",
                    "rel_target_node": {
                        "labels": ["pupils"],
                        "props": {
                            "firstname": "Wolfgang",
                            "age": 34,
                            "lastname": "Pauli",
                        },
                    },
                },
            ],
        },
        {
            "labels": ["pupils"],
            "props": {"firstname": "Wolfgang", "age": 34, "lastname": "Pauli"},
            "outgoing_rels": [],
        },
        {
            "labels": ["pupils"],
            "props": {"firstname": "Wolfgang", "age": 123, "lastname": "Pauli"},
            "outgoing_rels": [],
        },
        {
            "labels": ["pupils"],
            "props": {"firstname": "Wolfgang", "age": 147, "lastname": "Pauli"},
            "outgoing_rels": [],
        },
    ]
    assert_result(result, expected_res)


def test_create_list_of_obj_graph():
    wipe_all_neo4j_data(DRIVER)
    data = {
        "persons": [
            {"person": {"firstname": "Wolfgang", "lastname": "Pauli", "age": 34}},
            {"person": {"firstname": "Wolfgang", "lastname": "Pauli", "age": 123}},
        ]
    }
    d2g = Dict2graph()
    d2g.parse(data)
    d2g.create(DRIVER)
    result = get_all_neo4j_data(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_res: dict = [
        {
            "labels": ["CollectionHub", "CollectionHubpersons"],
            "props": {"id": "5cf48f5b18ab1bf7f29a9e98aa753a19"},
            "outgoing_rels": [
                {
                    "rel_props": {"_index": 1},
                    "rel_type": "CollectionHub_CollectionHubpersons_HAS_person",
                    "rel_target_node": {
                        "labels": ["person"],
                        "props": {
                            "firstname": "Wolfgang",
                            "age": 123,
                            "lastname": "Pauli",
                        },
                    },
                },
                {
                    "rel_props": {"_index": 0},
                    "rel_type": "CollectionHub_CollectionHubpersons_HAS_person",
                    "rel_target_node": {
                        "labels": ["person"],
                        "props": {
                            "firstname": "Wolfgang",
                            "age": 34,
                            "lastname": "Pauli",
                        },
                    },
                },
            ],
        },
        {
            "labels": ["person"],
            "props": {"firstname": "Wolfgang", "age": 34, "lastname": "Pauli"},
            "outgoing_rels": [],
        },
        {
            "labels": ["person"],
            "props": {"firstname": "Wolfgang", "age": 123, "lastname": "Pauli"},
            "outgoing_rels": [],
        },
    ]
    assert_result(result, expected_res)


def test_create_root_list_graph():
    wipe_all_neo4j_data(DRIVER)
    data = [
        {"person": {"firstname": "Wolfgang", "lastname": "Pauli", "age": 34}},
        {"person": {"firstname": "Wolfgang", "lastname": "Pauli", "age": 123}},
    ]
    d2g = Dict2graph()
    d2g.parse(data, "persons")
    d2g.create(DRIVER)
    result = get_all_neo4j_data(DRIVER)
    # print(json.dumps(result, indent=2))
    expected_res: dict = [
        {
            "labels": ["CollectionHub", "CollectionHubpersons"],
            "props": {"id": "5cf48f5b18ab1bf7f29a9e98aa753a19"},
            "outgoing_rels": [
                {
                    "rel_props": {"_index": 0},
                    "rel_type": "CollectionHub_CollectionHubpersons_HAS_person",
                    "rel_target_node": {
                        "labels": ["person"],
                        "props": {
                            "firstname": "Wolfgang",
                            "age": 34,
                            "lastname": "Pauli",
                        },
                    },
                },
                {
                    "rel_props": {"_index": 1},
                    "rel_type": "CollectionHub_CollectionHubpersons_HAS_person",
                    "rel_target_node": {
                        "labels": ["person"],
                        "props": {
                            "firstname": "Wolfgang",
                            "age": 123,
                            "lastname": "Pauli",
                        },
                    },
                },
            ],
        },
        {
            "labels": ["person"],
            "props": {"firstname": "Wolfgang", "age": 34, "lastname": "Pauli"},
            "outgoing_rels": [],
        },
        {
            "labels": ["person"],
            "props": {"firstname": "Wolfgang", "age": 123, "lastname": "Pauli"},
            "outgoing_rels": [],
        },
    ]
    assert_result(result, expected_res)


def test_create_mixed_list_graph():
    wipe_all_neo4j_data(DRIVER)
    data = [
        {
            "person": {
                "firstname": "Wolfgang",
                "lastname": "Pauli",
                "child": {"name": "Anne"},
            }
        },
        {"box": {"shape": "boxy", "color": "brown"}},
        {"somekey1": "yooo", "somekey2": "nooo"},
    ]
    d2g = Dict2graph()
    d2g.parse(data, "Stuff")
    d2g.create(DRIVER)
    result = get_all_neo4j_data(DRIVER)
    # print(json.dumps(result, indent=2))
    expected_res: dict = [
        {"labels": ["child"], "props": {"name": "Anne"}, "outgoing_rels": []},
        {
            "labels": ["person"],
            "props": {"firstname": "Wolfgang", "lastname": "Pauli"},
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "person_HAS_child",
                    "rel_target_node": {"labels": ["child"], "props": {"name": "Anne"}},
                }
            ],
        },
        {
            "labels": ["box"],
            "props": {"shape": "boxy", "color": "brown"},
            "outgoing_rels": [],
        },
        {
            "labels": ["Stuff"],
            "props": {"somekey1": "yooo", "somekey2": "nooo"},
            "outgoing_rels": [],
        },
        {
            "labels": ["CollectionHub", "CollectionHubStuff"],
            "props": {"id": "a8679369cb299d6b0f645e4e6ce6c510"},
            "outgoing_rels": [
                {
                    "rel_props": {"_index": 2},
                    "rel_type": "CollectionHub_CollectionHubStuff_HAS_Stuff",
                    "rel_target_node": {
                        "labels": ["Stuff"],
                        "props": {"somekey1": "yooo", "somekey2": "nooo"},
                    },
                },
                {
                    "rel_props": {"_index": 1},
                    "rel_type": "CollectionHub_CollectionHubStuff_HAS_box",
                    "rel_target_node": {
                        "labels": ["box"],
                        "props": {"shape": "boxy", "color": "brown"},
                    },
                },
                {
                    "rel_props": {"_index": 0},
                    "rel_type": "CollectionHub_CollectionHubStuff_HAS_person",
                    "rel_target_node": {
                        "labels": ["person"],
                        "props": {"firstname": "Wolfgang", "lastname": "Pauli"},
                    },
                },
            ],
        },
    ]
    assert_result(result, expected_res)


test_create_simple_obj()
test_create_simple_graph()
test_create_wrapped_list_graph()
test_create_list_of_obj_graph()
test_create_root_list_graph()
test_create_mixed_list_graph()
