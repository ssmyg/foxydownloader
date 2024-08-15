#!/bin/python
# coding=utf-8

import requests
import re
import sys
from simple_term_menu import TerminalMenu
import json
from bs4 import BeautifulSoup
from utils import id_to_name, save_utf8, save_sjis

def game_list(page, player_name, tournament_name):
    chessid = []
    names = []


    url = f"https://kifudepot.net/index.php?page={page}&move=&player={player_name}&event={tournament_name}&sort="
    try:
        res = requests.get(url)
    except Exception as e:
        print(e)
        sys.exit(1)

    if not res.ok:
        print("Error: ", res)
        sys.exit(1)

    res.encoding="utf-8"
    res_html = res.text

    soup = BeautifulSoup(res_html, 'lxml')
    # dataTableクラスを持つtableタグ内のすべてのtrタグを検索
    for tr in soup.select('.dataTable tr')[1:]:
        # 各trタグから必要な情報を抽出
        url = tr.select_one('td.td_ev a')['href']
        date = tr.select_one('td.td_dt').text.strip().replace('-', '.')
        event_name = tr.select_one('td.td_ev').text.strip()
        event_name = event_name.replace('&nbsp;<i class="fa fa-video-camera" aria-hidden="true"></i>', '')
        pb = tr.select_one('td.td_pb div').text.strip()
        pw = tr.select_one('td.td_pw div').text.strip()

        chessid.append(url)
        names.append(f"{date} {pb} VS {pw} - {event_name}")

    return chessid, names

def download_sgf(url):
    try:
        res = requests.get(f"https://kifudepot.net/{url}")
    except Exception as e:
        print(e)
        sys.exit(1)

    if not res.ok:
        print("Error: ", res)
        sys.exit(1)

    res.encoding="utf-8"
    res_html = res.text

    soup = BeautifulSoup(res_html, 'lxml')
    return soup.select('#sgf')[0].text

def main():
    player_name = input("Player Name: ").strip()
    tournament_name = input("Tournament Name: ").strip()
    
    page = 1
    while True:
        chessids, names = game_list(page, player_name, tournament_name)
        
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
