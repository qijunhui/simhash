# -*- coding: utf-8 -*-
"""
@Time    : 2020/12/31 18:55
@Author  : qijunhui
@File    : config.py
"""
import os

DATA_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")
RAW_DATA_PATH = os.path.join(DATA_PATH, "raw_data.csv")  # 原始数据

INDEX2WORDS_PATH = os.path.join(DATA_PATH, "index2words.json")  # 处理后数据
WORD2IDF_PATH = os.path.join(DATA_PATH, "word2idf.json")  # idf模型
INDEX2SIMHASH_PATH = os.path.join(DATA_PATH, "index2simhash.csv")  # simhash结果
