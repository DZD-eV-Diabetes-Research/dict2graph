from typing import TYPE_CHECKING, Callable, Union, Dict, Type, Any, Tuple, Literal, List
from dict2graph.node import Node
from dict2graph.relation import Relation
from dict2graph.transformers._base import (
    _NodeTransformerBase,
    AnyLabel,
)
import typing


class CapitalizeLabels(_NodeTransformerBase):
    def transform_node(self, node: Node):
        node.labels = [label.capitalize() for label in node.labels]


class OverrideLabel(_NodeTransformerBase):
    def __init__(self, value: str = None):
        """Override any generated labels with another string

        Args:
            value (bool, optional): The new label string. Defaults to None.
        """
        if not value:
            raise ValueError(f"Value must be a string. Got '{value}'")
        self.value = value

    def transform_node(self, node: Node):
        node.labels = [
            self.value if self.matcher.label_match in [label, None, AnyLabel] else label
            for label in node.labels
        ]


class SetMergeProperties(_NodeTransformerBase):
    def __init__(self, props: List[str]):
        self.props = props

    def transform_node(self, node: Node):
        node.merge_property_keys = self.props


class PopListHubNodes(_NodeTransformerBase):
    def custom_node_match(self, node: Node) -> bool:
        return node.is_list_collection_hub

    def transform_node(self, node: Node):
        new_list_item_nodes_parent = node.parent_node
        for list_item_rel in node.outgoing_relations:
            list_item_rel.start_node = new_list_item_nodes_parent
        for parent_rels in node.incoming_relations:
            parent_rels.deleted = True
        node.deleted = True


class CreateNewMergePropertyFromHash(_NodeTransformerBase):
    def __init__(
        self,
        hash_includes_properties: List[str] = None,
        hash_includes_existing_merge_props: bool = False,
        hash_includes_existing_other_props: bool = False,
        hash_includes_children_nodes_merge_properties: bool = False,
        hash_includes_children_nodes_merge_data: bool = False,
        hash_includes_parent_merge_properties: bool = False,
        new_merge_property_name: str = "_id",
    ):
        self.hash_includes_existing_merge_props = hash_includes_existing_merge_props
        self.hash_includes_existing_other_props = hash_includes_existing_other_props
        self.hash_includes_properties = hash_includes_properties
        self.hash_includes_children_nodes_merge_properties = (
            hash_includes_children_nodes_merge_properties
        )
        self.hash_includes_children_nodes_merge_data = (
            hash_includes_children_nodes_merge_data
        )
        self.hash_includes_children_nodes_merge_data = (
            hash_includes_children_nodes_merge_data
        )
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
            include_children_data=self.hash_includes_children_nodes_merge_data,
        )
        node.merge_property_keys = [self.new_merge_property_name]
