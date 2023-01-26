from typing import TYPE_CHECKING, Callable, Union, Dict, Type, Any, Tuple, Literal, List
from dict2graph.node import Node
from dict2graph.relation import Relation
from dict2graph.transformers._base import (
    _RelationTransformerBase,
    AnyLabel,
    AnyRelation,
)
import typing


class OverrideReliationType(_RelationTransformerBase):
    """_summary_"""

    def __init__(self, value: str = None):
        if not value:
            raise ValueError(f"Value must be a string. Got '{value}'")
        self.value = value

    def transform_rel(self, rel: Relation):
        rel.relation_type = self.value


class FlipNodes(_RelationTransformerBase):
    """_summary_"""

    def transform_rel(self, rel: Relation):
        start_node = rel.start_node
        end_node = rel.end_node
        for inc_rel in start_node.incoming_relations:
            inc_rel.end_node = end_node
        for out_rel in end_node.outgoing_relations:
            out_rel.start_node = start_node
        rel.start_node = rel.end_node
        rel.end_node = start_node


class UppercaseRelationType(_RelationTransformerBase):
    """_summary_"""

    def transform_rel(self, rel: Relation):
        rel.relation_type = rel.relation_type.upper()
