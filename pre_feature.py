import numpy as np
import re
import pandas as pd
from tools import *

def get_max_deficit(score_str: str, player: str):

    frames = [f.strip() for f in str(score_str).split(";") if f.strip()]

    p_lead = 0
    max_deficit = 0

    for frame in frames:

        result = parse_frame_score(frame)

        # 跳过脏数据
        if result is None:
            continue

        s1, s2 = result

        if s1 > s2:
            p_lead += 1
        elif s2 > s1:
            p_lead -= 1
        else:
            continue

        if player == "player1":
            current_deficit = max(0, -p_lead)
        else:
            current_deficit = max(0, p_lead)

        max_deficit = max(max_deficit, current_deficit)

    return max_deficit

def get_max_streak(score_str: str, player: str):
    frames = [frame.strip() for frame in score_str.split(";")]
    # 当前连胜
    current_1 = 0
    current_2 = 0
    # 最大连胜
    max_1 = 0
    max_2 = 0
    # 上一局赢家
    last_winner = None
    for frame in frames:
        result = parse_frame_score(frame)

        # 跳过脏数据
        if result is None:
            continue

        s1, s2 = result
        # 判断本局赢家
        if s1 > s2:
            current_winner = "player1"
        elif s2 > s1:
            current_winner = "player2"
        else:
            continue
        # 更新连胜
        if current_winner == last_winner:
            if current_winner == "player1":
                current_1 += 1
            else:
                current_2 += 1
        else:
            if current_winner == "player1":
                current_1 = 1
                current_2 = 0
            else:
                current_2 = 1
                current_1 = 0
        # 更新最大值
        max_1 = max(max_1, current_1)
        max_2 = max(max_2, current_2)
        # 更新上一局赢家
        last_winner = current_winner
    if player == "player1":
        return max_1
    else:
        return max_2

def get_winm_mask(df):
    return np.where(df["player"] == df["player_1"],
                    df["player_1_score"] > df["player_2_score"],
                    df["player_2_score"] > df["player_1_score"]
                    ).sum()

def get_losem_mask(df):
    return np.where(df["player"] == df["player_1"],
                    df["player_1_score"] < df["player_2_score"],
                    df["player_2_score"] < df["player_1_score"]
                    ).sum()

def get_winf_mask(df):
    return np.where(df["player"] == df["player_1"],
                         df["player_1_score"],
                         df["player_2_score"]
                         ).sum()

def get_losef_mask(df):
    return np.where(df["player"] == df["player_2"],
                    df["player_1_score"],
                    df["player_2_score"]
                    ).sum()
def safe_div(a, b):
    return a / b if b != 0 else 0

def pre_feature(df):
    df = df[~df.astype(str).apply(lambda x: x.str.strip().isin(['', 'None', 'none'])).any(axis=1)]
    df = df.copy()
    p_dict = {}

    #转换为数值列类型
    df.loc[:, "player_1_score"] = pd.to_numeric(df["player_1_score"], errors='coerce')
    df.loc[:, "player_2_score"] = pd.to_numeric(df["player_2_score"], errors='coerce')
    df.loc[:, "best_of"] = pd.to_numeric(df["best_of"], errors='coerce')

    # 总胜场、败场、平场
    all_win_m = get_winm_mask(df)
    all_lose_m = get_losem_mask(df)
    all_tie_m = len(df) - all_win_m - all_lose_m
    # 总胜局、败局
    all_win_f = get_winf_mask(df)
    all_lose_f = get_losef_mask(df)

    # 当赛季、上赛季的df
    season_now = "2025-2026"
    year_int = int(season_now.strip().split("-")[0])
    prefix1 = str(year_int - 1)
    prefix2 = season_now.strip()
    df_last = df[df["season"].str.strip().str.startswith(prefix1, na = False)].copy()
    df_now = df[df["season"].str.strip().str.startswith(prefix2, na = False)].copy()

    # 上赛季胜场数，败场数
    l_win_m = get_winm_mask(df_last)
    l_lose_m = get_losem_mask(df_last)
    # 上赛季胜局数，败局数
    l_win_f = get_winf_mask(df_last)
    l_lose_f = get_losef_mask(df_last)
    # 当赛季胜场数，败场数
    n_win_m = get_winm_mask(df_now)
    n_lose_m = get_losem_mask(df_now)
    # 当赛季胜局数，败局数
    n_win_f = get_winf_mask(df_now)
    n_lose_f = get_losef_mask(df_now)

    # 转换列为数值类型
    df_last.loc[:, "player_1_score"] = pd.to_numeric(df_last["player_1_score"], errors='coerce')
    df_last.loc[:, "player_2_score"] = pd.to_numeric(df_last["player_2_score"], errors='coerce')
    df_last.loc[:, "best_of"] = pd.to_numeric(df_last["best_of"], errors='coerce')
    df_now.loc[:, "player_1_score"] = pd.to_numeric(df_now["player_1_score"], errors='coerce')
    df_now.loc[:, "player_2_score"] = pd.to_numeric(df_now["player_2_score"], errors='coerce')
    df_now.loc[:, "best_of"] = pd.to_numeric(df_now["best_of"], errors='coerce')

    # 决胜局胜率
    df_is_decider = df[(abs(df["player_1_score"] - df["player_2_score"]).astype(int) == 1) & ((df["player_1_score"] + df["player_2_score"]).astype(int) == df["best_of"].astype(int))].copy()
    all_decider_winrate = safe_div(get_winm_mask(df_is_decider), len(df_is_decider))
    # 上赛季决胜局胜率
    df_last_is_decider = df_last[(abs(df_last["player_1_score"] - df_last["player_2_score"]).astype(int) == 1) & ((df_last["player_1_score"] + df_last["player_2_score"]).astype(int) == df_last["best_of"].astype(int))].copy()
    last_decider_winrate = safe_div(get_winm_mask(df_last_is_decider), len(df_last_is_decider))
    # 当赛季决胜局胜率
    df_now_is_decider = df_now[(abs(df_now["player_1_score"] - df_now["player_2_score"]).astype(int) == 1) & ((df_now["player_1_score"] + df_now["player_2_score"]).astype(int) == df_now["best_of"].astype(int))].copy()
    now_decider_winrate = safe_div(get_winm_mask(df_now_is_decider), len(df_now_is_decider))

    # 长局值胜率
    long_df = df[df["best_of"].astype(int) >= 17].copy()
    long_winrate = safe_div(get_winm_mask(long_df), len(long_df))
    # 短局值胜率
    short_df = df[df["best_of"].astype(int) <= 11].copy()
    short_winrate = safe_div(get_winm_mask(short_df), len(short_df))

    #定义用来判断逆转、横扫、连鞭的变量
    df["max_behind"] = np.where(df["player"] == df["player_1"],
                                df["scores"].apply(lambda x: get_max_deficit(x, "player1")),
                                df["scores"].apply(lambda x: get_max_deficit(x, "player2"))
                                )
    df["max_ahead"] = np.where(df["player"] == df["player_1"],
                                df["scores"].apply(lambda x: get_max_deficit(x, "player1")),
                                df["scores"].apply(lambda x: get_max_deficit(x, "player2"))
                                )
    count_w = 0
    count_w_r = 0
    for index, row in df.iterrows():
        if row["player"] == row["player_1"]:
            if (row["player_1_score"] > row["player_2_score"]) and (row["player_2_score"] < 4):#如果横扫条件定义里直接包含胜的话可以不用and
                count_w += 1
            if (row["player_1_score"] < row["player_2_score"]) and (row["player_1_score"] < 4):#如果被横扫条件定义里直接包含胜的话可以不用and
                count_w_r += 1
        elif row["player"] == row["player_2"]:
            if (row["player_2_score"] > row["player_1_score"]) and (row["player_1_score"] < 4):#如果横扫条件定义里直接包含胜的话可以不用and
                count_w += 1
            if (row["player_2_score"] < row["player_1_score"]) and (row["player_2_score"] < 4):#如果被横扫条件定义里直接包含胜的话可以不用and
                count_w_r += 1
    #筛选出满足条件的match
    df_comeback = df[(df["max_behind"] > 5) & (df["best_of"] > 5)].copy()
    df_comeback_r = df[(df["max_ahead"] > 5) & (df["best_of"] > 5)].copy()

    # 逆转率和被逆转率（最大落后如何的情况下获胜的；最大领先如何的情况下落败的）
    comeback_rate = safe_div(get_winm_mask(df_comeback), len(df_comeback))
    comeback_rate_r = safe_div(get_losem_mask(df_comeback_r), len(df_comeback_r))
    #横扫率和被横扫率（获胜比赛中对手被横扫的；落败比赛中被对手横扫的）
    whitewash_rate = safe_div(count_w, get_winm_mask(df))
    whitewash_rate_r = safe_div(count_w_r, get_losem_mask(df))
    #连鞭率和被连鞭率（全部比赛中曾打出..的，全部比赛中曾被对手打出..的）
    df["streak"] = np.where(df["player"] == df["player_1"],
                          df["scores"].apply(lambda x: get_max_streak(x, "player1")),
                          df["scores"].apply(lambda x: get_max_streak(x, "player2"))
                          )
    df["streak_r"] = np.where(df["player"] == df["player_1"],
                          df["scores"].apply(lambda x: get_max_streak(x, "player2")),
                          df["scores"].apply(lambda x: get_max_streak(x, "player1"))
                          )
    streak_rate = safe_div(len(df[df["streak"] > 5]), len(df))
    streak_rate_r = safe_div(len(df[df["streak_r"] > 5]), len(df))

    #排名赛的match
    df_ranking = df[(df["category"] == "Ranking") | (df["category"] == "Minor Ranking")].copy()
    rankings_winrate = safe_div(get_winm_mask(df_ranking), len(df_ranking))
    df_ranking_final = df_ranking[df_ranking["stage"] == "Final"].copy()
    final_count = len(df_ranking_final)
    rankings = get_winm_mask(df_ranking_final) if len(df_ranking_final) > 0 else 0

    #写入字典
    p_dict['总胜场数'] = all_win_m
    p_dict['总平场数'] = all_tie_m
    p_dict['总胜局数'] = all_win_f
    p_dict['总胜败场比'] = all_win_m / all_lose_m if all_lose_m > 0 else 0
    p_dict['总胜败局比'] = all_win_f / all_lose_f if all_lose_f > 0 else 0
    p_dict['上赛季胜场数'] = l_win_m
    p_dict['上赛季胜局数'] = l_win_f
    p_dict['上赛季胜败场比'] = l_win_m / l_lose_m if l_lose_m > 0 else 0
    p_dict['上赛季胜败局比'] = l_win_f / l_lose_f if l_lose_f > 0 else 0
    p_dict['当赛季胜场数'] = n_win_m
    p_dict['当赛季胜局数'] = n_win_f
    p_dict['当赛季胜败场比'] = n_win_m / n_lose_m if n_lose_m > 0 else 0
    p_dict['当赛季胜败局比'] = n_win_f / n_lose_f if n_lose_f > 0 else 0
    p_dict['总决胜局胜率']  = all_decider_winrate
    p_dict['上赛季决胜局胜率'] = last_decider_winrate
    p_dict['当赛季决胜局胜率'] = now_decider_winrate
    p_dict['长局制（17及以上）胜率'] = long_winrate
    p_dict['短局制（11及以下）胜率'] = short_winrate
    p_dict['逆转率'] = comeback_rate
    p_dict['被逆转率'] = comeback_rate_r
    p_dict['横扫率'] = whitewash_rate
    p_dict['被横扫率'] = whitewash_rate_r
    p_dict['连鞭率'] = streak_rate
    p_dict['被连鞭率'] = streak_rate_r
    p_dict['排名赛'] = rankings
    p_dict['排名赛胜场率'] = rankings_winrate
    p_dict['排名赛决赛'] = final_count
    return p_dict


#场合，双方交手记录，是否主场
#如果像O'Sullivan这种生涯能力和近期能力不均衡的，如何处理？