import pandas as pd
import csv

df = pd.read_csv('data/products.csv', on_bad_lines='skip', engine='python', quotechar='"')
print(f"Rows loaded: {len(df)}")
print(f"Columns: {df.columns.tolist()}")
df.to_csv('data/products.csv', index=False, quoting=csv.QUOTE_ALL)
print("Done!")