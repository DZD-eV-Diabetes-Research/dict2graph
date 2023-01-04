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
import hashlib
import collections
from typing import Callable, Union
import uuid
import graphio
from collections import defaultdict
from typing import List, Dict, Tuple, Literal
from py2neo import Graph
from neo4j import Driver

from graphio import NodeSet, RelationshipSet


class Dict2graph(object):
    def __init__(self):
        self.config_bool_capitalize_labels: bool = False
        self.config_dict_label_override: Dict[str, Union[str, Dict[str, str]]] = {}
        self.config_dict_reltype_override: Dict[str, Union[str, Dict[str, str]]] = {}
        self.config_dict_property_name_override: Dict[str, Dict[str, str]] = {}
        self.config_dict_property_casting: Dict[str, Dict[str, str]] = {}
        self.config_dict_primarykey_generated_hashed_attrs_by_label: Dict[
            str, Union[str, List[str]]
        ] = {}
        self.config_dict_primarykey_attr_by_label: Dict[str, List] = {}
        self.config_list_default_primarykeys: List[str] = ["id", "_id"]
        self.config_str_primarykey_generated_attr_name: str = "_id"
        self.config_dict_hubbing: Dict[str, Dict[str, Union[str, List[str]]]] = {}
        self.config_str_collection_hub_label: str = "{LIST_MEMBER_LABEL}Collection"
        self.config_list_collection_hub_extra_labels: List[str] = ["CollectionHub"]
        self.config_bool_collection_hub_attach_list_members_label: bool = False
        self.config_bool_collection_hub_only_when_len_min_2: bool = False
        self.config_dict_in_between_node: Dict[str, Dict[str, str]] = {}
        self.config_dict_concat_list_attr: Dict[str, Dict[str, str]] = {}

        self.config_func_node_post_modifier: Callable[
            ["Dict2graph.Node"], "Dict2graph.Node"
        ] = None
        self.config_func_node_pre_modifier: Callable[
            ["Dict2graph.Node"], "Dict2graph.Node"
        ] = None
        self.config_func_label_name_generator_func: Callable[
            ["Dict2graph.Node"], str
        ] = None
        self.config_func_custom_relation_name_generator: Callable[
            ["Dict2graph.Node", "Dict2graph.Node", dict], str
        ] = None

        self.config_dict_create_merge_depending_scheme: Dict[
            Literal["create", "merge"], List[str]
        ] = {"create": [], "merge": []}
        self.config_dict_property_to_extra_node: Dict[
            str, Union[List[str], Dict[str : Literal["copy", "move"]]]
        ] = {}

        self.config_dict_interfold_json_attr: Dict[str, Dict[str, str]] = None

        self.config_dict_attr_name_to_reltype_instead_of_label: Dict[str, str] = {}
        self.config_dict_node_prop_to_rel_prop: Dict[str, Dict[str, List[str]]] = {}

        self.config_list_allowlist_collection_hubs: List[str] = []
        self.config_list_allowlist_reltypes: List[str] = []
        self.config_list_allowlist_nodes: List[str] = []
        self.config_dict_allowlist_props: Dict[str, List[str]] = {}

        self.config_list_blocklist_collection_hubs: List[str] = []
        self.config_list_blocklist_reltypes: List[str] = []
        self.config_list_blocklist_nodes: List[str] = []
        self.config_dict_blocklist_props: Dict[str, List[str]] = {}

        self.config_list_deconstruction_limit_nodes: List[str] = []
        self.config_dict_flip_nodes: Dict[str, str] = {}

        self.config_list_throw_away_from_nodes: List[str] = []
        self.config_list_throw_away_nodes_with_empty_key_attr: List[str] = []
        self.config_list_throw_away_nodes_with_no_or_empty_attrs: List[str] = []

        self.relationshipSets: Dict[str, RelationshipSet] = {}
        self.nodeSets: Dict[str, NodeSet] = {}

        self.disable_config_sanity_check: bool = False
        self._blocked_reltypes: List[str] = []
        self._hash_alg = hashlib.md5
        self._debug: bool = False

        self._current_nodes: List[graphio.NodeSet] = None
        self._current_rels: List[graphio.RelationshipSet] = None

    def _config_sanity_check(self):
        if self.config_list_allowlist_reltypes and self.config_list_blocklist_reltypes:
            raise ValueError(
                "Can not mix config_list_allowlist_reltypes and config_list_blocklist_reltypes. At least one must contain None or an empty list."
            )
        if self.config_list_blocklist_nodes and self.config_list_allowlist_nodes:
            raise ValueError(
                "Can not mix config_list_blocklist_nodes and config_list_allowlist_nodes. At least one must contain None or an empty list."
            )
        if self.config_dict_allowlist_props and self.config_dict_blocklist_props:
            raise ValueError(
                "Can not mix config_dict_allowlist_props and config_dict_blocklist_props. At least one must contain None or an empty list."
            )
        if (
            self.config_list_allowlist_collection_hubs
            and self.config_list_blocklist_collection_hubs
        ):
            raise ValueError(
                "Can not mix config_list_allowlist_collection_hubs and config_list_blocklist_collection_hubs. At least one must contain None or an empty list."
            )
        if self.config_dict_primarykey_generated_hashed_attrs_by_label:
            for (
                label,
                config,
            ) in self.config_dict_primarykey_generated_hashed_attrs_by_label.items():
                if isinstance(config, str):
                    if config not in [
                        "AllAttributes",
                        "InnerContent",
                        "OuterContent",
                        "AllContent",
                        None,
                    ]:
                        raise ValueError(
                            "Invalid mode for 'config_dict_primarykey_generated_hashed_attrs_by_label' on label {}. For usage info have a look at 'https://git.connect.dzd-ev.de/dzdpythonmodules/dict2graph/-/blob/master/README.md#config_dict_primarykey_generated_hashed_attrs_by_label'".format(
                                label
                            )
                        )

    def parse(
        self, data: Dict, parent_label_name: str = None, instant_save: bool = True
    ) -> Tuple[List[graphio.NodeSet], List[graphio.RelationshipSet]]:
        """[summary]

        Args:
            data (Dict): Any Dictory that should be transformed into graphio Node-/RelationShipSets objects
            parent_label_name (str, optional): If the dict has no wrapping object (e.g. just a list) you can define a parent/anchor node name. Defaults to None.
            instant_save (bool, optional):  Defaults to True.
                                           If True: Resulting Node/RelationShip Sets will be saved to Dict2graph.nodeSets and Dict2graph.relationshipSets which mixes them up with before parsed data
                                           if False: Returns resulting Node-/RelationShipSets. This is helpful if you dont to mix up multiple parsing runs, You can manually save via Dict2graph.save()

        Raises:
            ValueError: [description]

        Returns:
            Tuple[List[graphio.NodeSet], List[graphio.RelationshipSet]]: Return two values; a list of generated graphio.NodeSet and a list of generated graphio.RelationshipSet
        """
        self._current_nodes = defaultdict(list)
        self._current_rels = defaultdict(list)
        if not self.disable_config_sanity_check:
            self._config_sanity_check()
        if isinstance(data, str):
            j = json.loads(data)
        else:
            j = data
        if not isinstance(j, dict) and not isinstance(j, list):
            raise ValueError(
                "Expected json string, dict or list. got {}".format(type(j).__name__)
            )
        self._jsondict2subgraph(parent_label_name, j)
        if instant_save:
            self.save()
        return self._current_nodes, self._current_rels

    def save(self):
        for nodeset_labels, node_properties in self._current_nodes.items():
            self.nodeSets[nodeset_labels].add_nodes(list_of_properties=node_properties)

        for relationshipset_identifier, relationships in self._current_rels.items():
            for rel in relationships:
                self.relationshipSets[relationshipset_identifier].add_relationship(
                    **rel
                )

    def get_nodesets(self):
        for nodeset in self.nodeSets:
            yield nodeset

    def get_relationshipsets(self):
        for relationshipSets in self.relationshipSets:
            yield relationshipSets

    def create_indexes(self, graph: Union[Graph, Driver]):
        for rels in self.relationshipSets.values():
            rels.create_index(graph)
        for nodes in self.nodeSets.values():
            nodes.create_index(graph)

    def create(self, graph: Union[Graph, Driver]):
        for nodes in self.nodeSets.values():
            nodes.create(graph)
        for rels in self.relationshipSets.values():
            rels.create(graph)

    def merge(self, graph: Union[Graph, Driver]):
        for nodes in self.nodeSets.values():
            nodes.merge(graph)
        for rels in self.relationshipSets.values():
            rels.merge(graph)

    def to_dict(self):
        """This is a debug function for showing all nodeset with all nodes and all relationshipset with all relations. Only use this on small datasets, using this on large sized datasets will propaply eat all your memory

        Returns:
            dict: {"nodesSets": [graphio.objects.nodeset.NodeSet], "relationshipSets": [
                graphio.objects.nodeset.RelationshipSet]}
        """
        nodesets = []
        for nodes in self.nodeSets.values():
            nodesets.append(
                {
                    "labels": nodes.labels,
                    "primary_keys": nodes.merge_keys,
                    "nodes": [dict(node) for node in nodes.nodes],
                }
            )
        relsets = []
        for rels in self.relationshipSets.values():
            relsets.append(
                {
                    "rel_type": rels.rel_type,
                    "start_node_labels": list(rels.start_node_labels),
                    "end_node_labels": list(rels.end_node_labels),
                    "rels": [rel.to_dict() for rel in rels.relationships],
                }
            )
        return {"nodesSets": nodesets, "relationshipSets": relsets}

    def clear(self):
        for ns in self.nodeSets.values():
            ns.nodes = []
        for rs in self.relationshipSets.values():
            rs.relationships = []

    def _is_basic_type(self, val):
        if isinstance(val, (str, int, float, bool)):
            return True
        else:
            return False

    def _is_empty(self, val):
        if not val:
            return True
        if isinstance(val, str) and val.upper() in ["", "NULL", "NONE"]:
            return True
        return False

    def _get_relation_name(self, node, child_node, relation_props):
        rel_name = None
        if callable(self.config_func_custom_relation_name_generator):
            rel_name = self.config_func_custom_relation_name_generator(
                node, child_node, relation_props
            )
        if rel_name is None:
            child_node_name = child_node.__primarylabel__.upper()
            node_name = node.__primarylabel__.upper()
            rel_name = "{}_HAS_{}".format(
                node_name,
                child_node_name,
            )
            if hasattr(node, "override_reltype"):
                if child_node.__primarylabel__ in node.override_reltype:
                    rel_name = node.override_reltype[
                        child_node.__primarylabel__
                    ].upper()
        if rel_name in self.config_dict_reltype_override:
            rel_name = self.config_dict_reltype_override[rel_name]
        return rel_name

    def _flip_nodes(self, node, child_node, parent_node, relation_props):
        # flip nodes according to self.config_dict_flip_nodes
        if (
            parent_node is not None
            and node.__primarylabel__ in self.config_dict_flip_nodes.keys()
            and child_node.__primarylabel__
            in self.config_dict_flip_nodes[node.__primarylabel__]
        ):
            self._add_relation(parent_node, child_node, relation_props)
            self._add_relation(child_node, node, relation_props)
            return True
        if (
            child_node.__primarylabel__ in self.config_dict_flip_nodes.keys()
            and node.__primarylabel__
            not in self.config_dict_flip_nodes[child_node.__primarylabel__]
        ):
            # supress relation because of flip according to self.config_dict_flip_nodes
            return True
        return False

    def _create_hubbing(self, node, child_node, relation_props):
        node_label = node.__primarylabel__
        child_node_label = child_node.__primarylabel__
        for hub_root_label, hub_definitons in self.config_dict_hubbing.items():

            if not isinstance(hub_definitons, list):
                hub_defs = [hub_definitons]
            else:
                hub_defs = hub_definitons
            # iterate all hub definitions
            for hub_def in hub_defs:
                # look if caller wants us to create a hub

                if (
                    node_label in hub_def["hub_member_labels"]
                    or node_label == hub_root_label
                ) and child_node_label in hub_def["hub_member_labels"]:

                    hubs = []
                    # do we allready have created a hub?

                    if (
                        hasattr(child_node, "_hub_member_of")
                        and child_node._hub_member_of
                    ):
                        hubs = child_node._hub_member_of
                    if not hubs:
                        # initalize hub
                        hubs = [
                            Dict2graph.Node(
                                d2g=self,
                                source_data_dict_attribute_name=hub_def["hub_label"],
                            )
                        ]
                        hubs[0]._members = [child_node]
                        hubs[0]._member_relation_props = []
                        hubs[0]._edge_node = child_node
                        # save hub to child node
                        child_node._hub_member_of = hubs

                    if node_label != hub_root_label:
                        if hasattr(node, "_hub_member_of"):
                            # # Nono, this generated a bug, because hubs will be compared with __eq__ by key/values not by memory address.
                            # # As hubs have no ID yet here, all are "equal" and will disappear here. only the first in list will be kept.
                            # node._hub_member_of = list(
                            #    set(node._hub_member_of) | set(hubs)
                            # )

                            # This makes more sense and is easier :).  duplicates will be removed when merging data the to db anyway as the hubs will have the same hash
                            node._hub_member_of.extend(hubs)
                        else:
                            node._hub_member_of = hubs
                        for hub in hubs:
                            hub._member_relation_props.append(relation_props)
                            hub._members.append(node)
                    if (
                        hub_root_label == node_label
                    ):  # we are at the root node of the hub. lets produce the (root)-(hub)-[(members)] subgraph
                        id_sources_info: str = None
                        hub_id: str = None
                        for hub in hubs:

                            if (
                                hub_def["hub_id_from"] == "lead"
                            ):  # when 'lead'-hubbing, we build the hub id from the root and fill nodes (nodes that are not on the edge of a node chain)
                                self._hash_alg

                                hub_id_str = node.get_id()
                                if self._debug:
                                    id_sources_info = node.to_string(True)
                                # if there is a end node (which is not a leading node) we remove it from the id building list
                                if len(hub._members) == len(
                                    hub_def["hub_member_labels"]
                                ):
                                    key_members = hub._members[:-1]
                                else:
                                    key_members = hub._members

                                for member in key_members:  # loop fill nodes
                                    if self._debug:
                                        id_sources_info += "\n" + member.to_string(True)
                                        hub.add_prop("_hubbing_type", "lead_hub")

                                    hub_id_str += member.get_id()

                                hub_id = self._hash_alg(hub_id_str.encode()).hexdigest()
                            elif (
                                hub_def["hub_id_from"] == "edge"
                            ):  # when 'edge'-hubbing, we build the hub id from the root and end node
                                self._hash_alg
                                hub_id_str = node.get_id()
                                if self._debug:
                                    id_sources_info = node.to_string(True)
                                if len(hub._members) == len(
                                    hub_def["hub_member_labels"]
                                ):  # only if there is a endnode existent
                                    hub_id_str += hub._edge_node.get_id()
                                    if self._debug:
                                        id_sources_info += (
                                            "\n" + hub._edge_node.to_string(True)
                                        )
                                        hub.add_prop("_hubbing_type", "edge-hub")

                                hub_id = self._hash_alg(hub_id_str.encode()).hexdigest()
                            if self._debug:
                                hub.add_prop("_hashed_from", id_sources_info)
                            hub.add_prop(
                                prop_name=self.config_str_primarykey_generated_attr_name,
                                prop_value=hub_id,
                                force_add_to_primary_key=True,
                            )
                            self._add_node(hub)
                            # connect members to hub

                            for index, member in enumerate(hub._members):
                                if len(hub._member_relation_props) > index:
                                    props = hub._member_relation_props[index - 1]
                                else:
                                    props = relation_props
                                self._create_relation(
                                    node=hub, child_node=member, relation_props=props
                                )
                            # connect hub to root
                            self._create_relation(
                                node=node, child_node=hub, relation_props=relation_props
                            )
                    return True
        return False

    def _create_relation(
        self, node: "Dict2graph.Node", child_node: "Dict2graph.Node", relation_props={}
    ):
        """
        self.config_dict_node_prop_to_rel_prop = {
            "NAME_TO_NAME": {"from": ["propname"], "to": []}
        }
        """
        node_labels = frozenset(node.labels)
        child_node_labels = frozenset(child_node.labels)
        # labels = ":".join(node.labels) + "|" + ":".join(child_node.labels)
        relationshipset_identifier = (
            node_labels,
            child_node_labels,
        )
        if (
            hasattr(node, "override_reltype")
            and child_node.__primarylabel__ in node.override_reltype
        ):
            relationshipset_identifier = (
                node_labels,
                child_node_labels,
                frozenset(node.override_reltype[child_node.__primarylabel__]),
            )
        rel_name = self._get_relation_name(node, child_node, relation_props)
        # Create new relationshipset if necessary
        if not relationshipset_identifier in self.relationshipSets:

            if (
                self.config_list_blocklist_reltypes
                and rel_name in self.config_list_blocklist_reltypes
            ):
                self._blocked_reltypes.append(relationshipset_identifier)
            elif (
                self.config_list_allowlist_reltypes
                and rel_name not in self.config_list_allowlist_reltypes
            ):
                self._blocked_reltypes.append(relationshipset_identifier)
            else:
                self.relationshipSets[relationshipset_identifier] = RelationshipSet(
                    rel_type=rel_name,
                    start_node_labels=list(node_labels),
                    end_node_labels=list(child_node_labels),
                    start_node_properties=node.get_merge_keys(
                        all_values_if_no_primary_keys=True
                    ),
                    end_node_properties=child_node.get_merge_keys(
                        all_values_if_no_primary_keys=True
                    ),
                )

        # move property from node to relation if configured so by caller
        for _node in [node, child_node]:
            if _node.__primarylabel__ in self.config_dict_node_prop_to_rel_prop:
                for _prop_name, _rel_names in self.config_dict_node_prop_to_rel_prop[
                    _node.__primarylabel__
                ].items():
                    if rel_name in _rel_names:
                        if _prop_name in _node:
                            relation_props[_prop_name] = _node.pop(_prop_name, None)

        # add relationship to rel-set if not blocked by caller config
        if not relationshipset_identifier in self._blocked_reltypes:
            # Temp safe relationship
            self._current_rels[relationshipset_identifier].append(
                {
                    "start_node_properties": node.get_merge_props(
                        all_values_if_no_primary_keys=True
                    ),
                    "end_node_properties": child_node.get_merge_props(
                        all_values_if_no_primary_keys=True
                    ),
                    "properties": relation_props,
                }
            )

    def _add_relation(
        self,
        node: "Dict2graph.Node",
        child_node: "Dict2graph.Node",
        relation_props={},
        parent_node=None,
    ):

        if node is None or child_node is None:
            return  # skip creation of relation if one node of the relation is empty
        if child_node.__primarylabel__ in self.config_list_throw_away_from_nodes:
            return
        if self._create_hubbing(node, child_node, relation_props):
            # Skip if relation will be hubbed (according to config_dict_hubbing)
            return
        if self._flip_nodes(node, child_node, parent_node, relation_props):
            # Skip if relation will be flipped (according to config_dict_flip_nodes)
            return

        if hasattr(node, "_thrown_away") or hasattr(child_node, "_thrown_away"):
            # node is ditched in _add_node() according to config_list_throw_away_nodes_with_empty_key_attr
            # we dont need this relations
            return

        if (
            (
                self.config_list_blocklist_nodes
                and node.__primarylabel__ in self.config_list_blocklist_nodes
            )
            or (
                self.config_list_allowlist_nodes
                and node.__primarylabel__ not in self.config_list_allowlist_nodes
            )
            or (
                self.config_list_blocklist_nodes
                and child_node.__primarylabel__ in self.config_list_blocklist_nodes
            )
            or (
                self.config_list_allowlist_nodes
                and child_node.__primarylabel__ not in self.config_list_allowlist_nodes
            )
        ):
            return  # Skip if one of the nodes is missing in allowlist or existent in blocklist

        if node.__primarylabel__ in self.config_dict_in_between_node:
            rel_name = self._get_relation_name(node, child_node, relation_props)
            if rel_name in self.config_dict_in_between_node[node.__primarylabel__]:
                # caller wants an etxra node in this relationship
                extra_node_label = self.config_dict_in_between_node[
                    node.__primarylabel__
                ][rel_name]
                extra_node = Dict2graph(extra_node_label)
                extra_node.__primarylabel__ = extra_node_label
                self._generate_id_attr(extra_node, dict(child_node), parent_node)
                self._add_node(extra_node)
                self._add_relation(node, extra_node)
                self._add_relation(extra_node, child_node)
                return  # relation is replaced by creating an in between node and two additonal relation

        self._create_relation(
            node=node,
            child_node=child_node,
            relation_props=relation_props,
        )

    def _add_node(self, node):
        if callable(self.config_func_node_post_modifier):
            node = self.config_func_node_post_modifier(node)
        if (
            self.config_list_blocklist_nodes
            and node.__primarylabel__ in self.config_list_blocklist_nodes
        ) or (
            self.config_list_allowlist_nodes
            and node.__primarylabel__ not in self.config_list_allowlist_nodes
        ):
            return

        # check if we need to throw away nodes with empty primary keys
        if (
            node.__primarylabel__
            in self.config_list_throw_away_nodes_with_empty_key_attr
        ):
            node_merge_vals = node.get_merge_values()
            if len(node_merge_vals) == 0 or node_merge_vals.count(None) == len(
                node_merge_vals
            ):
                # primarykeys/mergekeys are missing or none . Throw away according to caller config in config_list_throw_away_nodes_with_empty_key_attr
                node._thrown_away = True
                return

        if (
            node.__primarylabel__
            in self.config_list_throw_away_nodes_with_no_or_empty_attrs
        ):
            node_vals = node.get_values()
            if len(node_vals) == 0 or node_vals.count(None) == len(node_vals):
                # Dict2graph has no props or all props are None.Throw away according to caller config in config_list_throw_away_nodes_with_empty_attrs
                node._thrown_away = True
                return

        # create nodeSet if necessary
        labels = frozenset(node.labels)
        if not labels in self.nodeSets:
            # get primary keys
            self.nodeSets[labels] = NodeSet(
                list(labels),
                merge_keys=node.get_merge_keys(all_values_if_no_primary_keys=True),
            )
        # Temp save node
        self._current_nodes[labels].append(node.get_props())

    def _adjust_property_name(self, label, property_name):
        if label in self.config_dict_property_name_override:
            if property_name in self.config_dict_property_name_override[label]:
                return self.config_dict_property_name_override[label][property_name]
        return property_name

    def _get_hub_node_label_name(self, member_label_name):
        label = self.config_str_collection_hub_label.format(
            LIST_MEMBER_LABEL=member_label_name
        )
        if label in self.config_dict_label_override:
            label = self.config_dict_label_override[label]
        return label

    def _create_collection_hub_node(self, member_label_name, data_dict):
        hub_node_label = self._get_hub_node_label_name(member_label_name)
        if (
            (
                # allowlist mode: only create hub when hub name ist listed in config_list_allowlist_collection_hubs
                self.config_list_allowlist_collection_hubs
                and hub_node_label in self.config_list_allowlist_collection_hubs
            )
            or (
                # blocklist mode: only create hub when name is not in config_list_blocklist_collection_hubs
                self.config_list_blocklist_collection_hubs
                and hub_node_label not in self.config_list_blocklist_collection_hubs
            )
        ) or (
            # open mode: always create a collection hub
            not self.config_list_blocklist_collection_hubs
            and not self.config_list_allowlist_collection_hubs
        ):
            hub_node = Dict2graph.Node(
                d2g=self,
                source_data_dict_attribute_name=hub_node_label,
                parent_node=None,
                subordinate_data=None,
                id=self._hash_alg(json.dumps(data_dict).encode()).hexdigest(),
            )
            hub_node._is_collectionhub = True
            hub_node.__primarykeys__ = ["id"]
            for lbl in self.config_list_collection_hub_extra_labels:
                hub_node.add_label(lbl)
            if self.config_bool_collection_hub_attach_list_members_label:
                hub_node.add_label(member_label_name)
            return hub_node

    def _flatten_dict(self, d, sep="-"):
        obj = collections.OrderedDict()

        def recurse(t, parent_key=""):
            if isinstance(t, list):
                for i in range(len(t)):
                    recurse(t[i], parent_key + sep + str(i) if parent_key else str(i))
            elif isinstance(t, dict):
                for k, v in t.items():
                    recurse(v, parent_key + sep + k if parent_key else k)
            else:
                obj[parent_key] = t

        recurse(d)

        return obj

    def _fold_json_attrs(self, key, val):

        if (
            self.config_dict_interfold_json_attr
            and key in self.config_dict_interfold_json_attr
        ):
            folding_rules = self.config_dict_interfold_json_attr[key]
            for folding_attr, folding_param in folding_rules.items():
                if not folding_attr in val:
                    continue
                # default params
                # transfer all attrs
                child_content = val[folding_attr]
                # do not combine parent and child attrs
                if child_content is not None:
                    combine_names = False
                    if folding_param is not None:
                        if "combine_attr_names" in folding_param:
                            combine_names = folding_param["combine_attr_names"]
                        if "attrs" in folding_param:
                            child_content = {
                                key: val[key]
                                for key in val.keys()
                                if key in folding_attr["attrs"]
                            }

                    if not isinstance(child_content, list):
                        child_content = [child_content]
                    for index, child_content_item in enumerate(child_content):
                        for (
                            folding_child_attr_key,
                            folding_child_attr_val,
                        ) in child_content_item.items():
                            index_str = ""
                            if combine_names:
                                if index > 0:
                                    index_str = "_" + str(index) + "_"
                                new_attr_name = "{}{}{}".format(
                                    folding_attr, index_str, folding_child_attr_key
                                )
                            else:
                                if index > 0:
                                    index_str = str(index) + "_"
                                new_attr_name = index_str + folding_child_attr_key
                            val[new_attr_name] = folding_child_attr_val
                del val[folding_attr]
            return val

    def _jsondict2subgraph(
        self, label_name: str, data_dict, parent_node=None
    ) -> "Dict2graph.Node":
        """[summary]

        Arguments:
            self {[type]} -- [description]
            Dict2graph {[type]} -- [description]
        Returns:
            Node -- The generated top anchor node from the subgraph
        """
        node = None
        label_name_adjusted: str = None
        if self._is_empty(data_dict):
            return None
        if label_name is not None:
            node = Dict2graph.Node(
                d2g=self,
                source_data_dict_attribute_name=label_name,
                parent_node=parent_node,
                subordinate_data=data_dict,
            )
            label_name_adjusted = node.__primarylabel__
        if callable(self.config_func_node_pre_modifier):
            node = self.config_func_node_pre_modifier(node)

        # check if caller has set a parsing stop at this node
        if (
            label_name is not None
            and label_name_adjusted in self.config_list_throw_away_from_nodes
        ):
            # we are supposed to stop parsing this dict branch further. lets go back
            return

        if (
            label_name is not None
            and label_name_adjusted in self.config_list_deconstruction_limit_nodes
        ):
            data_dict = self._flatten_dict(data_dict)

        if self._is_basic_type(data_dict):
            # we just have a simple str,int,float value that we turn into an node
            node.add_prop(
                prop_name=label_name_adjusted,
                prop_value=data_dict,
                force_add_to_primary_key=True,
            )
            node.generate_primary_hash_key(do_not_raise=True)

        elif label_name is None and self._is_basic_type(data_dict):
            # Propably only a json value (aka json_data) was provided but not an attribute name (aka label_name)
            raise ValueError("Not a valid json: '{}'".format(data_dict))

        elif isinstance(data_dict, list):

            if (
                self.config_bool_collection_hub_only_when_len_min_2
                and len(data_dict) == 1
            ):
                node = self._jsondict2subgraph(label_name, data_dict[0], parent_node)

            else:
                # create collection hub for list children, if applicable
                # the id of the new Collection/Hub Dict2graph, is based on the list content hashed

                node_hub = self._create_collection_hub_node(
                    member_label_name=node.__primarylabel__,
                    data_dict=data_dict,
                )
                if node_hub is not None:
                    # if a collection hub was created we connect following list members to the collection hub
                    node = node_hub

                elif parent_node is not None:
                    # As we have a list we will create multiple instances of the nodes
                    # these will be connected to the parent node (because we dont have a hub)
                    node = parent_node
                for index, list_item in enumerate(data_dict):
                    # create nodes based on the list members and connect to them to collecion hub or parent node

                    if (
                        isinstance(list_item, dict)
                        and len(list(list_item.keys())) == 1
                        and isinstance(list(list_item.values())[0], dict)
                        and 1 == 2
                    ):
                        #  we have a list of nested objects e.g. [{"person":{"name":"John"}}]
                        # we do not create nodes based on the parent attribute as label, but rather based on the object names itself.
                        # DISABLED (by 1 == 2)
                        # ToDo: create config variable for this behavior
                        list_item_node = self._jsondict2subgraph(
                            list(list_item.keys())[0], list(list_item.values())[0], node
                        )
                    else:
                        # we have a list of objects e.g. [{"name":"John"}]
                        list_item_node = self._jsondict2subgraph(
                            label_name, list_item, node
                        )

                    if list_item_node is not None:
                        if node is not None and list_item_node != node:
                            if (
                                label_name
                                in self.config_dict_attr_name_to_reltype_instead_of_label
                            ):
                                override_val = {
                                    self.config_dict_attr_name_to_reltype_instead_of_label[
                                        label_name
                                    ]: label_name
                                }
                                node.override_reltype = override_val
                            self._add_relation(
                                node,
                                list_item_node,
                                {"position": index},
                                parent_node,
                            )
            # node = self._generate_id_attr(node, json_data, parent_node)
        elif isinstance(data_dict, dict) and label_name is not None:
            # We have a json object. Iterate through attributes and cast them into graph objects
            attrs_to_child_nodes = []
            self._fold_json_attrs(label_name, data_dict)
            for key, val in data_dict.items():

                if (
                    self.config_dict_property_to_extra_node is not None
                    and label_name_adjusted in self.config_dict_property_to_extra_node
                    and key
                    in self.config_dict_property_to_extra_node[label_name_adjusted]
                ):
                    # Move an property of that node to an extra child node, labeled with the property name
                    attrs_to_child_nodes.append((key, val))
                    if (
                        isinstance(
                            self.config_dict_property_to_extra_node[
                                label_name_adjusted
                            ],
                            dict,
                        )
                        and self.config_dict_property_to_extra_node[
                            label_name_adjusted
                        ][key].upper()
                        == "COPY"
                    ):
                        # Copy value instead of moving it
                        node.add_prop(key, val)
                elif self._is_basic_type(val):
                    # add json attr as prop to node
                    node.add_prop(key, val)
                elif (
                    isinstance(val, list)
                    and label_name_adjusted in self.config_dict_concat_list_attr
                    and key in self.config_dict_concat_list_attr[label_name_adjusted]
                ):
                    # aggregate list and add it as prop
                    node.add_prop(
                        key,
                        self.config_dict_concat_list_attr[label_name_adjusted][
                            key
                        ].join(val),
                    )

                else:

                    attrs_to_child_nodes.append((key, val))
            node.generate_primary_hash_key(do_not_raise=True)

            for attr_to_cn in attrs_to_child_nodes:
                # create child nodes and connect them to current node
                child_node = self._jsondict2subgraph(attr_to_cn[0], attr_to_cn[1], node)

                if child_node is not None and child_node != node:
                    if (
                        label_name
                        in self.config_dict_attr_name_to_reltype_instead_of_label
                    ):
                        node.override_reltype = {
                            self.config_dict_attr_name_to_reltype_instead_of_label[
                                label_name
                            ]: label_name
                        }
                    self._add_relation(node, child_node, {}, parent_node)
        elif isinstance(data_dict, dict) and label_name is None:
            # we skip translating outermost layer into nodes and just transform the json content
            node = None
            for key, val in data_dict.items():
                self._jsondict2subgraph(key, val, None)
        if node is not None:
            if node != parent_node:
                self._add_node(node)
                return node
            else:
                return parent_node

    class Node(dict):
        """Dict2graph class

        container class for node labels and properties

        """

        __primarykeys__ = None
        __primarylabel__ = None
        _origin_dict_attribute_name = None
        labels = None
        _d2g = None
        id_cache = None

        def __init__(
            self,
            d2g: "Dict2graph",
            source_data_dict_attribute_name: str,
            parent_node: "Dict2graph.Node" = None,
            subordinate_data=None,
            **kwargs
        ):

            self._d2g = d2g
            self.update(**kwargs)
            self._origin_dict_attribute_name = source_data_dict_attribute_name
            self.labels = []
            self.set_primary_label(source_data_dict_attribute_name)
            self._fetch_primary_key_names_from_config()
            self._hash_id_dirty = None
            self._subordinate_data = subordinate_data
            self._parent_node = parent_node

        def __getitem__(self, key):
            return dict.get(self, key)

        def __setitem__(self, key, value):
            if value is None:
                try:
                    dict.__delitem__(self, key)
                    self._hash_id_dirty = True
                except KeyError:
                    pass
            else:
                dict.__setitem__(self, key, value)
                self._hash_id_dirty = True

        def __eq__(self, other):
            return (
                self.__class__ == other.__class__
                and self.labels == other.labels
                and dict(self) == dict(other)
            )

        def __hash__(self):
            if self.__primarykeys__:
                return hash(frozenset(self.labels + list(self.get_merge_props.items())))
            return hash(frozenset(self.labels + list(self.items())))

        def __repr__(self):
            return "(" + ":".join(self.labels) + str(dict(self)) + ")"

        def __str__(self):
            if self.get_merge_props():
                return "(" + ":".join(self.labels) + str(self.get_merge_props()) + ")"
            else:
                return "(" + ":".join(self.labels) + str(id(self)) + ")"

        def to_string(self, show_all_props=False):
            if show_all_props:
                return self.__repr__()
            else:
                return self.__str__()

        def get_merge_props(self, all_values_if_no_primary_keys=False) -> dict:
            props = {k: v for k, v in self.items() if k in self.__primarykeys__}
            if all_values_if_no_primary_keys:
                return props or {
                    k: v
                    for k, v in self.items()
                    if k not in self.__blocked_as_primarykeys
                }
            else:
                return props

        def get_merge_keys(self, all_values_if_no_primary_keys=False) -> list:
            if all_values_if_no_primary_keys:
                return self.__primarykeys__ or [
                    attr
                    for attr in self.keys()
                    if attr not in self.__blocked_as_primarykeys
                ]
            else:
                return self.__primarykeys__

        def get_merge_values(self, all_values_if_no_primary_keys=False) -> list:
            vals = [v for k, v in self.items() if k in self.__primarykeys__]
            if all_values_if_no_primary_keys:
                return vals or [
                    v for v, k in self.items() if k not in self.__blocked_as_primarykeys
                ]
            else:
                return vals

        def get_props(self) -> dict:
            return self

        def get_keys(self) -> list:
            return list(self.keys())

        def get_values(self) -> list:
            return list(self.values())

        def _fetch_primary_key_names_from_config(self):
            if self.__primarylabel__ in self._d2g.config_dict_node_prop_to_rel_prop:
                # some attr should not taken into account, for generating a hash key.
                # e.g. some attrs will be removed later or can change when creating relations.
                # atm this only includes attrs that are removed by config_dict_node_prop_to_rel_prop, which will me moved to a relations

                self.__blocked_as_primarykeys = list(
                    self._d2g.config_dict_node_prop_to_rel_prop.get(
                        self.__primarylabel__
                    ).keys()
                )
            else:
                self.__blocked_as_primarykeys = []

            self.__primarykeys__ = []
            if self.__primarylabel__ in self._d2g.config_dict_primarykey_attr_by_label:
                self.__primarykeys__ = self._d2g.config_dict_primarykey_attr_by_label[
                    self.__primarylabel__
                ]
                return self.__primarykeys__
            if (
                self.__primarylabel__
                in self._d2g.config_dict_primarykey_generated_hashed_attrs_by_label
            ):
                self.__primarykeys__ = [
                    self._d2g.config_str_primarykey_generated_attr_name
                ]
                return self.__primarykeys__

        def get_id(self) -> str:
            """
            Similar purpose as pythons hash() function but deterministic. Will create the same result on all architectures and python versions
            """
            if self._id_cache is not None:
                # we have a cached id
                return self._id_cache
            if (
                self._d2g.config_str_primarykey_generated_attr_name in self
                and self[self._d2g.config_str_primarykey_generated_attr_name]
                is not None
            ):
                # we can reuse the merge key hash
                self._id_cache = self[
                    self._d2g.config_str_primarykey_generated_attr_name
                ]
                return self._id_cache
            # we need to create a new hash
            pk_vals = self.get_merge_props()
            if not pk_vals or all(val is not None for val in pk_vals):
                # pk list empty or all pk values are still empty, this will not create a usefull hash
                # we backup to take all props into account
                # print("GETID_PK", self.__primarylabel__, dict(self))
                pk_vals = dict(self)
            self._id_cache = self._d2g._hash_alg(
                str(json.dumps(pk_vals, sort_keys=True) + "".join(self.labels)).encode()
            ).hexdigest()
            return self._id_cache

        def generate_primary_hash_key(
            self,
            do_not_raise=False,
        ):
            if (
                self.__primarylabel__
                in self._d2g.config_dict_primarykey_generated_hashed_attrs_by_label
            ):
                """
                * `AllAttributes` - Generate an ID based on nodes properties
                * `InnerContent` - Generate an ID based on the Nodes properties and its children
                * `OuterContent` - Generate an ID based on the Nodes properties and its parent node
                * `AllContent` - Generate an ID based on the parent and children
                * [] - A list of node properties which should be taken into account to generate an ID
                """
                hash_mode = (
                    self._d2g.config_dict_primarykey_generated_hashed_attrs_by_label[
                        self.__primarylabel__
                    ]
                )
                children_id: str = None
                parent_id: str = None
                id_val: str = None
                if hash_mode is not None:

                    if isinstance(hash_mode, list):
                        # we have static set of properties to take into account, configured by caller
                        hash_keys = hash_mode
                    else:

                        # caller has not configured which properties we to take into account. we need to take all into account
                        hash_keys = [
                            key
                            for key in self.keys()
                            if key not in self.__blocked_as_primarykeys
                        ]
                    id_hash = self._d2g._hash_alg()

                    for key, val in self.items():
                        if key in hash_keys:
                            id_hash.update(str(val).encode())
                    attr_id = id_hash.hexdigest()
                    if hash_mode == "AllAttributes" or isinstance(hash_mode, list):
                        id_val = attr_id

                    if hash_mode in ("InnerContent", "AllContent"):
                        # based on children data
                        children_id = self._d2g._hash_alg(
                            json.dumps(self._subordinate_data).encode()
                        ).hexdigest()

                    if hash_mode in ("OuterContent", "AllContent"):
                        if self._parent_node is not None:
                            parent_id = self._parent_node.get_id()
                        else:
                            parent_id = ""

                    if hash_mode == "AllAttributes":
                        id_val = attr_id
                    elif hash_mode == "AllContent":
                        id_val = self._d2g._hash_alg(
                            (attr_id + children_id + parent_id).encode()
                        ).hexdigest()
                    elif hash_mode == "OuterContent":
                        id_val = self._d2g._hash_alg(
                            (attr_id + parent_id).encode()
                        ).hexdigest()
                    elif hash_mode == "InnerContent":
                        id_val = self._d2g._hash_alg(
                            (attr_id + children_id).encode()
                        ).hexdigest()
                else:
                    # Random id
                    id_val = uuid.uuid4().hex
                self.add_prop(
                    prop_name=self._d2g.config_str_primarykey_generated_attr_name,
                    prop_value=id_val,
                    force_add_to_primary_key=True,
                )
                self._hash_id_dirty = False
                return id_val
            else:
                if do_not_raise:
                    return None
                else:
                    raise ValueError(
                        "'(:{})' Nodes are not configured for hash ids. Use `config_dict_primarykey_generated_hashed_attrs_by_label` to enable hash ids for this node type."
                    )

        def add_label(self, label):
            self._id_cache = None
            self._hash_id_dirty = True
            self.labels.append(label)
            # remove double labels
            self.labels = list(set(self.labels))

        def clear_labels(self):
            self._id_cache = None
            self._hash_id_dirty = True
            self.labels = []

        def add_prop(self, prop_name, prop_value, force_add_to_primary_key=False):

            if (
                self.__primarylabel__ in self._d2g.config_dict_property_name_override
                and prop_name
                in self._d2g.config_dict_property_name_override[self.__primarylabel__]
            ):
                prop_name_adjusted = self._d2g.config_dict_property_name_override[
                    self.__primarylabel__
                ][prop_name]
            else:
                prop_name_adjusted = prop_name

            # when block- or allow-list mode is enabled, skip property if it is blocklisted or not allowlisted
            if (
                self.__primarylabel__ in self._d2g.config_dict_blocklist_props
                and prop_name_adjusted
                in self._d2g.config_dict_blocklist_props[self.__primarylabel__]
            ) or (
                self.__primarylabel__ in self._d2g.config_dict_allowlist_props
                and prop_name_adjusted
                not in self._d2g.config_dict_allowlist_props[self.__primarylabel__]
            ):
                return
            # empty id cache as entity will change
            self._id_cache = None
            # cast the value type if desired by caller
            if (
                self.__primarylabel__ in self._d2g.config_dict_property_casting
                and prop_name_adjusted
                in self._d2g.config_dict_property_casting[self.__primarylabel__]
            ):
                self[prop_name_adjusted] = self._d2g.config_dict_property_casting[
                    self.__primarylabel__
                ][prop_name_adjusted](prop_value)
            else:
                # Set the value
                self[prop_name_adjusted] = prop_value

            # determine if key is a primary key
            if force_add_to_primary_key:
                if self.__primarykeys__:
                    self.__primarykeys__ = [prop_name_adjusted]
                else:
                    self.__primarykeys__.append(prop_name_adjusted)
            elif not force_add_to_primary_key:
                if (
                    # Is key a default primary key for all nodes and there is not allready another primary key
                    prop_name_adjusted in self._d2g.config_list_default_primarykeys
                    and self.__primarykeys__
                ) or (
                    # If Key is configured as primarykey for this specific label
                    self.__primarylabel__
                    in self._d2g.config_dict_primarykey_attr_by_label
                    and prop_name_adjusted
                    in self._d2g.config_dict_primarykey_attr_by_label[
                        self.__primarylabel__
                    ]
                ):
                    if self.__primarykeys__:
                        self.__primarykeys__ = [prop_name_adjusted]
                    else:
                        self.__primarykeys__.append(prop_name_adjusted)

        def set_primary_label(self, source_data_dict_attribute_name) -> str:
            label_name = source_data_dict_attribute_name
            if callable(self._d2g.config_func_label_name_generator_func):
                custom_name = self._d2g.config_func_label_name_generator_func(
                    label_name
                )
                if custom_name is not None:
                    self.__primarylabel__ = custom_name
                    self.add_label(custom_name)
                    return custom_name
            label_name_adjusted = label_name

            if (
                label_name
                in self._d2g.config_dict_attr_name_to_reltype_instead_of_label
            ):
                label_name_adjusted = (
                    self._d2g.config_dict_attr_name_to_reltype_instead_of_label[
                        label_name
                    ]
                )
            extra_props = None
            if label_name in self._d2g.config_dict_label_override:
                label_name_override_config = self._d2g.config_dict_label_override[
                    label_name
                ]
                if isinstance(label_name_override_config, str):
                    label_name_adjusted = label_name_override_config
                elif isinstance(label_name_override_config, dict):
                    label_name_adjusted = list(label_name_override_config.keys())[0]
                    # temp save extra props as configured by caller later as we dont have the final primary label yet
                    extra_props = list(label_name_override_config.values())[0]

            label_name_adjusted = (
                label_name_adjusted.capitalize()
                if self._d2g.config_bool_capitalize_labels
                else label_name_adjusted
            )
            self.add_label(label_name_adjusted)
            self.__primarylabel__ = label_name_adjusted
            if extra_props:
                for extra_prop, extra_val in extra_props.items():
                    self.add_prop(prop_name=extra_prop, prop_value=extra_val)
            return label_name_adjusted
