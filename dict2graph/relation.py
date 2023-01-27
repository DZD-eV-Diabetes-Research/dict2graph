from dict2graph.node import Node


class Relation(dict):
    """Represantation of a property-graph relationship"""

    def __init__(
        self, start_node: Node, end_node: Node, relation_type: str = None, **kwargs
    ):
        """Create a new relationship

        Args:
            start_node (Node): The node from which the relationship will start
            end_node (Node): The node to which the relationship will go to
            relation_type (str, optional): The name if the relation. Defaults to None.
            **kwargs (Any, optional): Any further properties of this relationship. Defaults to None.
        """
        self._relation_type = relation_type
        self._start_node = None
        self._end_node = None
        self.start_node = start_node
        self.end_node = end_node

        self._origin_relation_type: str = relation_type
        self.deleted = False
        self.update(**kwargs)

    @property
    def relation_type(self) -> str:
        """The name of the relationship.
        As in [Neo4j Relation Type](https://neo4j.com/docs/getting-started/current/appendix/graphdb-concepts/#graphdb-relationship-type)

        Defaults to a string with following structure:

        `<start node first label>_HAS_<end_node_first_label>`

        Returns:
            str: The relationship type as str
        """
        if self._relation_type:
            return self._relation_type
        elif self.start_node is not None and self.end_node is not None:
            if (
                self.start_node.is_list_list_hub
                # and not self.start_node.is_root_node
            ):
                return f"{self.start_node.primary_label}_LIST_HAS_{self.end_node.primary_label}"
            else:
                return (
                    f"{self.start_node.primary_label}_HAS_{self.end_node.primary_label}"
                )
        else:
            return "NON_NAMED_REL"

    @relation_type.setter
    def relation_type(self, value: str) -> str:
        self._relation_type = value

    @property
    def start_node(self) -> Node:
        """The node from which the relationship is originating

        Returns:
            Node: The start node as a [Dict2Graph.Node](/api/api_node) instance
        """
        return self._start_node

    @start_node.setter
    def start_node(self, node: Node):
        if self._start_node:
            # relation changed. we need to remove the relation form the old node
            self._start_node.relations.remove(self)
        node.relations.append(self)
        self._start_node = node

    @property
    def end_node(self) -> Node:
        """The target node of the relationship

        Returns:
            Node: The end node as a [Dict2Graph.Node](/api/api_node) instance
        """
        return self._end_node

    @end_node.setter
    def end_node(self, node: Node):
        if self._end_node:
            self._end_node.relations.remove(self)
        node.relations.append(self)
        self._end_node = node

    def __str__(self):
        return f"{self.start_node}-[{self.relation_type}]->({self.end_node})"
