import pandas as pd
import glob

all_ = glob.glob("./*.csv")

df1 = pd.read_csv(all_[0], index_col=False)
dfs = [pd.read_csv(i, index_col=False) for i in all_[1:]]

result=df1.append(dfs)
result.fillna("NA")
result.to_csv('result.csv', index=False)
