# Create custom Transformers

This chapter needs some more informations. But in the meantime you have this short example on how to create a custom node Transformer


```python
from neo4j import GraphDatabase
from dict2graph import Dict2graph,Node
from dict2graph.transformers._base import _NodeTransformerBase

DRIVER = GraphDatabase.driver(os.getenv("NEO4J_URI", "neo4j://localhost"))

## The custom transfomer class
class NameHerChrissy(_NodeTransformerBase):
    def custom_node_match(self, node: Node) -> bool:
        return node["name"] == "Chrisjen Avasarala"

    def transform_node(self, node: Node):
        node["name"] = "Chrissy"

dic = {"person": {"name": "Chrisjen Avasarala"}}

d2g = Dict2graph()

## and how to apply it to your data
d2g.add_node_transformation(Transformer.match_nodes("person").do(NameHerChrissy()))

d2g.parse(dic)
d2g.create(DRIVER)

```

