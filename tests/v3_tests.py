import os, sys
from neo4j import GraphDatabase

if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(
        os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
    )
    MODULE_ROOT_DIR = os.path.join(SCRIPT_DIR, "..")
    sys.path.insert(0, os.path.normpath(MODULE_ROOT_DIR))
from dict2graph import Dict2graph

# init-test
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
json1 = [1, 2, 3, 4, 5]
json2 = {"Article": "dummes json"}
d2g = Dict2graph()
d2g.parse(json, "test")
d2g.create(GraphDatabase.driver("neo4j://localhost"))
