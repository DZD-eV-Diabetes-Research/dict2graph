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
from dict2graph.transformers._base import (
    _NodeTransformerBase,
    AnyLabel,
)
import typing
import hashlib


class CapitalizeLabels(_NodeTransformerBase):
    def transform_node(self, node: Node):
        node.labels = [label.capitalize() for label in node.labels]


class OverrideLabel(_NodeTransformerBase):
    def __init__(self, value: str, target_label: str = None):
        """_summary_

        Args:
            value (str): The new label
            target_label (str, optional): Optional set this if you dont want the labels from `match_node()` to be replaced. Defaults to None.

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
    def __init__(self, target_label: str = None):
        """_summary_

        Args:
            value (str): The new label
            target_label (str, optional): Optional set this if you dont want the labels from `match_node()` to be replaced. Defaults to None.

        Raises:
            ValueError: _description_
        """
        self.target_label = target_label

    def transform_node(self, node: Node):
        if self.target_label == AnyLabel:
            node.labels = []
        elif self.target_label is None:
            node.labels = [l for l in node.labels if l not in self.matcher.label_match]
        elif isinstance(self.target_label, str):
            node.labels = [l for l in node.labels if l != self.target_label]


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


class RemoveEmptyListRootNodes(_NodeTransformerBase):
    def custom_node_match(self, node: Node) -> bool:
        return node.is_list_collection_hub and len(node.outgoing_relations) == 0

    def transform_node(self, node: Node):
        for rel in node.relations:
            rel.deleted = True
        node.deleted = True


class RemoveListItemLabels(_NodeTransformerBase):
    def custom_node_match(self, node: Node) -> bool:
        return node.is_list_collection_item

    def transform_node(self, node: Node):
        node.labels = [
            l for l in node.labels if l not in self.d2g.list_item_additional_labels
        ]


class CreateHubbing(_NodeTransformerBase):
    def __init__(
        self,
        follow_nodes_labels: List[str],
        merge_property_mode: Literal["lead", "edge"],
        hub_labels: List[str] = ["Hub"],
    ):
        self.follow_nodes_labels = follow_nodes_labels
        self.merge_property_mode = merge_property_mode
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
        # Todo: you are here. maybe start from scratch today!
        hub = Node(labels=self.hub_labels, source_data={}, parent_node=node)
        start_node: Node = node
        fill_nodes: List[Node] = []
        end_node: Node = None
        for follow_node, follow_rel in self._walk_follow_nodes(
            node, follow_nodes_labels=self.follow_nodes_labels
        ):
            end_node = follow_node
            fill_nodes.append(follow_node)
            follow_rel.start_node = hub
        fill_nodes.remove(end_node)
        hash_sources = []
        if self.merge_property_mode.upper() == "EDGE":
            hash_sources.append(start_node.get_hash())
            hash_sources.append(end_node.get_hash())

        elif self.merge_property_mode.upper() == "LEAD":
            hash_sources.extend([n.get_hash() for n in fill_nodes])
        hub[self.d2g.list_hub_id_property_name] = hashlib.md5(
            "".join(hash_sources).encode("utf-8")
        ).hexdigest()
        self.d2g._node_cache.append(hub)
        self.d2g._rel_cache.append(Relation(start_node=node, end_node=hub))

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
