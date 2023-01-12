from dict2graph.node import Node


class Relation(dict):
    def __init__(
        self, start_node: Node, end_node: Node, relation_type: str = None, **kwargs
    ):
        self._relation_type = relation_type
        self.start_node = start_node
        self.start_node.relations.append(self)
        self.end_node = end_node
        self.end_node.relations.append(self)
        self._origin_relation_type: str = relation_type
        self.deleted = False
        self.update(**kwargs)

    @property
    def relation_type(self) -> str:
        if self._relation_type:
            return self._relation_type
        elif self.start_node is not None and self.end_node is not None:
            return f"{'_'.join(self.start_node.labels)}_HAS_{'_'.join(self.end_node.labels)}"
        else:
            return "NON_NAMED_REL"

    @relation_type.setter
    def relation_type(self, value: str) -> str:
        self._relation_type = value

    def __str__(self):
        return f"{self.start_node}-[{self.relation_type}]->({self.end_node})"
