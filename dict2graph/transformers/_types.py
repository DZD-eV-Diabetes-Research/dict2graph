import dict2graph.transformers.generic_transformers as _gentrans
import dict2graph.transformers.node_transformers as _nodetrans
import dict2graph.transformers.rel_transformers as _reltrans
import typing


class NodeTrans:
    OverridePropertyName = _gentrans.OverridePropertyName
    TypeCastProperty = _gentrans.TypeCastProperty
    RemoveProperty = _gentrans.RemoveProperty
    AddProperty = _gentrans.AddProperty
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
    RemoveNode = _nodetrans.RemoveNode
    RemoveNodesWithNoProps = _nodetrans.RemoveNodesWithNoProps
    RemoveNodesWithOnlyEmptyProps = _nodetrans.RemoveNodesWithOnlyEmptyProps
    PopNode = _nodetrans.PopNode
    MergeChildNodes = _nodetrans.MergeChildNodes
    OutsourcePropertiesToRelationship = _nodetrans.OutsourcePropertiesToRelationship
    ConvertLabelToProp = _nodetrans.ConvertLabelToProp
    EscapeInvalidNamesForNeo4JCompatibility = (
        _gentrans.EscapeInvalidNamesForNeo4JCompatibility
    )
    SanitizeInvalidNamesForNeo4JCompatibility = (
        _gentrans.SanitizeInvalidNamesForNeo4JCompatibility
    )


class RelTrans:
    OverridePropertyName = _gentrans.OverridePropertyName
    TypeCastProperty = _gentrans.TypeCastProperty
    RemoveProperty = _gentrans.RemoveProperty
    AddProperty = _gentrans.AddProperty
    UppercaseRelationType = _reltrans.UppercaseRelationType
    OverrideReliationType = _reltrans.OverrideReliationType
    FlipNodes = _reltrans.FlipNodes
    EscapeInvalidNamesForNeo4JCompatibility = (
        _gentrans.EscapeInvalidNamesForNeo4JCompatibility
    )
    SanitizeInvalidNamesForNeo4JCompatibility = (
        _gentrans.SanitizeInvalidNamesForNeo4JCompatibility
    )
