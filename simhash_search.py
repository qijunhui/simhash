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

    def get_hanming_another(self, simhash_int_a, simhash_int_b):
        # 另一种计算汉明距离的方法 事实证明这样耗时长
        xor_simhash = simhash_int_a ^ simhash_int_b  # 异或
        counter = 0
        while xor_simhash:  # 求异或结果中'1'的个数
            counter += 1
            xor_simhash &= xor_simhash - 1
        return counter

    def save(self):
        save_csv(SIMILAR_PATH, self.similar, columns=("index_a", "index_b", "hanming"))

    def fit_convention(self):
        # 最简单的检索方法 两两比较
        for index_a, simhash_a in self.index2simhash.items():
            for index_b, simhash_b in self.index2simhash.items():
                if index_b <= index_a:
                    continue
                hanming = self.get_hanming(int(simhash_a, 2), int(simhash_b, 2))
                if hanming <= 3:
                    self.similar.append((index_a, index_b, hanming))
        self.save()

    def binary_index_4part_3bin(self):
        # 检索海明距离在3以下的 建立两层索引 前一层是字典 第二层是列表 划分四段(8,8,8,8) 一段相同
        # 建立索引
        for index_first in range(0, 4):
            self.simhash_index[index_first] = {}
            for index_second in range(2 ** 8):
                self.simhash_index[index_first][index_second] = []
        # 添加索引
        for index, simhash in self.index2simhash.items():
            simhash_part = (
                int("0b" + simhash[2:10], 2),
                int("0b" + simhash[10:18], 2),
                int("0b" + simhash[18:26], 2),
                int("0b" + simhash[26:34], 2),
            )
            index_first = 0
            for second_temp in range(0, 4):
                index_second = simhash_part[second_temp]
                self.simhash_index[index_first][index_second].append(index)
                index_first += 1
        print("索引建立完毕")

    def fit_4part_3bin(self):
        # 建立索引
        self.binary_index_4part_3bin()
        # 检索海明距离在3以下的
        for index_a, simhash_a in self.index2simhash.items():
            # 取出待比较项
            compared = set()
            simhash_part = (
                int("0b" + simhash_a[2:10], 2),
                int("0b" + simhash_a[10:18], 2),
                int("0b" + simhash_a[18:26], 2),
                int("0b" + simhash_a[26:34], 2),
            )
            index_first = 0
            for second_temp in range(0, 4):
                index_second = simhash_part[second_temp]
                compared.update(self.simhash_index[index_first][index_second])
                index_first += 1
            # 比较
            for index_b in compared:
                if index_b <= index_a:
                    continue
                hanming = self.get_hanming(int(simhash_a, 2), int(self.index2simhash[index_b], 2))
                if hanming <= 3:
                    self.similar.append((index_a, index_b, hanming))
        self.save()

    def binary_index_5part_3bin(self):
        # 检索海明距离在3以下的 建立三层索引 前两层是字典 第三层是列表 划分五段(6,6,6,7,7) 两段相同
        # 建立索引
        for index_first in range(0, 10):
            self.simhash_index[index_first] = {}
            if index_first in [0, 1, 4]:
                for index_second in range(2 ** 6):
                    self.simhash_index[index_first][index_second] = {}
                    for index_third in range(2 ** 6):
                        self.simhash_index[index_first][index_second][index_third] = []
            elif index_first in [2, 3, 5, 6, 7, 8]:
                for index_second in range(2 ** 6):
                    self.simhash_index[index_first][index_second] = {}
                    for index_third in range(2 ** 7):
                        self.simhash_index[index_first][index_second][index_third] = []
            else:
                for index_second in range(2 ** 7):
                    self.simhash_index[index_first][index_second] = {}
                    for index_third in range(2 ** 7):
                        self.simhash_index[index_first][index_second][index_third] = []
        # 添加索引
        for index, simhash in self.index2simhash.items():
            simhash_part = (
                int("0b" + simhash[2:8], 2),
                int("0b" + simhash[8:14], 2),
                int("0b" + simhash[14:20], 2),
                int("0b" + simhash[20:27], 2),
                int("0b" + simhash[27:34], 2),
            )
            index_first = 0
            for second_temp in range(0, 4):
                for third_temp in range(second_temp + 1, 5):
                    index_second = simhash_part[second_temp]
                    index_third = simhash_part[third_temp]
                    self.simhash_index[index_first][index_second][index_third].append(index)
                    index_first += 1
        print("索引建立完毕")

    def fit_5part_3bin(self):
        # 建立索引
        self.binary_index_5part_3bin()
        # 检索海明距离在3以下的
        for index_a, simhash_a in self.index2simhash.items():
            # 取出待比较项
            compared = set()
            simhash_part = (
                int("0b" + simhash_a[2:8], 2),
                int("0b" + simhash_a[8:14], 2),
                int("0b" + simhash_a[14:20], 2),
                int("0b" + simhash_a[20:27], 2),
                int("0b" + simhash_a[27:34], 2),
            )
            index_first = 0
            for second_temp in range(0, 4):
                for index_third in range(second_temp + 1, 5):
                    index_second = simhash_part[second_temp]
                    index_third = simhash_part[index_third]
                    compared.update(self.simhash_index[index_first][index_second][index_third])
                    index_first += 1
            # 比较
            for index_b in compared:
                if index_b <= index_a:
                    continue
                hanming = self.get_hanming(int(simhash_a, 2), int(self.index2simhash[index_b], 2))
                if hanming <= 3:
                    self.similar.append((index_a, index_b, hanming))
        self.save()


if __name__ == "__main__":
    import time

    st = time.time()
    simhash_search = SimhashSearch()
    simhash_search.fit_convention()
    print(time.time() - st)

    st = time.time()
    simhash_search = SimhashSearch()
    simhash_search.fit_4part_3bin()
    print(time.time() - st)

    st = time.time()
    simhash_search = SimhashSearch()
    simhash_search.fit_5part_3bin()
    print(time.time() - st)
