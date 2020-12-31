# -*- coding: utf-8 -*-
"""
@Time    : 2020/12/31 18:55
@Author  : qijunhui
@File    : utils.py
"""
import os, csv, json
import jieba


def read_csv(filepath, filter_title=False, delimiter=","):
    data = []
    csv.field_size_limit(500 * 1024 * 1024)
    if os.path.exists(filepath):  # 如果目标文件存在:
        with open(filepath, "r", encoding="utf-8") as fr:
            data = csv.reader(fr, delimiter=delimiter)  # 逐行读取csv文件 迭代器变量
            if filter_title:
                next(data)  # 过滤首行
            data = list(data)
        print(f"{filepath} [{len(data)}] 已加载... ")
    else:
        print(f"{filepath} 文件不存在...")
    return data


def save_csv(filepath, data, columns=None, delimiter=","):
    with open(filepath, "w", newline="", encoding="utf-8") as fw:
        csv_writer = csv.writer(fw, delimiter=delimiter)
        if columns:
            csv_writer.writerow(columns)  # 写表头
        csv_writer.writerows(data)
    print(f"{filepath} [{len(data)}] 文件已存储...")


def read_json(filepath):
    data = {}
    if os.path.exists(filepath):  # 如果目标文件存在:
        with open(filepath, "r") as fr:
            data = json.load(fp=fr)
        print(f"{filepath} [{len(data)}] 已加载... ")
    else:
        print(f"{filepath} 文件不存在...")
    return data


def save_json(filepath, data):
    with open(filepath, "w") as fw:
        json.dump(data, fw)
    print(f"{filepath} [{len(data)}] 文件已存储...")


def tokenizer(text):
    return jieba.lcut(text)
