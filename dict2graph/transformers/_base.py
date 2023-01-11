from typing import TYPE_CHECKING, Callable, Union, Dict, Type, Any, Tuple, Literal, List
from dict2graph.node import Node
from dict2graph.relation import Relation


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

    def _set_label_match(self, label_match: Union[str, Type[AnyLabel]]):
        self.label_match = label_match

    def _run_node_match_and_transform(self, node: Node):
        if (
            self.label_match in node.labels or self.label_match in [None, AnyLabel]
        ) and self.custom_node_match(node):
            try:
                self.transform_node(node=node)
            except:
                print(f"Transformation failed for node '{node}'")
                raise

    def custom_node_match(self, node: Node) -> bool:
        return True

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
        if self.relation_type_match in [
            AnyRelation,
            rel.relation_type,
        ] and self.custom_rel_match(rel):
            try:
                self.transform_rel(rel=rel)
            except:
                print(f"Transformation failed for rel '{rel}'")
                raise

    def custom_rel_match(self, rel: Relation) -> bool:
        return True

    def transform_rel(self, rel: Relation):
        raise NotImplementedError


class Transformer:
    class NodeTransformerMatcher:
        def _set_node_matcher(self, label_match):
            self.label_match = label_match

        def do(self, transform: _NodeTransformerBase) -> _NodeTransformerBase:
            transform._set_label_match(self.label_match)
            return transform

    class RelTransformerMatcher:
        def _set_rel_matcher(self, relation_type_match):
            self.relation_type_match = relation_type_match

        def do(self, transform: _RelationTransformerBase) -> _RelationTransformerBase:
            transform._set_relation_type_match(self.relation_type_match)
            return transform

    @classmethod
    def match_node(
        cls,
        label: Union[str, AnyLabel] = AnyLabel,
    ) -> NodeTransformerMatcher:
        tm = Transformer.NodeTransformerMatcher()
        tm._set_node_matcher(
            label_match=label,
        )
        return tm

    @classmethod
    def match_rel(
        cls,
        relation_name: Union[str, AnyRelation] = AnyRelation,
    ) -> RelTransformerMatcher:
        tm = Transformer.RelTransformerMatcher()
        tm._set_rel_matcher(
            relation_type_match=relation_name,
        )
        return tm
