import numpy as np
from numpy.ma.extras import ndenumerate
from scipy.stats import entropy
from sympy.codegen.ast import continue_

from pre_feature import parse_frame_score
from collections import Counter
import pandas as pd
from tqdm import tqdm
from tools import *
'''
def dataset_for_cluster(df):
    df = df[["match_id", "player_1_score", "player_2_score", "best_of", "scores"]].copy()

    # 过滤条件
    df = df[df["best_of"].astype(int) >= 7]
    df = df[~df["scores"].str.contains(r'[a-zA-Z]', na=False)]

    # 拆分每局比分
    df["scores"] = df["scores"].astype(str).str.split(";")
    df = df.explode("scores")
    df["scores"] = df["scores"].apply(parse_frame_score)
    df = df.dropna(subset=["scores"]).reset_index(drop=True)

    # 展开成分数列
    df[["p1_frame", "p2_frame"]] = pd.DataFrame(df["scores"].tolist(), index=df.index)
    df = df.drop(columns=["scores"])

    dataset = []

    for match_id, group in df.groupby("match_id"):
        if len(group) < 7:
            continue

        group = group.reset_index(drop=True)

        # 计算累计比分
        group["p1_win"] = (group["p1_frame"] > group["p2_frame"]).astype(int)
        group["player_1_score"] = group["p1_win"].cumsum()
        group["player_2_score"] = (1 - group["p1_win"]).cumsum()

        # 滑动窗口
        for i in range(len(group) - 6):
            window = group.iloc[i:i + 7]
            features = m_mode_reg_vectorized(window)
            dataset.append(list(features.values()))

    return dataset

def get_change(list):
    index_change = []
    for i in range(1, len(list)):
        if list[i] != list[i - 1]:
            index_change.append(i)
    changes = len(index_change)
    run_length = []
    if len(index_change) == 0:
        return [], [len(list)], 0
    for i in range(len(index_change) + 1):
        if i == 0:
            run_length.append(index_change[0])
        elif i == len(index_change):
            run_length.append(len(list) - index_change[-1])
        else:
            run_length.append(index_change[i] - index_change[i - 1])
    return index_change, run_length, changes


def m_mode_reg_vectorized(window):
    """向量化版本的 m_mode_reg，接收7局窗口"""
    df = window[["player_1_score", "player_2_score"]].copy()

    list1 = df["player_1_score"].values
    list2 = df["player_2_score"].values

    # 向量化计算每局胜负 (1=player1胜, 0=player2胜)
    win_1 = (np.diff(list1) == 1).astype(int)

    # ==================== get_change 向量化 ====================
    diff = np.diff(win_1)
    changes_idx = np.where(diff != 0)[0] + 1
    changes = len(changes_idx)

    if changes == 0:
        run_length = np.array([len(win_1)])
    else:
        starts = np.concatenate(([0], changes_idx))
        ends = np.concatenate((changes_idx, [len(win_1)]))
        run_length = ends - starts

    # ==================== 特征计算 ====================
    feature_dict = {
        "转换次数": int(changes),
        "转换分散度": float(np.std(changes_idx)) if changes > 1 else 0.0,
        "最大连续得分段": int(run_length.max()),
        "最小连续得分段": int(run_length.min()),
        "平均连续得分段": float(run_length.mean()),
        "得分段方差": float(run_length.var()),
        "熵": float(entropy(np.unique(run_length, return_counts=True)[1], base=2)),
        "首次转换位置": int(changes_idx[0]) if changes > 0 else 0,
        "最后一次转换位置": int(changes_idx[-1]) if changes > 0 else 0,
        "胜败局数差": int(abs(len(win_1) - 2 * win_1.sum())),
        "是否被追平": int(np.any(list1[1:] == list2[1:])),
        "最大差距": int(np.max(np.abs(list1 - list2))),
        "是否存在长连胜": int(run_length.max() >= 3)
    }
    return feature_dict
'''
#筛选各条件下的比赛df做模式EDA
def get_various_matches_set(df):
    """
    输入df_agg，返回一个列表，每个元素是特定条件下的df

    """
    df['decade'] = df["date"].apply(get_decade)
    df['period'] = df["date"].apply(get_date_period)
    various_set = []
    #三大赛
    pattern = r'\b\d{4}\s+Masters\b'
    df_TC = df[(df["tournament_name"].str.contains("World Championship|UK Championship")) | (df["tournament_name"].str.contains(pattern, regex = True, na = False))].copy()
    #普通排名赛
    df_Rankings = df[(df["category"] == "Rankings")].copy()
    df_Rankings = df_Rankings[~df_Rankings["tournament_name"].isin(df_TC["tournament_name"])].copy()
    #小型排名赛
    df_MinorRankings = df[df["category"] == "Minor Rankings"].copy()
    #邀请赛
    df_Invitational = df[df["category"] == "Invitational"].copy()
    #资格赛
    df_Qualifier = df[df["category"] == "Tour Qualifier"].copy()

    #决赛
    df_Final = df[df["stage"] == "Final"]
    #半决赛
    df_SemiFinal = df[df["stage"] == "Semi-final"]
    #1/4决赛
    df_last8 = df[df["stage"] == "Quarter-final"]
    #1/8决赛
    df_last16 = df[df["stage"] == "Last 16"]

    #BO
    df_BO17 = df[df["best_of"] == 17]
    df_BO19 = df[df["best_of"] == 19]
    df_BO25 = df[df["best_of"] == 25]
    df_BO33 = df[df["best_of"] == 33]
    df_BO35 = df[df["best_of"] == 35]

    df["decade"] = df["season"].apply(get_decade)

    #90s
    df_90s = df[df["decade"] == "90s"]
    #00s
    df_00s = df[df["decade"] == "00s"]
    #10s
    df_10s = df[df["decade"] == "10s"]
    #20s
    df_20s = df[df["decade"] == "20s"]

    df["period"] = df["dates"].apply(get_date_period)

    #赛季初
    df_front = df_Rankings[df_Rankings["period"] == "赛季前期"].copy()
    #中期
    df_middle = df_Rankings[df_Rankings["period"] == "赛季中期"].copy()
    #临世锦赛及世锦赛
    df_back = df_Rankings[df_Rankings["period"] == "临世锦赛及世锦赛时期"].copy()

    various_set.extend([df_TC, df_Invitational, df_Qualifier, df_Final, df_SemiFinal, df_last8, df_last16, df_BO17, df_BO19, df_BO25, df_BO33, df_BO35, df_90s, df_00s, df_10s, df_20s])
    return various_set

def get_win_sequence_dataset(df):
    """
    返回所有滑动窗口的 6局胜负序列
    0 = player1赢该局
    1 = player2赢该局
    """

    # =========================
    # 转为单行比赛格式
    # =========================
    df = turn_df_agg_into_single(df)

    df = df[
        ["match_id", "player_1_score",
         "player_2_score", "best_of", "scores"]
    ].copy()

    # =========================
    # 拆分 scores
    # =========================
    df["scores"] = (
        df["scores"]
        .astype(str)
        .str.split(";")
    )

    # 一局一行
    df = df.explode("scores")

    # parse
    df["scores"] = (
        df["scores"]
        .apply(parse_frame_score)
    )

    # =========================
    # 找出非法局
    # =========================
    mask = df["scores"].apply(
        lambda x:
        isinstance(x, tuple)
        and len(x) == 2
    )

    bad_rows = df.loc[~mask]

    if len(bad_rows) > 0:

        print("\n发现非法 scores 数据：")

        print(
            bad_rows[
                ["match_id", "scores"]
            ].head(50)
        )

    # =========================
    # 删除整场坏比赛
    # =========================
    bad_match_ids = (
        bad_rows["match_id"]
        .unique()
    )

    print(
        f"\n删除坏比赛数量: {len(bad_match_ids)}"
    )

    df = df[
        ~df["match_id"]
        .isin(bad_match_ids)
    ].copy()

    # =========================
    # 展开 tuple
    # =========================
    score_df = pd.DataFrame(
        df["scores"].tolist(),
        columns=["p1_frame", "p2_frame"],
        index=df.index
    )

    df = pd.concat(
        [df, score_df],
        axis=1
    )

    df = df.drop(columns=["scores"])

    # =========================
    # 每局胜负
    # =========================
    df["p1_win"] = (
        df["p1_frame"]
        > df["p2_frame"]
    ).astype(int)

    # =========================
    # 滑动窗口
    # =========================
    sequences = []

    grouped = df.groupby("match_id")

    print("\n正在处理滑动窗口...")

    for match_id, group in tqdm(
            grouped,
            total=len(grouped),
            desc="处理比赛"
    ):

        if len(group) < 7:
            continue

        win_series = (
            group["p1_win"]
            .values
        )

        for i in range(
                len(win_series) - 5
        ):

            seq = tuple(
                win_series[i:i + 6]
            )

            sequences.append(seq)
        sequences.append(1)

    return sequences


def analyze_top_sequences(sequences, top_n=32):
    """统计最常见的6局胜负序列，并考虑镜像对称"""

    def normalize(seq):
        if seq == 1:
            return None

        # 关键修复：强制转为 Python int
        seq = tuple(int(x) for x in seq)

        flipped = tuple(1 - x for x in seq)
        return min(seq, flipped)

    normalized = [normalize(seq) for seq in sequences if normalize(seq) is not None]
    count = Counter(normalized)

    print(f"\n总共生成 {len(sequences)} 个6局窗口")
    print(f"归一化后唯一模式数量: {len(count)} 个\n")

    print(f"前 {top_n} 最常见的6局胜负序列：")
    for seq, cnt in count.most_common(top_n):
        print(f"{cnt:6d} 次 | {seq}")

def get_single_seq(sequences):       #未做normalized，输出都是64个序列版本的
    """
    :param sequences: 一个列表，每个元素是一个元组seq（胜负序列）或1，1分隔开各场比赛
    :return: result: 一个列表，每个元素（一场比赛）是一个每个元素是一个元组(一个窗口)的列表
    :return: matrix_into_num: 一个np数组，与result类似，但元组按照字典被映射到了模式序号
    :return: mode_dict: 一个字典，键是窗口，值是模式序号，从1开始
    """
    def normalize(seq):
        if seq == 1:
            return 1
        else:
            flipped = tuple(1 - x for x in seq)
            seq = tuple(int(x) for x in seq)
        return min(flipped, seq)

    result = []
    current_group = []
    mode_dict = {}

    sequences = [normalize(seq) for seq in sequences]   # 因为get_single_seq函数仅用于模式分析，因此可以将sequences内的窗口都统一化，避免镜像

    for seq in sequences:
        if seq == 1:
            if current_group:
                result.append(current_group)
                current_group = []
        else:
            current_group.append(seq)           #current里面会有
            if seq not in mode_dict.keys():
                seq = tuple(int(x) for x in seq)
                mode_dict[seq] = len(mode_dict) + 1

    # mode_dict加应对(0, 0, 0, 0, 0, 0)的情况
    mode_dict[(2, 2, 2, 2, 2, 2)] = 1000

    #补齐result各行的长度
    max_length = max(len(row) for row in result)
    filled_result = []
    for row in result:
        padded_row = row + [(2, 2, 2, 2, 2, 2)] * (max_length - len(row))
        filled_result.append(padded_row)

    def match_no(list):
        return mode_dict[tuple(list)]

    #转成3维列表
    for i in range(len(filled_result)):
        for j in range(len(filled_result[i])):
            filled_result[i][j] = list(filled_result[i][j])
            filled_result[i][j] = match_no(filled_result[i][j])

    return filled_result, mode_dict

def get_change_time(list):
    """
    :param list:传入filled_result
    :return change:键是所有比赛出现过的转换，值是次数，如3-8: 6代表胜负序列3向胜负序列8转换过6次
    """
    change = {}
    def single_matrix(list):
        """
        :param: matrix_into_num的一个维度，即一场比赛
        :return:一个模式序号维度的np数组，每个位置是转化次数
        """
        result = [str(list[i-1]) + "-" + str(list[i]) for i in range(1, len(list)) if list[i] != 1000]
        for item in result:
            if item not in change.keys():
                change[item] = 1
            else:
                change[item] += 1

    for row in list:
        single_matrix(row)

    return change

def probability_matrix(dict1, dict2):  #dict1:change; dict2:mode_dict
    n = len(dict2)
    arr = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(n):
            arr[i, j] = dict1.get(f"{i+1}-{j+1}", 0)

    for i in range(n):
        if sum(arr[i, :]) != 0:
            arr[i, :] /= sum(arr[i, :])


    #for (i, j), value in np.ndenumerate(arr):
     #   if value != 0:
      #      print(f"模式{i+1}到模式{j+1}的转换概率：{value}")
    return arr

def get_probability(arr, dict):
    """
    根据输入的序列，从对应的转换概率数组中，匹配相应转换概率
    :param arr: 转换概率数组
    :return: 该模式转化成各模式的概率
    """
    reverse_mode_dict = {v:k for k, v in dict.items()}
    print(reverse_mode_dict)
    user_input = input("请输入模式，每个数字之间用空格隔开：")
    mode = tuple(map(int, user_input.split(" ")))
    mode_flipped = tuple(1-x for x in mode)
    mode = min(mode, mode_flipped)
    mode_no = dict[mode]
    for j, value in enumerate(arr[mode_no - 1]):
        if value != 0:
            print(f"转换成模式{reverse_mode_dict[j + 1]}的概率: {value}")



