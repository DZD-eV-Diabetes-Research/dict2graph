from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict, Tuple, Union, FrozenSet, Any
import json
import uuid
import hashlib

if TYPE_CHECKING:
    from dict2graph import Dict2graph
    from dict2graph.relation import Relation
from dict2graph.graph_object_transformer_meta_data import (
    TransformerMetaDataMixin,
)


class Node(dict, TransformerMetaDataMixin):
    """Represantation of a property-graph node"""

    def __init__(
        self,
        labels: List[str],
        source_data: Union[Dict, List, str, int],
        parent_node: Node,
        **kwargs,
    ):
        if isinstance(labels, str):
            labels = [labels]
        self._labels: List[str] = labels
        self.parent_node: Node = parent_node
        self.source_data: Dict = source_data
        self._merge_property_keys: List[str] = None
        self.update(**kwargs)
        self._relations: List[Relation] = []
        self.is_list_list_hub: bool = False
        self.is_list_list_item: bool = False
        self.is_root_node: bool = False
        self.deleted = False
        self._transformer_meta_data: Dict = {}

    @property
    def id(self) -> str:
        """Deterministic identifier of the Node.
        Will change if the nodes changes merge properties change.
        The `id` is for internal use will not end up in the Neo4j graph.

        Returns:
            str: The id. A hex number string
        """
        if self.merge_property_keys and len(self.merge_property_keys) == 1:
            if self.merge_property_keys[0] in self:
                return self[self.merge_property_keys[0]]
            else:
                return None
        elif len(self.keys()) == 0:
            return None
        else:
            return hashlib.md5(
                bytes(
                    json.dumps([self[key] for key in self.merge_property_keys]),
                    "utf-8",
                ),
            ).hexdigest()

    @property
    def labels(self) -> List[str]:
        """All labels of the node as a list

        Returns:
            List[str]: Labels
        """
        return self._labels

    @labels.setter
    def labels(self, val: List[str]):
        if isinstance(val, list):
            self._labels = val
        else:
            raise ValueError(f"Labels must be provided as list, got {val}")

    @property
    def primary_label(self) -> str:
        """The label to visually represent the node.

        Returns:
            str: the primary label as a string
        """
        return self._labels[0] if self.labels else None

    @primary_label.setter
    def primary_label(self, val: str):
        if val in self._labels:
            self._labels.insert(0, self._labels.pop(self._labels.index(val)))
        else:
            self._labels.insert(0, val)

    @property
    def merge_property_keys(self) -> List[str]:
        """When merging to Neo4j instead of creating, these properties will be taken into account.
        Similar to primary keys in the SQL World.

        Defaults include all properties of the node.

        Returns:
            List[str]: The
        """
        return (
            self._merge_property_keys
            if self._merge_property_keys
            else list(self.keys())
        )

    @merge_property_keys.setter
    def merge_property_keys(self, primary_props: List[str]):
        self._merge_property_keys = primary_props

    def get_hash(
        self,
        include_properties: List[str] = None,
        include_merge_properties: bool = True,
        include_other_properties: bool = True,
        include_parent_properties: bool = False,
        include_children_properties: bool = False,
        include_children_data: bool = False,
    ) -> str:
        """Generate a deterministic hash of the node.
        Optionaly this hahs can include data from child or parents to distinguish from nodes with equal properties.

        Args:
            include_properties (List[str], optional): A list of properties to include in the hash. Defaults to None.
            include_merge_properties (bool, optional): Set True to also include merge properties. Defaults to True.
            include_other_properties (bool, optional): Set True to also include non merge properties. Defaults to True.
            include_parent_properties (bool, optional): Set True to also include merge properties of parent nodes. Defaults to False.
            include_children_properties (bool, optional): Set True to also include merge properties of direct child nodes. Defaults to False.
            include_children_data (bool, optional): Set True to also include all properties of the child tree. Defaults to False.

        Returns:
            str: A hex number string
        """
        if include_properties is None:
            include_properties = []

        hash_source_values = []
        if include_properties:
            hash_source_values.extend(
                [{key: val} for key, val in self.items() if key in include_properties]
            )
        if include_merge_properties:
            hash_source_values.extend(
                [
                    {key: val}
                    for key, val in self.items()
                    if key in self.merge_property_keys + include_properties
                ]
            )
        if include_other_properties:
            hash_source_values.extend(
                [
                    {key: val}
                    for key, val in self.items()
                    if key not in self.merge_property_keys + include_properties
                ]
            )
        if include_parent_properties and self.parent_node is not None:
            hash_source_values.extend(
                [
                    {key: val}
                    for key, val in self.parent_node.items()
                    if key not in self.parent_node.merge_property_keys
                ]
            )
        if include_children_properties:
            for child in self.child_nodes:
                hash_source_values.extend(
                    [
                        {key: val}
                        for key, val in child.items()
                        if key not in child.merge_property_keys
                    ]
                )
        if include_children_data:
            for child in self.child_nodes:
                hash_source_values.append(child.source_data)

        return hashlib.md5(
            bytes(
                json.dumps(hash_source_values),
                "utf-8",
            ),
        ).hexdigest()

    @property
    def relations(self) -> List[Relation]:
        """All relationships a node is connected with

        Returns:
            List[Relation]: A list of relations
        """
        return self._relations

    @relations.setter
    def relations(self, relations: List[Relation]):

        self._relations = [rel for rel in relations if not rel.deleted]

    @property
    def outgoing_relations(self) -> List[Relation]:
        """All outgoing relationships a node is connected with

        Returns:
            List[Relation]: A list of relations
        """
        return [
            rel
            for rel in self.relations
            if rel.start_node == self and not rel.end_node.deleted
        ]

    @property
    def incoming_relations(self) -> List[Relation]:
        """All incoming relationships a node is connected with

        Returns:
            List[Relation]: A list of relations
        """
        return [
            rel
            for rel in self.relations
            if rel.end_node == self and not rel.start_node.deleted
        ]

    @property
    def child_nodes(self) -> List[Node]:
        """All nodes of outgoing relationshipsets

        Returns:
            List[Node]: A list of Nodes
        """
        return [rel.end_node for rel in self.outgoing_relations]

    def __str__(self):
        return f"({':'.join(self.labels)}{super().__str__()})"
