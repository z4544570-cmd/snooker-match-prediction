from prefect import flow
from pre_vector import get_data, agg_extract
from date_validation import data_validation
from mode_recognition import *

@flow
def main():
    df_match, df_player, df_tournament = get_data()
    pre_vector, df_agg = agg_extract(df_match, df_tournament, df_player)
    print(pre_vector["Mark Selby"])
    print(pre_vector["John Higgins"])
    data_validation(df_agg)
    various_matches_set = get_various_matches_set(df_agg)
    various_matches_set.append(df_agg)
    for df in various_matches_set:
        sequences = get_win_sequence_dataset(df)
        analyze_top_sequences(sequences, top_n=20)

if __name__ == "__main__":
    main()
