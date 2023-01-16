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
            "labels": ["CollectionHub", "pupils"],
            "props": {"id": "15ae1bf7a577ae4c5e429418639cc81d"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 2},
                    "rel_type": "pupils_HAS_pupils",
                    "rel_target_node": {
                        "labels": ["pupils", "CollectionItem"],
                        "props": {
                            "firstname": "Wolfgang",
                            "age": 147,
                            "lastname": "Pauli",
                        },
                    },
                },
                {
                    "rel_props": {"_list_item_index": 1},
                    "rel_type": "pupils_HAS_pupils",
                    "rel_target_node": {
                        "labels": ["pupils", "CollectionItem"],
                        "props": {
                            "firstname": "Wolfgang",
                            "age": 123,
                            "lastname": "Pauli",
                        },
                    },
                },
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "pupils_HAS_pupils",
                    "rel_target_node": {
                        "labels": ["pupils", "CollectionItem"],
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
            "labels": ["pupils", "CollectionItem"],
            "props": {"firstname": "Wolfgang", "age": 34, "lastname": "Pauli"},
            "outgoing_rels": [],
        },
        {
            "labels": ["pupils", "CollectionItem"],
            "props": {"firstname": "Wolfgang", "age": 123, "lastname": "Pauli"},
            "outgoing_rels": [],
        },
        {
            "labels": ["pupils", "CollectionItem"],
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
            "labels": ["CollectionHub", "persons"],
            "props": {"id": "5cf48f5b18ab1bf7f29a9e98aa753a19"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "persons_HAS_person",
                    "rel_target_node": {
                        "labels": ["person", "CollectionItem"],
                        "props": {
                            "firstname": "Wolfgang",
                            "age": 34,
                            "lastname": "Pauli",
                        },
                    },
                },
                {
                    "rel_props": {"_list_item_index": 1},
                    "rel_type": "persons_HAS_person",
                    "rel_target_node": {
                        "labels": ["person", "CollectionItem"],
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
            "labels": ["person", "CollectionItem"],
            "props": {"firstname": "Wolfgang", "age": 34, "lastname": "Pauli"},
            "outgoing_rels": [],
        },
        {
            "labels": ["person", "CollectionItem"],
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
            "labels": ["CollectionHub", "persons"],
            "props": {"id": "5cf48f5b18ab1bf7f29a9e98aa753a19"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 1},
                    "rel_type": "persons_HAS_person",
                    "rel_target_node": {
                        "labels": ["person", "CollectionItem"],
                        "props": {
                            "firstname": "Wolfgang",
                            "age": 123,
                            "lastname": "Pauli",
                        },
                    },
                },
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "persons_HAS_person",
                    "rel_target_node": {
                        "labels": ["person", "CollectionItem"],
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
            "labels": ["person", "CollectionItem"],
            "props": {"firstname": "Wolfgang", "age": 34, "lastname": "Pauli"},
            "outgoing_rels": [],
        },
        {
            "labels": ["person", "CollectionItem"],
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
        {
            "labels": ["CollectionHub", "Stuff"],
            "props": {"id": "a8679369cb299d6b0f645e4e6ce6c510"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 2},
                    "rel_type": "Stuff_HAS_Stuff",
                    "rel_target_node": {
                        "labels": ["Stuff", "CollectionItem"],
                        "props": {"somekey1": "yooo", "somekey2": "nooo"},
                    },
                },
                {
                    "rel_props": {"_list_item_index": 1},
                    "rel_type": "Stuff_HAS_box",
                    "rel_target_node": {
                        "labels": ["box", "CollectionItem"],
                        "props": {"shape": "boxy", "color": "brown"},
                    },
                },
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "Stuff_HAS_person",
                    "rel_target_node": {
                        "labels": ["person", "CollectionItem"],
                        "props": {"firstname": "Wolfgang", "lastname": "Pauli"},
                    },
                },
            ],
        },
        {"labels": ["child"], "props": {"name": "Anne"}, "outgoing_rels": []},
        {
            "labels": ["person", "CollectionItem"],
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
            "labels": ["box", "CollectionItem"],
            "props": {"shape": "boxy", "color": "brown"},
            "outgoing_rels": [],
        },
        {
            "labels": ["Stuff", "CollectionItem"],
            "props": {"somekey1": "yooo", "somekey2": "nooo"},
            "outgoing_rels": [],
        },
    ]
    assert_result(result, expected_res)


def test_nested_obj():
    wipe_all_neo4j_data(DRIVER)
    data = {"name": "Holden", "stationed": {"ship": {"name": "Zheng Fei"}}}
    d2g = Dict2graph()
    d2g.parse(data, "Person")
    d2g.create(DRIVER)
    result = get_all_neo4j_data(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_res: dict = [
        {"labels": ["ship"], "props": {"name": "Zheng Fei"}, "outgoing_rels": []},
        {
            "labels": ["Person"],
            "props": {"name": "Holden"},
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "stationed",
                    "rel_target_node": {
                        "labels": ["ship"],
                        "props": {"name": "Zheng Fei"},
                    },
                }
            ],
        },
    ]
    # print("DIFF:", DeepDiff(expected_res, result, ignore_order=True))
    assert_result(result, expected_res)


def test_nested_obj_2():
    wipe_all_neo4j_data(DRIVER)
    data = {
        "Person": "Holden",
        "Ship": {"Engine": {"type": "Epstein Drive"}, "name": "Zheng Fei"},
    }
    d2g = Dict2graph()
    d2g.parse(data, "Person")
    d2g.create(DRIVER)
    result = get_all_neo4j_data(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_res: dict = [
        {"labels": ["Engine"], "props": {"type": "Epstein Drive"}, "outgoing_rels": []},
        {
            "labels": ["Ship"],
            "props": {"name": "Zheng Fei"},
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "Ship_HAS_Engine",
                    "rel_target_node": {
                        "labels": ["Engine"],
                        "props": {"type": "Epstein Drive"},
                    },
                }
            ],
        },
        {
            "labels": ["Person"],
            "props": {"Person": "Holden"},
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "Person_HAS_Ship",
                    "rel_target_node": {
                        "labels": ["Ship"],
                        "props": {"name": "Zheng Fei"},
                    },
                }
            ],
        },
    ]
    # print("DIFF:", DeepDiff(expected_res, result, ignore_order=True))
    assert_result(result, expected_res)


test_create_simple_obj()
test_create_simple_graph()
test_create_wrapped_list_graph()
test_create_list_of_obj_graph()
test_create_root_list_graph()
test_create_mixed_list_graph()
test_nested_obj()
test_nested_obj_2()
