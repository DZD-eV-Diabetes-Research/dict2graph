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


class AddLabel(_NodeTransformerBase):
    def __init__(self, labels: Union[str, List[str]]):
        if isinstance(labels, str):
            labels = [labels]
        self.new_labels = labels

    def transform_node(self, node: Node):
        node.labels = node.labels + self.new_labels


class SetMergeProperties(_NodeTransformerBase):
    def __init__(self, props: List[str]):
        self.props = props

    def transform_node(self, node: Node):
        node.merge_property_keys = self.props


class PopListHubNodes(_NodeTransformerBase):
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
        return node.is_list_list_hub and len(node.outgoing_relations) == 0

    def transform_node(self, node: Node):
        for rel in node.relations:
            rel.deleted = True
        node.deleted = True


class RemoveListItemLabels(_NodeTransformerBase):
    def custom_node_match(self, node: Node) -> bool:
        return node.is_list_list_item

    def transform_node(self, node: Node):
        node.labels = [
            l for l in node.labels if l not in self.d2g.list_item_additional_labels
        ]


class OutsourcePropertiesToNewNode(_NodeTransformerBase):
    def __init__(
        self,
        property_keys: List[str],
        new_node_labels: List[str],
        relation_type: str = None,
        skip_if_keys_empty: bool = True,
    ):
        self.property_keys = property_keys
        self.new_node_labels = new_node_labels
        self.relation_type = relation_type
        self.skip_if_keys_empty = skip_if_keys_empty

    def transform_node(self, node: Node):
        outsourced_props_node: Node = Node(
            labels=self.new_node_labels, source_data={}, parent_node=node
        )
        for key in self.property_keys:

            if key in node:
                outsourced_props_node[key] = node.pop(key)
        if not outsourced_props_node and self.skip_if_keys_empty:
            return
        self.d2g._node_cache.append(outsourced_props_node)
        self.d2g._rel_cache.append(
            Relation(node, outsourced_props_node, relation_type=self.relation_type)
        )


class OutsourcePropertiesToRelationship(_NodeTransformerBase):
    def __init__(
        self,
        property_keys: List[str],
        relation_type: str = None,
        skip_if_keys_empty: bool = True,
        keep_prop_if_relation_does_not_exist: bool = True,
    ):
        self.property_keys = property_keys
        self.relation_type = relation_type
        self.skip_if_keys_empty = skip_if_keys_empty
        self.keep_prop_if_relation_does_not_exist = keep_prop_if_relation_does_not_exist

    def transform_node(self, node: Node):
        for rel in node.relations:
            if rel.relation_type == self.relation_type:
                for prop in self.property_keys:
                    if prop in node and (
                        node[prop] not in ["", None] or not self.skip_if_keys_empty
                    ):
                        rel[prop] = node.pop(prop)
        if not self.keep_prop_if_relation_does_not_exist:
            [node.pop(prop, None) for prop in self.property_keys]


class CreateHubbing(_NodeTransformerBase):
    def __init__(
        self,
        follow_nodes_labels: List[str],
        merge_property_mode: Literal["lead", "edge"],
        hub_labels: List[str] = ["Hub"],
    ):
        if len(follow_nodes_labels) <= 1:
            raise ValueError(
                f"At least chains of 3 node are needed for hubbing. Please provide min. 2 `follow_nodes_labels`. Got only {len(follow_nodes_labels)} labels"
            )
        if merge_property_mode.upper() not in ["LEAD", "EDGE"]:
            raise ValueError(
                f"Only 'lead' and 'edge' mode are supported. got '{merge_property_mode}'"
            )
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


class RemoveNode(_NodeTransformerBase):
    def __init__(self, remove_children: bool = False):
        self.remove_children = remove_children

    def transform_node(self, node: Node):
        node.deleted = True
        for o_rel in node.outgoing_relations:
            o_rel.deleted = True
            if self.remove_children:
                self.transform_node(o_rel.end_node)


class RemoveNodesWithNoProps(_NodeTransformerBase):
    def __init__(self, only_if_no_child_nodes: bool = True):
        self.only_if_no_child_nodes = only_if_no_child_nodes

    def transform_node(self, node: Node):
        if len(node.keys()) == 0 and (
            not self.only_if_no_child_nodes or len(node.outgoing_relations) == 0
        ):
            node.deleted = True
            for o_rel in node.relations:
                o_rel.deleted = True


class RemoveNodesWithOnlyEmptyProps(_NodeTransformerBase):
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
    def transform_node(self, node: Node):
        for i_rel in node.incoming_relations:
            for o_rel in node.outgoing_relations:
                i_rel.end_node = o_rel.end_node
        node.deleted


class MergeChildNodes(_NodeTransformerBase):
    def __init__(
        self,
        child_labels: Union[str, AnyLabel] = AnyLabel,
        child_relation_type: Union[str, AnyRelation] = AnyRelation,
        overwrite_existing_props: bool = True,
        prefix_merged_props_with_primary_label_of_child: bool = False,
        prefix_merged_props_with_hash_of_child: bool = False,
        include_relation_props: bool = True,
    ):
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
