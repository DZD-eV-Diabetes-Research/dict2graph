from typing import TYPE_CHECKING, Callable, Union, Dict, Type, Any, Tuple, Literal, List
from dict2graph.node import Node
from dict2graph.relation import Relation
from dict2graph.transformers._base import (
    _NodeTransformerBase,
    _RelationTransformerBase,
    AnyLabel,
    AnyRelation,
)
import typing


class OverridePropertyName(_RelationTransformerBase, _NodeTransformerBase):
    def __init__(self, source_property_name: str, target_property_name: str):
        self.source_property_name = source_property_name
        self.target_property_name = target_property_name

    def transform(self, obj: Dict):
        if self.source_property_name in obj:
            obj[self.target_property_name] = obj.pop(self.source_property_name)

    def transform_node(self, node: Node):
        self.transform(node)

    def transform_rel(self, rel: Relation):
        self.transform(rel)
