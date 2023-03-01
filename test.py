data = [
    CreateHubbing.ToBeHubbedNode(
        depth_level=0,
        node={"PMID": "12345", "CompleteYN": "Y"},
        parent_rels=[],
        parent_nodes=[],
        is_end_node=False,
    ),
    CreateHubbing.ToBeHubbedNode(
        depth_level=1,
        node={"LastName": "Clay", "ForeName": "J"},
        parent_rels=[{"_list_item_index": 0}],
        parent_nodes=[
            CreateHubbing.ToBeHubbedNode(
                depth_level=0,
                node={"PMID": "12345", "CompleteYN": "Y"},
                parent_rels=[],
                parent_nodes=[],
                is_end_node=False,
            )
        ],
        is_end_node=False,
    ),
    CreateHubbing.ToBeHubbedNode(
        depth_level=1,
        node={"LastName": "Kalla", "ForeName": "Roger"},
        parent_rels=[{"_list_item_index": 1}],
        parent_nodes=[
            CreateHubbing.ToBeHubbedNode(
                depth_level=0,
                node={"PMID": "12345", "CompleteYN": "Y"},
                parent_rels=[],
                parent_nodes=[],
                is_end_node=False,
            )
        ],
        is_end_node=False,
    ),
    CreateHubbing.ToBeHubbedNode(
        depth_level=2,
        node={"Affiliation": "University Hospital Bern"},
        parent_rels=[{"_list_item_index": 0}],
        parent_nodes=[
            CreateHubbing.ToBeHubbedNode(
                depth_level=1,
                node={"LastName": "Kalla", "ForeName": "Roger"},
                parent_rels=[{"_list_item_index": 1}],
                parent_nodes=[
                    CreateHubbing.ToBeHubbedNode(
                        depth_level=0,
                        node={"PMID": "12345", "CompleteYN": "Y"},
                        parent_rels=[],
                        parent_nodes=[],
                        is_end_node=False,
                    )
                ],
                is_end_node=False,
            )
        ],
        is_end_node=True,
    ),
    CreateHubbing.ToBeHubbedNode(
        depth_level=2,
        node={"Affiliation": "German Center for Vertigo and Balance Disorders"},
        parent_rels=[{"_list_item_index": 1}],
        parent_nodes=[
            CreateHubbing.ToBeHubbedNode(
                depth_level=1,
                node={"LastName": "Kalla", "ForeName": "Roger"},
                parent_rels=[{"_list_item_index": 1}],
                parent_nodes=[
                    CreateHubbing.ToBeHubbedNode(
                        depth_level=0,
                        node={"PMID": "12345", "CompleteYN": "Y"},
                        parent_rels=[],
                        parent_nodes=[],
                        is_end_node=False,
                    )
                ],
                is_end_node=False,
            )
        ],
        is_end_node=True,
    ),
    CreateHubbing.ToBeHubbedNode(
        depth_level=1,
        node={"LastName": "Strupp", "ForeName": "Michael"},
        parent_rels=[{"_list_item_index": 2}],
        parent_nodes=[
            CreateHubbing.ToBeHubbedNode(
                depth_level=0,
                node={"PMID": "12345", "CompleteYN": "Y"},
                parent_rels=[],
                parent_nodes=[],
                is_end_node=False,
            )
        ],
        is_end_node=False,
    ),
    CreateHubbing.ToBeHubbedNode(
        depth_level=2,
        node={"Affiliation": "German Center for Vertigo and Balance Disorders"},
        parent_rels=[{"_list_item_index": 0}],
        parent_nodes=[
            CreateHubbing.ToBeHubbedNode(
                depth_level=1,
                node={"LastName": "Strupp", "ForeName": "Michael"},
                parent_rels=[{"_list_item_index": 2}],
                parent_nodes=[
                    CreateHubbing.ToBeHubbedNode(
                        depth_level=0,
                        node={"PMID": "12345", "CompleteYN": "Y"},
                        parent_rels=[],
                        parent_nodes=[],
                        is_end_node=False,
                    )
                ],
                is_end_node=False,
            )
        ],
        is_end_node=True,
    ),
    CreateHubbing.ToBeHubbedNode(
        depth_level=1,
        node={"LastName": "Miller", "ForeName": "Tom"},
        parent_rels=[{"_list_item_index": 3}],
        parent_nodes=[
            CreateHubbing.ToBeHubbedNode(
                depth_level=0,
                node={"PMID": "12345", "CompleteYN": "Y"},
                parent_rels=[],
                parent_nodes=[],
                is_end_node=False,
            )
        ],
        is_end_node=False,
    ),
    CreateHubbing.ToBeHubbedNode(
        depth_level=2,
        node={"Affiliation": "University Hospital Bern"},
        parent_rels=[{"_list_item_index": 0}],
        parent_nodes=[
            CreateHubbing.ToBeHubbedNode(
                depth_level=1,
                node={"LastName": "Miller", "ForeName": "Tom"},
                parent_rels=[{"_list_item_index": 3}],
                parent_nodes=[
                    CreateHubbing.ToBeHubbedNode(
                        depth_level=0,
                        node={"PMID": "12345", "CompleteYN": "Y"},
                        parent_rels=[],
                        parent_nodes=[],
                        is_end_node=False,
                    )
                ],
                is_end_node=False,
            )
        ],
        is_end_node=True,
    ),
]
