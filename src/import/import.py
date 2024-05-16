from itertools import chain
import pandas as pd
from pyalex import Works, Authors


def main():
    dyn_sync_networks = Works().filter(topics= {"id":"t11187"})
    works_dyn_sync = []
    for w in chain(*dyn_sync_networks.paginate(per_page=200)):
        works_dyn_sync.append(w)

    df_dyn=pd.DataFrame(works_dyn_sync)
    df_dyn.to_parquet("dyn_sync_networks.parquet")

    stat_mech_networks = Works().filter(topics= {"id":"t10064"})
    works_stat_mech = []
    for w in chain(*stat_mech_networks.paginate(per_page=200)):
        works_stat_mech.append(w)
    df_stat=pd.DataFrame(works_stat_mech)
    df_stat.to_parquet("stat_mech_networks.parquet")

if __name__ == "__main__":
    main()
