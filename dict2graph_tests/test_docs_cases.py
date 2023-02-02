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


def test_readme_tiny_example():
    wipe_all_neo4j_data(DRIVER)

    # lets create a small random  dict
    dic = {
        "Action": {
            "id": 1,
            "target": "El Oued",
            "Entities": [{"id": "Isabelle Eberhardt"}, {"id": "Slimène Ehnni"}],
        }
    }
    # create a dict2graph instance, parse our dict and load it into our neo4j instance.
    Dict2graph().parse(dic).create(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    expected_result_nodes: dict = [
        {
            "labels": ["Entities", "ListHub"],
            "props": {"id": "e9c915649e338a805eda93f4cff31d31"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 1},
                    "rel_type": "Entities_LIST_HAS_Entities",
                    "rel_target_node": {
                        "labels": ["Entities", "ListItem"],
                        "props": {"id": "Slimène Ehnni"},
                    },
                },
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "Entities_LIST_HAS_Entities",
                    "rel_target_node": {
                        "labels": ["Entities", "ListItem"],
                        "props": {"id": "Isabelle Eberhardt"},
                    },
                },
            ],
        },
        {
            "labels": ["Entities", "ListItem"],
            "props": {"id": "Isabelle Eberhardt"},
            "outgoing_rels": [],
        },
        {
            "labels": ["Entities", "ListItem"],
            "props": {"id": "Slimène Ehnni"},
            "outgoing_rels": [],
        },
        {
            "labels": ["Action"],
            "props": {"id": 1, "target": "El Oued"},
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "Action_HAS_Entities",
                    "rel_target_node": {
                        "labels": ["Entities", "ListHub"],
                        "props": {"id": "e9c915649e338a805eda93f4cff31d31"},
                    },
                }
            ],
        },
    ]
    assert_result(result, expected_result_nodes)


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
            Transformer.match_nodes().do(NodeTrans.CapitalizeLabels()),
            Transformer.match_rels().do(RelTrans.UppercaseRelationType()),
            Transformer.match_nodes().do(NodeTrans.PopListHubNodes()),
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


def test_transformer_docs_RemoveLabel():
    wipe_all_neo4j_data(DRIVER)
    dic = {"person": [{"name": "Camina Drummer"}, {"name": "James Holden"}]}
    d2g = Dict2graph()
    d2g.add_node_transformation(
        Transformer.match_nodes("person").do(NodeTrans.RemoveLabel("ListItem"))
    )
    d2g.parse(dic)
    d2g.create(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    expected_result_nodes: dict = [
        {
            "labels": ["person", "ListHub"],
            "props": {"id": "b848c3f039e28d0c9bc28202b3c079f2"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "person_LIST_HAS_person",
                    "rel_target_node": {
                        "labels": ["person"],
                        "props": {"name": "Camina Drummer"},
                    },
                },
                {
                    "rel_props": {"_list_item_index": 1},
                    "rel_type": "person_LIST_HAS_person",
                    "rel_target_node": {
                        "labels": ["person"],
                        "props": {"name": "James Holden"},
                    },
                },
            ],
        },
        {
            "labels": ["person"],
            "props": {"name": "Camina Drummer"},
            "outgoing_rels": [],
        },
        {"labels": ["person"], "props": {"name": "James Holden"}, "outgoing_rels": []},
    ]

    assert_result(result, expected_result_nodes)


def test_transformer_docs_PopListHubNodes():
    wipe_all_neo4j_data(DRIVER)
    data = {
        "bookshelf": {
            "books": [
                {
                    "title": "Fine-structure constant - God set our instance a fine environment variable",
                    "condition": "good",
                },
                {
                    "title": "Goodhart's law - Better benchmark nothing, stupid!",
                    "condition": "bad",
                },
            ]
        }
    }
    d2g = Dict2graph()
    d2g.add_node_transformation(
        Transformer.match_nodes().do(NodeTrans.PopListHubNodes())
    )
    d2g.parse(data)
    d2g.create(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    expected_result_nodes: dict = [
        {
            "labels": ["books", "ListItem"],
            "props": {
                "condition": "good",
                "title": "Fine-structure constant - God set our instance a fine environment variable",
            },
            "outgoing_rels": [],
        },
        {
            "labels": ["books", "ListItem"],
            "props": {
                "condition": "bad",
                "title": "Goodhart's law - Better benchmark nothing, stupid!",
            },
            "outgoing_rels": [],
        },
        {
            "labels": ["bookshelf"],
            "props": {"id": "1aa507ea0b53abae8f1f87c699de705c"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 1},
                    "rel_type": "bookshelf_HAS_books",
                    "rel_target_node": {
                        "labels": ["books", "ListItem"],
                        "props": {
                            "condition": "bad",
                            "title": "Goodhart's law - Better benchmark nothing, stupid!",
                        },
                    },
                },
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "bookshelf_HAS_books",
                    "rel_target_node": {
                        "labels": ["books", "ListItem"],
                        "props": {
                            "condition": "good",
                            "title": "Fine-structure constant - God set our instance a fine environment variable",
                        },
                    },
                },
            ],
        },
    ]
    assert_result(result, expected_result_nodes)


def test_matching_tutorial():
    wipe_all_neo4j_data(DRIVER)
    data = {
        "bookshelf": {
            "books": [
                {
                    "title": "Fine-structure constant - God set our instance a fine environment variable",
                    "condition": "good",
                }
            ]
        }
    }

    book_matcher = Transformer.match_nodes("books")
    d2g = Dict2graph()
    d2g.add_node_transformation(book_matcher.do(NodeTrans.PopListHubNodes()))
    d2g.parse(data)
    d2g.create(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    expected_result_nodes: dict = [
        {
            "labels": ["books", "ListItem"],
            "props": {
                "condition": "good",
                "title": "Fine-structure constant - God set our instance a fine environment variable",
            },
            "outgoing_rels": [],
        },
        {
            "labels": ["bookshelf"],
            "props": {"id": "293fb136da090a860e65980b492a417f"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "bookshelf_HAS_books",
                    "rel_target_node": {
                        "labels": ["books", "ListItem"],
                        "props": {
                            "condition": "good",
                            "title": "Fine-structure constant - God set our instance a fine environment variable",
                        },
                    },
                }
            ],
        },
    ]
    assert_result(result, expected_result_nodes)


def test_matching_tutorial_02():
    wipe_all_neo4j_data(DRIVER)
    data = {
        "bookshelf": {
            "Genre": "Explaining the world",
            "books": [
                {
                    "title": "Fine-structure constant - God set our instance a fine environment variable",
                },
                {
                    "title": "Goodhart's law - Better benchmark nothing, stupid!",
                },
            ],
        }
    }

    d2g = Dict2graph()
    d2g.parse(data)
    d2g.create(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    expected_result_nodes: dict = [
        {
            "labels": ["books", "ListItem"],
            "props": {"title": "Goodhart's law - Better benchmark nothing, stupid!"},
            "outgoing_rels": [],
        },
        {
            "labels": ["bookshelf"],
            "props": {"Genre": "Explaining the world"},
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "bookshelf_HAS_books",
                    "rel_target_node": {
                        "labels": ["books", "ListHub"],
                        "props": {"id": "4e39bbf1e5507d360b19a9fedfde26a4"},
                    },
                }
            ],
        },
        {
            "labels": ["books", "ListHub"],
            "props": {"id": "4e39bbf1e5507d360b19a9fedfde26a4"},
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
                },
                {
                    "rel_props": {"_list_item_index": 1},
                    "rel_type": "books_LIST_HAS_books",
                    "rel_target_node": {
                        "labels": ["books", "ListItem"],
                        "props": {
                            "title": "Goodhart's law - Better benchmark nothing, stupid!"
                        },
                    },
                },
            ],
        },
        {
            "labels": ["books", "ListItem"],
            "props": {
                "title": "Fine-structure constant - God set our instance a fine environment variable"
            },
            "outgoing_rels": [],
        },
    ]
    assert_result(result, expected_result_nodes)


def test_transforming_tut_01():
    wipe_all_neo4j_data(DRIVER)

    data = {
        "bookshelf": {
            "Genre": "Explaining the world",
            "books": [
                {
                    "title": "Fine-structure constant - God set our instance a fine environment variable",
                },
                {
                    "title": "Goodhart's law - Better benchmark nothing, stupid!",
                },
            ],
        }
    }
    # we just learned how to "match". lets apply it:
    bookshelf_matcher = Transformer.match_nodes("bookshelf")
    add_prop_transformator = NodeTrans.AddProperty({"material": "wood"})

    # the next thing we should do is to attach the transformator to our dict2graph instance
    match_and_transform = bookshelf_matcher.do(add_prop_transformator)

    # to be able to enjoy our work lets push the data to neo4j
    # From here this works the same way as we allready learned in the basic tutorial
    d2g = Dict2graph()
    d2g.add_transformation(match_and_transform)

    # parse our dict...
    d2g.parse(data)

    # ...and push it to the database

    d2g.create(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    expected_result_nodes: dict = [
        {
            "labels": ["books", "ListHub"],
            "props": {"id": "4e39bbf1e5507d360b19a9fedfde26a4"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 1},
                    "rel_type": "books_LIST_HAS_books",
                    "rel_target_node": {
                        "labels": ["books", "ListItem"],
                        "props": {
                            "title": "Goodhart's law - Better benchmark nothing, stupid!"
                        },
                    },
                },
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "books_LIST_HAS_books",
                    "rel_target_node": {
                        "labels": ["books", "ListItem"],
                        "props": {
                            "title": "Fine-structure constant - God set our instance a fine environment variable"
                        },
                    },
                },
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
            "labels": ["books", "ListItem"],
            "props": {"title": "Goodhart's law - Better benchmark nothing, stupid!"},
            "outgoing_rels": [],
        },
        {
            "labels": ["bookshelf"],
            "props": {"material": "wood", "Genre": "Explaining the world"},
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "bookshelf_HAS_books",
                    "rel_target_node": {
                        "labels": ["books", "ListHub"],
                        "props": {"id": "4e39bbf1e5507d360b19a9fedfde26a4"},
                    },
                }
            ],
        },
    ]
    assert_result(result, expected_result_nodes)


def test_CreateNewMergePropertyFromHash_tut_01():
    wipe_all_neo4j_data(DRIVER)

    dic = [
        {"person": {"fname": "Joe ", "lname": "Miller", "children": []}},
        {"person": {"fname": "Joe ", "lname": "Miller", "children": ["Tom", "Jane"]}},
    ]
    d2g = Dict2graph()
    d2g.add_node_transformation(
        Transformer.match_nodes("person").do(
            NodeTrans.CreateNewMergePropertyFromHash(hash_includes_children_data=True)
        )
    )
    d2g.parse(dic)
    d2g.merge(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    expected_result_nodes: dict = [
        {
            "labels": ["Dict2GraphRoot", "ListHub"],
            "props": {"id": "c40073e2de4c5a6e7f70ab6f5a683e46"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 1},
                    "rel_type": "Dict2GraphRoot_LIST_HAS_person",
                    "rel_target_node": {
                        "labels": ["person", "ListItem"],
                        "props": {
                            "fname": "Joe ",
                            "lname": "Miller",
                            "_id": "e3a6c806eef68776c81ca9a00739dd9c",
                        },
                    },
                },
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "Dict2GraphRoot_LIST_HAS_person",
                    "rel_target_node": {
                        "labels": ["person", "ListItem"],
                        "props": {
                            "fname": "Joe ",
                            "lname": "Miller",
                            "_id": "c676ed1d3bec334e54b7133560eb6275",
                        },
                    },
                },
            ],
        },
        {
            "labels": ["children", "ListHub"],
            "props": {"id": "d751713988987e9331980363e24189ce"},
            "outgoing_rels": [],
        },
        {
            "labels": ["children", "ListHub"],
            "props": {"id": "911568efcb8fdfac62558e2d9a9f8c3c"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 1},
                    "rel_type": "children_LIST_HAS_children",
                    "rel_target_node": {
                        "labels": ["children", "ListItem"],
                        "props": {"_list_item_data": "Jane"},
                    },
                },
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "children_LIST_HAS_children",
                    "rel_target_node": {
                        "labels": ["children", "ListItem"],
                        "props": {"_list_item_data": "Tom"},
                    },
                },
            ],
        },
        {
            "labels": ["person", "ListItem"],
            "props": {
                "fname": "Joe ",
                "lname": "Miller",
                "_id": "c676ed1d3bec334e54b7133560eb6275",
            },
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "person_HAS_children",
                    "rel_target_node": {
                        "labels": ["children", "ListHub"],
                        "props": {"id": "d751713988987e9331980363e24189ce"},
                    },
                }
            ],
        },
        {
            "labels": ["person", "ListItem"],
            "props": {
                "fname": "Joe ",
                "lname": "Miller",
                "_id": "e3a6c806eef68776c81ca9a00739dd9c",
            },
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "person_HAS_children",
                    "rel_target_node": {
                        "labels": ["children", "ListHub"],
                        "props": {"id": "911568efcb8fdfac62558e2d9a9f8c3c"},
                    },
                }
            ],
        },
        {
            "labels": ["children", "ListItem"],
            "props": {"_list_item_data": "Tom"},
            "outgoing_rels": [],
        },
        {
            "labels": ["children", "ListItem"],
            "props": {"_list_item_data": "Jane"},
            "outgoing_rels": [],
        },
    ]
    assert_result(result, expected_result_nodes)


def test_RemoveEmptyListRootNodes_tut_01():
    wipe_all_neo4j_data(DRIVER)

    dic = {
        "person": {"fname": "Marco ", "lname": "Inaros", "children": ["Filip Inaros"]}
    }

    dic2 = {"person": {"fname": "Joe ", "lname": "Miller", "children": []}}

    d2g = Dict2graph()
    d2g.add_node_transformation(
        Transformer.match_nodes("children").do(NodeTrans.RemoveEmptyListRootNodes())
    )
    d2g.parse(dic)
    d2g.parse(dic2)

    d2g.create(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    expected_result_nodes: dict = [
        {
            "labels": ["children", "ListHub"],
            "props": {"id": "f51cced5b17d86b8c7d175446dc9210d"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "children_LIST_HAS_children",
                    "rel_target_node": {
                        "labels": ["children", "ListItem"],
                        "props": {"_list_item_data": "Filip Inaros"},
                    },
                }
            ],
        },
        {
            "labels": ["children", "ListItem"],
            "props": {"_list_item_data": "Filip Inaros"},
            "outgoing_rels": [],
        },
        {
            "labels": ["person"],
            "props": {"fname": "Marco ", "lname": "Inaros"},
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "person_HAS_children",
                    "rel_target_node": {
                        "labels": ["children", "ListHub"],
                        "props": {"id": "f51cced5b17d86b8c7d175446dc9210d"},
                    },
                }
            ],
        },
        {
            "labels": ["person"],
            "props": {"fname": "Joe ", "lname": "Miller"},
            "outgoing_rels": [],
        },
    ]
    assert_result(result, expected_result_nodes)


def test_OutsourcePropertiesToNewNode_tut_01():
    wipe_all_neo4j_data(DRIVER)

    dic = {"person": {"fname": "Marco ", "lname": "Inaros", "child": "Filip Inaros"}}

    d2g = Dict2graph()
    d2g.add_node_transformation(
        Transformer.match_nodes("person").do(
            NodeTrans.OutsourcePropertiesToNewNode(
                property_keys=["child"],
                new_node_labels=["person"],
                relation_type="person_has_child",
            )
        )
    )
    d2g.parse(dic)
    d2g.create(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)

    expected_result_nodes: dict = [
        {
            "labels": ["person"],
            "props": {"fname": "Marco ", "lname": "Inaros"},
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "person_has_child",
                    "rel_target_node": {
                        "labels": ["person"],
                        "props": {"child": "Filip Inaros"},
                    },
                }
            ],
        },
        {"labels": ["person"], "props": {"child": "Filip Inaros"}, "outgoing_rels": []},
    ]
    assert_result(result, expected_result_nodes)


def test_OutsourcePropertiesToRelationship_tut_01():
    wipe_all_neo4j_data(DRIVER)

    dic = {
        "person": {
            "fname": "Marco ",
            "lname": "Inaros",
            "child_rel": "biological",
            "child": {"person": {"fname": "Filip", "lname": "Inaros"}},
        }
    }

    d2g = Dict2graph()
    d2g.add_node_transformation(
        Transformer.match_nodes("person").do(
            NodeTrans.OutsourcePropertiesToRelationship(
                property_keys=["child_rel"],
                relation_type="child",
            )
        )
    )
    d2g.parse(dic)
    d2g.create(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)

    expected_result_nodes: dict = [
        {
            "labels": ["person"],
            "props": {"fname": "Filip", "lname": "Inaros"},
            "outgoing_rels": [],
        },
        {
            "labels": ["person"],
            "props": {"fname": "Marco ", "lname": "Inaros"},
            "outgoing_rels": [
                {
                    "rel_props": {"child_rel": "biological"},
                    "rel_type": "child",
                    "rel_target_node": {
                        "labels": ["person"],
                        "props": {"fname": "Filip", "lname": "Inaros"},
                    },
                }
            ],
        },
    ]
    assert_result(result, expected_result_nodes)


if __name__ == "__main__" or os.getenv("DICT2GRAPH_RUN_ALL_TESTS", False) == "true":
    test_readme_tiny_example()
    test_readme_start_example()
    test_readme_start_example_transformed()
    test_basics_start_example()
    test_basics_why_merge_example()
    test_basics_merge_example()
    test_transformer_docs_RemoveLabel()
    test_transformer_docs_PopListHubNodes()
    test_matching_tutorial()
    test_matching_tutorial_02()
    test_transforming_tut_01()
    test_CreateNewMergePropertyFromHash_tut_01()
    test_RemoveEmptyListRootNodes_tut_01()
    test_OutsourcePropertiesToNewNode_tut_01()
    test_OutsourcePropertiesToRelationship_tut_01()
