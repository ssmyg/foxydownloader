#!/bin/python
# coding=utf-8

import requests
import re
from simple_term_menu import TerminalMenu
import sys
from dotenv import load_dotenv
import os
import json
from utils import id_to_name, save_utf8, save_sjis

# .envファイルを読み込む
load_dotenv()
USER_ID = os.getenv("USER_ID")


def game_list(page):
    chessid = []
    names = []

    page_size = 50
    url = f"https://www.19x19.com/api/engine/situations/{USER_ID}/默认?folder=默认&username={USER_ID}"
    try:
        res = requests.get(url)
    except Exception as e:
        print(e)
        sys.exit(1)

    if not res.ok:
        print("Error: ", res)
        sys.exit(1)

    res.encoding = "utf-8"
    res_json = res.json()

    # # golaxy.jsonファイルを読み込む
    # with open('golaxy_list.json', 'r') as f:
    #     res_json = json.load(f)

    if res_json["code"] != "0":
        print("Error: ", res_json["msg"])
        sys.exit(1)
    chesslist = res_json["data"]

    for d in chesslist:
        chessid.append(d["id"])
        dt = d["createTime"]

        names.append(
            f"{dt['date']['year']}.{dt['date']['month']}.{dt['date']['day']} {d['id']} {d['name']}"
        )
    return chessid, names


def download_sgf(cid):
    url = f"https://www.19x19.com/api/engine/games/guest/{cid}"

    try:
        res = requests.get(url)
    except Exception as e:
        print(e)
        sys.exit(1)

    if not res.ok:
        print("Error: ", res)
        sys.exit(1)

    res.encoding = "utf-8"
    res_json = res.json()

    # # golaxy.jsonファイルを読み込む
    # with open('golaxy_detail.json', 'r') as f:
    #     res_json = json.load(f)

    if res_json["code"] != "0":
        print("Error: ", res_json["msg"])
        sys.exit(1)

    return res_json["data"]["sgf"]


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

        terminal_menu = TerminalMenu(
            names, multi_select=True, show_multi_select_hint=True
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
        if n + 1 in indexs:
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
