import pandas as pd
from collections import Counter
from itertools import combinations
import numpy as np

def extract_subfield(x): 
    # we take the set of each field by paper
    return list(set([_['subfield']['display_name'] for _ in x]))

def extract_field(x): 
    # we take the set of each field by paper
    return list(set([_['field']['display_name'] for _ in x]))

cols2keep = ['id', 'doi', 'title', 'publication_year', 'topics', 'display_name', 'authorships', 'cited_by_count', 'keywords', 'grants']

df = pd.read_parquet("../stat_mech_networks.parquet")

subfield2field = {}
for topics in df.topics:
    for topic in topics:
        subfield2field[topic['subfield']['display_name']] = topic['field']['display_name']

df = df.loc[~df.title.duplicated(), cols2keep]

df['subfield'] = df.topics.map(lambda x: extract_subfield(x))
df['subfield_edge'] = df['subfield'].map(lambda x: list(combinations(x, 2)) if len(x) > 1 else [(x[0],x[0])])


# we now have duplicated titles when > 2 

tidy_df = df.explode('subfield_edge')

tidy_df['subfield_edge'] = tidy_df['subfield_edge'].map(lambda x: ";".join(list(x)))

tidy_df[['source', 'target']] = tidy_df.subfield_edge.str.split(";", expand=True)

tidy_df.drop(columns=['subfield_edge'], inplace=True)

tidy_df[['source', 'target']] = pd.DataFrame(np.sort(tidy_df[['source', 'target']], axis=1))

tidy_df['source_field'] = tidy_df['source'].map(lambda x: subfield2field[x])
tidy_df['target_field'] = tidy_df['target'].map(lambda x: subfield2field[x])

# aggregated_df = df.groupby(['source', 'target'], as_index=False)['value'].sum()

tidy_df.to_parquet("../../docs/data/stat_mech_networks_clean.parquet")


df=pd.read_parquet("../dyn_sync_networks.parquet")
df['subfield'] = df.topics.map(lambda x: extract_field(x))
df=df[~df.title.duplicated()][cols2keep]

df.to_parquet("../../docs/data/dyn_sync_networks_clean.parquet")