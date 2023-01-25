import py2neo
import sys
import os
import json

if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(
        os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
    )
    MODULE_ROOT_DIR = os.path.join(SCRIPT_DIR, "..")
    sys.path.insert(0, os.path.normpath(MODULE_ROOT_DIR))
from dict2graph import Dict2graph

NEO4J_CONF = os.getenv("NEO4J", {})
g = py2neo.Graph(**NEO4J_CONF)
g.run("match (a) -[r] -> () delete a, r")
g.run("match (a) delete a")
d2g = Dict2graph()
d2g._debug = True
json = {
    "Article": {
        "title": "Science Behind The Cyberpunks-Genre Awesomeness",
        "Authors": [
            {
                "firstName": "Mike",
                "lastName": "Pondsmith",
                "affiliation": [{"name": "University 1"}],
            },
        ],
    }
}
json2 = {
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
d2g.config_list_allowlist_list_hubs = ["NONE"]
# hubbing config:
d2g.config_dict_hubbing = {
    "Article": {
        "hub_member_labels": ["Authors", "affiliation"],
        "hub_label": "Contribution",
        "hub_id_from": "edge",
    }
}
# d2g.parse(json)
d2g.parse(json2)
d2g.merge(g)
