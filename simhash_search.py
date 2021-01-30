# -*- coding: utf-8 -*-
"""
@Time    : 2021/1/5 19:02
@Author  : qijunhui
@File    : simhash_search.py
"""
from config import INDEX2SIMHASH_PATH, SIMILAR_PATH
from utils import save_csv
import csv
from tqdm import tqdm


class SimhashSearch(object):
    def __init__(self):
        self.index2simhash = {}
        with open(INDEX2SIMHASH_PATH, "r", encoding="utf-8") as fr:
            data_reader = csv.reader(fr)  # 逐行读取csv文件 迭代器变量
            next(data_reader)  # 过滤首行
            for index, simhash in data_reader:
                self.index2simhash[int(index)] = simhash
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
        with tqdm(desc="检索", total=len(self.index2simhash)) as bar:
            # 最简单的检索方法 两两比较
            for index_a, simhash_a in self.index2simhash.items():
                for index_b, simhash_b in self.index2simhash.items():
                    if index_b <= index_a:
                        continue
                    hanming = self.get_hanming(int(simhash_a, 2), int(simhash_b, 2))
                    if hanming <= 3:
                        self.similar.append((index_a, index_b, hanming))
                bar.update(1)  # 更新bar
        self.save()

    def binary_index_4part_3bin(self):
        # 检索海明距离在3以下的 建立两层索引 前一层是字典 第二层是列表 划分四段(8,8,8,8) 一段相同
        # 建立索引
        for index_first in range(0, 4):
            self.simhash_index[index_first] = {}
            for index_second in range(2 ** 8):
                self.simhash_index[index_first][index_second] = []
        with tqdm(desc="建立索引", total=len(self.index2simhash)) as bar:
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
                bar.update(1)  # 更新bar
        print("索引建立完毕")

    def fit_4part_3bin(self):
        # 建立索引
        self.binary_index_4part_3bin()
        with tqdm(desc="检索", total=len(self.index2simhash)) as bar:
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
                bar.update(1)  # 更新bar
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
        with tqdm(desc="建立索引", total=len(self.index2simhash)) as bar:
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
                bar.update(1)  # 更新bar
        print("索引建立完毕")

    def fit_5part_3bin(self):
        # 建立索引
        self.binary_index_5part_3bin()
        with tqdm(desc="检索", total=len(self.index2simhash)) as bar:
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
                bar.update(1)  # 更新bar
        self.save()

    def binary_index_6part_3bin(self):
        # 检索海明距离在3以下的 建立四层索引 前三层是字典 第四层是列表 划分六段(5,5,5,5,6,6) 三段相同
        # 建立索引
        for index_first in range(0, 20):
            self.simhash_index[index_first] = {}
            if index_first in [0, 1, 4, 10]:
                for index_second in range(2 ** 5):
                    self.simhash_index[index_first][index_second] = {}
                    for index_third in range(2 ** 5):
                        self.simhash_index[index_first][index_second][index_third] = {}
                        for index_fourth in range(2 ** 5):
                            self.simhash_index[index_first][index_second][index_third][index_fourth] = []
            elif index_first in [2, 3, 5, 6, 7, 8, 11, 12, 13, 14, 16, 17]:
                for index_second in range(2 ** 5):
                    self.simhash_index[index_first][index_second] = {}
                    for index_third in range(2 ** 5):
                        self.simhash_index[index_first][index_second][index_third] = {}
                        for index_fourth in range(2 ** 6):
                            self.simhash_index[index_first][index_second][index_third][index_fourth] = []
            else:
                for index_second in range(2 ** 5):
                    self.simhash_index[index_first][index_second] = {}
                    for index_third in range(2 ** 6):
                        self.simhash_index[index_first][index_second][index_third] = {}
                        for index_fourth in range(2 ** 6):
                            self.simhash_index[index_first][index_second][index_third][index_fourth] = []
        with tqdm(desc="建立索引", total=len(self.index2simhash)) as bar:
            # 添加索引
            for index, simhash in self.index2simhash.items():
                simhash_part = (
                    int("0b" + simhash[2:7], 2),
                    int("0b" + simhash[7:12], 2),
                    int("0b" + simhash[12:17], 2),
                    int("0b" + simhash[17:22], 2),
                    int("0b" + simhash[22:28], 2),
                    int("0b" + simhash[28:34], 2),
                )
                index_first = 0
                for second_temp in range(0, 4):
                    for third_temp in range(second_temp + 1, 5):
                        for fourth_temp in range(third_temp + 1, 6):
                            index_second = simhash_part[second_temp]
                            index_third = simhash_part[third_temp]
                            index_fourth = simhash_part[fourth_temp]
                            self.simhash_index[index_first][index_second][index_third][index_fourth].append(index)
                            index_first += 1
                bar.update(1)  # 更新bar
        print("索引建立完毕")

    def fit_6part_3bin(self):
        # 建立索引
        self.binary_index_6part_3bin()
        with tqdm(desc="检索", total=len(self.index2simhash)) as bar:
            # 检索海明距离在3以下的
            for index_a, simhash_a in self.index2simhash.items():
                # 取出待比较项
                compared = set()
                simhash_part = (
                    int("0b" + simhash_a[2:7], 2),
                    int("0b" + simhash_a[7:12], 2),
                    int("0b" + simhash_a[12:17], 2),
                    int("0b" + simhash_a[17:22], 2),
                    int("0b" + simhash_a[22:28], 2),
                    int("0b" + simhash_a[28:34], 2),
                )
                index_first = 0
                for second_temp in range(0, 4):
                    for third_temp in range(second_temp + 1, 5):
                        for fourth_temp in range(third_temp + 1, 6):
                            index_second = simhash_part[second_temp]
                            index_third = simhash_part[third_temp]
                            index_fourth = simhash_part[fourth_temp]
                            compared.update(self.simhash_index[index_first][index_second][index_third][index_fourth])
                            index_first += 1
                # 比较
                for index_b in compared:
                    if index_b <= index_a:
                        continue
                    hanming = self.get_hanming(int(simhash_a, 2), int(self.index2simhash[index_b], 2))
                    if hanming <= 3:
                        self.similar.append((index_a, index_b, hanming))
                bar.update(1)  # 更新bar
        self.save()

    def binary_index_8part_3bin(self):
        # 检索海明距离在3以下的 建立六层索引 前五层是字典 第六层是列表 划分八段(4,4,4,4,4,4,4,4) 五段相同
        # 建立索引
        for index_first in range(0, 56):
            self.simhash_index[index_first] = {}
            for index_second in range(2 ** 4):
                self.simhash_index[index_first][index_second] = {}
                for index_third in range(2 ** 4):
                    self.simhash_index[index_first][index_second][index_third] = {}
                    for index_fourth in range(2 ** 4):
                        self.simhash_index[index_first][index_second][index_third][index_fourth] = {}
                        for index_fifth in range(2 ** 4):
                            self.simhash_index[index_first][index_second][index_third][index_fourth][index_fifth] = {}
                            for index_sixth in range(2 ** 4):
                                self.simhash_index[index_first][index_second][index_third][index_fourth][index_fifth][
                                    index_sixth
                                ] = []
        with tqdm(desc="建立索引", total=len(self.index2simhash)) as bar:
            # 添加索引
            for index, simhash in self.index2simhash.items():
                simhash_part = (
                    int("0b" + simhash[2:6], 2),
                    int("0b" + simhash[6:10], 2),
                    int("0b" + simhash[10:14], 2),
                    int("0b" + simhash[14:18], 2),
                    int("0b" + simhash[18:22], 2),
                    int("0b" + simhash[22:26], 2),
                    int("0b" + simhash[26:30], 2),
                    int("0b" + simhash[30:34], 2),
                )
                index_first = 0
                for second_temp in range(0, 4):
                    for third_temp in range(second_temp + 1, 5):
                        for fourth_temp in range(third_temp + 1, 6):
                            for fifth_temp in range(fourth_temp + 1, 7):
                                for sixth_temp in range(fifth_temp + 1, 8):
                                    index_second = simhash_part[second_temp]
                                    index_third = simhash_part[third_temp]
                                    index_fourth = simhash_part[fourth_temp]
                                    index_fifth = simhash_part[fifth_temp]
                                    index_sixth = simhash_part[sixth_temp]
                                    self.simhash_index[index_first][index_second][index_third][index_fourth][
                                        index_fifth
                                    ][index_sixth].append(index)
                                    index_first += 1
                bar.update(1)  # 更新bar
        print("索引建立完毕")

    def fit_8part_3bin(self):
        # 建立索引
        self.binary_index_8part_3bin()
        with tqdm(desc="检索", total=len(self.index2simhash)) as bar:
            # 检索海明距离在3以下的
            for index_a, simhash_a in self.index2simhash.items():
                # 取出待比较项
                compared = set()
                simhash_part = (
                    int("0b" + simhash_a[2:6], 2),
                    int("0b" + simhash_a[6:10], 2),
                    int("0b" + simhash_a[10:14], 2),
                    int("0b" + simhash_a[14:18], 2),
                    int("0b" + simhash_a[18:22], 2),
                    int("0b" + simhash_a[22:26], 2),
                    int("0b" + simhash_a[26:30], 2),
                    int("0b" + simhash_a[30:34], 2),
                )
                index_first = 0
                for second_temp in range(0, 4):
                    for third_temp in range(second_temp + 1, 5):
                        for fourth_temp in range(third_temp + 1, 6):
                            for fifth_temp in range(fourth_temp + 1, 7):
                                for sixth_temp in range(fifth_temp + 1, 8):
                                    index_second = simhash_part[second_temp]
                                    index_third = simhash_part[third_temp]
                                    index_fourth = simhash_part[fourth_temp]
                                    index_fifth = simhash_part[fifth_temp]
                                    index_sixth = simhash_part[sixth_temp]
                                    compared.update(
                                        self.simhash_index[index_first][index_second][index_third][index_fourth][
                                            index_fifth
                                        ][index_sixth]
                                    )  # 根据域名的hash获取对比项
                                    index_first += 1
                # 比较
                for index_b in compared:
                    if index_b <= index_a:
                        continue
                    hanming = self.get_hanming(int(simhash_a, 2), int(self.index2simhash[index_b], 2))
                    if hanming <= 3:
                        self.similar.append((index_a, index_b, hanming))
                bar.update(1)  # 更新bar
        self.save()


if __name__ == "__main__":

    simhash_search = SimhashSearch()
    simhash_search.fit_convention()

    simhash_search = SimhashSearch()
    simhash_search.fit_4part_3bin()

    simhash_search = SimhashSearch()
    simhash_search.fit_5part_3bin()

    simhash_search = SimhashSearch()
    simhash_search.fit_6part_3bin()

    simhash_search = SimhashSearch()
    simhash_search.fit_8part_3bin()
