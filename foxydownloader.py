#!/bin/python
# coding=utf-8

import requests
import sys
import appdirs
import re
import yaml
import io
from getpass import getpass
from simple_term_menu import TerminalMenu

def komi_replacement(m):
    s = m.group()
    if s == "KM[375]":
        return "KM[7.5]"
    if s == "KM[650]":
        return "KM[6.5]"
    return s

def fix_komi(sgf):
    regex = r"KM\[[1-9][0-9]*\]"
    return re.sub(regex, komi_replacement, sgf)

def standardize_ranks(sgf):
    return sgf.replace("级","k*").replace("段","d*")

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

def get_uid(username):
    values = { 
            "srcuid":0,
            "dstuid":0,
            "dstuin":0,
            "username":username,
            "accounttype":0,
            "clienttype":0
            }
    url = "http://h5.foxwq.com/getFechInfo/wxnseed/txwq_fetch_personal_info"
    try:
        response = requests.get(url,params=values)
        return response.json()['uid']
    except Exception as e:
        print(e)
        sys.exit(1)

def game_list(lastCode, username, uid):
    chessid = []
    names = []
 
    values = {
    "type": 4,
    "lastCode": lastCode,
    "FindUserName": username, 
    "uid": uid, 
    
    "RelationTag": 0}

    url = "http://happyapp.huanle.qq.com/cgi-bin/CommonMobileCGI/TXWQFetchChessList"
    try:
        response = requests.post(url,data=values)
        response.encoding="utf-8"
        chesslist = response.json()['chesslist']
        for d in chesslist:
            chessid.append(d['chessid'])
            starttime = d['starttime'].split(' ')[0].replace('-', '.')
            id = d['chessid'][10:]
            blackenname = d['blackenname']
            whiteenname = d['whiteenname']
            names.append(starttime + ' ' + blackenname + ' VS ' + whiteenname + ' (' + id + ')' )
        return chessid, names
    except Exception as e:
        print(e)
        sys.exit(1)

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
    values = {
    "chessid": cid
    }
    url = "http://happyapp.huanle.qq.com/cgi-bin/CommonMobileCGI/TXWQFetchChess"
    sgf = ""
    for i in range(10):
        try:
            response = requests.post(url,data=values)
            response.encoding="utf-8"
            sgf = response.json()['chess']
            break
        except Exception as e:
            if i == 9:
                print(e)
                sys.exit(1)
    return sgf

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
    while True:
        username = input("Fox username: ").strip()
        if len(username) > 0:
            break

    uid = get_uid(username)

    lastCode = ""
    while True:
        chessids, names = game_list(lastCode, username, uid)
        
        n = len(names)
        names.append("select all")
        names.append("older games ...")

        if n == 0:
            if lastCode == "":
                print("No games found. Exiting.")
                break
            else:
                print("No older games found.")
                chessids = oldchessids
                names = oldnames

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
            lastCode = chessids[-1]
            oldchessids = chessids
            oldnames = names
        else:
            for idx in indexs:
                print(f"Downloading {names[idx]} ...")
                sgf = id_to_name(standardize_ranks(fix_komi(download_sgf(chessids[idx]))))

                save_utf8(names[idx], sgf)
                save_sjis(names[idx], sgf)

                # filename=f"utf8/{names[idx]}.sgf"
                # with open(filename, 'w', encoding='utf-8') as f:
                #     f.write(sgf)
            break

if __name__ == "__main__":
    main()
