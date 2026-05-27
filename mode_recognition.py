import numpy as np
from scipy.stats import entropy
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

    various_set.extend([df_TC, df_Rankings, df_MinorRankings, df_Invitational, df_Qualifier, df_Final, df_SemiFinal, df_last8, df_last16, df_BO17, df_BO19, df_BO25, df_BO33, df_BO35, df_90s, df_00s, df_10s, df_20s, df_front, df_middle, df_back])
    return various_set

def get_win_sequence_dataset(df):
    """
    返回所有滑动窗口的 6局胜负序列
    0 = player1赢该局
    1 = player2赢该局
    """

    # 转为单行比赛格式
    df = turn_df_agg_into_single(df)

    # 只保留需要列
    df = df[
        ["match_id", "player_1_score", "player_2_score", "best_of", "scores"]
    ].copy()

    # =========================
    # 拆分 scores
    # =========================
    df["scores"] = df["scores"].astype(str).str.split(";")

    # 一局一行
    df = df.explode("scores")

    # parse_frame_score:
    # 正常返回 (p1_frame, p2_frame)
    # 异常返回 None
    df["scores"] = df["scores"].apply(parse_frame_score)

    # 删除 None
    df = df.dropna(subset=["scores"])

    # =========================
    # 检查非法 scores
    # =========================
    mask = df["scores"].apply(
        lambda x: isinstance(x, tuple) and len(x) == 2
    )

    bad_rows = df.loc[~mask]

    if len(bad_rows) > 0:
        print("\n发现非法 scores 数据：")
        print(
            bad_rows.loc[:, ["match_id", "scores"]]
            .head(50)
        )

    # 只保留合法 tuple
    df = df.loc[mask].copy()

    # =========================
    # 展开 tuple
    # =========================
    score_df = pd.DataFrame(
        df["scores"].tolist(),
        columns=["p1_frame", "p2_frame"],
        index=df.index
    )

    df = pd.concat([df, score_df], axis=1)

    # 删除原始 scores
    df = df.drop(columns=["scores"])

    # =========================
    # 每局胜负
    # =========================
    df["p1_win"] = (
        df["p1_frame"] > df["p2_frame"]
    ).astype(int)

    # =========================
    # 滑动窗口
    # =========================
    sequences = []

    grouped = df.groupby("match_id")

    print("正在处理所有比赛的滑动窗口...")

    for match_id, group in tqdm(
            grouped,
            total=len(grouped),
            desc="处理比赛"
    ):

        # 至少需要7局
        if len(group) < 7:
            continue

        win_series = group["p1_win"].values

        # 长度6窗口
        for i in range(len(win_series) - 5):

            seq = tuple(
                win_series[i:i + 6]
            )

            sequences.append(seq)

    return sequences


def analyze_top_sequences(sequences, top_n=20):
    """统计最常见的6局胜负序列，并考虑镜像对称"""

    def normalize(seq):
        seq = tuple(int(x) for x in seq)
        flipped = tuple(1 - x for x in seq)
        return min(seq, flipped)

    normalized = [normalize(seq) for seq in sequences]
    count = Counter(normalized)

    print(f"\n总共生成 {len(sequences)} 个6局窗口")
    print(f"归一化后唯一模式数量: {len(count)} 个\n")

    print(f"前 {top_n} 最常见的6局胜负序列：")
    for seq, cnt in count.most_common(top_n):
        flipped = tuple(1 - x for x in seq)
        print(f"{cnt:6d} 次 | {seq}")
