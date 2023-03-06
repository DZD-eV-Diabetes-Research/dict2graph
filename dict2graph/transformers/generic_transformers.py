from typing import TYPE_CHECKING, Callable, Union, Dict, Type, Any, Tuple, Literal, List
from dict2graph.node import Node
from dict2graph.relation import Relation
from dict2graph.transformers._base import _NodeTransformerBase, _RelationTransformerBase
import json


class EscapeInvalidNamesForNeo4JCompatibility(
    _RelationTransformerBase, _NodeTransformerBase
):
    """Rename labels and property keys to be valid with Neo4j rules
    # https://neo4j.com/docs/cypher-manual/current/syntax/naming/
    """

    def is_string_valid(self, val: str):

        if len(val) == 0:
            return False
        if not val[0].isalpha():
            return False
        elif not val.isalnum():
            return False
        elif len(val) > 65355:
            return False
        else:
            return True

    def make_valid(self, val: str):
        return f"`{val[:65354]}`"

    def _transform(self, obj: Dict):
        new_keys = {}
        for key in obj.keys():
            if not self.is_string_valid(key):
                new_keys[self.make_valid(key)] = obj[key]
        obj.update(new_keys)

    def transform_node(self, node: Node):
        new_labels = []
        for label in node.labels:
            if not self.is_string_valid(label):
                new_labels.append(self.make_valid(label))
            else:
                new_labels.append(label)
        node.labels = new_labels
        self._transform(node)

    def transform_rel(self, rel: Relation):
        if self.is_string_valid(rel.relation_type):
            rel.relation_type = self.make_valid(rel.relation_type)
        self._transform(rel)


class OverridePropertyName(_RelationTransformerBase, _NodeTransformerBase):
    """Replace a property name/key with a new string of your choice.
    Usage:
    ```python
    from dict2graph import Dict2graph, Transformer, NodeTrans
    from neo4j import GraphDatabase

    NEO4J_DRIVER = GraphDatabase.driver("neo4j://localhost")

    dic = {"person": {"name": "Camina Drummer"}}
    d2g = Dict2graph()
    d2g.add_node_transformation(
        Transformer.match_nodes("person").do(NodeTrans.OverridePropertyName("name","fullname"))
    )
    d2g.parse(dic)
    d2g.create(NEO4J_DRIVER)
    ```
    Results in a Neo4j node `(:Person{fullname:'Camina Drummer'})`
    """

    def __init__(self, source_property_name: str, target_property_name: str):
        """
        Args:
            source_property_name (str): The property key you want to be replaced.
            target_property_name (str): The The new name of the property.
        """
        self.source_property_name = source_property_name
        self.target_property_name = target_property_name

    def _transform(self, obj: Dict):
        if self.source_property_name in obj:
            obj[self.target_property_name] = obj.pop(self.source_property_name)

    def transform_node(self, node: Node):
        self._transform(node)

    def transform_rel(self, rel: Relation):
        self._transform(rel)


class TypeCastProperty(_RelationTransformerBase, _NodeTransformerBase):
    """change the type of property values.
    Usage:
    ```python
    from dict2graph import Dict2graph, Transformer, NodeTrans
    from neo4j import GraphDatabase

    NEO4J_DRIVER = GraphDatabase.driver("neo4j://localhost")

    dic = {"person": {"name": "Camina", "captain":"true", "age":"39"}}
    d2g = Dict2graph()
    d2g.add_node_transformation([
        Transformer.match_nodes("person").do(NodeTrans.TypeCastProperty("captain",bool)),
        Transformer.match_nodes("person").do(NodeTrans.TypeCastProperty("age",int)),
    ])
    d2g.parse(dic)
    d2g.create(NEO4J_DRIVER)
    ```
    Results in a Neo4j node `(:Person{name:'Camina',captain:true,age:27})`
    """

    def __init__(self, property_name: str, target_type: Union[str, int, float, bool]):
        """
        Args:
            property_name (str): The property key that should be changed
            target_type (Union[str, int, float, bool]): The type that should result
        """
        self.property_name = property_name
        self.target_type = target_type

    def _transform(self, obj: Dict):
        if self.property_name in obj:
            if self.target_type == bool:
                obj[self.property_name] = True
                if obj[self.property_name] in [
                    0,
                    "0",
                    None,
                    "Null",
                    "false",
                    "False",
                    "f",
                    "F",
                    "No",
                    "no",
                ]:
                    obj[self.property_name] = False
            else:
                obj[self.property_name] = self.target_type(obj[self.property_name])

    def transform_node(self, node: Node):
        self._transform(node)

    def transform_rel(self, rel: Relation):
        self._transform(rel)


class RemoveProperty(_RelationTransformerBase, _NodeTransformerBase):
    """Remove a property from a node
    Usage:
    ```python
    from dict2graph import Dict2graph, Transformer, NodeTrans
    from neo4j import GraphDatabase

    NEO4J_DRIVER = GraphDatabase.driver("neo4j://localhost")

    dic = {"person": {"name": "Camina", "id":"sdf343"}}
    d2g = Dict2graph()
    d2g.add_node_transformation(
        Transformer.match_nodes("person").do(NodeTrans.RemoveProperty(id))
        )
    d2g.parse(dic)
    d2g.create(NEO4J_DRIVER)
    ```
    Results in a Neo4j node `(:Person{name:'Camina'})`. the `id` property will be thrown away.
    """

    def __init__(self, property_keys: Union[str, List[str]]):
        """_summary_

        Args:
            property_keys (Union[str, List[str]]): A property key or a list of property keys as strings that should be removed
        """
        if isinstance(property_keys, str):
            property_keys = [property_keys]
        self.property_keys = property_keys

    def custom_node_match(self, node: Node) -> bool:
        # check if node keys and defined properties have an overlap
        return not set(self.property_keys).isdisjoint(set(node.keys()))

    def transform_node(self, node: Node):
        self._transform(node)

    def transform_rel(self, rel: Relation):
        self._transform(rel)

    def _transform(self, obj: Union[Node, Relation]):
        for prop in self.property_keys:
            obj.pop(prop, None)


class AddProperty(_RelationTransformerBase, _NodeTransformerBase):
    """Add a property to a node
    Usage:
    ```python
    from dict2graph import Dict2graph, Transformer, NodeTrans
    from neo4j import GraphDatabase

    NEO4J_DRIVER = GraphDatabase.driver("neo4j://localhost")

    dic = {"person": {"name": "Camina"}}
    d2g = Dict2graph()
    d2g.add_node_transformation(
        Transformer.match_nodes("person").do(NodeTrans.AddProperty({"my_new_prop_key":"my_new_prop_value_1111"}))
        )
    d2g.parse(dic)
    d2g.create(NEO4J_DRIVER)
    ```
    Results in a Neo4j node `(:Person{name:'Camina',my_new_prop_key:"my_new_prop_value_1111"})`.
    """

    def __init__(self, properties: Dict):
        """_summary_

        Args:
            properties (Union[str, List[str]]): A property key or a list of property keys as strings that should be removed
        """
        if not isinstance(properties, dict):
            raise ValueError(
                f"Transformer `AddProperty` init failed. Parameters `properties` malformed: Expected dict, got {type(properties)}"
            )
        self.properties = properties

    def transform_node(self, node: Node):
        self._transform(node)

    def transform_rel(self, rel: Relation):
        self._transform(rel)

    def _transform(self, obj: Union[Node, Relation]):
        obj.update(self.properties)
