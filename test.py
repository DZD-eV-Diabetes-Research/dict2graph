import sys
import os
from py2neo import Graph
from DZDjson2GraphIO import Json2graphio
from linetimer import CodeTimer

if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(
        os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
    )
    sys.path.insert(0, os.path.normpath(SCRIPT_DIR))

print(SCRIPT_DIR)
from dict2graph import Dict2graph
from py2neo import Graph

"""
json = {
    "MeshHeadingList": {
        "MeshHeading": [
            {
                "DescriptorName": {
                    "UI": "D013507",
                    "MajorTopicYN": "Y",
                    "text": "Endocrine Surgical Procedures",
                }
            },
            {
                "DescriptorName": {
                    "UI": "D000311",
                    "MajorTopicYN": "N",
                    "text": "Adrenal Glands",
                },
                "QualifierName": [
                    {"UI": "Q000601", "MajorTopicYN": "Y", "text": "surgery"}
                ],
            },
        ]
    }
}
d2g = Dict2graph()
d2g.config_list_allowlist_collection_hubs = [None]
# d2g.config_dict_primarykey_attr_by_label = {"Person": "name"}
# d2g.config_list_throw_away_nodes_with_empty_key_attr = ["Person"]
d2g.config_dict_primarykey_attr_by_label = {
    "DescriptorName": "UI",
    "QualifierName": "UI",
}
d2g.config_dict_primarykey_generated_hashed_attrs_by_label = {
    "MeshHeadingList": "AllContent",
    "MeshHeading": "InnerContent",
}

d2g.config_dict_node_prop_to_rel_prop = {
    "MESHHEADING_HAS_DESCRIPTORNAME": {"to": ["MajorTopicYN"]},
    "MESHHEADING_HAS_QUALIFIERNAME": {"to": ["MajorTopicYN"]},
}
d2g.load_json(json)
d2g.merge(Graph())
print(d2g.to_dict())
print(d2g._stats_per_set)
#  This will only insert one person node `(:Person{"name": "Mahony", "age": 23})` instead of another additional node with only the age `(:Person{"age": 25})` (or actually throwing an py2neo error, because of the missing merge key)
"""


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
d2g.config_dict_node_prop_to_rel_prop = {"child": {"type": "PERSON_HAS_CHILD"}}
d2g.config_dict_primarykey_attr_by_label = {"child": ["name"]}
d2g.load_json(json)
d2g.merge(Graph())
