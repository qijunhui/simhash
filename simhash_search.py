# -*- coding: utf-8 -*-
"""
@Time    : 2021/1/5 19:02
@Author  : qijunhui
@File    : simhash_search.py
"""
from config import INDEX2SIMHASH_PATH, SIMILAR_PATH
from utils import read_csv, save_csv


class SimhashSearch(object):
    def __init__(self):
        self.index2simhash = dict(
            zip(
                [int(index) for index, simhash in read_csv(INDEX2SIMHASH_PATH, filter_title=True)],
                [simhash for index, simhash in read_csv(INDEX2SIMHASH_PATH, filter_title=True)],
            )
        )
        self.simhash_index = {}  # 存储索引，优化时间
        self.similar = []  # 存储最终结果

    def get_hanming(self, simhash_int_a, simhash_int_b):
        # 最简单计算汉明距离的方法 事实证明这样耗时更短
        xor_simhash = simhash_int_a ^ simhash_int_b  # 异或
        return bin(xor_simhash).count("1")

    def get_hanming_bak(self, simhash_int_a, simhash_int_b):
        # 另一种计算汉明距离的方法 事实证明这样耗时长
        xor_simhash = simhash_int_a ^ simhash_int_b  # 异或
        counter = 0
        while xor_simhash:  # 求异或结果中'1'的个数
            counter += 1
            xor_simhash &= xor_simhash - 1
        return counter

    def fit_convention(self):
        for index_a, simhash_a in self.index2simhash.items():
            for index_b, simhash_b in self.index2simhash.items():
                if index_b <= index_a:
                    continue
                hanming = self.get_hanming(int(simhash_a, 2), int(simhash_b, 2))
                if hanming <= 3:
                    self.similar.append((index_a, index_b, hanming))
        save_csv(SIMILAR_PATH, self.similar, columns=("index_a", "index_b", "hanming"))


if __name__ == "__main__":
    simhash_search = SimhashSearch()
    simhash_search.fit_convention()
