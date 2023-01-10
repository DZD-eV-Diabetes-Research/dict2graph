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
        return (
            self._relation_type
            if self._relation_type
            else f"{self.start_node.primary_label}_HAS_{self.end_node.primary_label}"
        )

    @relation_type.setter
    def relation_type(self, value: str) -> str:
        self._relation_type = value
