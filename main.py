import random
from prefect import flow
from pre_vector import get_data, agg_extract
from date_validation import data_validation
from m_mode_recognition import *
from f_mode_recognition import *
from p_base import *
from p_base_model import *
from tools import *
import matplotlib.pyplot as plt
from collections import Counter
import joblib
from input_livestream import *
from p_pattern_model import *
from Log_Odds_Evidence_Update import *
from prefect import flow
import joblib
import numpy as np


@flow
def main(mode: str = "train"):
    df_match, df_player, df_tournament = get_data()
    pre_vector, df_agg = agg_extract(df_match, df_tournament, df_player)
    df_agg = df_agg[(df_agg["player_1"].isin(pre_vector.keys())) &
                    (df_agg["player_2"].isin(pre_vector.keys()))]

    df_agg = turn_df_agg_into_single(df_agg)

    # 50%随机翻转数据增强
    for idx, row in df_agg.iterrows():
        if random.random() < 0.5:
            flipped_row = random_flip(row)
            df_agg.loc[idx] = flipped_row

    print("数据泄露检查：")
    print((df_agg["player_1_score"] > df_agg["player_2_score"]).mean())
    df_agg_copy = df_agg.copy()

    if mode == "train":
        print("=== 开始训练模式 ===")
        dataset_p_base_training, dataset_label = dataset_for_p_base(df_agg, pre_vector)
        dataset_p_pattern_training = dataset_for_p_pattern(df_agg_copy)

        print("=" * 50)
        print("长度检查：")
        print(len(dataset_p_base_training))
        print(len(dataset_label))
        print(len(dataset_p_pattern_training))
        print("=" * 50)

        model_2, importance_df_2, p_base = train_pattern_model(dataset_p_pattern_training, dataset_label)
        model_1, importance_df_1 = train_xgb(dataset_p_base_training, dataset_label)

        joblib.dump(model_1, 'p_base_model.pkl')
        print("✅ 模型已保存为 p_base_model.pkl")
        joblib.dump(model_2, 'p_pattern_model.pkl')
        print("✅ 模型已保存为 p_pattern_model.pkl")
        return model_1, model_2

    elif mode == "predict":
        print("=== 开始预测模式 ===")
        try:
            model_1 = joblib.load('p_base_model.pkl')
            print("✅ 已成功加载模型")
        except FileNotFoundError:
            print("❌ 未找到模型文件，请先运行 train 模式")
            return None

        try:
            model_2 = joblib.load('p_pattern_model.pkl')
            print("✅ 已成功加载模型")
        except FileNotFoundError:
            print("❌ 未找到模型文件，请先运行 train 模式")
            return None


        # 输入两名选手
        player1 = input("请输入球员1：")
        player2 = input("请输入球员2：")

        v1 = list(pre_vector[player1].values())
        v2 = list(pre_vector[player2].values())
        v = pre_vector_diff(v1, v2)  # 基础对战特征

        n = int(input("请输入需要预测的局数："))

        match = []
        proba1_list = []
        proba2_list = []
        p_post_list = []
        for i in range(n):
            df_mid = input_live_stream(player1, player2)  # 输入当前局实时数据
            match.append(df_mid["f_mode"][0])

            samples, indices = extract_match_samples(match)
            v3 = mid_vector(df_mid)

            if len(match) < 6:
                print(f"第 {i + 1} 局输入完成，从第6局开始产生预测结果...")
                continue

            # ====================== 模型预测 ======================
            X1 = np.array([v])  # p_base 特征
            X2 = np.array([samples[-1]])  # 模式识别特征

            proba_1 = model_1.predict_proba(X1)[0][1]  # p_base
            proba_2 = model_2.predict_proba(X2)[0][1]  # 模式识别

            p_post = log_odds_update(
                proba_1,
                proba_2,
                p_pattern_base=0.5,
                alpha=1.0,
                verbose=True
            )

            # 保存数据用于画图
            proba1_list.append(proba_1)
            proba2_list.append(proba_2)
            p_post_list.append(p_post)

            print(f"\n第 {i + 1} 局预测：")
            print(f"→ p_base      : {proba_1:.4f}")
            print(f"→ p_pattern   : {proba_2:.4f}")
            print(f"→ p_post      : {p_post:.4f} ({p_post * 100:.2f}%)")
            print("-" * 50)

        if len(p_post_list) > 0:
            plt.figure(figsize=(12, 7))

            x = range(6, 6 + len(p_post_list))  # 从第6局开始

            plt.plot(x, proba1_list, 'b--', label='p_base (基础模型)', linewidth=2, alpha=0.8)
            plt.plot(x, proba2_list, 'g--', label='p_pattern (模式识别)', linewidth=2, alpha=0.8)
            plt.plot(x, p_post_list, 'r-', label='p_post (Log-Odds 融合)', linewidth=3)

            plt.title(f'{player1} vs {player2} 逐局胜率变化趋势', fontsize=14)
            plt.xlabel('局数', fontsize=12)
            plt.ylabel('预测胜率', fontsize=12)
            plt.ylim(0, 1)
            plt.grid(True, alpha=0.3)
            plt.legend(fontsize=11)

            # 添加数据标签
            for i, (p1, p2, pp) in enumerate(zip(proba1_list, proba2_list, p_post_list)):
                plt.text(x[i], pp + 0.02, f'{pp:.3f}', ha='center', fontsize=9, color='red')

            plt.tight_layout()
            plt.show()
        else:
            print("没有足够局数进行预测画图。")

        return proba_1, proba_2, p_post

if __name__ == "__main__":
    main("train")
    main("predict")




    '''
        print(pre_vector["Mark Selby"])
        print(pre_vector["John Higgins"])
        print(pre_vector["Zhao Xintong"])
        print(pre_vector["Judd Trump"])
        data_validation(df_agg)
        various_matches_set = get_various_matches_set(df_agg)
        various_matches_set.append(df_agg)
        for i in range(len(various_matches_set)):
            print(f"第{i+1}个表:")
            print("前32高频模式分析（已去镜像）：")
            sequences = get_win_sequence_dataset(various_matches_set[i])
            analyze_top_sequences(sequences, top_n=32)
            print("该表序列与模式序号的对应关系：")
            filled_result, mode_dict = get_single_seq(sequences)
            print(mode_dict)
            change = get_change_time(filled_result)

            print("转换矩阵分析（已去镜像）")
            arr = probability_matrix(change, mode_dict)
            get_probability(arr, mode_dict)

        df = df_agg[df_agg["match_id"] == 92797]
        df = turn_into_frame_level(df)
        for index, row in df.iterrows():
            mode_list = f_mode_recognition(row)
            print("小比分模式：")
            print(row["scores"])
            print(mode_list)
        '''
