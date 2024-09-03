import re
import sys

def replace_id(m):
    player = m.group()
    tag = player[:2]
    id = player[3:-1]
    if id in id_name_map:
        return f"{tag}[{id_name_map[id]}]"
    return f"{tag}[{id}]"

def id_to_name(sgf):
    regex_pb = r"PB\[.*?\]"
    regex_pw = r"PW\[.*?\]"

    sgf_pb = re.sub(regex_pb, replace_id, sgf)
    return re.sub(regex_pw, replace_id, sgf_pb)

# id_name_map.txtを読み込んで、idとnameの対応を返す（#から始まる行は無視）
def read_id_name_map():
    id_name_map = {}
    with open("id_name_map.txt", "r") as f:
        for line in f:
            line = line.strip()
            if len(line) == 0:
                continue
            if line[0] == "#":
                continue
            try:
                id, name = line.split("=")
            except ValueError:
                print(f"Error: {line}")
                sys.exit(1)
            id_name_map[id.strip()] = name.strip()
    return id_name_map

id_name_map = read_id_name_map()

def read_sjis_utf8_map():
    utf8_sjis_map = {}
    with open("utf8_sjis_map.txt", "r") as f:
        for line in f:
            line = line.strip()
            if len(line) == 0:
                continue
            if line[0] == "#":
                continue
            try:
                utf8, sjis = line.split("=")
            except ValueError:
                print(f"Error: {line}")
                sys.exit(1)
            utf8_sjis_map[utf8.strip()] = sjis.strip()
    return utf8_sjis_map

utf8_sjis_map = read_sjis_utf8_map()

def save_utf8(name, sgf):
    filename=f"utf8/{name}.sgf"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(sgf)

def apply_utf8_sjis_map(c):
    if c in utf8_sjis_map:
        return utf8_sjis_map[c]
    return c

def save_sjis(name, sgf):
    # 全ての文字に対して、utf8_sjis_mapを適用
    name = ''.join(map(apply_utf8_sjis_map, name))
    sgf = ''.join(map(apply_utf8_sjis_map, sgf))

    filename=f"sjis/{name}.sgf".encode('shift_jis', errors='replace').decode('shift_jis').replace("?", "_")
    with open(filename, 'w', encoding='shift_jis', errors='replace') as f:
        f.write(sgf)

