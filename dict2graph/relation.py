from dict2graph.node import Node


class Relation(dict):
    def __init__(self, relation_type: str, start_node: Node, end_node: Node, **kwargs):
        self.relation_type = relation_type
        self.start_node = start_node
        self.start_node.relations.append(self)
        self.end_node = end_node
        self.end_node.relations.append(self)
        self._origin_relation_type: str = relation_type
        self.update(**kwargs)
