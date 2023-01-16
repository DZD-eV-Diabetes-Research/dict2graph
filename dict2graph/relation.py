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
            if (
                self.start_node.is_list_collection_hub
                and not self.start_node.is_root_node
            ):
                return f"{self.start_node.incoming_relations[0].start_node.primary_label}_HAS_{self.end_node.primary_label}"
            else:
                return (
                    f"{self.start_node.primary_label}_HAS_{self.end_node.primary_label}"
                )
        else:
            return "NON_NAMED_REL"

    @relation_type.setter
    def relation_type(self, value: str) -> str:
        self._relation_type = value

    def __str__(self):
        return f"{self.start_node}-[{self.relation_type}]->({self.end_node})"
