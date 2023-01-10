from dict2graph.transformers._base import AnyLabel, AnyRelation
import dict2graph.transformers.generic_transformers as _gentrans
import dict2graph.transformers.node_transformers as _nodetrans
import dict2graph.transformers.rel_transformers as _reltrans
import typing


class NodeTrans:
    OverridePropertyName = _gentrans.OverridePropertyName
    OverrideLabel = _nodetrans.OverrideLabel
    CapitalizeLabels = _nodetrans.CapitalizeLabels
    BlankListHubNodes = _nodetrans.PopListHubNodes


class RelTrans:
    UppercaseRelationType = _reltrans.UppercaseRelationType
    OverrideReliationType = _reltrans.OverrideReliationType
    OverridePropertyName = _reltrans.OverridePropertyName


NODE_TRANSFORMER_TYPE = typing.Union[
    _gentrans.OverridePropertyName,
    _nodetrans.OverrideLabel,
    _nodetrans.CapitalizeLabels,
    _nodetrans.PopListHubNodes,
]
REL_TRANSFORMER_TYPE = typing.Union[
    _gentrans.OverridePropertyName,
    _reltrans.OverrideReliationType,
    _reltrans.UppercaseRelationType,
]
