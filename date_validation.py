from tools import *

def data_validation(df):
    #检查match_id是否都对应2行，检查各列在一个match_id内是否除player和nationality以外都相同
    for match_id, group in df.groupby("match_id"):
        if len(group) != 2:
            print("以下match_id非2行：")
            print(f"{match_id}, {len(group)}")
            continue
        for col in group.columns:
            if col in ["player"]:
                if group[col].nunique() != 2:
                    print(f"{match_id}, {col}, {group[col].nunique()}")
            elif col in ["nationality"]:
                continue
            else:
                if group[col].nunique() != 1:
                    print(f"{match_id}, {col}, {group[col].nunique()}")

    print(df.dtypes)
    report = missing_value_report(df)
    print(report)
    print("bestof是否合法；")
    print(df["best_of"].value_counts())

    print("比分是否合法：")
    bad_score = df[df["player_1_score"] + df["player_2_score"] > df["best_of"]]
    print(bad_score)
    print("是否达到胜利条件：")
    need_win = df["best_of"] // 2 + 1
    bad_finish = df[df[["player_1_score", "player_2_score"]].max(axis=1) != need_win]
    print(bad_finish)

    print("scores是否合法？")
    bad_scores = df[df["player_1_score"] + df["player_2_score"] != df["scores"].apply(valid_scores_num)]
    print("scores与双方大比分不符：")
    print(bad_scores)

    print("重复：")
    duplicates = df.duplicated(keep = False)
    print(duplicates.any())

    print("邀请赛包括:")
    print(df[df["category"] == "Invitational"]["tournament_name"].unique())


def clean_id(df):

    illegal_match_id = []
    bad_score = df[df["player_1_score"] + df["player_2_score"] > df["best_of"]]
    illegal_match_id.extend(bad_score["match_id"].tolist())

    need_win = df["best_of"] // 2 + 1
    bad_finish = df[df[["player_1_score", "player_2_score"]].max(axis = 1) != need_win]
    illegal_match_id.extend(bad_finish["match_id"].tolist())

    bad_scores = df[df["player_1_score"] + df["player_2_score"] != df["scores"].apply(valid_scores_num)]
    illegal_match_id.extend(bad_scores["match_id"].tolist())

    illegal_match_id = list(set(illegal_match_id))

    df = df[~df["match_id"].isin(illegal_match_id)].copy()
    return df
