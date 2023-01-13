from typing import TYPE_CHECKING, Callable, Union, Dict, Type, Any, Tuple, Literal, List
from dict2graph.node import Node
from dict2graph.relation import Relation
from dict2graph.transformers._base import _NodeTransformerBase, _RelationTransformerBase
import typing


class OverridePropertyName(_RelationTransformerBase, _NodeTransformerBase):
    def __init__(self, source_property_name: str, target_property_name: str):
        self.source_property_name = source_property_name
        self.target_property_name = target_property_name

    def _transform(self, obj: Dict):
        if self.source_property_name in obj:
            obj[self.target_property_name] = obj.pop(self.source_property_name)

    def transform_node(self, node: Node):
        self._transform(node)

    def transform_rel(self, rel: Relation):
        self._transform(rel)


class TypeCastProperty(_RelationTransformerBase, _NodeTransformerBase):
    def __init__(self, property_name: str, target_type: Union[str, int, float, bool]):
        self.property_name = property_name
        self.target_type = target_type

    def _transform(self, obj: Dict):
        if self.property_name in obj:
            if self.target_type == bool:
                obj[self.property_name] = True
                if obj[self.property_name] in [
                    0,
                    "0",
                    None,
                    "Null",
                    "false",
                    "False",
                    "f",
                    "F",
                    "No",
                    "no",
                ]:
                    obj[self.property_name] = False
            else:
                obj[self.property_name] = self.target_type(obj[self.property_name])

    def transform_node(self, node: Node):
        self._transform(node)

    def transform_rel(self, rel: Relation):
        self._transform(rel)
