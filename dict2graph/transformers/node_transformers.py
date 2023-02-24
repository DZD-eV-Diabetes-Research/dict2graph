from typing import (
    TYPE_CHECKING,
    Callable,
    Union,
    Dict,
    Type,
    Any,
    Tuple,
    Literal,
    List,
    Generator,
)
from dict2graph.node import Node
from dict2graph.relation import Relation
from dict2graph.transformers._base import _NodeTransformerBase, AnyLabel, AnyRelation
import typing
import hashlib
from dataclasses import dataclass


class CapitalizeLabels(_NodeTransformerBase):
    """Uppercase the first char of node labels.

    **Usage:**

    ```python
    from dict2graph import Dict2graph, Transformer, NodeTrans
    from neo4j import GraphDatabase

    NEO4J_DRIVER = GraphDatabase.driver("neo4j://localhost")

    dic = {"person": {"name": "Camina Drummer"}}
    d2g = Dict2graph()
    d2g.add_node_transformation(
        Transformer.match_nodes("person").do(NodeTrans.CapitalizeLabels())
    )
    d2g.parse(dic)
    d2g.create(NEO4J_DRIVER)
    ```
    Results in a Neo4j node `(:Person{name:'Camina Drummer'})`
    """

    def transform_node(self, node: Node):
        node.labels = [label.capitalize() for label in node.labels]


class OverrideLabel(_NodeTransformerBase):
    """Replace a node label with a new string
    **Usage:**

    ```python
    from dict2graph import Dict2graph, Transformer, NodeTrans
    from neo4j import GraphDatabase

    NEO4J_DRIVER = GraphDatabase.driver("neo4j://localhost")

    dic = {"person": {"name": "Camina Drummer"}}
    d2g = Dict2graph()
    d2g.add_node_transformation(
        Transformer.match_nodes("person").do(NodeTrans.OverrideLabel("Character"))
    )
    d2g.parse(dic)
    d2g.create(NEO4J_DRIVER)
    ```
    Results in a Neo4j node `(:Character{name:'Camina Drummer'})`
    """

    def __init__(self, value: str, target_label: str = None):
        """_summary_

        Args:
            value (str): The new labels string.
            target_label (str, optional): The label you want to be replaced.
                If none, the labels defined in the `node_match()` function will be replaced.
                Defaults to None.

        Raises:
            ValueError: _description_
        """
        if not value:
            raise ValueError(f"Value must be a string. Got '{value}'")
        self.value = value
        self.target_label = target_label

    def transform_node(self, node: Node):
        if self.target_label:
            replace_labels = [self.target_label]
        else:
            replace_labels = self.matcher.label_match
        for origin_label in replace_labels:
            node.labels = list(
                map(lambda x: x.replace(origin_label, self.value), node.labels)
            )


class RemoveLabel(_NodeTransformerBase):
    """Remove a certain label from nodes

    **Usage:**

    ```python
    from dict2graph import Dict2graph, Transformer, NodeTrans
    from neo4j import GraphDatabase

    NEO4J_DRIVER = GraphDatabase.driver("neo4j://localhost")

    dic = {"person": [{"name": "Camina Drummer"},{"name":"James Holden"}]}
    d2g = Dict2graph()
    d2g.add_node_transformation(
        Transformer.match_nodes("person").do(NodeTrans.RemoveLabel("ListItem"))
    )
    d2g.parse(dic)
    d2g.create(NEO4J_DRIVER)
    ```

    Results in removing the `:ListItem` label from `:Person` nodes
    """

    def __init__(
        self,
        target_labels: Union[None, str, List[str], AnyLabel] = None,
        omit_removal_for_labels: Union[None, str, List[str]] = None,
    ):
        """_summary_

        Args:
            target_labels (Union[None, str, List[str], AnyLabel], optional): Optional set this if you dont want the labels from `match_nodes()` to be replaced. Defaults to None.
            omit_removal_for_labels (Union[None, str, List[str]], optional): _description_. Defaults to None.
        """
        if isinstance(target_labels, str):
            target_labels = [target_labels]
        if isinstance(omit_removal_for_labels, str):
            omit_removal_for_labels = [omit_removal_for_labels]

        if (
            target_labels not in [None, AnyLabel]
            and omit_removal_for_labels
            not in [
                None,
                AnyLabel,
            ]
            and set(target_labels).intersection(set(omit_removal_for_labels))
        ):
            raise ValueError(
                f"`target_labels` and `omit_removal_for_labels` are contradicting: \ntarget_labels: {target_labels}\nomit_removal_for_labels:{omit_removal_for_labels}"
            )
        self.target_labels = target_labels
        self.omit_removal_for_labels = omit_removal_for_labels

    def transform_node(self, node: Node):
        # ToDo: Refactor this mess.
        target_labels: Union[List[str], AnyLabel] = (
            self.target_labels
            if self.target_labels is not None
            else self.matcher.label_match
        )
        if isinstance(target_labels, str):
            target_labels = [target_labels]
        if isinstance(target_labels, str):
            target_labels = [target_labels]
        new_labels = []
        for existing_label in node.labels:
            if target_labels == AnyLabel or existing_label in target_labels:
                if (
                    self.omit_removal_for_labels
                    and existing_label in self.omit_removal_for_labels
                ):
                    new_labels.append(existing_label)
                else:
                    continue
            else:
                new_labels.append(existing_label)

        node.labels = new_labels


class ConvertLabelToProp(_NodeTransformerBase):
    """Convert a certain label to a node property

     **Usage:**

    ```python
    from dict2graph import Dict2graph, Transformer, NodeTrans
    from neo4j import GraphDatabase

    NEO4J_DRIVER = GraphDatabase.driver("neo4j://localhost")

    dic = {"person": [{"name": "Camina"}, {"name": "Asom"}]}
    d2g = Dict2graph()
    d2g.add_node_transformation(
        Transformer.match_nodes("person").do(
            [
                NodeTrans.AddLabel("Agent"),
                NodeTrans.ConvertLabelToProp(
                    "type",
                    target_labels=AnyLabel,
                    omit_move_labels=["Agent", "ListItem", "ListHub"],
                ),
            ]
        )

    d2g.parse(dic)
    d2g.create(NEO4J_DRIVER)
    ```

    This removes the `:person` labels nad add a new property `type` with the value `person`
    """

    def __init__(
        self,
        prop_key: str,
        target_labels: Union[None, str, List[str], AnyLabel] = None,
        omit_move_labels: Union[None, str, List[str]] = None,
    ):
        """_summary_

        Args:
            prop_key (str): _description_
            target_labels (Union[None, str, List[str], AnyLabel], optional): _description_. Defaults to None.
            omit_move_labels (Union[None, str, List[str]], optional): _description_. Defaults to None.

        Raises:
            ValueError: _description_
        """
        self.prop_key = prop_key
        if isinstance(target_labels, str):
            target_labels = [target_labels]
        if isinstance(omit_move_labels, str):
            omit_move_labels = [omit_move_labels]
        if omit_move_labels is None:
            omit_move_labels = []

        self.target_labels: Union[None, List[str], AnyLabel] = target_labels

        self.omit_move_labels: List[str] = omit_move_labels

    def transform_node(self, node: Node):
        # ToDo: Refactor this mess.
        target_labels: Union[List[str], AnyLabel] = (
            self.target_labels
            if self.target_labels is not None
            else self.matcher.label_match
        )
        if isinstance(target_labels, str):
            target_labels = [target_labels]
        converted_labels = []
        for existing_label in node.labels:
            if target_labels == AnyLabel or existing_label in target_labels:
                if not existing_label in self.omit_move_labels:
                    converted_labels.append(existing_label)
                else:
                    continue
            else:
                converted_labels.append(existing_label)
        if len(converted_labels) == 1:
            node.labels.pop(node.labels.index(converted_labels[0]))
            node[self.prop_key] = converted_labels[0]
        elif len(converted_labels) > 1:
            for index, convert_label in enumerate(converted_labels):
                node.labels.pop(node.labels.index(convert_label))
                node[f"{self.prop_key}_{index}"] = convert_label


class AddLabel(_NodeTransformerBase):
    """Add one or more new labels to nodes

    **Usage:**

    ```python
    from dict2graph import Dict2graph, Transformer, NodeTrans
    from neo4j import GraphDatabase

    NEO4J_DRIVER = GraphDatabase.driver("neo4j://localhost")

    dic = {"person": {"name": "Camina Drummer"}}
    d2g = Dict2graph()
    d2g.add_node_transformation(
        Transformer.match_nodes("person").do(NodeTrans.AddLabel("Character"))
    )
    d2g.parse(dic)
    d2g.create(NEO4J_DRIVER)
    ```

    Results in a Neo4j node `(:person:Character{name:'Camina Drummer'})`
    """

    def __init__(self, labels: Union[str, List[str]]):
        """

        Args:
            labels (Union[str, List[str]]): A string or a list of strings that will be added as new labels to the matched nodes
        """
        if isinstance(labels, str):
            labels = [labels]
        self.new_labels = labels

    def transform_node(self, node: Node):
        node.labels = node.labels + self.new_labels


class SetMergeProperties(_NodeTransformerBase):
    """Set the primary properties that will be taken into account when comparing nodes while merging them together.
    ```python
    from dict2graph import Dict2graph, Transformer, NodeTrans
    from neo4j import GraphDatabase

    NEO4J_DRIVER = GraphDatabase.driver("neo4j://localhost")

    data = {
        "books": [
            {
                "title": "Science Behind The Cyberpunks-Genre Awesomeness",
            },
            {
                "title": "Science Behind The Cyberpunks-Genre Awesomeness",
            }
        ]
    }
    d2g = Dict2graph()
    d2g.add_node_transformation(
        Transformer.match_nodes(["books", "ListItem"]).do(
            NodeTrans.SetMergeProperties(props=["title"])
        )
    )
    d2g.parse(data)
    d2g.merge(NEO4J_DRIVER)
    ```

    Will result in one Node `(:book)` because we only compare by the property `title` when mergin nodes together.
    """

    def __init__(self, props: List[str]):
        """
        Args:
            props (List[str]): A list of property keys to take into account for merging.
        """
        self.props = props

    def transform_node(self, node: Node):
        node.merge_property_keys = self.props


class PopListHubNodes(_NodeTransformerBase):
    """When dict2grapg parses dict lists it create a hub node to attach all list items.
    In most cases this is unnecessary and will make your graph model larger as it has to be.
    `PopListHubNodes` will just remove these list hubs.


    **Usage:**

    ```python
    from dict2graph import Dict2graph, Transformer, NodeTrans
    from neo4j import GraphDatabase

    NEO4J_DRIVER = GraphDatabase.driver("neo4j://localhost")

    data = {
        "bookshelf": {
            "book": [
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
    d2g.create(NEO4J_DRIVER)
    ```

    This will result in a `(:bookshelf)`node directly connected to 2 `(:book)` nodes instead of a `:ListHub:book` node in between.

    """

    def custom_node_match(self, node: Node) -> bool:
        return node.is_list_list_hub

    def transform_node(self, node: Node):
        new_list_item_nodes_parent = node.parent_node
        for list_item_rel in node.outgoing_relations:
            if new_list_item_nodes_parent is not None:
                list_item_rel.start_node = new_list_item_nodes_parent
            else:
                # we are at the root node level. the list will now without any parent.
                list_item_rel.deleted
        for parent_rels in node.incoming_relations:
            parent_rels.deleted = True
        node.deleted = True


class CreateNewMergePropertyFromHash(_NodeTransformerBase):
    """Create a new merge-property for the node.
    The value of this property will be a configurable hash.
    See __init__() for configruation details.


    **Usage:**

    ```python
    from dict2graph import Dict2graph, Transformer, NodeTrans
    from neo4j import GraphDatabase

    NEO4J_DRIVER = GraphDatabase.driver("neo4j://localhost")

    dic = [
        {"person": {"fname": "Joe ", "lname": "Miller", "domiciles": ["Ceres", "Belt", "SOL"]}},
        {"person": {"fname": "Joe ", "lname": "Miller", "domiciles": ["Earth"]}},
    ]
    d2g = Dict2graph()
    d2g.add_node_transformation(
        Transformer.match_nodes("person").do(
            NodeTrans.CreateNewMergePropertyFromHash(
                hash_includes_children_data=True
            )
        )
    )
    d2g.parse(dic)
    d2g.merge(NEO4J_DRIVER)
    ```
    Results in a Graph with two different `Joe Miller`s.

    Initially the disambiguation is only determinable by the `Joe Miller` child nodes `domiciles`.
    With `NodeTrans.CreateNewMergePropertyFromHash` we can create a hash from the node and its children.
    This way merging will not result in false positives regarding distinguishing objects.
    See `__init__()` for more options to modify the hash.
    """

    def __init__(
        self,
        hash_includes_properties: List[str] = None,
        hash_includes_existing_merge_props: bool = False,
        hash_includes_existing_other_props: bool = False,
        hash_includes_children_nodes_merge_properties: bool = False,
        hash_includes_children_data: bool = False,
        hash_includes_parent_merge_properties: bool = False,
        new_merge_property_name: str = "_id",
    ):
        """_summary_

        Args:
            hash_includes_properties (List[str], optional): Define certain properties to go into the hash. Defaults to None.
            hash_includes_existing_merge_props (bool, optional): Include merge-properties in the hash. Defaults to False.
            hash_includes_existing_other_props (bool, optional): Include all non merge-properties in the hash. Defaults to False.
            hash_includes_children_nodes_merge_properties (bool, optional): Include all merge-properties of all direct child nodes. Defaults to False.
            hash_includes_children_data (bool, optional): Include all data from direct and indirect children. Defaults to False.
            hash_includes_parent_merge_properties (bool, optional): Include merge properties of parent nodes. Defaults to False.
            new_merge_property_name (str, optional): The key for the newly generated property. Defaults to "_id".
        """
        self.hash_includes_existing_merge_props = hash_includes_existing_merge_props
        self.hash_includes_existing_other_props = hash_includes_existing_other_props
        self.hash_includes_properties = hash_includes_properties
        self.hash_includes_children_nodes_merge_properties = (
            hash_includes_children_nodes_merge_properties
        )
        self.hash_includes_children_data = hash_includes_children_data
        self.hash_includes_children_data = hash_includes_children_data
        self.hash_includes_parent_merge_properties = (
            hash_includes_parent_merge_properties
        )
        self.new_merge_property_name = new_merge_property_name

    def transform_node(self, node: Node):
        if self.hash_includes_properties:
            node.merge_property_keys = list(
                set(node.merge_property_keys + self.hash_includes_properties)
            )
        node[self.new_merge_property_name] = node.get_hash(
            include_properties=self.hash_includes_properties,
            include_merge_properties=self.hash_includes_existing_merge_props,
            include_other_properties=self.hash_includes_existing_other_props,
            include_parent_properties=self.hash_includes_parent_merge_properties,
            include_children_properties=self.hash_includes_children_nodes_merge_properties,
            include_children_data=self.hash_includes_children_data,
        )
        node.merge_property_keys = [self.new_merge_property_name]


class RemoveEmptyListRootNodes(_NodeTransformerBase):
    """Remove any list root/hub nodes with no children.

    **Usage:**

    ```python
    from dict2graph import Dict2graph, Transformer, NodeTrans
    from neo4j import GraphDatabase

    NEO4J_DRIVER = GraphDatabase.driver("neo4j://localhost")

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

    d2g.create(NEO4J_DRIVER)
    ```

    Results in two person nodes. The `Joe Miller`-node will not have any `children` list nodes related.
    Without the `RemoveEmptyListRootNodes` the `Joe Miller`-node would have attached an empty `ListHub:Children`-node
    """

    def custom_node_match(self, node: Node) -> bool:
        return node.is_list_list_hub and len(node.outgoing_relations) == 0

    def transform_node(self, node: Node):
        for rel in node.relations:
            rel.deleted = True
        node.deleted = True


class RemoveListItemLabels(_NodeTransformerBase):
    """Remove `ListItem` labels that are automatic attached to every list item by dict2graph.
        **Usage:**

    ```python
    from dict2graph import Dict2graph, Transformer, NodeTrans
    from neo4j import GraphDatabase

    NEO4J_DRIVER = GraphDatabase.driver("neo4j://localhost")

    dic = {
        "person": {"fname": "Marco ", "lname": "Inaros", "children": ["Filip Inaros"]}
    }

    d2g = Dict2graph()
    d2g.add_node_transformation(
        Transformer.match_nodes().do(NodeTrans.RemoveListItemLabels())
    )
    d2g.parse(dic)

    d2g.create(NEO4J_DRIVER)
    ```

    The "Filip Inaros"-`children`-node will not have an extra label `ListItem`.
    """

    def custom_node_match(self, node: Node) -> bool:
        return node.is_list_list_item

    def transform_node(self, node: Node):
        node.labels = [
            l for l in node.labels if l not in self.d2g.list_item_additional_labels
        ]


class OutsourcePropertiesToNewNode(_NodeTransformerBase):
    """Move one or multiple properties to a new node.

    **Usage:**

    ```python
    from dict2graph import Dict2graph, Transformer, NodeTrans
    from neo4j import GraphDatabase

    NEO4J_DRIVER = GraphDatabase.driver("neo4j://localhost")

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
    d2g.create(NEO4J_DRIVER)
    ```

    instead of only one person-"Marco Inaros"-node, with a property "child:'Filip Inaros'", we have a second person-"Filip Inaros"-node.
    They are connected with a relation `person_has_child`.
    """

    def __init__(
        self,
        property_keys: List[str],
        new_node_labels: List[str],
        relation_type: str = None,
        skip_if_prop_val_empty: bool = True,
    ):
        self.property_keys = property_keys
        self.new_node_labels = new_node_labels
        self.relation_type = relation_type
        self.skip_if_prop_val_empty = skip_if_prop_val_empty

    def transform_node(self, node: Node):
        outsourced_props_node: Node = Node(
            labels=self.new_node_labels, source_data={}, parent_node=node
        )
        for key in self.property_keys:

            if key in node:
                outsourced_props_node[key] = node.pop(key)

        if not outsourced_props_node and self.skip_if_prop_val_empty:
            return
        self.d2g.add_node_to_cache(outsourced_props_node)
        self.d2g.add_rel_to_cache(
            Relation(node, outsourced_props_node, relation_type=self.relation_type)
        )


class OutsourcePropertiesToRelationship(_NodeTransformerBase):
    """Move one or multiple properties to an existing relation.

    **Usage:**

    ```python
    from dict2graph import Dict2graph, Transformer, NodeTrans
    from neo4j import GraphDatabase

    NEO4J_DRIVER = GraphDatabase.driver("neo4j://localhost")

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
    d2g.create(NEO4J_DRIVER)
    ```

    Shifts the fathers prop `"child_rel": "biological"` on the relation between child and father.
    """

    def __init__(
        self,
        property_keys: List[str],
        relation_types: Union[str, List[str]],
        skip_if_prop_val_empty: bool = False,
        keep_prop_if_no_relation_exist: bool = True,
    ):
        """
        Args:
            property_keys (List[str]): The properties, defined by their keys, that should be moved to the relationship.
            relation_types (Union[str, List[str]]): The relation(s), the properties should be moved to.
            skip_if_prop_val_empty (bool, optional): If the property has no value, dont move it to the relation. Defaults to False.
            keep_prop_if_no_relation_exist (bool, optional): Set to `False` if the property should be removed from the node, even if there is no relation it can move to. Defaults to True.
        """
        self.property_keys = property_keys
        if isinstance(relation_types, str):
            relation_types = [relation_types]
        self.relation_types = relation_types
        self.skip_if_prop_val_empty = skip_if_prop_val_empty
        self.keep_prop_if_no_relation_exist = keep_prop_if_no_relation_exist

    def transform_node(self, node: Node):
        for prop_key in self.property_keys:
            if prop_key in node:
                prop_val = node.pop(prop_key)
            else:
                continue
            if not prop_val and self.skip_if_prop_val_empty:
                continue
            found_rel: bool = False
            for rel in node.relations:
                if rel.relation_type in self.relation_types:
                    found_rel = True
                    rel[prop_key] = prop_val
            if not found_rel and self.keep_prop_if_no_relation_exist:
                node[prop_key] = prop_val


class CreateHubbing(_NodeTransformerBase):
    """Convert a chain of nodes to a tree of nodes. Details are explained in the [hubbing article](/hubbing)

    **usage**:

    ```python
    from dict2graph import Dict2graph, Transformer, NodeTrans
    from neo4j import GraphDatabase

    DRIVER = GraphDatabase.driver("neo4j://localhost")
    d2g = Dict2graph()

    # we define the start node by matching it with dict2graph
    transformer = Transformer.match_nodes("article").do(
            # apply the hubbing-transformer
            NodeTrans.CreateHubbing(
                # define the node chain by defining the follow node labels
                follow_nodes_labels=["author", "affiliation"],
                # define the merge mode
                merge_mode="edge",
                # give the hub node one or more labels
                hub_labels=["Contribution"],
            )
        )
    # Add the transformer the tranformator stack of our Dict2graph instance
    d2g.add_transformation(transformer)

    dataset_1 = {
        "article": {
            "title": "Blood money: Bayer's inventory of HIV-contaminated blood products and third world hemophiliacs",
            "author": {
                "name": "Leemon McHenry",
                "affiliation": {
                    "name": "Department of Philosophy, California State University"
                },
            },
        },
    }
    d2g.parse(dataset_1)
    d2g.merge(DRIVER)
    ```

    Results in a Y-formed graph with a new hub node in the middle, instead of three nodes in a chain.

    """

    @dataclass
    class ToBeHubbedNode:
        depth_level: int
        node: Node
        parent_rels: List[Relation]
        child_nodes: List["CreateHubbing.ToBeHubbedNode"]
        end_node: bool = (True,)

    def __init__(
        self,
        follow_nodes_labels: List[str],
        merge_mode: Literal["lead", "edge"],
        hub_labels: List[str] = ["Hub"],
    ):
        """
        Args:
            follow_nodes_labels (List[str]): The child nodes in the chain.
            merge_mode (Literal["lead", "edge"]): Should the hash ID for the hub be based on parent nodes or the outer nodes.
            hub_labels (List[str], optional): The labels for the new hub node. Defaults to ["Hub"].
        """
        if len(follow_nodes_labels) <= 1:
            raise ValueError(
                f"At least chains of 3 node are needed for hubbing. Please provide min. 2 `follow_nodes_labels`. Got only {len(follow_nodes_labels)} labels"
            )
        if merge_mode.upper() not in ["LEAD", "EDGE"]:
            raise ValueError(
                f"Only 'lead' and 'edge' mode are supported. got '{merge_mode}'"
            )
        self.follow_nodes_labels = follow_nodes_labels
        self.merge_mode = merge_mode
        if isinstance(hub_labels, str):
            hub_labels = [hub_labels]
        self.hub_labels = hub_labels

    def custom_node_match(self, node: Node) -> bool:
        # walk the node tree to check if this subtree needs to be hubbed.
        # if all follow_nodes_labels exists in the right order, according follow_nodes_labels, to we will hub
        return len(
            list(self._walk_follow_nodes(node, self.follow_nodes_labels))
        ) >= len(self.follow_nodes_labels)

    def transform_node(self, node: Node):

        hub = Node(labels=self.hub_labels, source_data={}, parent_node=node)
        start_node: Node = node
        fill_nodes: List[Node] = []
        end_node: Node = None
        subg = self._get_to_be_hubbed_sub_graph(start_node=start_node)
        # YOU ARE HERE AND HAVE THE SUBGRAPH. nice! next step will be easier :)
        print(subg)
        exit()

    def _get_to_be_hubbed_sub_graph(
        self, start_node: Node, depth: int = 0
    ) -> List[ToBeHubbedNode]:
        nodes: List[CreateHubbing.ToBeHubbedNode] = []
        for outgoing_rel in start_node.outgoing_relations:
            node = outgoing_rel.end_node
            if self.follow_nodes_labels[depth] in node.labels:
                is_end_node: bool = depth == len(self.follow_nodes_labels) - 1
                existing_node: CreateHubbing.ToBeHubbedNode = next(
                    (
                        to_be_hubbed_node
                        for to_be_hubbed_node in nodes
                        if to_be_hubbed_node.node == node
                        and to_be_hubbed_node.depth_level == depth
                    ),
                    None,
                )
                if existing_node:
                    existing_node.parent_rels.append(outgoing_rel)
                else:
                    nodes.append(
                        CreateHubbing.ToBeHubbedNode(
                            depth_level=depth,
                            node=node,
                            parent_rels=[outgoing_rel],
                            child_nodes=None
                            if is_end_node
                            else self._get_to_be_hubbed_sub_graph(
                                node, depth=depth + 1
                            ),
                            end_node=is_end_node,
                        )
                    )
        return nodes

    def _walk_follow_nodes(
        self, node: Node, follow_nodes_labels: List[str]
    ) -> Generator[Tuple[Node, Relation], None, None]:
        if len(follow_nodes_labels) == 0:
            return
        for o_rel in [r for r in node.outgoing_relations if not r.deleted]:
            for end_node_label in o_rel.end_node.labels:
                if end_node_label in follow_nodes_labels[0]:
                    yield o_rel.end_node, o_rel
                    for n, r in self._walk_follow_nodes(
                        o_rel.end_node,
                        [l for l in follow_nodes_labels if l != end_node_label],
                    ):
                        yield n, r


class RemoveNode(_NodeTransformerBase):
    """Removes matched nodes.

    **Usage:**

    ```python
    from dict2graph import Dict2graph, Transformer, NodeTrans
    from neo4j import GraphDatabase

    NEO4J_DRIVER = GraphDatabase.driver("neo4j://localhost")

    dic = {
        "person": {
            "fname": "Marco ",
            "lname": "Inaros",
            "child": {"fname": "Filip", "lname": "Inaros"},
        }
    }

    d2g = Dict2graph()
    d2g.add_node_transformation(
        Transformer.match_nodes("child").do(
            NodeTrans.RemoveNode()
        )
    )
    d2g.parse(dic)
    d2g.create(NEO4J_DRIVER)
    ```

    Shifts the fathers prop `"child_rel": "biological"` on the relation between child and father.
    """

    def __init__(self, remove_children: bool = False):
        """_summary_

        Args:
            remove_children (bool, optional): Remove all nodes and relations down the tree as well. Defaults to False.
        """
        self.remove_children = remove_children

    def transform_node(self, node: Node):
        node.deleted = True
        for o_rel in node.outgoing_relations:
            o_rel.deleted = True
            if self.remove_children:
                self.transform_node(o_rel.end_node)


class RemoveNodesWithNoProps(_NodeTransformerBase):
    """Removes nodes if they have no properties.
    **Usage:**

    ```python
    from dict2graph import Dict2graph, Transformer, NodeTrans
    from neo4j import GraphDatabase

    NEO4J_DRIVER = GraphDatabase.driver("neo4j://localhost")

    dic = {
        "person": {
            "name": "Roberta W. Draper",
            "child": {},
        }
    }

    d2g = Dict2graph()

    d2g.add_node_transformation(
        Transformer.match_nodes("child").do(NodeTrans.RemoveNodesWithNoProps())
    )

    d2g.parse(dic)
    d2g.create(NEO4J_DRIVER)
    ```

    Results in removing the empty `child`-node
    """

    def __init__(self, only_if_no_child_nodes: bool = True):
        """_summary_

        Args:
            only_if_no_child_nodes (bool, optional): Remove the node only if it is  at the edge of our graph and has not outgoing relationshsips. Defaults to True.
        """
        self.only_if_no_child_nodes = only_if_no_child_nodes

    def transform_node(self, node: Node):
        if len(node.keys()) == 0 and (
            not self.only_if_no_child_nodes or len(node.outgoing_relations) == 0
        ):
            node.deleted = True
            for o_rel in node.relations:
                o_rel.deleted = True


class RemoveNodesWithOnlyEmptyProps(_NodeTransformerBase):
    """Removes nodes if they have only empty properties.
    "Empty" in terms of null/"" values
    **Usage:**

    ```python
    from dict2graph import Dict2graph, Transformer, NodeTrans
    from neo4j import GraphDatabase

    NEO4J_DRIVER = GraphDatabase.driver("neo4j://localhost")

    dic = {
        "person": {
            "name": "Roberta W. Draper",
            "child": {"name":""},
        }
    }

    d2g = Dict2graph()

    d2g.add_node_transformation(
        Transformer.match_nodes("child").do(NodeTrans.RemoveNodesWithOnlyEmptyProps())
    )

    d2g.parse(dic)
    d2g.create(NEO4J_DRIVER)
    ```

    Results in removing the empty `child`-node
    """

    def __init__(self, only_if_no_child_nodes: bool = True):
        self.only_if_no_child_nodes = only_if_no_child_nodes

    def transform_node(
        self,
        node: Node,
    ):
        if set(node.values()) in [set([None]), set([""]), set([None, ""])]:
            if not self.only_if_no_child_nodes or len(node.outgoing_relations) == 0:
                node.deleted = True
                for o_rel in node.outgoing_relations:
                    o_rel.deleted = True


class PopNode(_NodeTransformerBase):
    """Removes nodes but connect its children and parents to not lose the path.


    **Usage:**

    ```python
    from dict2graph import Dict2graph, Transformer, NodeTrans
    from neo4j import GraphDatabase

    NEO4J_DRIVER = GraphDatabase.driver("neo4j://localhost")

    dic = {
        "person": {
            "name": "Chrisjen Avasarala",
            "connections": {
                "child_1": {"name": "Charanpal"},
                "child_2": {"name": "Ashanti"},
            },
        }
    }

    d2g = Dict2graph()

    d2g.add_node_transformation(
        Transformer.match_nodes("connections").do(NodeTrans.PopNode())
    )

    d2g.parse(dic)
    d2g.create(NEO4J_DRIVER)
    ```

    Results in directly conneting children to person "Chrisjen Avasarala" without an in between node "connections"
    """

    def transform_node(self, node: Node):
        for parent_rel in node.incoming_relations:
            for child_rel in node.outgoing_relations:
                child_rel.start_node = parent_rel.start_node
            parent_rel.deleted = True
        node.deleted = True


class MergeChildNodes(_NodeTransformerBase):
    """A node will absorb the properties of one or multiple child nodes
    and the child nodes will be poped (aka. removed but a relation to grandchild nodes keeps existing)


    **Usage:**

    ```python
    from dict2graph import Dict2graph, Transformer, NodeTrans
    from neo4j import GraphDatabase

    NEO4J_DRIVER = GraphDatabase.driver("neo4j://localhost")

    dic = {
        "person": {
            "name": "Chrisjen Avasarala",
            "personal_info": {
                "Home": "New York, Earth",
                "occupation": "United Nations Government",
            },
        }
    }

    d2g = Dict2graph()

    d2g.add_node_transformation(
        Transformer.match_nodes("person").do(NodeTrans.MergeChildNodes("personal_info"))
    )

    d2g.parse(dic)
    d2g.create(NEO4J_DRIVER)
    ```

    Results in one person-node with all attributes instead of an extra "personal_info"-node connected to the person-node "Chrisjen Avasarala"
    """

    def __init__(
        self,
        child_labels: Union[str, List[str], AnyLabel] = AnyLabel,
        child_relation_type: Union[str, AnyRelation] = AnyRelation,
        overwrite_existing_props: bool = True,
        prefix_merged_props_with_primary_label_of_child: bool = False,
        prefix_merged_props_with_hash_of_child: bool = False,
        include_relation_props: bool = True,
    ):
        """_summary_

        Args:
            child_labels (Union[str, List[str], AnyLabel], optional): Label to match a specific child. Defaults to AnyLabel which merges all children
            child_relation_type (Union[str, AnyRelation], optional): If you want to match children with a specifi relationshop only. Defaults to AnyRelation.
            overwrite_existing_props (bool, optional): If parent and children share property keys overwrite them on the parent. If set so false, the props will get an index. Defaults to True.
            prefix_merged_props_with_primary_label_of_child (bool, optional): Prefix the merged properties with the primary label of the child. Defaults to False.
            prefix_merged_props_with_hash_of_child (bool, optional): Prefix the merged properties with a hash of the child. Defaults to False.
            include_relation_props (bool, optional): Merge properties from the Node-child relationship as well. Defaults to True.
        """
        if isinstance(child_labels, str):
            child_labels = [child_labels]
        self.child_labels = child_labels
        self.child_relation_type = child_relation_type
        self.overwrite_existing_props = overwrite_existing_props
        self.prefix_merged_props_with_primary_label = (
            prefix_merged_props_with_primary_label_of_child
        )
        self.prefix_merged_props_with_hash_of_child = (
            prefix_merged_props_with_hash_of_child
        )
        self.include_relation_props = include_relation_props

    def transform_node(self, node: Node):
        for outgoing_rel in node.outgoing_relations:
            child_node = outgoing_rel.end_node
            if not (
                self.child_labels == AnyLabel
                or set(self.child_labels).issubset(set(child_node.labels))
            ):
                continue
            if not (
                self.child_relation_type == AnyRelation
                or outgoing_rel.relation_type == self.child_relation_type
            ):
                continue
            if self.include_relation_props:
                self._merge_props(target_node=node, obj=outgoing_rel)

            self._merge_props(target_node=node, obj=child_node)
            for outgoing_child_rel in child_node.outgoing_relations:
                outgoing_child_rel.start_node = node
            for incoming_child_rel in child_node.incoming_relations:
                if incoming_child_rel.start_node != node:
                    incoming_child_rel.start_node = node
                else:
                    incoming_child_rel.deleted = True
            child_node.deleted = True

    def _merge_props(
        self,
        target_node: Node,
        obj: Union[Node, Relation],
    ):

        for key, val in obj.items():
            result_key = key
            if self.prefix_merged_props_with_primary_label:
                prefix = (
                    obj.primary_label if isinstance(obj, Node) else obj.relation_type
                )
                result_key = f"{prefix}_{result_key}"
            if self.prefix_merged_props_with_hash_of_child and isinstance(obj, Node):
                result_key = f"{obj.get_hash()}_{result_key}"
            if key in target_node and not self.overwrite_existing_props:
                max_index = max(
                    [
                        k.split("_")[-1]
                        for k in list(target_node.keys())
                        if k.startswith(key) and k.split("_")[-1].isnumeric()
                    ],
                    default="-1",
                )
                result_key = f"{result_key}_{int(max_index)+1}"
            target_node[result_key] = val
