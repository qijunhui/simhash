# -*- coding: utf-8 -*-
"""
@Time    : 2020/12/31 18:56
@Author  : qijunhui
@File    : idf_model.py
"""
import math
from config import RAW_DATA_PATH, INDEX2WORDS_PATH, WORD2IDF_PATH
from utils import read_csv, save_json, tokenizer


class IdfModel(object):
    def __init__(self):
        self.d = 0  # 文档总个数
        self.df = {}  # 存储每个词及出现了该词的文档数量
        self.idf = {}  # 存储每个词及对应的idf值
        self.index2words = {}  # 字典的每一个元素是一个dict，dict存储着一个文档中每个词的出现次数  {index:{info}...}

    def add_text(self, index, text):
        words = {}
        for word in tokenizer(text):
            words[word] = words.get(word, 0) + 1  # 存储着一个文档中每个词的出现次数
        self.index2words[index] = words  # 字典的每一个元素是一个dict，dict存储着一个文档中每个词的出现次数
        for word in words.keys():
            self.df[word] = self.df.get(word, 0) + 1  # 存储每个词及出现了该词的文档数量
        self.d += 1  # 计算文档总个数

    def count_idf(self):
        for word, num in self.df.items():
            self.idf[word] = math.log(self.d + 1) - math.log(num + 1)  # 计算每个词及对应的idf值

    def fit(self, raw_data_path):
        raw_data = read_csv(raw_data_path, filter_title=True)  # 读取原数据
        for index, text in raw_data:
            self.add_text(index, text)  # 累计df
        self.count_idf()  # 计算idf
        save_json(INDEX2WORDS_PATH, self.index2words)
        save_json(WORD2IDF_PATH, self.idf)


if __name__ == "__main__":
    idf_model = IdfModel()
    idf_model.fit(RAW_DATA_PATH)
