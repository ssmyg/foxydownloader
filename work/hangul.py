
# id_name_map.txtを開く
with open("hangul.txt", "r") as f:
  id_name_map = f.read().splitlines()

prev = ""
for line in id_name_map:
  # id1(id2) nameとなっていた場合、id1,id2,nameを取得する
  words = line.split()
  if len(words) == 0:
    continue
  if len(words) == 3:
    prev = words[0]
    print(f"{words[1]}\t{words[0]}")
  else:
    print(f"{words[0]}\t{prev}")
