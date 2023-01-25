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


def test_merge_two_dicts_and_remove_list_hubs():
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
    d2g.add_node_transformation(
        Transformer.match_node().do(NodeTrans.PopListHubNodes())
    )
    d2g.parse(dic1)
    d2g.parse(dic2)
    d2g.merge(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_result_nodes: dict = [
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
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "Authors_HAS_affiliation",
                    "rel_target_node": {
                        "labels": ["affiliation", "ListItem"],
                        "props": {"name": "University 1"},
                    },
                },
                {
                    "rel_props": {"_list_item_index": 1},
                    "rel_type": "Authors_HAS_affiliation",
                    "rel_target_node": {
                        "labels": ["affiliation", "ListItem"],
                        "props": {"name": "University 2"},
                    },
                },
            ],
        },
        {
            "labels": ["Article"],
            "props": {"title": "Science Behind The Cyberpunk-Genres Awesomeness"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "Article_HAS_Authors",
                    "rel_target_node": {
                        "labels": ["ListItem", "Authors"],
                        "props": {"firstName": "Mike", "lastName": "Pondsmith"},
                    },
                }
            ],
        },
        {
            "labels": ["Article"],
            "props": {"title": "Transhumanism in Computergames"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "Article_HAS_Authors",
                    "rel_target_node": {
                        "labels": ["ListItem", "Authors"],
                        "props": {"firstName": "Mike", "lastName": "Pondsmith"},
                    },
                }
            ],
        },
    ]
    # print("DIFF:", DeepDiff(expected_result_nodes, result, ignore_order=True))
    assert_result(result, expected_result_nodes)


def test_hubbing_edge():
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
    d2g.add_node_transformation(
        [
            Transformer.match_node().do(NodeTrans.PopListHubNodes()),
            Transformer.match_node().do(NodeTrans.RemoveListItemLabels()),
            Transformer.match_node("Article").do(
                NodeTrans.CreateHubbing(
                    follow_nodes_labels=["Authors", "affiliation"],
                    merge_property_mode="edge",
                    hub_labels=["Contribution"],
                )
            ),
        ]
    )
    d2g.parse(dic1)
    d2g.parse(dic2)
    d2g.merge(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    # print(json.dumps(result, indent=2))

    expected_result_nodes: dict = [
        {
            "labels": ["affiliation"],
            "props": {"name": "University 1"},
            "outgoing_rels": [],
        },
        {
            "labels": ["affiliation"],
            "props": {"name": "University 2"},
            "outgoing_rels": [],
        },
        {
            "labels": ["Authors"],
            "props": {"firstName": "Mike", "lastName": "Pondsmith"},
            "outgoing_rels": [],
        },
        {
            "labels": ["Article"],
            "props": {"title": "Science Behind The Cyberpunk-Genres Awesomeness"},
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "Article_HAS_Contribution",
                    "rel_target_node": {
                        "labels": ["Contribution"],
                        "props": {"id": "7fcd494bd8e15df89a8c970efcb1beeb"},
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
                    "rel_type": "Article_HAS_Contribution",
                    "rel_target_node": {
                        "labels": ["Contribution"],
                        "props": {"id": "d6d0f91b22b1aa33ccb4584344c07508"},
                    },
                }
            ],
        },
        {
            "labels": ["Contribution"],
            "props": {"id": "7fcd494bd8e15df89a8c970efcb1beeb"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "Contribution_HAS_Authors",
                    "rel_target_node": {
                        "labels": ["Authors"],
                        "props": {"firstName": "Mike", "lastName": "Pondsmith"},
                    },
                },
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "Contribution_HAS_affiliation",
                    "rel_target_node": {
                        "labels": ["affiliation"],
                        "props": {"name": "University 1"},
                    },
                },
            ],
        },
        {
            "labels": ["Contribution"],
            "props": {"id": "d6d0f91b22b1aa33ccb4584344c07508"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "Contribution_HAS_Authors",
                    "rel_target_node": {
                        "labels": ["Authors"],
                        "props": {"firstName": "Mike", "lastName": "Pondsmith"},
                    },
                },
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "Contribution_HAS_affiliation",
                    "rel_target_node": {
                        "labels": ["affiliation"],
                        "props": {"name": "University 1"},
                    },
                },
                {
                    "rel_props": {"_list_item_index": 1},
                    "rel_type": "Contribution_HAS_affiliation",
                    "rel_target_node": {
                        "labels": ["affiliation"],
                        "props": {"name": "University 2"},
                    },
                },
            ],
        },
    ]
    # print("DIFF:", DeepDiff(expected_result_nodes, result, ignore_order=True))
    assert_result(result, expected_result_nodes)


def test_pubmed_article_base_test():
    wipe_all_neo4j_data(DRIVER)
    data = {
        "MedlineCitation": {
            "DateRevised": {"Year": "2011", "Month": "03", "Day": "29"},
            "Article": {
                "PublicationTypeList": {
                    "PublicationType": [{"UI": "D016428", "text": "Journal Article"}]
                }
            },
        }
    }
    d2g = Dict2graph()
    d2g.parse(data, "PubMedArticle")
    d2g.create(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    expected_result_nodes: dict = [
        {
            "labels": ["DateRevised"],
            "props": {"Month": "03", "Year": "2011", "Day": "29"},
            "outgoing_rels": [],
        },
        {
            "labels": ["ListHub", "PublicationType"],
            "props": {"id": "7aa3fd5ff651c125c73af3f384babf5d"},
            "outgoing_rels": [
                {
                    "rel_props": {"_list_item_index": 0},
                    "rel_type": "PublicationType_LIST_HAS_PublicationType",
                    "rel_target_node": {
                        "labels": ["ListItem", "PublicationType"],
                        "props": {"UI": "D016428", "text": "Journal Article"},
                    },
                }
            ],
        },
        {
            "labels": ["ListItem", "PublicationType"],
            "props": {"UI": "D016428", "text": "Journal Article"},
            "outgoing_rels": [],
        },
        {
            "labels": ["PublicationTypeList"],
            "props": {"id": "bca5a10f0c4403c7be9acd27725f7338"},
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "PublicationTypeList_HAS_PublicationType",
                    "rel_target_node": {
                        "labels": ["ListHub", "PublicationType"],
                        "props": {"id": "7aa3fd5ff651c125c73af3f384babf5d"},
                    },
                }
            ],
        },
        {
            "labels": ["MedlineCitation"],
            "props": {"id": "4f4a0c4f33aec00c43684378af5e9e76"},
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "Article",
                    "rel_target_node": {
                        "labels": ["PublicationTypeList"],
                        "props": {"id": "bca5a10f0c4403c7be9acd27725f7338"},
                    },
                },
                {
                    "rel_props": {},
                    "rel_type": "MedlineCitation_HAS_DateRevised",
                    "rel_target_node": {
                        "labels": ["DateRevised"],
                        "props": {"Month": "03", "Year": "2011", "Day": "29"},
                    },
                },
            ],
        },
        {
            "labels": ["PubMedArticle"],
            "props": {"id": "cec410694c4c446d67ac991f40bf9762"},
            "outgoing_rels": [
                {
                    "rel_props": {},
                    "rel_type": "PubMedArticle_HAS_MedlineCitation",
                    "rel_target_node": {
                        "labels": ["MedlineCitation"],
                        "props": {"id": "4f4a0c4f33aec00c43684378af5e9e76"},
                    },
                }
            ],
        },
    ]
    # print("DIFF:", DeepDiff(expected_result_nodes, result, ignore_order=True))
    assert_result(result, expected_result_nodes)


def test_pubmed_article():
    wipe_all_neo4j_data(DRIVER)
    data = {
        "MedlineCitation": {
            "Status": "PubMed-not-MEDLINE",
            "Owner": "NLM",
            "PMID": {"Version": "1", "text": "20764441"},
            "DateCompleted": {"Year": "2011", "Month": "03", "Day": "29"},
            "DateRevised": {"Year": "2011", "Month": "03", "Day": "29"},
            "Article": {
                "PubModel": "Print",
                "Journal": {
                    "ISSN": {"IssnType": "Print", "text": "0007-1447"},
                    "JournalIssue": {
                        "CitedMedium": "Print",
                        "Volume": "1",
                        "Issue": "2522",
                        "PubDate": {"Year": "1909", "Month": "May", "Day": "01"},
                    },
                    "Title": "British medical journal",
                    "ISOAbbreviation": "Br Med J",
                },
                "ArticleTitle": "BILATERAL NEPHRO-LITHOTOMY, IN WHICH THE KIDNEY WAS KEPT OUTSIDE THE WOUND FOR SEVEN DAYS BEFORE RETURNING IT TO THE LOIN.",
                "Pagination": {"MedlinePgn": "1059-60"},
                "AuthorList": {
                    "CompleteYN": "Y",
                    "Author": [
                        {
                            "ValidYN": "Y",
                            "LastName": "Clay",
                            "ForeName": "J",
                            "Initials": "J",
                        }
                    ],
                },
                "Language": ["eng"],
                "PublicationTypeList": {
                    "PublicationType": [{"UI": "D016428", "text": "Journal Article"}]
                },
            },
            "MeshHeadingList": {
                "MeshHeading": [
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
                    {
                        "DescriptorName": {
                            "UI": "D013507",
                            "MajorTopicYN": "Y",
                            "text": "Endocrine Surgical Procedures",
                        }
                    },
                    {
                        "DescriptorName": {
                            "UI": "D006801",
                            "MajorTopicYN": "N",
                            "text": "Humans",
                        }
                    },
                    {
                        "DescriptorName": {
                            "UI": "D008216",
                            "MajorTopicYN": "Y",
                            "text": "Lymphocytic Choriomeningitis",
                        }
                    },
                    {
                        "DescriptorName": {
                            "UI": "D008581",
                            "MajorTopicYN": "Y",
                            "text": "Meningitis",
                        }
                    },
                ]
            },
            "MedlineJournalInfo": {
                "Country": "England",
                "MedlineTA": "Br Med J",
                "NlmUniqueID": "0372673",
                "ISSNLinking": "0007-1447",
            },
        },
        "PubmedData": {
            "History": {
                "PubMedPubDate": [
                    {
                        "PubStatus": "entrez",
                        "Year": "2010",
                        "Month": "8",
                        "Day": "27",
                        "Hour": "6",
                        "Minute": "0",
                    },
                    {
                        "PubStatus": "pubmed",
                        "Year": "1909",
                        "Month": "5",
                        "Day": "1",
                        "Hour": "0",
                        "Minute": "0",
                    },
                    {
                        "PubStatus": "medline",
                        "Year": "1909",
                        "Month": "5",
                        "Day": "1",
                        "Hour": "0",
                        "Minute": "1",
                    },
                ]
            },
            "PublicationStatus": "ppublish",
            "ArticleIdList": {
                "ArticleId": [
                    {"IdType": "pubmed", "text": "20764441"},
                    {"IdType": "pmc", "text": "PMC2318724"},
                ]
            },
        },
    }
    d2g = Dict2graph()

    d2g.add_node_transformation(
        [
            Transformer.match_node().do(NodeTrans.PopListHubNodes()),
            Transformer.match_node().do(NodeTrans.RemoveListItemLabels()),
            Transformer.match_node("Article").do(
                NodeTrans.CreateHubbing(
                    follow_nodes_labels=["Authors", "affiliation"],
                    merge_property_mode="edge",
                    hub_labels=["Contribution"],
                )
            ),
        ]
    )

    d2g.parse(data)
    d2g.merge(DRIVER)
    result = get_all_neo4j_nodes_with_rels(DRIVER)
    expected_result_nodes: dict = []
    # print("DIFF:", DeepDiff(expected_result_nodes, result, ignore_order=True))
    assert_result(result, expected_result_nodes)


# test_merge_two_dicts_and_remove_list_hubs()
test_hubbing_edge()
test_pubmed_article_base_test()
test_pubmed_article()
