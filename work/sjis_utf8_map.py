import sys

# id_name_map.txtを開く
with open("../sjis_utf8_map.txt", "r") as f:
  sjis_utf8_map = f.read().splitlines()

dup = {}
for line in sjis_utf8_map:
  # id1(id2) nameとなっていた場合、id1,id2,nameを取得する
  line = line.strip()
  if len(line) == 0:
    continue
  cols = line.split()
  if cols[3] in dup:
    print(f"Duplicate: {cols[3]} {cols[2]} {dup[cols[3]]}", file=sys.stderr)
  else:
    dup[cols[3]] = cols[2]
    print(f"{cols[3]}={cols[2]}")
