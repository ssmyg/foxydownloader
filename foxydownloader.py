#!/bin/python
# coding=utf-8

import requests
import sys
import appdirs
import re
import yaml
import io
import codecs
from getpass import getpass
from simple_term_menu import TerminalMenu

# yes this code looks weird but so is fox's komi notation 
# which is giving a number without specifying the decimal point
# seriously wtf?
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

def get_ogs_token(client_id, client_secret, username, password):
    values = { 
            "grant_type":"password",
            "username":username,
            "password":password,
            "client_id":client_id,
            "client_secret":client_secret,
            }
    url = "https://online-go.com/oauth2/token/"
    try:
        response = requests.post(url,data=values)
        response_json = response.json()
        return response_json['token_type'], response_json['access_token']
    except Exception as e:
        print(e)
        sys.exit(1)

def upload_to_ogs(filename, sgf, token_type, access_token):
    headers = {
            "Authorization":token_type+" "+access_token
            }
    files = {'file': (filename, sgf, 'application/x-go-sgf')}
    url = "https://online-go.com/api/v1/me/games/sgf/0"
    try:
        response = requests.post(url,headers=headers,files=files)
        if response.json()['success'] == "Files uploaded":
            return True
        else:
            return False
    except Exception as e:
        print(e)
        sys.exit(1)


def main():
    no_ogs=False
    try:
        ogs_option_file = io.open(appdirs.user_config_dir("foxydownloader")+'/config', 'r', encoding='utf8')
        data_loaded = yaml.safe_load(ogs_option_file)
        OGS_CLIENT_ID = data_loaded['ogs-client-id']
        OGS_CLIENT_SECRET=data_loaded['ogs-client-secret']
    except Exception as e:
        print(e)
        print("OGS client data not set or set incorrectly. Please refer to the readme on how to configure this to upload to OGS.")
        no_ogs = True

    ogs_upload = False
    if not(no_ogs):
        ogs_access_token = ""
        ogs_token_type = ""

        print("What do you want to do with the downloaded Fox games?")
        options = ["Save to disk","Upload to OGS"]
        terminal_menu = TerminalMenu(options)
        index = terminal_menu.show()

        if index == None:
            print("Aborting.")
            sys.exit(0)
        elif index == 1:
            ogs_upload = True
            ogs_token_type, ogs_access_token = get_ogs_token(OGS_CLIENT_ID, OGS_CLIENT_SECRET, \
                    input("OGS username: "), getpass("OGS password: "))

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
                filename=f"{names[idx]}.sgf"
                sgf = standardize_ranks(fix_komi(download_sgf(chessids[idx])))
                if ogs_upload:
                    upload_to_ogs(filename, sgf, ogs_token_type, ogs_access_token)
                else:
                    f = codecs.open(filename, 'w', 'utf-8')
                    f.write(sgf)
                    f.close()
            break

if __name__ == "__main__":
    main()
