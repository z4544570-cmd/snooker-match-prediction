import pandas as pd
import numpy as np
from tools import *

def break_category(tuple):
    """
    输入scores后两个中的一个
    :param tuple:
    :return:
    """
    if int(tuple[0]) == 147:
        return "147"
    elif (int(tuple[0]) < 147) and (int(tuple[0]) >= 140):
        return "140+"
    elif (int(tuple[0]) < 140) and (int(tuple[0]) >= 130):
        return "130+"
    elif (int(tuple[0]) < 130) and (int(tuple[0]) >= 120):
        return "120+"
    elif (int(tuple[0]) < 120) and (int(tuple[0]) >= 110):
        return "110+"
    elif (int(tuple[0]) < 110) and (int(tuple[0]) >= 100):
        return "100+"
    elif (int(tuple[0]) < 100) and (int(tuple[0]) >= 90):
        return "90+"
    elif (int(tuple[0]) < 90) and (int(tuple[0]) >= 80):
        return "80+"
    elif (int(tuple[0]) < 80) and (int(tuple[0]) >= 70):
        return "70+"
    elif (int(tuple[0]) < 70) and (int(tuple[0]) >= 60):
        return "60+"
    elif (int(tuple[0]) < 60) and (int(tuple[0]) >= 50):
        return "50+"

def get_frame_style_both_break(tuple):
    """
    传入parse后的元组，这个元组第一个元素是s1s2元组，第二三个元素是1、2的单杆元组
    :param tuple:
    :return:
    """
    if (int(tuple[-2][0]) > int(tuple[-1][0])) and (int(tuple[0][0]) > int(tuple[0][1])):
        #单杆高的胜
        return "双方单杆型逆转/逆转失败"
    elif (int(tuple[-2][0]) > int(tuple[-1][0])) and (int(tuple[0][0]) < int(tuple[0][1])):
        #单杆高的败
        return "前单杆+后缠斗胜"
    elif (int(tuple[-2][0]) < int(tuple[-1][0])) and (int(tuple[0][0]) > int(tuple[0][1])):
        return "前单杆+后缠斗胜"
    elif (int(tuple[-2][0]) < int(tuple[-1][0])) and (int(tuple[0][0]) < int(tuple[0][1])):
        return "双方单杆型逆转/逆转失败"
    else:
        #双方单杆相同
        return "双方单杆相同"


def get_frame_style_single_break(tuple, num):#元组，1，2
    """
    传入元组，传出一方有单杆的情况下的小比分模式分类
    :param tuple: 
    :param int: 有单杆方在元组（s1，s2）的索引，0或1
    :return:
    """
    if len(tuple[num - 2]) == 2:
        #一方有两个单杆
        return "crushing"
    elif tuple[0][num] < tuple[0][1 - num]:
        #有单杆的一方败
        return "单杆打不过零碎节奏，单杆败"
    else:
        tup_1 = tuple[num - 2][0]
        tup_2 = tuple[0][1 - num]
        #有单杆的一方胜
        if int(tup_1) >= 70:
            #高分
            return "Crushing"
        elif int(tup_2) < 20:#[0][1],即2是败方，则indexNone是1；[0][0],即1是败方，indexNone是0
            #低分，且败方分数太低
            return "Crushing"
        else:
            #低分，且败方分数不低
            return "相持"

def turn_into_frame_level(df):
    """
    输入df_agg, 输出处理好后的
    :param df:
    :return:
    """
    df = turn_df_agg_into_single(df)
    df["scores"] = df["scores"].str.split(";")
    #转成局级别
    df = df.explode("scores")
    #parse后，变成一个3元素元组，第一个元素是s1,s2元组，第二三个元素是1和2的break元组，无则None
    df["scores"] = df["scores"].apply(parse_frame_score_keep_break)

    return df

def f_mode_recognition(df):
    """
    输入某个match_id对应的一场比赛，得出模式列表
    :param df:
    :return:
    """
    mode_list = []
    #1的单杆；2的单杆；净差；局风格
    if df["scores"][-2] is None and df["scores"][-1] is None:
        mode_list[0:2] = ["无单杆", "无单杆"]
        mode_list.append(abs(df["scores"][0][0] - df["scores"][0][1]))
        mode_list.append("相持型")
    elif (df["scores"][-2] is None) and (df["scores"][-1] is not None):
        break_category_2 = break_category(df["scores"][-1])
        mode_list.append("无单杆")
        mode_list.append(break_category_2)
        mode_list.append(abs(df["scores"][0][0] - df["scores"][0][1]))
        frame_style = get_frame_style_single_break(df["scores"], 1)
        mode_list.append(frame_style)
    elif (df["scores"][-2] is not None) and (df["scores"][-1] is None):
        break_category_1 = break_category(df["scores"][-2])
        mode_list.append(break_category_1)
        mode_list.append("无单杆")
        mode_list.append(abs(df["scores"][0][0] - df["scores"][0][1]))
        frame_style = get_frame_style_single_break(df["scores"], 0)
        mode_list.append(frame_style)
    else:
        break_category_1 = break_category(df["scores"][-2])
        break_category_2 = break_category(df["scores"][-1])
        mode_list.append(break_category_1)
        mode_list.append(break_category_2)
        margin = abs(df["scores"][0][0] - df["scores"][0][1])
        mode_list.append(margin)
        #局风格：
        frame_style = get_frame_style_both_break(df["scores"])
        mode_list.append(frame_style)

    return mode_list