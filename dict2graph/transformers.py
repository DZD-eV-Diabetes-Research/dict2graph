from typing import Callable, Union, Dict, Type, Any, Tuple, Literal
from dict2graph.node import Node
from dict2graph.relation import Relation
import typing


class AnyLabel:
    pass


class AnyRelation:
    pass


class _NodeTransformerBase:
    def __init__(
        self,
        **kwargs,
    ):
        pass

    def _set_primary_label_match(
        self, primary_label_match: Union[str, Type[AnyLabel]] = AnyLabel
    ):
        self.primary_label_match = primary_label_match

    def _set_label_match(self, label_match: Union[str, Type[AnyLabel]]):
        self.label_match = label_match

    def _run_node_match_and_transform(self, node: Node):
        if self.label_match in [AnyLabel, node.__primarylabel__]:
            self.transform_node(node=node)

    def transform_node(self, node: Node):
        raise NotImplementedError


class _RelationTransformerBase:
    def __init__(
        self,
        **kwargs,
    ):
        pass

    def _set_relation_type_match(
        self, relation_type_match: Union[str, Type[AnyLabel]] = AnyLabel
    ):
        self.relation_type_match = relation_type_match

    def _run_rel_match_and_transform(self, rel: Relation):
        if self.relation_type_match in [AnyRelation, rel.relation_type]:
            self.transform_rel(rel=rel)

    def transform_rel(self, rel: Relation):
        raise NotImplementedError


class CapitalizeLabels(_NodeTransformerBase):
    def transform(self, node: Node, parent_node: Node, child_data: Dict):
        node.labels = [label.capitalize() for label in node.labels]
        node.primary_label = node.primary_label.capitalize()


class OverridePrimaryLabel(_NodeTransformerBase):
    def __init__(self, value: str = None):
        """Override any generated labels with another string

        Args:
            label_match (Union[str, Type[AnyLabel]], optional): _description_. Defaults to AnyLabel.
            value (bool, optional): _description_. Defaults to None.
        """
        if not value:
            raise ValueError(f"Value must be a string. Got '{value}'")
        self.value = value

    def transform_node(self, node: Node):
        node.primary_label = self.value


class OverrideReliationType(_RelationTransformerBase):
    def __init__(self, value: str = None):
        if not value:
            raise ValueError(f"Value must be a string. Got '{value}'")
        self.value = value

    def transform_rel(self, rel: Relation):
        rel.relation_type = self.value


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


NODE_TRANSFORMERS = typing.Union[
    OverridePrimaryLabel, CapitalizeLabels, OverridePropertyName
]
REL_TRANSFORMERS = typing.Union[OverrideReliationType, OverridePropertyName]


class Transformer:
    class NodeTransformerMatcher:
        def _set_node_matcher(self, primary_label_match, label_match):
            self.primary_label_match = primary_label_match
            self.label_match = label_match

        def do(self, transform: NODE_TRANSFORMERS):
            transform._set_primary_label_match = self.label_match

    class RelTransformerMatcher:
        def _set_rel_matcher(self, relation_match):
            self.relation_match = relation_match

        def do(self, transform: REL_TRANSFORMERS):
            transform._set_primary_label_match = self.label_match

    @classmethod
    def match_node(
        cls,
        primary_label: Union[str, AnyLabel] = AnyLabel,
        label: Union[str, AnyLabel] = AnyLabel,
        relation_name: Union[str, AnyLabel] = AnyRelation,
    ) -> NodeTransformerMatcher:
        tm = Transformer.TransformerMatcher()
        tm._set_matcher(
            primary_label_match=primary_label,
            label_match=label,
            relation_match=relation_name,
        )
        return tm

    @classmethod
    def match_rel(
        cls,
        relation_name: Union[str, AnyRelation] = AnyRelation,
    ) -> RelTransformerMatcher:
        tm = Transformer.TransformerMatcher()
        tm._set_matcher(
            relation_match=relation_name,
        )
        return tm


Transformer.match_node(label="thing").do(OverridePropertyName())
Transformer.match_rel(relation_name="thing").do(OverrideReliationType("Thong"))
