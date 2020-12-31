# -*- coding: utf-8 -*-
"""
@Time    : 2020/12/31 18:56
@Author  : qijunhui
@File    : text2simhash.py
"""
import hashlib
from concurrent.futures import ThreadPoolExecutor
from config import INDEX2WORDS_PATH, WORD2IDF_PATH, INDEX2SIMHASH_PATH
from utils import read_json, save_csv


class Text2Simhash(object):
    def __init__(self):
        self.simhash_length = 32  # 32 or 64 or 128
        self.index2simhash = {}
        self.word2idf = read_json(WORD2IDF_PATH)

    def word2md5(self, word):
        md5 = hashlib.md5()  # 获取MD5对象
        md5.update(word.encode("utf-8"))
        return md5.hexdigest()  # 32位十六进制

    def words2simhash(self, words):
        total = sum(words.values())  # 获取对比文档长度
        simhash_lst = [0] * self.simhash_length
        for word, num in words.items():
            word_md5 = int(self.word2md5(word)[8:16], 16)
            word_score = self.word2idf[word] * num / total
            # print(word, word_md5, word_score)
            for i in range(self.simhash_length):
                if word_md5 & 1:
                    simhash_lst[self.simhash_length - (i + 1)] += word_score
                else:
                    simhash_lst[self.simhash_length - (i + 1)] -= word_score
                word_md5 >>= 1
        simhash = "0b" + "".join(["1" if item > 0 else "0" for item in simhash_lst])
        return simhash

    def fit(self, thread=1):
        index2words = read_json(INDEX2WORDS_PATH)
        if thread <= 1:
            for index, words in index2words.items():
                self.index2simhash[index] = self.words2simhash(words)
            save_csv(
                INDEX2SIMHASH_PATH,
                [(index, simhash) for index, simhash in self.index2simhash.items()],
                columns=("index", "simhash"),
            )
        else:
            index_lst = [index for index, words in index2words.items()]
            with ThreadPoolExecutor(thread) as executor:
                simhash_lst = list(executor.map(self.words2simhash, [words for index, words in index2words.items()]))
            save_csv(INDEX2SIMHASH_PATH, list(zip(index_lst, simhash_lst)), columns=("index", "simhash"))


if __name__ == "__main__":
    text2simhash = Text2Simhash()
    text2simhash.fit(thread=1000)
