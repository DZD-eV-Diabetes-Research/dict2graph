import os
import sys

from py2neo import Graph


if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(
        os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
    )

    sys.path.append(os.path.normpath(SCRIPT_DIR))

from dict2graph import Dict2graph


person = {
    "firstName": "John",
    "lastName": "Smith",
    "isAlive": True,
    "age": 27,
    "address": {
        "streetAddress": "21 2nd Street",
        "city": "New York",
        "state": "NY",
        "postalCode": "10021-3100",
    },
    "phoneNumbers": [
        {"type": "home", "number": "212 555-1234"},
        {"type": "office", "number": "646 555-4567"},
        {"type": "mobile", "number": "123 456-7890"},
    ],
    "children": [],
    "spouse": "Rita Smith",
}


person2 = {
    "firstName": "Rita",
    "lastName": "Smith",
    "isAlive": True,
    "age": 35,
    "address": {
        "streetAddress": "21 2nd Street",
        "city": "New York",
        "state": "NY",
        "postalCode": "10021-3100",
    },
    "phoneNumbers": [
        {"type": "home", "number": "212 555-1234"},
        {"type": "office", "number": "2345 456"},
        {"type": "mobile", "number": "34 456 56565"},
    ],
    "NestedList": [
        [{"ListItem": "1.1"}, {"ListItem": "1.2"}, {"ListItem": "1.3"}],
        [{"ListItem": "2.1"}, {"ListItem": "2.2"}],
        [],
    ],
    "children": ["Fria", "Seli"],
    "spouse": "John Smith",
}

d2g = Dict2graph()
d2g.config_list_skip_collection_hubs = ["PhonenumberCollection", "NestedlistCollection"]

d2g.config_dict_primarykey_attr_by_label = {
    "Address": "streetAddress",
    "Phonenumbers": "number",
    "Nestedlist": "ListItem",
}
d2g.config_dict_primarykey_generated_hashed_attrs_by_label = {
    "Person": "AllAttributes",
    "Address": ["streetAddress", "postalCode"],
}

d2g.config_dict_json_attr_to_reltype_instead_of_label = {
    "daughters": "Child",
    "sons": "Child",
}

d2g.config_dict_property_name_override = {
    "Child": {"daughters": "child", "sons": "child"}
}


d2g.config_dict_label_override = {"phoneNumbers": "phoneNumber"}
d2g.config_dict_property_name_override = {"children": {"children": "child"}}
d2g.load_json(person, "Person")
d2g.load_json(person2, "Person")

persons = [
    {
        "firstName": "Maria",
        "lastName": "Longhorn",
        "isAlive": True,
        "age": 45,
        "address": {
            "streetAddress": "56 Street",
            "city": "Los Santos",
            "state": "GTA",
            "postalCode": "68453456",
        },
        "phoneNumbers": [
            {"type": "home", "number": "5645"},
            {"type": "office", "number": "26854121"},
            {"type": "mobile", "number": "9844684"},
        ],
        "NestedList": [
            [{"ListItem": "A.1"}, {"ListItem": "A.2"}, {"ListItem": "A.3"}],
            [{"ListItem": "B.1"}, {"ListItem": "B.2"}],
        ],
        "children": ["Alfred", "Elenora"],
        "spouse": "Frank Longhorn",
    },
    {
        "firstName": "Frank",
        "lastName": "Longhorn",
        "isAlive": True,
        "age": 56,
        "address": {
            "streetAddress": "56 Street",
            "city": "Los Santos",
            "state": "GTA",
            "postalCode": "68453456",
        },
        "phoneNumbers": [
            {"type": "home", "number": "5645"},
            {"type": "office", "number": "26854121"},
            {"type": "mobile", "number": "9844684"},
        ],
        "children": [],
        "spouse": "Maria Longhorn",
    },
]

d2g.load_json(persons, "Person")
g = Graph()
# print(d2g.relationshipSets[frozenset({"Phonenumbers", "CollectionHub"})])
print("Indexes...")
d2g.create_indexes(g)
print("..created")
d2g.config_dict_create_merge_depending_scheme["create"] = [
    ["Phonenumber"],
    "PERSON_HAS_NESTEDLIST",
]
d2g.config_dict_create_merge_depending_scheme["merge"] = []
d2g.create_merge_depending(g, "merge")


person5 = {
    "Human": {
        "firstName": "Alfred",
        "lastName": "Inner",
        "isAlive": False,
        "age": 89,
        "address": {
            "streetAddress": "25 1nd Street",
            "city": "Startdust City",
            "state": "SC",
            "postalCode": "11111",
        },
        "phoneNumbers": [{"type": "home", "number": "212 555-1234"}],
        "daughters": ["Sik"],
        "sons": ["John"],
        "spouse": None,
    }
}

d2g.config_list_skip_collection_hubs.append("ChildCollection")
d2g.config_dict_json_attr_to_reltype_instead_of_label = {
    "daughters": "Child",
    "sons": "Child",
}

d2g.config_dict_property_name_override = {
    "Child": {"daughters": "child", "sons": "child"}
}

d2g.config_dict_reltype_override = {"DAUGHTERS": "DAUGHTER", "SONS": "SON"}

# d2g.config_dict_property_name_override["daughters"] = "child"
# d2g.config_dict_property_name_override["sons"] = "child"
d2g.config_dict_label_override["Human"] = "Person"
d2g.load_json(person5)

person6 = {
    "Person": {
        "firstName": "Ronald",
        "lastName": "FoldingTest",
        "isAlive": False,
        "age": 89,
        "address": {},
        "phoneNumbers": [{"type": "home", "number": "212 555-1234"}],
        "children": {"sons": ["MagicMike"], "daughters": ["AmazingDona"]},
        "spouse": None,
    }
}
d2g.config_dict_interfold_json_attr = {"Person": {"children": None}}

d2g.config_dict_json_attr_to_reltype_instead_of_label.update(
    {"children_daughters": "Child", "children_sons": "Child",}
)
d2g.config_dict_property_name_override.update(
    {"Child": {"children_daughters": "child", "children_sons": "child"}}
)
d2g.config_dict_reltype_override.update(
    {"CHILDREN_SONS": "SON", "CHILDREN_DAUGHTERS": "DAUGHTER"}
)
"""
d2g.config_dict_label_override.update(
    {"children_daughters": "Child", "children_sons": "Child"}
)
d2g.config_dict_property_name_override.update(
    {"Child": {"children_daughters": "child", "children_sons": "child"}}
)
"""
d2g.load_json(person6)


person7 = {
    "Person": {
        "firstName": "Peter",
        "lastName": "ExtraPropsTest",
        "isAlive": False,
        "age": 89,
        "address": {},
        "alt_address": {
            "streetAddress": "25 1nd Street",
            "city": "Startdust City",
            "state": "SC",
            "postalCode": "11111",
        },
        "phoneNumbers": [{"type": "home", "number": "212 555-1234"}],
        "children": {"sons": ["Laurence"], "daughters": ["Sonja"]},
        "spouse": "Maria",
    }
}
d2g.config_dict_label_override.update(
    {"alt_address": {"address": {"type": "alternative"}}}
)
d2g.config_dict_property_to_extra_node = {"Person": "spouse"}

d2g.load_json(person7)
d2g.make_distinct_before_insert = True
d2g.merge(g)
