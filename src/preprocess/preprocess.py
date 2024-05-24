import pandas as pd
from collections import Counter
from itertools import combinations
import numpy as np
from pathlib import Path
import argparse

def extract_subfield(x): 
    # we take the set of each field by paper
    return list(set([_['subfield']['display_name'] for _ in x]))

def extract_field(x): 
    # we take the set of each field by paper
    return list(set([_['field']['display_name'] for _ in x]))

def parse_args():
    parser = argparse.ArgumentParser("Data Downloader")
    parser.add_argument(
        "-t", "--topic", type=str, help="topic id", required=True
    )
    parser.add_argument(
        "-o", "--output", type=Path, help="output directory", required=True
    )
    return parser.parse_args()

def main():
    cols2keep = ['id', 'doi', 'title', 'publication_year', 'topics', 'display_name', 'authorships', 'cited_by_count', 'keywords', 'grants']

    args = parse_args()
    # topic_id = "t10064"
    topic_id = args.topic
    output = args.output
    input_f = Path("data") / f"{topic_id}.parquet"
    df = pd.read_parquet(input_f)
    print(len(df))
    subfield2field = {}
    for topics in df.topics:
        for topic in topics:
            subfield2field[topic['subfield']['display_name']] = topic['field']['display_name']

    df = df.loc[~df.title.duplicated(), cols2keep]

    df['subfield'] = df.topics.map(lambda x: extract_subfield(x))
    df['subfield_edge'] = df['subfield'].map(lambda x: list(combinations(x, 2)) if len(x) > 1 else [(x[0],x[0])])


    tidy_df = df.explode('subfield_edge')

    tidy_df['subfield_edge'] = tidy_df['subfield_edge'].map(lambda x: ";".join(list(x)))

    tidy_df[['source', 'target']] = tidy_df.subfield_edge.str.split(";", expand=True)

    tidy_df.drop(columns=['subfield_edge'], inplace=True)

    tidy_df[['source', 'target']] = pd.DataFrame(np.sort(tidy_df[['source', 'target']], axis=1))

    # add mapping from source/target subfield -> field
    tidy_df['source_field'] = tidy_df['source'].map(lambda x: subfield2field[x])
    tidy_df['target_field'] = tidy_df['target'].map(lambda x: subfield2field[x])

    tidy_df.to_parquet(output / f"{topic_id}_clean.parquet")

if __name__ == "__main__":
    main()