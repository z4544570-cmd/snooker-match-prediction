from pre_vector import agg_extract, get_data
from mode_recognition import get_win_sequence_dataset, analyze_top_sequences

if __name__ == "__main__":
    df_match, df_player, df_tournament = get_data()
    pre_vector, df_agg = agg_extract(df_match, df_tournament, df_player)

    for df in...
        sequences = get_win_sequence_dataset(df)
        analyze_top_sequences(sequences, top_n=30)