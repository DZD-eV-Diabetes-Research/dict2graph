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


def test_readme_start_example():
    wipe_all_neo4j_data(DRIVER)
    data = {
        "action": {
            "id": 1,
            "target": "El Oued",
            "entities": [{"id": "Isabelle Eberhardt"}, {"id": "Slimène Ehnni"}],
        }
    }
    d2g = Dict2graph()
    d2g.parse(data)
    d2g.create(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    expected_result_nodes: dict = [
        {
            "labels": ["ListHub", "entities"],
            "props": {"id": "e9c915649e338a805eda93f4cff31d31"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "entities_LIST_HAS_entities",
                    "rel_target_node": {
                        "labels": ["ListItem", "entities"],
                        "props": {"id": "Isabelle Eberhardt"},
                    },
                },
                {
                    "rel_props": {"_list_item_index": 1},
                    "rel_type": "entities_LIST_HAS_entities",
                    "rel_target_node": {
                        "labels": ["ListItem", "entities"],
                        "props": {"id": "Slimène Ehnni"},
                    },
                },
            ],
        },
        {
            "labels": ["ListItem", "entities"],
            "props": {"id": "Isabelle Eberhardt"},
            "outgoing_rels": [],
        },
        {
            "labels": ["ListItem", "entities"],
            "props": {"id": "Slimène Ehnni"},
            "outgoing_rels": [],
        },
        {
            "labels": ["action"],
            "props": {"id": 1, "target": "El Oued"},
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "action_HAS_entities",
                    "rel_target_node": {
                        "labels": ["ListHub", "entities"],
                        "props": {"id": "e9c915649e338a805eda93f4cff31d31"},
                    },
                }
            ],
        },
    ]
    assert_result(result, expected_result_nodes)


def test_readme_start_example_transformed():
    wipe_all_neo4j_data(DRIVER)
    data = {
        "Action": {
            "id": 1,
            "target": "El Oued",
            "Entities": [{"id": "Isabelle Eberhardt"}, {"id": "Slimène Ehnni"}],
        }
    }
    d2g = Dict2graph()
    d2g.add_transformation(
        [
            Transformer.match_node().do(NodeTrans.CapitalizeLabels()),
            Transformer.match_rel().do(RelTrans.UppercaseRelationType()),
            Transformer.match_node().do(NodeTrans.PopListHubNodes()),
        ]
    )
    d2g.parse(data)
    d2g.create(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    expected_result_nodes: dict = [
        {
            "labels": ["Entities", "Listitem"],
            "props": {"id": "Isabelle Eberhardt"},
            "outgoing_rels": [],
        },
        {
            "labels": ["Entities", "Listitem"],
            "props": {"id": "Slimène Ehnni"},
            "outgoing_rels": [],
        },
        {
            "labels": ["Action"],
            "props": {"id": 1, "target": "El Oued"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "ACTION_HAS_ENTITIES",
                    "rel_target_node": {
                        "labels": ["Entities", "Listitem"],
                        "props": {"id": "Isabelle Eberhardt"},
                    },
                },
                {
                    "rel_props": {"_list_item_index": 1},
                    "rel_type": "ACTION_HAS_ENTITIES",
                    "rel_target_node": {
                        "labels": ["Entities", "Listitem"],
                        "props": {"id": "Slimène Ehnni"},
                    },
                },
            ],
        },
    ]
    assert_result(result, expected_result_nodes)


def test_basics_start_example():
    wipe_all_neo4j_data(DRIVER)
    data = {
        "person": {
            "firstname": "Rudolf",
            "lastname": "Manga Bell",
            "age": 41,
            "affiliation": {"name": "Duálá"},
        }
    }
    d2g = Dict2graph()
    d2g.parse(data)
    d2g.create(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    expected_result_nodes: dict = [
        {"labels": ["affiliation"], "props": {"name": "Duálá"}, "outgoing_rels": []},
        {
            "labels": ["person"],
            "props": {"firstname": "Rudolf", "age": 41, "lastname": "Manga Bell"},
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "person_HAS_affiliation",
                    "rel_target_node": {
                        "labels": ["affiliation"],
                        "props": {"name": "Duálá"},
                    },
                }
            ],
        },
    ]
    assert_result(result, expected_result_nodes)


def test_basics_why_merge_example():
    wipe_all_neo4j_data(DRIVER)
    data_1 = {
        "person": {
            "firstname": "Rudolf",
            "lastname": "Manga Bell",
            "age": 41,
            "affiliation": {"name": "Duálá"},
        }
    }
    data_2 = {
        "person": {
            "firstname": "Rudolf",
            "lastname": "Manga Bell",
            "age": 41,
            "mission": {"name": "resistance leader"},
        }
    }
    d2g = Dict2graph()
    d2g.parse(data_1)
    d2g.parse(data_2)
    d2g.create(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    expected_result_nodes: dict = [
        {"labels": ["affiliation"], "props": {"name": "Duálá"}, "outgoing_rels": []},
        {
            "labels": ["person"],
            "props": {"firstname": "Rudolf", "age": 41, "lastname": "Manga Bell"},
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "person_HAS_mission",
                    "rel_target_node": {
                        "labels": ["mission"],
                        "props": {"name": "resistance leader"},
                    },
                },
                {
                    "rel_props": {},
                    "rel_type": "person_HAS_affiliation",
                    "rel_target_node": {
                        "labels": ["affiliation"],
                        "props": {"name": "Duálá"},
                    },
                },
            ],
        },
        {
            "labels": ["person"],
            "props": {"firstname": "Rudolf", "age": 41, "lastname": "Manga Bell"},
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "person_HAS_mission",
                    "rel_target_node": {
                        "labels": ["mission"],
                        "props": {"name": "resistance leader"},
                    },
                },
                {
                    "rel_props": {},
                    "rel_type": "person_HAS_affiliation",
                    "rel_target_node": {
                        "labels": ["affiliation"],
                        "props": {"name": "Duálá"},
                    },
                },
            ],
        },
        {
            "labels": ["mission"],
            "props": {"name": "resistance leader"},
            "outgoing_rels": [],
        },
    ]
    assert_result(result, expected_result_nodes)


def test_basics_merge_example():
    wipe_all_neo4j_data(DRIVER)
    data_1 = {
        "person": {
            "firstname": "Rudolf",
            "lastname": "Manga Bell",
            "age": 41,
            "affiliation": {"name": "Duálá"},
        }
    }
    data_2 = {
        "person": {
            "firstname": "Rudolf",
            "lastname": "Manga Bell",
            "age": 41,
            "mission": {"name": "resistance leader"},
        }
    }
    d2g = Dict2graph()
    d2g.parse(data_1)
    d2g.parse(data_2)
    d2g.merge(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    expected_result_nodes: dict = [
        {"labels": ["affiliation"], "props": {"name": "Duálá"}, "outgoing_rels": []},
        {
            "labels": ["person"],
            "props": {"firstname": "Rudolf", "age": 41, "lastname": "Manga Bell"},
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "person_HAS_mission",
                    "rel_target_node": {
                        "labels": ["mission"],
                        "props": {"name": "resistance leader"},
                    },
                },
                {
                    "rel_props": {},
                    "rel_type": "person_HAS_affiliation",
                    "rel_target_node": {
                        "labels": ["affiliation"],
                        "props": {"name": "Duálá"},
                    },
                },
            ],
        },
        {
            "labels": ["mission"],
            "props": {"name": "resistance leader"},
            "outgoing_rels": [],
        },
    ]
    assert_result(result, expected_result_nodes)


if __name__ == "__main__" or os.getenv("DICT2GRAPH_RUN_ALL_TESTS", None) == "true":
    test_readme_start_example()
    test_readme_start_example_transformed()
    test_basics_start_example()
    test_basics_why_merge_example()
    test_basics_merge_example()
