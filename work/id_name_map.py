
# id_name_map.txtを開く
with open("id_name_map.txt", "r") as f:
  id_name_map = f.read().splitlines()

for line in id_name_map:
  # id1(id2) nameとなっていた場合、id1,id2,nameを取得する
  if "(" in line:
    ids, name = line.split()
    id1, id2 = ids.split("(")
    id2 = id2.replace(")", "")
    print(f"{id1}\t{name}")
    print(f"{id2}\t{name}")
  else:
    print(line)