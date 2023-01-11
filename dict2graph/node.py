from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict, Tuple, Union, FrozenSet
import json
import uuid
import hashlib

if TYPE_CHECKING:
    from dict2graph import Dict2graph
    from dict2graph.relation import Relation


class Node(dict):
    def __init__(
        self,
        labels: FrozenSet[str],
        source_data: Union[Dict, List, str, int],
        parent_node: Node,
        **kwargs,
    ):
        if isinstance(labels, str):
            labels = [labels]
        self.labels = frozenset(labels) if labels else frozenset()
        self.primary_label: str = labels[0] if self.labels else None
        self.parent_node: Node = parent_node
        self.source_data: Dict = source_data
        self._merge_property_keys: List[str] = None
        self.update(**kwargs)
        self.relations: List[Relation] = []
        self.is_list_collection_hub: bool = False
        self.is_root_node: bool = False
        self.deleted = False

    @property
    def merge_property_keys(self) -> List[str]:
        return (
            self._merge_property_keys
            if self._merge_property_keys
            else list(self.keys())
        )

    @merge_property_keys.setter
    def merge_property_keys(self, primary_props: List[str]):
        self._merge_property_keys = primary_props

    @property
    def id(self):
        if self.merge_property_keys and len(self.merge_property_keys) == 1:
            return self[self.merge_property_keys[0]]
        else:
            return hashlib.md5(
                bytes(
                    json.dumps([self[key] for key in self.merge_property_keys]),
                    "utf-8",
                ),
            ).hexdigest()

    def get_hash(
        self,
        include_merge_properties: bool = True,
        include_other_properties: bool = True,
        include_parent_properties: bool = False,
        include_children_properties: bool = False,
        include_children_data: bool = False,
    ) -> str:
        hash_source_values = []
        if include_merge_properties:
            hash_source_values.extend(
                [
                    {key: val}
                    for key, val in self.items()
                    if key in self.merge_property_keys
                ]
            )
        if include_other_properties:
            hash_source_values.extend(
                [
                    {key: val}
                    for key, val in self.items()
                    if key not in self.merge_property_keys
                ]
            )
        if include_parent_properties and self.parent_node is not None:
            hash_source_values.extend(
                [
                    {key: val}
                    for key, val in self.parent_node.items()
                    if key not in self.parent_node.merge_property_keys
                ]
            )
        if include_children_properties:
            for child in self.child_nodes:
                hash_source_values.extend(
                    [
                        {key: val}
                        for key, val in child.items()
                        if key not in child.merge_property_keys
                    ]
                )
        if include_children_data:
            for child in self.child_nodes:
                hash_source_values.append(child.source_data)

        return hashlib.md5(
            bytes(
                json.dumps(hash_source_values),
                "utf-8",
            ),
        ).hexdigest()

    @property
    def outgoing_relations(self) -> List[Relation]:
        return [rel for rel in self.relations if rel.start_node == self]

    @property
    def incoming_relations(self) -> List[Relation]:
        return [rel for rel in self.relations if rel.end_node == self]

    @property
    def child_nodes(self) -> List[Node]:
        return [rel.end_node for rel in self.outgoing_relations]

    def __str__(self):

        return f"({':'.join(self.labels)}{super().__str__()})"


class Node_old(dict):
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
        d2g: Dict2graph,
        source_data_dict_attribute_name: str,
        parent_node: Node = None,
        subordinate_data=None,
        **kwargs,
    ):

        self._d2g = d2g
        self.update(**kwargs)
        self._origin_dict_attribute_name = source_data_dict_attribute_name
        self.labels: List[str] = []
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
                k: v for k, v in self.items() if k not in self.__blocked_as_primarykeys
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
            self.__primarykeys__ = [self._d2g.config_str_primarykey_generated_attr_name]
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
            and self[self._d2g.config_str_primarykey_generated_attr_name] is not None
        ):
            # we can reuse the merge key hash
            self._id_cache = self[self._d2g.config_str_primarykey_generated_attr_name]
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
                self.__primarylabel__ in self._d2g.config_dict_primarykey_attr_by_label
                and prop_name_adjusted
                in self._d2g.config_dict_primarykey_attr_by_label[self.__primarylabel__]
            ):
                if self.__primarykeys__:
                    self.__primarykeys__ = [prop_name_adjusted]
                else:
                    self.__primarykeys__.append(prop_name_adjusted)

    def set_primary_label(self, source_data_dict_attribute_name) -> str:
        label_name = source_data_dict_attribute_name
        if callable(self._d2g.config_func_label_name_generator_func):
            custom_name = self._d2g.config_func_label_name_generator_func(label_name)
            if custom_name is not None:
                self.__primarylabel__ = custom_name
                self.add_label(custom_name)
                return custom_name
        label_name_adjusted = label_name

        if label_name in self._d2g.config_dict_attr_name_to_reltype_instead_of_label:
            label_name_adjusted = (
                self._d2g.config_dict_attr_name_to_reltype_instead_of_label[label_name]
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

        self.add_label(label_name_adjusted)
        self.__primarylabel__ = label_name_adjusted
        if extra_props:
            for extra_prop, extra_val in extra_props.items():
                self.add_prop(prop_name=extra_prop, prop_value=extra_val)
        return label_name_adjusted
