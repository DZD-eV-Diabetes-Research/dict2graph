# Examples

This page is still under construction but as a entry read our blog post about dict2graph which comes with a nice little use case

[https://blog.connect.dzd-ev.de/dict2graph/](https://blog.connect.dzd-ev.de/dict2graph/)


## common errors:

Todo:

These are just notes atm:

`neo4j.exceptions.DatabaseError: {code: Neo.DatabaseError.Statement.ExecutionFailed} {message: Property value is too large to index` when merging
Too large values for creating merge indexes. Solution: Create merge keys with `NodeTrans.SetMergeProperties` avoiding the properties with large values or `NodeTrans.CreateNewMergePropertyFromHash`