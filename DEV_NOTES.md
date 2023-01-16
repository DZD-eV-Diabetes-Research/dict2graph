# good example why we need tranformation

`data` makes no sense as a graph but `data2` does besided the same structure

```python
data = {
    "name": "Holden",
    "stationed": {"ship": {"name": "Zheng Fei"}, "deployment_active": False},
}
data2 = {
    "Person": "Holden",
    "Ship": {"Engine": {"type": "Epstein Drive"}, "name": "Zheng Fei"},
}
d2g = Dict2graph()
d2g.parse(data, "Person")
d2g.create(DRIVER)
```