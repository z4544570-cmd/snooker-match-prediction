import pandas as pd

def input_live_stream(player_1: str, player_2: str):
    """
    live stream includes：本局双方局分，双方单杆；过去六局的胜负序列；双方名字；
    :return:
    """
    #输入live stream
    input_1 = player_1
    input_2 = player_2
    input_3 = input(f"请输入本局{input_1}总得分：")
    input_4 = input(f"请输入本局{input_2}总得分：")
    input_5 = input(f"请输入本局{input_1}单杆，如有2个单杆用逗号隔开，如无enter：")
    input_6 = input(f"请输入本局{input_2}单杆，如有2个单杆用逗号隔开，如无enter：")
    input_7 = "8 8 9" #input(f"请输入最近6局的胜负序列，{input_1}胜为1，{input_2}胜为0，用空格隔开：")
    input_8 = 9 #int(input("请输入BO："))
    input_9 =  1 #int(input(f"请输入当前{input_1}大比分："))
    input_10 =  2 #int(input(f"请输入当前{input_2}大比分："))


    #转成dataframe
    f_mode = [8, 8, 8]
    f_mode[-1] = (int(input_6),) if input_6 != "" else None
    f_mode[-2] = (int(input_5),) if input_5 != "" else None
    f_mode[0] = (int(input_3), int(input_4))
    f_mode = tuple(f_mode)
    m_mode = tuple(map(int, input_7.split(" ")))
    df = pd.DataFrame({
        "player1": input_1,
        "player2": input_2,
        "BO": input_8,
        "p1_m": input_9,
        "p2_m": input_10,
        "m_mode": (m_mode,),
        "f_mode": (f_mode,)
    })

    return df

