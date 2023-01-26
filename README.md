# Dict2graph

V3 - BRANCH - Total Refactoring WIP!

Transfer (json compatible) Python dicts into a Neo4j graph database with the help of https://github.com/kaiserpreusse/graphio . dict2graph also comes with some data transform capabilities.

## About

**Maintainer**: tim.bleimehl@dzd-ev.de

**Licence**: MIT

**issue tracker**: https://git.connect.dzd-ev.de/dzdtools/pythonmodules/-/issues?label_name%5B%5D=DZDdict2graph

**user docs**: https://dzd-ev.github.io/dict2graph-docs/

**source code**: https://git.connect.dzd-ev.de/dzdpythonmodules/dict2graph

## Content

- [Dict2graph](#dict2graph)
  - [About](#about)
  - [Content](#content)
  - [Install](#install)
  - [What is dict2graph](#what-is-dict2graph)
    - [Recommended workflow](#recommended-workflow)
  - [What dict2graph is **not**](#what-dict2graph-is-not)
  - [py2neo depcrecation warning](#py2neo-depcrecation-warning)
  - [Basic Usage Example](#basic-usage-example)
    - [Load a dict](#load-a-dict)
      - [Transform the model](#transform-the-model)


## Install

at the moment if dev:

`pip3 install git+https://git.connect.dzd-ev.de/dzdpythonmodules/dict2graph.git@V3`

Later will be:

`pip3 install dict2graph`
## What is dict2graph 

With dict2graph you can transfer python dicts into a neo4j graph out of the box. If you are not happy with the structure of the result, dict2graph comes with a bunch of transformation tools.

### Recommended workflow

The recommended workflow is:

- Load your dict (or a sample of your larger datasets) as it is, with dict2graph into a neo4j test instance
- Inspect the result in neo4j
- Add dict2graph-transformators to shape your resulting graph model
- Wipe your neo4j test instance
- Repeat the work flow with the changed dict2graph-transformators until your happy with the result

## What dict2graph is **not**

dict2graph can **not** be used for de-/serializing your dict into a graph database. There is no `graph2dict` functionality (nore is it planned to have one).  
Your data/dict will be transformed to be more suitable in a graph represantation. On the way, certain informations can be lost. Reproducing the exact same dict from the graph is not possible in many cases.

## py2neo depcrecation warning

In past versions of `dict2graph`, the awesome [`py2neo`](https://py2neo.org/2021.1/) library was the only way to connect to a Neo4j instance.  
But (sadly) this lib is in a low-maintanance mode. For now it is still supported but marked as deprecated. We recommend to switch to the official [Neo4j Python Driver](https://neo4j.com/docs/api/python-driver/current/). 

## Basic Usage Example

Lets show a simple example.

### Load a dict

```python
from dict2graph import Dict2graph, Transformer, NodeTrans, RelTrans
from neo4j import GraphDatabase, Driver
NEO4J_DRIVER = GraphDatabase.driver("neo4j://localhost")

dic = {
    "Action": {
        "id": 1,
        "target": "El Oued",
        "Entities": [{"id": "Isabelle Eberhardt"}, {"id": "Slimène Ehnni"}],
    }
}
d2g = Dict2graph()
d2g.create(dic)
d2g.merge(NEO4J_DRIVER)
```

This will result in following graph:

![](dict2graph_docs/img/readme_basic_example.png "Result example 1")

#### Transform the model

We now have loaded the dict into a Neo4j Graph. But usally we dont need explicit `list`s in graph. Also it is common to uppercase relationship types and capitalize labels.

So we need to make some adjustments to improve the visual graph represenation of the dict.  
This is where `dict2graph.Transformers` come into play.

```python
from dict2graph import Dict2graph, Transformer, NodeTrans, RelTrans
from py2neo import Graph

data = {
    "Action": {
        "id": 1,
        "target": "El Oued",
        "Entities": [{"id": "Isabelle Eberhardt"}, {"id": "Slimène Ehnni"}],
    }
}
d2g = Dict2graph()
d2g.add_transformation(
    [
        Transformer.match_node().do(NodeTrans.CapitalizeLabels()),
        Transformer.match_rel().do(RelTrans.UppercaseRelationType()),
        Transformer.match_node().do(NodeTrans.PopListHubNodes()),
    ]
)
d2g.parse(data)
d2g.create(DRIVER)
```
 Now thats look more like a graph we are used to, isn't it?

![](dict2graph_docs/img/readme_basic_example_trans.png "Result example 1")

 There are a lot of more powerfull `Transformators` and you can even make your own 🚀!  
 Have a deeper look into the docs to learn more.