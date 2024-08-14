#!/bin/python
# coding=utf-8

import requests
import re
from simple_term_menu import TerminalMenu
import sys
from dotenv import load_dotenv
import os
import json

# .envファイルを読み込む
load_dotenv()
USER_ID = os.getenv("USER_ID")

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

def game_list(page):
    chessid = []
    names = []
 
    page_size = 50
    url = f"https://www.19x19.com/api/engine/games/{USER_ID}?game_type=1&page={page}&size={page_size}&username={USER_ID}"
    try:
        res = requests.get(url)
    except Exception as e:
        print(e)
        sys.exit(1)

    res.encoding="utf-8"
    res_json = res.json()

    # # golaxy.jsonファイルを読み込む
    # with open('golaxy_list.json', 'r') as f:
    #     res_json = json.load(f)

    if res_json['code'] != '0':
        print("Error: ", res_json['msg'])
        sys.exit(1)
    chesslist = res_json['data']['gameMetaList']

    for d in chesslist:
        chessid.append(d['id'])
        dt = d['createTime']
        names.append(f"{dt['date']['year']}.{dt['date']['month']}.{dt['date']['day']} {d['id']} {d['pb']} VS {d['pw']}")
    return chessid, names


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

def download_sgf(cid):
    url = f"https://www.19x19.com/api/engine/games/guest/{cid}"

    try:
        res = requests.get(url)
    except Exception as e:
        print(e)
        sys.exit(1)

    res.encoding="utf-8"
    res_json = res.json()

    # # golaxy.jsonファイルを読み込む
    # with open('golaxy_detail.json', 'r') as f:
    #     res_json = json.load(f)

    if res_json['code'] != '0':
        print("Error: ", res_json['msg'])
        sys.exit(1)
    
    return res_json['data']['sgf']


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

    filename=f"sjis/{name}.sgf".encode('shift_jis', errors='replace').decode('shift_jis')
    with open(filename, 'w', encoding='shift_jis', errors='replace') as f:
        f.write(sgf)

def main():
    page = 0
    while True:
        chessids, names = game_list(page)
        
        n = len(names)
        names.append("select all")
        names.append("older games ...")

        if n == 0:
            print("No games found. Exiting.")
            break

        terminal_menu = TerminalMenu(names,
            multi_select=True,
            show_multi_select_hint=True
        )
        indexs = terminal_menu.show()

        if indexs == None:
            print("Aborting.")
            break
        if len(indexs) == 0:
            print("Aborting.")
            break
        if n in indexs:
            print("select all")
            indexs = tuple(range(n))
        if n+1 in indexs:
            page = page + 1
        else:
            for idx in indexs:
                print(f"Downloading {names[idx]} ...")

                sgf = id_to_name(download_sgf(chessids[idx]))

                save_utf8(names[idx], sgf)
                save_sjis(names[idx], sgf)
            break


if __name__ == "__main__":
    main()
