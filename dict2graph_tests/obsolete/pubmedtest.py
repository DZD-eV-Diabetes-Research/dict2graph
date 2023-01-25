import py2neo
import sys
import os
import json
from neo4j import GraphDatabase

if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(
        os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
    )
    MODULE_ROOT_DIR = os.path.join(SCRIPT_DIR, "..")
    sys.path.insert(0, os.path.normpath(MODULE_ROOT_DIR))
from dict2graph import Dict2graph

data = {
    "Author": [
        {
            "ValidYN": "Y",
            "LastName": "Cohrs",
            "ForeName": "Christian M",
            "Initials": "CM",
            "Affiliation": [
                {
                    "Affiliation2": "Paul Langerhans Institute Dresden (PLID) of the Helmholtz Zentrum M\u00fcnchen at the University Clinic Carl Gustav Carus of Technische Universit\u00e4t Dresden, Helmholtz Zentrum M\u00fcnchen, Neuherberg, Germany."
                },
                {
                    "Affiliation2": "Institute of Physiology, Faculty of Medicine, Technische Universit\u00e4t Dresden, Dresden, Germany."
                },
                {
                    "Affiliation2": "German Center for Diabetes Research (DZD), M\u00fcnchen-Neuherberg, Germany."
                },
            ],
        },
        {
            "ValidYN": "Y",
            "LastName": "Cohrs",
            "ForeName": "Franz M",
            "Initials": "CM",
            "Affiliation": [
                {
                    "Affiliation2": "Paul Langerhans Institute Dresden (PLID) of the Helmholtz Zentrum M\u00fcnchen at the University Clinic Carl Gustav Carus of Technische Universit\u00e4t Dresden, Helmholtz Zentrum M\u00fcnchen, Neuherberg, Germany."
                },
                {
                    "Affiliation2": "Institute of Physiology, Faculty of Medicine, Technische Universit\u00e4t Dresden, Dresden, Germany."
                },
            ],
        },
    ]
}


NEO4J_CONF = os.getenv("NEO4J", {})
# g = py2neo.Graph(**NEO4J_CONF)
g = GraphDatabase.driver("neo4j://localhost")
# g.run("match (a) -[r] -> () delete a, r")
# g.run("match (a) delete a")
# data_dict = json.loads(data)
data_dict = data
d2g = Dict2graph()
d2g._debug = True
d2g.config_list_allowlist_list_hubs = ["None"]
d2g.config_dict_hubbing = {
    "PubMedArticle": [
        {
            "hub_member_labels": ["Author", "Affiliation"],
            "hub_label": "Contribution",
            "hub_id_from": "edge",
        },
        {
            "hub_member_labels": ["Investigator", "Affiliation"],
            "hub_label": "Contribution",
            "hub_id_from": "edge",
        },
    ]
}
d2g.parse(data_dict, "PubMedArticle")
d2g.merge(g)
