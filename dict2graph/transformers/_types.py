import dict2graph.transformers.generic_transformers as _gentrans
import dict2graph.transformers.node_transformers as _nodetrans
import dict2graph.transformers.rel_transformers as _reltrans
import typing


class NodeTrans:
    OverridePropertyName = _gentrans.OverridePropertyName
    TypeCastProperty = _gentrans.TypeCastProperty
    OverrideLabel = _nodetrans.OverrideLabel
    CapitalizeLabels = _nodetrans.CapitalizeLabels
    BlankListHubNodes = _nodetrans.PopListHubNodes
    SetMergeProperties = _nodetrans.SetMergeProperties
    CreateNewMergePropertyFromHash = _nodetrans.CreateNewMergePropertyFromHash


class RelTrans:
    OverridePropertyName = _gentrans.OverridePropertyName
    TypeCastProperty = _gentrans.TypeCastProperty
    UppercaseRelationType = _reltrans.UppercaseRelationType
    OverrideReliationType = _reltrans.OverrideReliationType
