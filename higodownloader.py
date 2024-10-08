#!/bin/python
# coding=utf-8

import requests
import re
import sys
from simple_term_menu import TerminalMenu
import json
from utils import id_to_name, save_utf8, save_sjis

def game_list(page, player_name, tournament_name):
    chessid = []
    names = []

    headers = {
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
    }
    value = {
        "operationName":"GetPublicKifus",
        "variables": {
            "filter": {
                "page": page,
                "limit": 50,
                "isPublished": True,
                # "orderBy":[{"column":"seq","reverse": False},{"column":"gameStartedAt","reverse": True}],
                "orderBy":[{"column":"gameStartedAt","reverse": True}],
                # "playerName": player_name,
                # "tournamentName": tournament_name,
            },
            "isLogin": False
        },
        "query": "query GetPublicKifus($filter: PublicKifuFilter!, $isLogin: Boolean!) {\n  publicKifus(filter: $filter) {\n    kifus {\n      id\n      gameStartedAt\n      sgf\n      winningWay\n      seq\n      source\n      tournamentName\n      blackPlayer {\n        id\n        name\n        avatarUrl\n        __typename\n      }\n      whitePlayer {\n        id\n        name\n        avatarUrl\n        __typename\n      }\n      series {\n        id\n        name\n        tournament {\n          id\n          name\n          __typename\n        }\n        __typename\n      }\n      isPublished\n      isPopular\n      isCommentedByCommentator\n      isStreaming\n      isCollected @include(if: $isLogin)\n      __typename\n    }\n    count\n    __typename\n  }\n}\n"
    }

    if len(player_name) > 0:
        value['variables']['filter']['playerName'] = player_name
    if len(tournament_name) > 0:
        value['variables']['filter']['tournamentName'] = tournament_name

    url = "https://api.higohigo.org/graphql"
    try:
        res = requests.post(url, json=value, headers=headers)
    except Exception as e:
        print(e)
        sys.exit(1)

    if not res.ok:
        print("Error: ", res)
        sys.exit(1)

    res.encoding="utf-8"
    chesslist = res.json()['data']['publicKifus']['kifus']

    for d in chesslist:
        chessid.append(d['id'])
        started_at = d['gameStartedAt'].split('T')[0].replace('-', '.')
        names.append(f"{started_at} {d['id']} {d['blackPlayer']['name']} VS {d['whitePlayer']['name']} - {d['series']['tournament']['name']} {d['series']['name']}")
    return chessid, names, chesslist

def convert_result(str):
    str = str.replace("黑", "B+").replace("黒", "B+").replace("白", "W+")
    if "中盤勝" in str or "不計點勝" in str:
        return str.replace("中盤勝", "R").replace("不計點勝", "R")
    if "時間勝" in str:
        return str.replace("時間勝", "T")
    if "規則勝" in str:
        return str.replace("規則勝", "F")
    if "目勝" in str or "子勝" in str or "點勝" in str:
        return str.replace("目勝", "").replace("子勝", "").replace("點勝", "")
    return str

def download_sgf(chesslist, idx):
    sgf = chesslist[idx]['sgf']

    started_at = chesslist[idx]['gameStartedAt'].split('T')[0]
    series_name = chesslist[idx]['series']['name']
    tournament = chesslist[idx]['series']['tournament']['name']

    pw = f"PW[{chesslist[idx]['whitePlayer']['name']}]"
    if "PW[" in sgf:
        sgf = re.sub(r"PW\[.*?\]", lambda x: pw, sgf)
    else:
        sgf = f"({pw} {sgf[1:]}"

    pb = f"PB[{chesslist[idx]['blackPlayer']['name']}]"
    if "PB[" in sgf:
        sgf = re.sub(r"PB\[.*?\]", lambda x: pb, sgf)
    else:
        sgf = f"({pb} {sgf[1:]}"

    result = f"RE[{convert_result(chesslist[idx]['winningWay'])}]"
    if "RE[" in sgf:
        sgf = re.sub(r"RE\[.*?\]", lambda x: result, sgf)
    else:
        sgf = f"({result} {sgf[1:]}"

    dt = f"DT[{started_at}]"
    if "DT[" in sgf:
        sgf = re.sub(r"DT\[.*?\]", lambda x: dt, sgf)
    else:
        sgf = f"({dt} {sgf[1:]}"

    gn = f"GN[{tournament} {series_name}]"
    if "GN[" in sgf:
        sgf = re.sub(r"GN\[.*?\]", lambda x: gn, sgf)
    else:
        sgf = f"({gn} {sgf[1:]}"

    return sgf

def main():
    player_name = input("Player Name: ").strip()
    tournament_name = input("Tournament Name: ").strip()
    
    page = 1
    while True:
        chessids, names, chesslist = game_list(page, player_name, tournament_name)
        
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

                sgf = id_to_name(download_sgf(chesslist, idx))

                save_utf8(names[idx], sgf)
                save_sjis(names[idx], sgf)
            break


if __name__ == "__main__":
    main()
