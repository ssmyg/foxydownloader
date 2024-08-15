#!/bin/python
# coding=utf-8


import sys
import glob
import os


def main():
    # confirm
    print("Are you sure you want to REMOVE all sgf files in utf8 and sjis folders? (y/N): ", end="")
    answer = input()
    if len(answer) == 0:
        # 中止メッセージ
        print("Aborting.")
        return
    if answer != "y":
        print("Aborting.")
        return

    # utf8, sjisフォルダ内のsgfファイルを全て削除する
    for filename in glob.glob("utf8/*.sgf"):
        print(f"Removing {filename}")
        os.remove(filename)
    for filename in glob.glob("sjis/*.sgf"):
        print(f"Removing {filename}")
        os.remove(filename)

if __name__ == "__main__":
    main()
