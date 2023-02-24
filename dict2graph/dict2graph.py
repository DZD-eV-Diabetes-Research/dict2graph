"""
Dict2graph

Transfer a python dict into a neo4j graph with the help of https://github.com/kaiserpreusse/graphio

Author: tim.bleimehl@helmholtz-muenchen.de

Source: https://git.connect.dzd-ev.de/dzdtools/pythonmodules/-/tree/master/dict2graph


Copyright 2019 German Center for Diabetes Research (DZD)
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import json
from typing import Union
from typing import List, Dict, Tuple, Type
from py2neo import Graph
from neo4j import Driver

from graphio import NodeSet, RelationshipSet
from dict2graph.node import Node
from dict2graph.relation import Relation
from dict2graph.transformers._base import (
    _NodeTransformerBase,
    _RelationTransformerBase,
)
from dict2graph.transformers import Transformer
from dict2graph.matcher_transformators_container import (
    MatcherTransformersContainer,
    MatcherTransformersContainerStack,
)


class Dict2graph:
    """
    The central class for dict2graph. Must be instanced to do get started and access the dict2graph api.

    **Class attributes**
    Dict2Graph has some basic options, packed into class attributes. You can change them after instantiating Dict2Graph.
    Usally you can go with the default values and dont need to change anything here.

    **example**

    ```python
    from dict2graph import Dict2graph

    d2g = Dict2graph()
    d2g.list_hub_additional_labels = ["Collection"]
    ```
    This will (later when parsing/transforming) add a label `Collection` to all list hubs


    Attributes:
        list_hub_additional_labels: Add these labels to list hub nodes. Defaults to `["ListHub"]`.

        list_item_additional_labels: Add these labels to list item nodes. Defaults to `["ListItem"]`.

        list_hub_id_property_name: A hub node has hash generated property based on its items.
            This is the name/key of the property. Defaults to `id`.

        list_item_relation_index_property_name: To preserve a json/dict list sequence,
            the index will be added to the relation from a list item node.
            This is the name/key of this property. Defaults to `_list_item_index`.

        simple_list_item_data_property_name: A list of basic types like `[1,2,3]` will get the label from its parents,
            but needs a default name/key for the value properties. Defaults to `_list_item_data`.

        root_node_default_labels: Will be used as root node label, if no root node label can be captured
            and no articial root node labels (via `Dict2Graph.parse(root_node_labels)`) are provided. Defaults to `["Dict2GraphRoot"]`.

        root_node_default_id_property_name: The root node will have a primary key based on a hash of the dict input. This is the name/key fir this property.

        empty_node_default_id_property_name: To prevent all empty nodes to merging together when doing
            `Dict2Graph.merge()`, they get an hash id by default.
            This is name/key for this property. Defaults to `id`.
    """

    # Replacement strings {ITEM_PRIMARY_LABEL} and {ITEM_LABELs} are available
    list_hub_additional_labels: List[str] = ["ListHub"]
    list_item_additional_labels: List[str] = ["ListItem"]
    list_hub_id_property_name: str = "id"
    list_item_relation_index_property_name: str = "_list_item_index"

    simple_list_item_data_property_name: str = "_list_item_data"
    root_node_default_labels: List[str] = ["Dict2GraphRoot"]
    root_node_default_id_property_name: str = "id"

    empty_node_default_id_property_name: str = "id"

    def __init__(
        self,
        create_ids_for_empty_nodes: bool = True,
        interpret_single_props_as_labels: bool = True,
    ):
        """
        Usage:
        ```python
        from dict2graph import Dict2graph

        d2g = Dict2Graph()
        ```

        Args:
            create_ids_for_empty_nodes (bool, optional): When input dicts results in empty 'hub' nodes, this will create artificially key properties based on the child data. The key will be deterministic . Defaults to True.
            interpret_single_props_as_labels (bool, optional): When having objects with a single property like `{"animal":{"name":"dog"}}` `animal` will be interpreted as label. If set to false "animal" will result in an extra Node. Defaults to True.
        """
        self.create_ids_for_empty_nodes = create_ids_for_empty_nodes

        # Todo: "interpret_single_props_as_labels" should be a regualr NodeTransformer instead of a class param
        self.interpret_single_props_as_labels = interpret_single_props_as_labels

        self._node_cache: List[Node] = []
        self._node_cache_feeder: List[Node] = []

        self._rel_cache: List[Relation] = []
        self._rel_cache_feeder: List[Node] = []
        self._nodeSets: Dict[Tuple, NodeSet] = {}
        self._relSets: Dict[Tuple, RelationshipSet] = {}
        self.matcher_and_node_transformers_stack = MatcherTransformersContainerStack([])
        self.matcher_and_rel_transformers_stack = MatcherTransformersContainerStack([])

    def add_transformation(
        self,
        transformer: Union[
            _NodeTransformerBase,
            _RelationTransformerBase,
            List[Union[_NodeTransformerBase, _RelationTransformerBase]],
        ],
    ):
        """Add one or a list of [`Transformers`](/use_transformers.md) to the Dict2Graph instance.
        Transformers can re-model your graph befor writing it to a Neo4j database.

        **usage**:
        ```python
        from dict2graph import Dict2graph, Transformer, NodeTrans

        d2g = Dict2Graph()
        d2g.add_transformation(
            Transformer.match_nodes("article").do(NodeTrans.OverrideLabel("book"))
        )
        ```

        Args:
            transformer (Union[ _NodeTransformerBase, _RelationTransformerBase, List[Union[_NodeTransformerBase, _RelationTransformerBase]], ]): A list or single instance of a Transformer

        """

        if isinstance(transformer, list):
            for trans in transformer:
                self.add_transformation(trans)
            return
        if self._get_transformer_class(transformer) == _NodeTransformerBase:
            self.add_node_transformation(transformer)

        elif self._get_transformer_class(transformer) == _RelationTransformerBase:
            self.add_relation_transformation(transformer)
        else:
            raise ValueError(
                f"Expected transformer of subclass '{_NodeTransformerBase}' or '{_RelationTransformerBase}', got '{transformer.__class__}' (child of '{transformer.__class__.__bases__}')"
            )

    def _get_transformer_class(
        self, transformer: Union[_NodeTransformerBase, _RelationTransformerBase]
    ) -> Union[Type[_NodeTransformerBase], type[_RelationTransformerBase]]:
        if issubclass(transformer.__class__, _NodeTransformerBase) and issubclass(
            transformer.__class__, _RelationTransformerBase
        ):
            # We got a generic transformer. we have to look at the matcher to determine the transformer type.
            if isinstance(transformer.matcher, Transformer.RelTransformerMatcher):
                return _RelationTransformerBase
            elif isinstance(transformer.matcher, Transformer.NodeTransformerMatcher):
                return _NodeTransformerBase
        elif issubclass(transformer.__class__, _NodeTransformerBase):
            return _NodeTransformerBase
        elif issubclass(transformer.__class__, _RelationTransformerBase):
            return _RelationTransformerBase

    def add_node_transformation(
        self, transformer: Union[_NodeTransformerBase, List[_NodeTransformerBase]]
    ):
        if isinstance(transformer, list):
            for trans in transformer:
                self.add_node_transformation(trans)
            return
        if transformer.matcher is None:
            raise ValueError(f"No matcher added to {transformer}")
        if not issubclass(transformer.__class__, _NodeTransformerBase):
            raise ValueError(
                f"Expected transformer of subclass '{_NodeTransformerBase}', got '{transformer.__class__}' (child of '{transformer.__class__.__bases__}').\nMaybe you wanted to use function `Dict2graph.add_relation_transformation()` instead of `add_node_transformation`?"
            )
        elif transformer.matcher.__class__ != Transformer.NodeTransformerMatcher:
            raise ValueError(
                f"Expected transformer matcher of class '{Transformer.NodeTransformerMatcher}', got '{transformer.matcher.__class__}'.\nMaybe you accidentally added a relationship matcher instead of a node matcher (`match_nodes()` vs. `match_rels()`) while using `Dict2graph.add_node_transformation()`?"
            )
        else:
            transformer.d2g = self
            self.matcher_and_node_transformers_stack.add_container(transformer)

    def add_relation_transformation(
        self,
        transformer: Union[_RelationTransformerBase, List[_RelationTransformerBase]],
    ):
        if isinstance(transformer, list):
            for trans in transformer:
                self.add_relation_transformation(trans)
            return
        elif not issubclass(transformer.__class__, _RelationTransformerBase):
            raise ValueError(
                f"Expected transformer of subclass '{_RelationTransformerBase}', got '{transformer.__class__}' (child of '{transformer.__class__.__bases__}').\nMaybe you wanted to use function `Dict2graph.add_node_transformation()` instead of `add_relation_transformation`?"
            )
        elif transformer.matcher.__class__ != Transformer.RelTransformerMatcher:
            raise ValueError(
                f"Expected transformer matcher of class '{Transformer.RelTransformerMatcher}', got '{transformer.matcher.__class__}'.\nMaybe you accidentally added a node matcher instead of a relationship matcher (`match_rels()` vs. `match_nodes()`) while using `Dict2graph.add_relation_transformation()`?"
            )
        else:
            self.matcher_and_rel_transformers_stack.add_container(transformer)

    def parse(
        self, data: Dict, root_node_labels: Union[str, List[str]] = None
    ) -> "Dict2graph":
        """Submit your actual data (as dict) to dict2graph. The data will be transformed instantly but not yet pushed to your Neo4j database.
        It will land in a dict2graph internal cache. You can run multiple `Dict2Graph.parse()` passes before pushing the data to your Neo4j database.

        **usage**
        ```python
        from dict2graph import Dict2graph
        # provide any dict that is json compatible (basic typed values and keys)
        data = {"myDictKey":"myValue"}
        d2g = Dict2Graph()
        d2g.parse(data)
        ```
        Args:
            data (Dict): Your data as a dict with only basic typed valued, as a rule of thumb it should be json compatible.
                If you have json string you may use the build-in python module "json" in before(`json.loads(your_data_as_json)`)
            root_node_labels (Union[str, List[str]], optional): Dict2graph tries to determine a sensible root node.
                But that is not possible in many cases and dict2graph
                will return to the default label in `Dict2graph.root_node_default_labels`.
                with `Dict2graph.parse(root_node_labels)` you can force a root label.
                Defaults to None.

        Raises:
            ValueError: When data is not parsable.

        Returns:
            Dict2graph: Returns itself to be able to chains commands like `dict2graph_ints.parse(data).parse(data2).create(NEO4J_DRIVER)`
        """
        if root_node_labels is None:
            if isinstance(data, dict) and len(data.keys()) == 1:
                # we only have one key and therefore only one Node on the top-/root-level. We dont need a root Node to connect the toplevels nodes.
                root_node_labels = [list(data.keys())[0]]
                data = data[root_node_labels[0]]
            else:
                root_node_labels = self.root_node_default_labels
        if isinstance(root_node_labels, str):
            root_node_labels = [root_node_labels]

        if isinstance(data, str):
            data_obj = json.loads(data)
        else:
            data_obj = data
        if not isinstance(data_obj, dict) and not isinstance(data_obj, list):
            raise ValueError(
                "Expected json compatible object like a dict or list. got {}".format(
                    type(data_obj).__name__
                )
            )
        if isinstance(data_obj, dict):

            root_node = self._parse_traverse_dict_fragment(
                labels=root_node_labels, data=data_obj, parent_node=None
            )

        elif isinstance(data_obj, list):
            root_node = self._parse_traverse_list_fragment(
                labels=root_node_labels, data=data_obj, parent_node=None
            )
        self._prepare_root_node(root_node)

        self._flush_cache()
        return self

    def merge(self, graph: Union[Graph, Driver]):
        """Push the data to a Neo4h database, with a merge operation.

        **usage**
        ```python
        from dict2graph import Dict2graph
        from neo4j import GraphDatabase
        # provide any dict that is json compatible (basic typed values and keys)
        data = {"car":{"wheels":"4"}}
        data2 = {"car":{"wheels":"4"}}
        d2g = Dict2Graph()
        d2g.parse(data)
        d2g.parse(dat2)
        d2g.merge(GraphDatabase.driver("neo4j://localhost"))
        ```

        Will result in one node `(:car{wheels:4})` because the two datasets where merged (based on same labels and properties).

        Args:
            graph (Union[Graph, Driver]): A [`neo4j.GraphDatabase` instance](https://neo4j.com/docs/api/python-driver/current/)
                or a [`py2neo.Graph` instance](https://py2neo.org/2021.1/workflow.html#graph-objects)
        """
        for nodes in self._nodeSets.values():
            nodes.merge(graph)
        for rels in self._relSets.values():
            rels.merge(graph)

    def create(self, graph: Union[Graph, Driver]):
        """Push the data to a Neo4h database, with a create operation.

        **usage**
        ```python
        from dict2graph import Dict2graph
        from neo4j import GraphDatabase
        # provide any dict that is json compatible (basic typed values and keys)
        data = {"car":{"wheels":"4"}}
        data2 = {"car":{"wheels":"4"}}
        d2g = Dict2Graph()
        d2g.parse(data)
        d2g.parse(dat2)
        d2g.create(GraphDatabase.driver("neo4j://localhost"))
        ```

         Will result in two nodes `(:car{wheels:4})`.

        Args:
            graph (Union[Graph, Driver]): A [Neo4j python driver instance](https://neo4j.com/docs/api/python-driver/current/)
                or a [`py2neo.Graph` instance](https://py2neo.org/2021.1/workflow.html#graph-objects)
        """
        for nodes in self._nodeSets.values():
            nodes.create(graph)
        for rels in self._relSets.values():
            rels.create(graph)

    def _prepare_root_node(self, node: Node):
        node.is_root_node = True
        if len(node.keys()) == 0:
            node[self.root_node_default_id_property_name] = node.get_hash(
                include_children_data=True
            )

            node.merge_property_keys = [self.root_node_default_id_property_name]

    def _parse_traverse_dict_fragment(
        self, data: Dict, parent_node: Node, labels: List[str] = None
    ) -> Node:
        new_node = Node(labels=labels, source_data=data, parent_node=parent_node)
        new_child_nodes: List[Node] = []
        new_rels: List[Relation] = []
        for key, val in data.items():
            if self._is_basic_attribute_type(val):
                # value is a simple type. attach as property to node
                new_node[key] = val
            else:
                # value is dict or list in itself and therefore one or multiple child nodes
                r = None
                n = None
                if isinstance(val, dict):
                    if self._is_named_obj(val):
                        n = self._parse_traverse_dict_fragment(
                            labels=list(val.keys()),
                            data=val[list(val.keys())[0]],
                            parent_node=new_node,
                        )
                        r = Relation(start_node=new_node, end_node=n, relation_type=key)
                    else:
                        n = self._parse_traverse_dict_fragment(
                            labels=[key], data=val, parent_node=new_node
                        )
                elif isinstance(val, list):
                    n = self._parse_traverse_list_fragment(
                        labels=[key], data=val, parent_node=new_node
                    )
                elif val is not None:
                    raise ValueError(
                        f"Expected dict val to be a None, basic type, a list or a dict. Got `{type(val)}` for key '{key}' value '{val}'"
                    )
                if n is not None:
                    new_child_nodes.append(n)
                    if r is None:
                        r = Relation(
                            start_node=new_node,
                            end_node=n,
                        )
                    new_rels.append(r)
        self._node_cache.append(new_node)
        self._rel_cache.extend(new_rels)
        return new_node

    def _parse_traverse_list_fragment(
        self, labels: List[str], parent_node: Node, data: Dict
    ) -> Node:

        # create/set list root node. this is the node on which the list items will attach to
        # the parent_node is the default root

        list_root_hub_node: Node = Node(
            labels=labels,
            source_data=data,
            parent_node=parent_node,
        )
        self._set_list_root_hub_node_labels(list_root_hub_node)
        list_root_hub_node.is_list_list_hub = True
        self._node_cache.append(list_root_hub_node)
        # parse nodes
        new_list_item_nodes: List[Node] = []
        for index, obj in enumerate(data):
            if self._is_basic_attribute_type(obj):
                n = Node(labels, source_data=obj, parent_node=list_root_hub_node)

                n[self.simple_list_item_data_property_name] = obj
                self._node_cache.append(n)
                new_list_item_nodes.append(n)
            elif self._is_named_obj(obj):
                obj_label = list(obj.keys())[0]
                obj_data = obj[obj_label]
                new_list_item_nodes.append(
                    self._parse_traverse_dict_fragment(
                        labels=obj_label, data=obj_data, parent_node=list_root_hub_node
                    )
                )
            elif isinstance(obj, dict):
                new_list_item_nodes.append(
                    self._parse_traverse_dict_fragment(
                        labels=labels, data=obj, parent_node=list_root_hub_node
                    )
                )
            elif isinstance(obj, list):
                new_list_item_nodes.append(
                    self._parse_traverse_list_fragment(
                        labels=labels, data=obj, parent_node=list_root_hub_node
                    )
                )

        # create relations to list root node
        child_ids: List[str] = []

        for index, node in enumerate(new_list_item_nodes):
            if node is None:
                continue
            self._set_list_item_node_labels(node)
            node.is_list_list_item = True
            child_ids.append(node.id)
            r = Relation(
                start_node=list_root_hub_node,
                end_node=node,
            )

            r[self.list_item_relation_index_property_name] = index
            node.parent_node = list_root_hub_node
            self._rel_cache.append(r)
            #

        list_root_hub_node[
            self.list_hub_id_property_name
        ] = list_root_hub_node.get_hash(include_children_data=True)
        list_root_hub_node.merge_property_keys = [self.list_hub_id_property_name]

        return list_root_hub_node

    def _is_empty(self, val):
        if not val:
            return True
        if isinstance(val, str) and val.upper() in ["", "NULL"]:
            return True
        return False

    def _is_basic_attribute_type(self, val):
        if isinstance(val, (str, int, float, bool)):
            return True
        else:
            return False

    def _is_named_obj(self, data: Dict):
        """If an object is a one-keyd dict on the first layer and there is a dict behind this key,
        we determine that this one key is the label/type and the inner dict are the props

        Args:
            data (List): _description_

        Returns:
            _type_: _description_
        """
        # {"person":{"name":"tom","lastname":"schilling"}} -> we know its a person
        # {"name":"tom","lastname":"schilling"} -> Could be a person or a lama
        # {"client":{"name":"tom","lastname":"schilling"},"cert":"yes"} -> -> Could be a person or a computer
        if not self.interpret_single_props_as_labels:
            return False
        if (
            isinstance(data, dict)
            and len(data.keys()) == 1
            and isinstance(data[list(data.keys())[0]], dict)
        ):
            return True
        return False

    def _set_list_root_hub_node_labels(self, node: Node) -> str:
        addi_labels = [
            l.replace("{{ITEM_PRIMARY_LABEL}}", node.primary_label)
            for l in self.list_hub_additional_labels
        ]
        addi_labels = [
            l.replace("{{ITEM_LABELS}}", "_".join(node.primary_label))
            for l in addi_labels
        ]

        node.labels = node.labels + addi_labels

    def _set_list_item_node_labels(self, node: Node) -> str:
        node.labels = node.labels + self.list_item_additional_labels

    def _manifest_node_from_cache(self, cached_node: Node):
        node_set: NodeSet = self._get_or_create_nodeSet(cached_node)
        if self.create_ids_for_empty_nodes and cached_node.id is None:
            cached_node[
                self.empty_node_default_id_property_name
            ] = cached_node.get_hash(include_children_data=True)
            cached_node.merge_property_keys = [self.empty_node_default_id_property_name]
        node_set.add_node(cached_node)

    def _get_or_create_nodeSet(self, node: Node) -> NodeSet:
        node_type_fingerprint = (
            frozenset(node.labels),
            frozenset(node.merge_property_keys),
        )
        if node_type_fingerprint not in self._nodeSets:
            self._nodeSets[node_type_fingerprint] = NodeSet(
                labels=node.labels,
                merge_keys=node.merge_property_keys
                if node.merge_property_keys
                else list(node.keys()),
            )
        return self._nodeSets[node_type_fingerprint]

    def _manifest_rel_from_cache(self, cached_relation: Relation):
        rel_set: RelationshipSet = self._get_or_create_relSet(cached_relation)
        rel_set.add_relationship(
            start_node_properties=cached_relation.start_node,
            end_node_properties=cached_relation.end_node,
            properties=cached_relation,
        )

    def _get_or_create_relSet(self, relation: Relation) -> RelationshipSet:
        rel_id = (
            frozenset(relation.start_node.labels),
            frozenset(relation.start_node.merge_property_keys),
            relation.relation_type,
            frozenset(relation.end_node.labels),
            frozenset(relation.end_node.merge_property_keys),
        )

        if rel_id not in self._relSets:
            self._relSets[rel_id] = RelationshipSet(
                rel_type=relation.relation_type,
                start_node_labels=relation.start_node.labels,
                end_node_labels=relation.end_node.labels,
                start_node_properties=relation.start_node.merge_property_keys,
                end_node_properties=relation.end_node.merge_property_keys,
            )
        return self._relSets[rel_id]

    def add_node_to_cache(self, node: Node):
        """Add a new [dict2graph.Node][] to the dict2graph cache.
        This method is only relevant for [`Transformers`](/use_transformers).

        You will propably only need it of you create [custom Transformers](/diy_transformer).

        Args:
            node (Node): The [dict2graph.Node][] to add.
        """
        self._node_cache_feeder.append(node)

    def add_rel_to_cache(self, rel: Relation):
        """Add a new [dict2graph.Relation][] to the dict2graph cache.
        This method is only relevant for [`Transformers`](/use_transformers).

        You will propably only need it of you create [custom Transformers](/diy_transformer).

        Args:
            node (Node): The [dict2graph.Relation][] to add.
        """
        self._rel_cache_feeder.append(rel)

    def _flush_cache(self):
        self._feed_cache_with_new_nodes_and_rels()
        self._run_transformations()
        for node in self._node_cache:
            if not node.deleted:
                self._manifest_node_from_cache(node)
        for rel in self._rel_cache:
            if not rel.deleted:
                self._manifest_rel_from_cache(rel)
        self._node_cache = []
        self._rel_cache = []

    def _run_transformations(self):
        for (
            matcher_trans_node_container
        ) in self.matcher_and_node_transformers_stack.containers:
            for node in self._node_cache:
                if matcher_trans_node_container.matcher._match(node):
                    for trans in matcher_trans_node_container.transformers:
                        trans._run_custom_node_match_and_transform(node)
            self._feed_cache_with_new_nodes_and_rels()

        for (
            matcher_trans_rel_container
        ) in self.matcher_and_rel_transformers_stack.containers:
            for rel in self._rel_cache:
                if matcher_trans_rel_container.matcher._match(rel):
                    for trans in matcher_trans_rel_container.transformers:
                        trans._run_custom_rel_match_and_transform(rel)

            self._feed_cache_with_new_nodes_and_rels()

    def _feed_cache_with_new_nodes_and_rels(self):
        self._node_cache.extend(self._node_cache_feeder)
        self._node_cache_feeder = []
        self._rel_cache.extend(self._rel_cache_feeder)
        self._rel_cache_feeder = []
