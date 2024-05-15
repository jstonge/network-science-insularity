import pandas as pd

cols2keep = ['id', 'doi', 'title', 'publication_year', 'display_name', 'authorships', 'cited_by_count', 'topics', 'keywords', 'grants']

df=pd.read_parquet("../stat_mech_networks.parquet")

df=df[~df.title.duplicated()][cols2keep]

df.to_parquet("../../docs/data/stat_mech_networks_clean.parquet")

df=pd.read_parquet("../dyn_sync_networks.parquet")

df=df[~df.title.duplicated()][cols2keep]

df.to_parquet("../../docs/data/dyn_sync_networks_clean.parquet")