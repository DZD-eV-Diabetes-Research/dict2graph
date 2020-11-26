import os
import sys
import unittest
from py2neo import Graph

if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(
        os.path.realpath(os.path.join(
            os.getcwd(), os.path.expanduser(__file__)))
    )
    MODULE_ROOT_DIR = os.path.join(SCRIPT_DIR, "..")
    sys.path.insert(0, os.path.normpath(MODULE_ROOT_DIR))
from dict2graph import Dict2graph
NEO4J_CONF = os.getenv("NEO4J", {})
g = Graph(**NEO4J_CONF)


class TestConfigParameters(unittest.TestCase):
    def test_config_list_deconstruction_limit_nodes(self):
        json = {
            "Members": [
                {
                    "Person": {
                        "name": "Eva Saxl",
                        "age": "34",
                        "adresse": [{"street": "Backogstreet", "city": "Wankufer"}],
                    }
                },
                {"Person": {"name": "bronko alberts", "age": "34"}},
            ]
        }
        g.run("Match (n) DETACH DELETE n")
        d2g = Dict2graph()
        d2g.config_list_allowlist_collection_hubs = ["None"]
        d2g.config_list_deconstruction_limit_nodes = ["Person"]
        d2g.config_dict_primarykey_attr_by_label = {"Person": "name"}
        d2g.parse(json)
        d2g.merge(g)
        result = g.run("Match(n)-[r] -> (m) Return n, r, m").data()
        expected_result = []
        self.assertListEqual(result, expected_result)

    def test_config_dict_json_attr_to_reltype_instead_of_label(self):
        json = {
            "Person": {"name": "Ben", "daughters": ["Kielyr"], "sons": ["Bodevan"], }
        }
        d2g = Dict2graph()
        d2g.config_dict_json_attr_to_reltype_instead_of_label = {
            "daughters": "Child",
            "sons": "Child",
        }
        d2g.parse(json)
        expected_result = {
            "nodesSets": [
                {
                    "labels": ["Child"],
                    "primary_keys": ["Child"],
                    "nodes": [{"Child": "Kielyr"}, {"Child": "Bodevan"}],
                },
                {
                    "labels": ["Person"],
                    "primary_keys": ["name"],
                    "nodes": [{"name": "Ben"}],
                },
            ],
            "relationshipSets": [
                {
                    "rel_type": "DAUGHTERS",
                    "start_node_labels": frozenset({"Person"}),
                    "end_node_labels": frozenset({"Child"}),
                    "start_node_properties": ["name"],
                    "end_node_properties": ["Child"],
                    "rels": [
                        {
                            "start_node_properties": {"name": "Ben"},
                            "end_node_properties": {"Child": "Kielyr"},
                            "properties": {"position": 0},
                        }
                    ],
                },
                {
                    "rel_type": "SONS",
                    "start_node_labels": frozenset({"Person"}),
                    "end_node_labels": frozenset({"Child"}),
                    "start_node_properties": ["name"],
                    "end_node_properties": ["Child"],
                    "rels": [
                        {
                            "start_node_properties": {"name": "Ben"},
                            "end_node_properties": {"Child": "Bodevan"},
                            "properties": {"position": 0},
                        }
                    ],
                },
            ],
        }
        self.assertDictEqual(d2g.to_dict(), expected_result)

        def test_config_dict_node_prop_to_rel_prop(self):
            json = {
                "Person": {
                    "name": "Ben",
                    "child": [
                        {"type": "Son", "name": "Kielyr"},
                        {"type": "Daughter", "name": "Bodevan"},
                    ],
                }
            }

            d2g = Dict2graph()
            d2g.config_list_allowlist_collection_hubs = ["None"]
            d2g.config_dict_node_prop_to_rel_prop = {
                "PERSON_HAS_CHILD": {"to": ["type"]}
            }
            d2g.config_dict_primarykey_attr_by_label = {"child": "name"}
            d2g.parse(json)

            expected_result = {
                "nodesSets": [
                    {
                        "labels": ["child"],
                        "primary_keys": ["name"],
                        "nodes": [{"name": "Kielyr"}, {"name": "Bodevan"}],
                    },
                    {
                        "labels": ["Person"],
                        "primary_keys": ["name"],
                        "nodes": [{"name": "Ben"}],
                    },
                ],
                "relationshipSets": [
                    {
                        "rel_type": "PERSON_HAS_CHILD",
                        "start_node_labels": frozenset({"Person"}),
                        "end_node_labels": frozenset({"child"}),
                        "start_node_properties": ["name"],
                        "end_node_properties": ["name"],
                        "rels": [
                            {
                                "start_node_properties": {"name": "Ben"},
                                "end_node_properties": {"name": "Kielyr"},
                                "properties": {"position": 0, "type": "Son"},
                            },
                            {
                                "start_node_properties": {"name": "Ben"},
                                "end_node_properties": {"name": "Bodevan"},
                                "properties": {"position": 1, "type": "Daughter"},
                            },
                        ],
                    }
                ],
            }
            self.assertDictEqual(d2g.to_dict(), expected_result)

        def test_(self):
            json = {
                "Philosophers": {
                    "Person": [
                        {
                            "id": 1,
                            "name": "Hypatia",
                            "unwanted_data": {"stuff": "we", "dont": "want"},
                        },
                        {"id": 2, "name": "Other"},
                    ]
                }
            }
            d2g = Dict2graph()
            d2g.config_list_throw_away_from_nodes = ["unwanted_data"]
            d2g.load_json(json)

            expected_result = {
                "nodesSets": [
                    {
                        "labels": ["Person"],
                        "primary_keys": ["id", "name"],
                        "nodes": [
                            {"id": 1, "name": "Hypatia"},
                            {"id": 2, "name": "Other"},
                        ],
                    },
                    {"labels": ["Philosophers"],
                        "primary_keys": [], "nodes": [{}]},
                ],
                "relationshipSets": [
                    {
                        "rel_type": "PHILOSOPHERS_HAS_PERSON",
                        "start_node_labels": frozenset({"Philosophers"}),
                        "end_node_labels": frozenset({"Person"}),
                        "start_node_properties": [],
                        "end_node_properties": ["id", "name"],
                        "rels": [
                            {
                                "start_node_properties": {},
                                "end_node_properties": {"id": 1, "name": "Hypatia"},
                                "properties": {"position": 0},
                            },
                            {
                                "start_node_properties": {},
                                "end_node_properties": {"id": 2, "name": "Other"},
                                "properties": {"position": 1},
                            },
                        ],
                    }
                ],
            }
            self.assertDictEqual(d2g.to_dict(), expected_result)


if __name__ == "__main__":
    unittest.main()
