from input_livestream import *

def get_streaks(m_mode):
    n = len(m_mode)

    last_value = m_mode[-1]
    streak_1 = 0

    i = n - 1
    while i >= 0 and m_mode[i] == last_value:
        streak_1 += 1
        i -= 1

    if i < 0:
        return streak_1, 0

    second_value = m_mode[i]
    streak_2 = 0

    while i >= 0 and m_mode[i] == second_value:
        streak_2 += 1
        i -= 1

    return streak_1, streak_2

def mid_vector(df):
    """
    构造mid_vector
    :param df: live stream
    :return: mid_vector
    includes: 此刻大比分分差， 局制， 还差几局赢， 是否赛点， 是否决胜局， 最近连胜， 最近3局胜率
    """
    m_mode = df["m_mode"].iloc[0]

    current_m_diff = (abs(df["p1_m"] - df["p2_m"])).iloc[0]
    BO = df["BO"].iloc[0]
    frame_to_win_1 = ((BO // 2) + 1 - df["p1_m"]).iloc[0]
    frame_to_win_2 = ((BO // 2) + 1 - df["p2_m"]).iloc[0]

    #是否赛点
    match_point_1 = int(frame_to_win_1 == 1)
    match_point_2 = int(frame_to_win_2 == 1)

    #是否决胜局
    decider = int((frame_to_win_1 == 1) & (frame_to_win_2 == 1))

    #最近连胜
    streak_1, streak_2 = get_streaks(m_mode)

    if m_mode[-1] == 0:
        temp = streak_1
        streak_1 = streak_2
        streak_2 = temp

    #最近3局胜率
    m_mode_list = df["m_mode"].iloc[0]
    win_rate3_1 = sum(m_mode_list[-3:]) / 3
    win_rate3_2 = 1 - win_rate3_1

    #当前领先方
    leader = 0
    if df["p1_m"].iloc[0] > df["p2_m"].iloc[0]:
        leader = 1
    elif df["p1_m"].iloc[0] < df["p2_m"].iloc[0]:
        leader = 2

    #窗口内最大分差，为正
    diff = []
    p1 = df["p1_m"].iloc[0]
    p2 = df["p2_m"].iloc[0]
    max_diff = p1 - p2
    diff.append(max_diff)
    for i in range(1, len(m_mode)):
        if m_mode[-i] == 1:
            p1 -= 1
        elif m_mode[-i] == 0:
            p2 -= 1
        current_diff = p1 - p2
        diff.append(current_diff)
        signed_max_diff = max(diff, key=lambda x: abs(x))

    mid_vector = [current_m_diff, BO, frame_to_win_1, frame_to_win_2, match_point_1, match_point_2, decider, streak_1, streak_2, win_rate3_1, win_rate3_2, leader, signed_max_diff]
    return mid_vector

#mid:
#Cancel: BO, win_rate3_1
#Add: 最近6局净胜局，最近3局得分差，最近N局单杆能力，