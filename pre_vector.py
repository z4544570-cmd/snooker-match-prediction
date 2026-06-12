import sqlite3
from tools import *
from pre_feature import *
from date_validation import *

def get_data():
    conn = sqlite3.connect(r"C:\Users\赵梓健\PyCharmMiscProject\snooker predict\snookerdb\Database\snookerdb.db")

    df_match = pd.read_sql_query('''
        SELECT * 
        FROM matches
        ''', conn)

    df_player = pd.read_sql_query('''
        SELECT * 
        FROM players
        ''', conn)

    df_tournament = pd.read_sql_query('''
        SELECT * 
        FROM tournament
        ''', conn)

    return df_match, df_player, df_tournament

def name_concat(df):
    df['name'] = df['first_name'].str.strip() + ' ' + df["surname"].str.strip()
    df = df.drop(columns=['first_name', 'surname', 'url'])
    return df

def clean(df):
    df["best_of"] = pd.to_numeric(df["best_of"], errors="coerce")
    df = df[(df["best_of"] != 0) & (df["best_of"] != 1)]
    return df

def agg_extract(df1, df2, df3):#比赛，赛事，球员
    trn_list = ["Ranking", "Minor Ranking", "Tour Qualifier", "Invitational"]

    # 准备球员表
    players = name_concat(df3)
    name_cancel_list = ["Lewis John Calcutt", "Harry D Thomson", "Jack AP Holmes", "So Man Yan"]
    players = players[~players["name"].isin(name_cancel_list)]

    # 处理比赛表
    df1 = clean(df1)
    df1 = df1.assign(both_player=lambda x: x[["player_1", "player_2"]].values.tolist())
    df1 = df1.drop(columns=["player_1_url", "player_2_url"])
    df1 = df1[df1["walkover"] != "True"]

    #处理赛事表
    tour_cancel_list = ["1993 European Open", "1999 British Open", "2003 Challenge Tour - Event 2", "2007 PIOS - Event 4", "2007 PIOS - Event 5", "2013 European Tour - Event 6", "2020 European Masters", "2020 World Grand Prix", "2022 European Masters", "2023 Snooker Shoot Out", "1978 Pot Black", "1979 Bombay International", "1980 Classic", "2021 Championship League", "2022 Championship League", "2023 Championship League", "2024 Championship League", "2025 Championship League"]
    df2 = df2[~df2["name"].isin(tour_cancel_list)]

    df1 = df1[
        df1["player_1"].notna() &
        df1["player_2"].notna()
    ]

    df1 = df1[
        (df1["player_1"] != "") &
        (df1["player_2"] != "")
    ]

    # Explode 展开成每行一个球员
    df1 = df1.explode("both_player")
    bad_match_ids = df1[
        df1["player_1"].isin(name_cancel_list) |
        df1["player_2"].isin(name_cancel_list)
    ]["match_id"].unique()

    df1 = df1[~df1["match_id"].isin(bad_match_ids)]

    # 重命名方便后续处理
    df1 = df1.rename(columns={"both_player": "player"})

    # 关联球员信息（国籍等）
    df1 = df1.merge(
        players[['name', 'nationality']],
        left_on='player',
        right_on='name',
        how='left'
    )
    df1 = df1.drop(columns=['name'])

    # 筛选需要的赛事类型
    df2 = df2.drop(columns=['url'])
    df2 = df2[df2["category"].isin(trn_list)]
    df2 = df2.rename(columns={"name": "tournament_name"})

    # Join 赛事信息
    df_agg = df1.join(df2.set_index('tourn_id'), on='tourn_id', how='inner')


    df_agg = df_agg[df_agg["scores"].apply(valid_scores)].copy()


    for col in df_agg.columns:
        if col in ["tourn_id", "match_id", "player_1_score", "player_2_score", "best_of"]:
            df_agg[col] = pd.to_numeric(df_agg[col], errors="coerce")
        if col in ["stage", "player_1", "player_2", "scores", "walkover", "player", "dates", "tournament_name", "season", "category"]:
            df_agg[col] = df_agg[col].astype("string").str.strip()

    df_agg = clean_id(df_agg)

    print(df_agg.columns)

    all_b_raw = df_agg[["tournament_name"]].drop_duplicates().reset_index(drop=True)
    all_b_raw.to_csv("all_b_raw.csv", index=False, encoding="utf-8-sig")

    # ==================== 建立 pre_vector 字典 ====================
    pre_vector = {}

    # 按球员分组，key 为球员名
    for player_name, group in df_agg.groupby('player'):
        if len(group) <= 100:
            continue
        pre_vector[player_name] = pre_feature(group)
    return pre_vector, df_agg  # 可以同时返回 df_agg 供后续使用







