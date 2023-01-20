import dict2graph.transformers.generic_transformers as _gentrans
import dict2graph.transformers.node_transformers as _nodetrans
import dict2graph.transformers.rel_transformers as _reltrans
import typing


class NodeTrans:
    OverridePropertyName = _gentrans.OverridePropertyName
    TypeCastProperty = _gentrans.TypeCastProperty
    RemoveProperty = _gentrans.RemoveProperty
    OverrideLabel = _nodetrans.OverrideLabel
    RemoveLabel = _nodetrans.RemoveLabel
    AddLabel = _nodetrans.AddLabel
    CapitalizeLabels = _nodetrans.CapitalizeLabels
    PopListHubNodes = _nodetrans.PopListHubNodes
    SetMergeProperties = _nodetrans.SetMergeProperties
    CreateNewMergePropertyFromHash = _nodetrans.CreateNewMergePropertyFromHash
    RemoveEmptyListRootNodes = _nodetrans.RemoveEmptyListRootNodes
    CreateHubbing = _nodetrans.CreateHubbing
    RemoveListItemLabels = _nodetrans.RemoveListItemLabels
    OutsourcePropertiesToNewNode = _nodetrans.OutsourcePropertiesToNewNode
    RemoveNodesWithNoProps = _nodetrans.RemoveNodesWithNoProps
    RemoveNodesWithOnlyEmptyProps = _nodetrans.RemoveNodesWithOnlyEmptyProps


class RelTrans:
    OverridePropertyName = _gentrans.OverridePropertyName
    TypeCastProperty = _gentrans.TypeCastProperty
    RemoveProperty = _gentrans.RemoveProperty
    UppercaseRelationType = _reltrans.UppercaseRelationType
    OverrideReliationType = _reltrans.OverrideReliationType
