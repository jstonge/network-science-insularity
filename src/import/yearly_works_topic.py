from itertools import chain
import pandas as pd
from pyalex import Works, Authors
from time import sleep
from tqdm import tqdm

def main():
    
    # dyn_sync_networks = Works().filter(topics= {"id":"t11187"}, publication_year=2010)
    # works_dyn_sync = []
    # for w in chain(*dyn_sync_networks.paginate(per_page=200)):
    #     works_dyn_sync.append(w)

    # df_dyn=pd.DataFrame(works_dyn_sync)
    # df_dyn.to_parquet("dyn_sync_networks.parquet")

    for year in tqdm(range(1970, 2023)):
        stat_mech_networks = Works().filter(primary_topic= {"id":"t10064"}, publication_year=year)
        works_stat_mech = []
        for w in chain(*stat_mech_networks.paginate(per_page=200)):
            works_stat_mech.append(w)
        df_stat=pd.DataFrame(works_stat_mech)
        df_stat.to_parquet(f"primary_stat_mech_networks_{year}.parquet")
        sleep(2)


if __name__ == "__main__":
    main()
