from typing import Union, List
from dataclasses import dataclass
from dict2graph.transformers._base import (
    Transformer,
    _NodeTransformerBase,
    _RelationTransformerBase,
)


@dataclass
class MatcherTransformersContainer:
    matcher: Union[
        Transformer.NodeTransformerMatcher, Transformer.RelTransformerMatcher
    ]
    transformers: Union[List[_NodeTransformerBase], List[_RelationTransformerBase]]


@dataclass
class MatcherTransformersContainerStack:
    containers: List[MatcherTransformersContainer]

    def add_container(
        self,
        transformers: Union[
            _NodeTransformerBase,
            _RelationTransformerBase,
            List[_NodeTransformerBase],
            List[_RelationTransformerBase],
        ],
    ):
        if not isinstance(transformers, list):
            transformers = [transformers]
        for transformer in transformers:
            matcher: Union[
                Transformer.NodeTransformerMatcher, Transformer.RelTransformerMatcher
            ] = transformer.matcher
            transformer_assigned_to_container: bool = False
            for existing_container in self.containers:
                if existing_container.matcher == matcher:
                    existing_container.transformers.append(transformer)
                    transformer_assigned_to_container = True
                    break
            if not transformer_assigned_to_container:
                self.containers.append(
                    MatcherTransformersContainer(
                        matcher=transformer.matcher, transformers=[transformer]
                    )
                )
