#includes dataset and model training
import pandas as pd
from tools import *
import math
from pre_vector import *
from mid_vector import *
from p_pattern import *

def pre_vector_diff(v1:list, v2:list):
    v = []
    log = [0, 1, 2, 5, 6, 9, 10, 24, 26]#计数项取对数差，比率项取diff
    for i in range (len(v1)):
        if i in log:
            v.append(math.log(1 + v1[i], 2) - math.log(1 + v2[i], 2))
        else:
            v.append(v1[i] - v2[i])
    return v


def random_flip(row: pd.Series) -> pd.Series:
    """随机翻转一场比赛的双方信息"""
    row = row.copy()  # 重要：避免修改原数据

    # 交换选手和比分
    row["player_1_score"], row["player_2_score"] = row["player_2_score"], row["player_1_score"]
    row["player_1"], row["player_2"] = row["player_2"], row["player_1"]

    # 交换 scores（关键修复）
    if isinstance(row["scores"], str):
        row["scores"] = switch_score(row["scores"])

    return row


def dataset_for_p_base(df, vector):
    """
    赛前向量和赛中向量，赛前向量或许可以改造一下，diff/ratio
    :param df: df_agg
    :return: two list, X, Y.
    """
    dataset_p_base_training = []
    dataset_label = []

    #转成局级别
    df["scores"] = df["scores"].str.split(";")
    df = df.explode("scores")
    df["scores"] = df["scores"].apply(parse_frame_score_keep_break)

    #scores清洗
    bad_ids = df[df["scores"].apply(lambda x: pd.isna(x[0]))]["match_id"]
    df = df[~df["match_id"].isin(bad_ids)]

    df["scores"] = df["scores"].apply(lambda x: [x[0]])

    for match_id, group in df.groupby("match_id"):
        p1_m, p2_m = 0, 0
        sequence = []

        rows = list(group.iterrows())
        for i, (_, row) in enumerate(rows):
            v1 = vector[f"{row['player_1']}"]
            v2 = vector[f"{row['player_2']}"]

            #赛中向量
            if row["scores"][0][0] > row["scores"][0][1]:
                p1_m += 1
                sequence.append(1)
            else:
                p2_m += 1
                sequence.append(0)

            #前5局构造不出特征，最后一局没有下一局，都不要
            if len(sequence) < 6:
                continue
            if i == len(rows) - 1:
                continue

            df_mid = pd.DataFrame({
                "player1": row['player_1'],
                "player2": row['player_2'],
                "BO": row['best_of'],
                "p1_m": p1_m,
                "p2_m": p2_m,
                "m_mode": [sequence[-6:]],
                "f_mode": (row["scores"],)
            })
            v3 = mid_vector(df_mid)

            #检查v1,v2,v3类型：dict,dict,list,转化格式作为向量存入data
            v1 = list(v1.values())
            v2 = list(v2.values())
            v = pre_vector_diff(v1, v2)

            data1 = v
            dataset_p_base_training.append(data1)

        if len(sequence) > 6:
            dataset_label.append(sequence[6:]) #，标签说下一局胜负，因此取这场比赛的第7-最后一局

    dataset_label = [item for sublist in dataset_label for item in sublist]
    return dataset_p_base_training, dataset_label

def dataset_for_p_pattern(df):
    dataset_p_pattern_training = []

    #转成局级别
    df["scores"] = df["scores"].str.split(";")
    df = df.explode("scores")
    df["scores"] = df["scores"].apply(parse_frame_score_keep_break)

    #scores清洗
    bad_ids = df[df["scores"].apply(lambda x: pd.isna(x[0]))]["match_id"]
    df = df[~df["match_id"].isin(bad_ids)]

    #每场比赛的第六局至最后一局做成列表
    for match_id, group in df.groupby("match_id"):
        match_frames = []
        for idx, row in group.iterrows():
            match_frames.append(row["scores"])

        data = build_training_data(match_frames)
        for item in data:
            dataset_p_pattern_training.append(item)

    return dataset_p_pattern_training



def build_training_data(frames_data, min_frames=2):
    """
    frames_data: 一场完整比赛
    return: X
    """
    samples, indices = extract_match_samples(frames_data, min_frames)
    # 直接从第5个（索引4）开始取
    dataset_p_pattern_training = []
    for features, i in zip(samples[4:], indices[4:]):  # 切片从索引4开始
        if i >= len(frames_data):
            break
        dataset_p_pattern_training.append(features)
    return dataset_p_pattern_training