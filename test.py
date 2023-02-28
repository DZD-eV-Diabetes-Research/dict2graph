obj_a = {"a": "1"}
aList = [{"a": "1"}, {"b": "2"}]

print(obj_a in aList)
print(any(obj_a is listItem for listItem in aList))
