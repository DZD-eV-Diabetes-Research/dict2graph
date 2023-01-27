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
    get_all_neo4j_nodes_with_rels,
    assert_result,
)


def test_create_simple_obj():
    wipe_all_neo4j_data(DRIVER)
    data = {"person": {"firstname": "Wolfgang", "lastname": "Pauli", "age": 34}}

    d2g = Dict2graph()
    d2g.parse(data)
    d2g.create(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_result_nodes: dict = [
        {
            "labels": ["person"],
            "props": {"firstname": "Wolfgang", "age": 34, "lastname": "Pauli"},
            "outgoing_rels": [],
        }
    ]
    assert_result(result, expected_result_nodes)


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
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_result_nodes: dict = [
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
    assert_result(result, expected_result_nodes)


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
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))
    expected_result_nodes: dict = [
        {
            "labels": ["ListHub", "pupils"],
            "props": {"id": "15ae1bf7a577ae4c5e429418639cc81d"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 1},
                    "rel_type": "pupils_LIST_HAS_pupils",
                    "rel_target_node": {
                        "labels": ["pupils", "ListItem"],
                        "props": {
                            "firstname": "Wolfgang",
                            "age": 123,
                            "lastname": "Pauli",
                        },
                    },
                },
                {
                    "rel_props": {"_list_item_index": 2},
                    "rel_type": "pupils_LIST_HAS_pupils",
                    "rel_target_node": {
                        "labels": ["pupils", "ListItem"],
                        "props": {
                            "firstname": "Wolfgang",
                            "age": 147,
                            "lastname": "Pauli",
                        },
                    },
                },
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "pupils_LIST_HAS_pupils",
                    "rel_target_node": {
                        "labels": ["pupils", "ListItem"],
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
            "labels": ["pupils", "ListItem"],
            "props": {"firstname": "Wolfgang", "age": 34, "lastname": "Pauli"},
            "outgoing_rels": [],
        },
        {
            "labels": ["pupils", "ListItem"],
            "props": {"firstname": "Wolfgang", "age": 123, "lastname": "Pauli"},
            "outgoing_rels": [],
        },
        {
            "labels": ["pupils", "ListItem"],
            "props": {"firstname": "Wolfgang", "age": 147, "lastname": "Pauli"},
            "outgoing_rels": [],
        },
    ]
    assert_result(result, expected_result_nodes)


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
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_result_nodes: dict = [
        {
            "labels": ["ListHub", "persons"],
            "props": {"id": "5cf48f5b18ab1bf7f29a9e98aa753a19"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "persons_LIST_HAS_person",
                    "rel_target_node": {
                        "labels": ["person", "ListItem"],
                        "props": {
                            "firstname": "Wolfgang",
                            "age": 34,
                            "lastname": "Pauli",
                        },
                    },
                },
                {
                    "rel_props": {"_list_item_index": 1},
                    "rel_type": "persons_LIST_HAS_person",
                    "rel_target_node": {
                        "labels": ["person", "ListItem"],
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
            "labels": ["person", "ListItem"],
            "props": {"firstname": "Wolfgang", "age": 34, "lastname": "Pauli"},
            "outgoing_rels": [],
        },
        {
            "labels": ["person", "ListItem"],
            "props": {"firstname": "Wolfgang", "age": 123, "lastname": "Pauli"},
            "outgoing_rels": [],
        },
    ]
    assert_result(result, expected_result_nodes)


def test_create_root_list_graph():
    wipe_all_neo4j_data(DRIVER)
    data = [
        {"person": {"firstname": "Wolfgang", "lastname": "Pauli", "age": 34}},
        {"person": {"firstname": "Wolfgang", "lastname": "Pauli", "age": 123}},
    ]
    d2g = Dict2graph()
    d2g.parse(data, "persons")
    d2g.create(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))
    expected_result_nodes: dict = [
        {
            "labels": ["ListHub", "persons"],
            "props": {"id": "5cf48f5b18ab1bf7f29a9e98aa753a19"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "persons_LIST_HAS_person",
                    "rel_target_node": {
                        "labels": ["person", "ListItem"],
                        "props": {
                            "firstname": "Wolfgang",
                            "age": 34,
                            "lastname": "Pauli",
                        },
                    },
                },
                {
                    "rel_props": {"_list_item_index": 1},
                    "rel_type": "persons_LIST_HAS_person",
                    "rel_target_node": {
                        "labels": ["person", "ListItem"],
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
            "labels": ["person", "ListItem"],
            "props": {"firstname": "Wolfgang", "age": 34, "lastname": "Pauli"},
            "outgoing_rels": [],
        },
        {
            "labels": ["person", "ListItem"],
            "props": {"firstname": "Wolfgang", "age": 123, "lastname": "Pauli"},
            "outgoing_rels": [],
        },
    ]
    assert_result(result, expected_result_nodes)


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
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))
    expected_result_nodes: dict = [
        {
            "labels": ["ListHub", "Stuff"],
            "props": {"id": "a8679369cb299d6b0f645e4e6ce6c510"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 2},
                    "rel_type": "Stuff_LIST_HAS_Stuff",
                    "rel_target_node": {
                        "labels": ["Stuff", "ListItem"],
                        "props": {"somekey1": "yooo", "somekey2": "nooo"},
                    },
                },
                {
                    "rel_props": {"_list_item_index": 1},
                    "rel_type": "Stuff_LIST_HAS_box",
                    "rel_target_node": {
                        "labels": ["box", "ListItem"],
                        "props": {"shape": "boxy", "color": "brown"},
                    },
                },
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "Stuff_LIST_HAS_person",
                    "rel_target_node": {
                        "labels": ["person", "ListItem"],
                        "props": {"firstname": "Wolfgang", "lastname": "Pauli"},
                    },
                },
            ],
        },
        {"labels": ["child"], "props": {"name": "Anne"}, "outgoing_rels": []},
        {
            "labels": ["person", "ListItem"],
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
            "labels": ["box", "ListItem"],
            "props": {"shape": "boxy", "color": "brown"},
            "outgoing_rels": [],
        },
        {
            "labels": ["Stuff", "ListItem"],
            "props": {"somekey1": "yooo", "somekey2": "nooo"},
            "outgoing_rels": [],
        },
    ]
    assert_result(result, expected_result_nodes)


def test_nested_obj():
    wipe_all_neo4j_data(DRIVER)
    data = {"name": "Holden", "stationed": {"ship": {"name": "Zheng Fei"}}}
    d2g = Dict2graph()
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
                    "rel_type": "stationed",
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


def test_nested_obj_2():
    wipe_all_neo4j_data(DRIVER)
    data = {
        "Person": "Holden",
        "Ship": {"Engine": {"type": "Epstein Drive"}, "name": "Zheng Fei"},
    }
    d2g = Dict2graph()
    d2g.parse(data, "Person")
    d2g.create(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_result_nodes: dict = [
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
    # print("DIFF:", DeepDiff(expected_result_nodes, result, ignore_order=True))
    assert_result(result, expected_result_nodes)


def test_merge_two_dicts():
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
    d2g.parse(dic1)
    d2g.parse(dic2)
    d2g.merge(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_result_nodes: dict = [
        {
            "labels": ["ListHub", "Authors"],
            "props": {"id": "a7a883e2547c5af03676543b2325ea96"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "Authors_LIST_HAS_Authors",
                    "rel_target_node": {
                        "labels": ["ListItem", "Authors"],
                        "props": {"firstName": "Mike", "lastName": "Pondsmith"},
                    },
                }
            ],
        },
        {
            "labels": ["ListHub", "Authors"],
            "props": {"id": "b8f6cc9fa9ce70b36d1d7d4dbc57d0f9"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "Authors_LIST_HAS_Authors",
                    "rel_target_node": {
                        "labels": ["ListItem", "Authors"],
                        "props": {"firstName": "Mike", "lastName": "Pondsmith"},
                    },
                }
            ],
        },
        {
            "labels": ["ListHub", "affiliation"],
            "props": {"id": "44de0fb70ce9cd28873b3ba6142dd159"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "affiliation_LIST_HAS_affiliation",
                    "rel_target_node": {
                        "labels": ["affiliation", "ListItem"],
                        "props": {"name": "University 1"},
                    },
                }
            ],
        },
        {
            "labels": ["ListHub", "affiliation"],
            "props": {"id": "19f20f7210d4d743bdaf83b1b541d8a7"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 1},
                    "rel_type": "affiliation_LIST_HAS_affiliation",
                    "rel_target_node": {
                        "labels": ["affiliation", "ListItem"],
                        "props": {"name": "University 2"},
                    },
                },
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "affiliation_LIST_HAS_affiliation",
                    "rel_target_node": {
                        "labels": ["affiliation", "ListItem"],
                        "props": {"name": "University 1"},
                    },
                },
            ],
        },
        {
            "labels": ["affiliation", "ListItem"],
            "props": {"name": "University 1"},
            "outgoing_rels": [],
        },
        {
            "labels": ["affiliation", "ListItem"],
            "props": {"name": "University 2"},
            "outgoing_rels": [],
        },
        {
            "labels": ["ListItem", "Authors"],
            "props": {"firstName": "Mike", "lastName": "Pondsmith"},
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "Authors_HAS_affiliation",
                    "rel_target_node": {
                        "labels": ["ListHub", "affiliation"],
                        "props": {"id": "44de0fb70ce9cd28873b3ba6142dd159"},
                    },
                },
                {
                    "rel_props": {},
                    "rel_type": "Authors_HAS_affiliation",
                    "rel_target_node": {
                        "labels": ["ListHub", "affiliation"],
                        "props": {"id": "19f20f7210d4d743bdaf83b1b541d8a7"},
                    },
                },
            ],
        },
        {
            "labels": ["Article"],
            "props": {"title": "Science Behind The Cyberpunk-Genres Awesomeness"},
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "Article_HAS_Authors",
                    "rel_target_node": {
                        "labels": ["ListHub", "Authors"],
                        "props": {"id": "a7a883e2547c5af03676543b2325ea96"},
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
                    "rel_type": "Article_HAS_Authors",
                    "rel_target_node": {
                        "labels": ["ListHub", "Authors"],
                        "props": {"id": "b8f6cc9fa9ce70b36d1d7d4dbc57d0f9"},
                    },
                }
            ],
        },
    ]
    # print("DIFF:", DeepDiff(expected_result_nodes, result, ignore_order=True))
    assert_result(result, expected_result_nodes)


def test_empty_obj01():
    wipe_all_neo4j_data(DRIVER)
    data = {
        "ship": [
            {"name": "Agatha King", "navy": "United Nations Navy"},
            {},
        ]
    }
    d2g = Dict2graph()
    d2g.parse(data)
    d2g.create(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))

    # ToReview: i am not sure if iam happy with this result. its missing a rel but it makes sense from a database perspective. we can not connect to an anaonymous node with no props
    expected_result_nodes: dict = [
        {
            "labels": ["ListHub", "ship"],
            "props": {"id": "be18eceea6105854d14dab4ea36cbf41"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 1},
                    "rel_type": "ship_LIST_HAS_ship",
                    "rel_target_node": {
                        "labels": ["ListItem", "ship"],
                        "props": {"id": "d751713988987e9331980363e24189ce"},
                    },
                },
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "ship_LIST_HAS_ship",
                    "rel_target_node": {
                        "labels": ["ListItem", "ship"],
                        "props": {"navy": "United Nations Navy", "name": "Agatha King"},
                    },
                },
            ],
        },
        {
            "labels": ["ListItem", "ship"],
            "props": {"navy": "United Nations Navy", "name": "Agatha King"},
            "outgoing_rels": [],
        },
        {
            "labels": ["ListItem", "ship"],
            "props": {"id": "d751713988987e9331980363e24189ce"},
            "outgoing_rels": [],
        },
    ]
    assert_result(result, expected_result_nodes)


def test_empty_obj02():
    wipe_all_neo4j_data(DRIVER)
    data = {
        "nothing": {},
    }
    d2g = Dict2graph()
    d2g.parse(data)
    d2g.create(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_result_nodes: dict = [
        {
            "labels": ["nothing"],
            "props": {"id": "d751713988987e9331980363e24189ce"},
            "outgoing_rels": [],
        }
    ]
    assert_result(result, expected_result_nodes)


def test_error_case_list_01():
    wipe_all_neo4j_data(DRIVER)
    data = {
        "ship": [
            {"name": "Agatha King", "navy": "United Nations Navy"},
            {"name": "", "navy": None},
        ]
    }
    d2g = Dict2graph()
    d2g.parse(data)
    d2g.create(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))

    # ToReview: i am not sure if iam happy with this result. its missing a rel but it makes sense from a database perspective. we can not connect to an anaonymous node with no props
    expected_result_nodes: dict = [
        {
            "labels": ["ListHub", "ship"],
            "props": {"id": "2061e61739236751d14ae01dfe54023a"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 1},
                    "rel_type": "ship_LIST_HAS_ship",
                    "rel_target_node": {
                        "labels": ["ListItem", "ship"],
                        "props": {"name": ""},
                    },
                },
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "ship_LIST_HAS_ship",
                    "rel_target_node": {
                        "labels": ["ListItem", "ship"],
                        "props": {"navy": "United Nations Navy", "name": "Agatha King"},
                    },
                },
            ],
        },
        {
            "labels": ["ListItem", "ship"],
            "props": {"navy": "United Nations Navy", "name": "Agatha King"},
            "outgoing_rels": [],
        },
        {
            "labels": ["ListItem", "ship"],
            "props": {"name": ""},
            "outgoing_rels": [],
        },
    ]
    assert_result(result, expected_result_nodes)


def test_match_filter_rel():
    wipe_all_neo4j_data(DRIVER)
    data = {
        "bookshelf": {
            "books": [
                {
                    "title": "Fine-structure constant - God set our instance a fine environment variable",
                },
            ],
        }
    }
    d2g = Dict2graph()
    d2g.add_transformation(
        Transformer.match_rel(relation_type_is_not_in=["books_LIST_HAS_books"]).do(
            RelTrans.AddProperty({"matched": True})
        )
    )
    d2g.parse(data)
    d2g.create(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))

    # ToReview: i am not sure if iam happy with this result. its missing a rel but it makes sense from a database perspective. we can not connect to an anaonymous node with no props
    expected_result_nodes: dict = [
        {
            "labels": ["books", "ListHub"],
            "props": {"id": "9aacef856f873c8156b5e596424b710c"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "books_LIST_HAS_books",
                    "rel_target_node": {
                        "labels": ["books", "ListItem"],
                        "props": {
                            "title": "Fine-structure constant - God set our instance a fine environment variable"
                        },
                    },
                }
            ],
        },
        {
            "labels": ["books", "ListItem"],
            "props": {
                "title": "Fine-structure constant - God set our instance a fine environment variable"
            },
            "outgoing_rels": [],
        },
        {
            "labels": ["bookshelf"],
            "props": {"id": "873aefa9444fb733b8438536edcd1e95"},
            "outgoing_rels": [
                {
                    "rel_props": {"matched": True},
                    "rel_type": "bookshelf_HAS_books",
                    "rel_target_node": {
                        "labels": ["books", "ListHub"],
                        "props": {"id": "9aacef856f873c8156b5e596424b710c"},
                    },
                }
            ],
        },
    ]
    assert_result(result, expected_result_nodes)


if __name__ == "__main__" or os.getenv("DICT2GRAPH_RUN_ALL_TESTS", None) == "true":
    test_create_simple_obj()
    test_create_simple_graph()
    test_create_wrapped_list_graph()
    test_create_list_of_obj_graph()
    test_create_root_list_graph()
    test_create_mixed_list_graph()
    test_nested_obj()
    test_nested_obj_2()
    test_merge_two_dicts()
    test_empty_obj01()
    test_empty_obj02()
    test_error_case_list_01()
    test_match_filter_rel()
