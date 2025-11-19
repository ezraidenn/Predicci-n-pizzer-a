import sqlite3
import pandas as pd

# Revisar BD
conn = sqlite3.connect('data/pizzeria_max.db')
cursor = conn.cursor()

print("="*60)
print("COLUMNAS EN BASE DE DATOS")
print("="*60)
cursor.execute('PRAGMA table_info(ventas_diarias)')
for row in cursor.fetchall():
    print(f"  {row[1]:30} {row[2]}")

print("\n" + "="*60)
print("EJEMPLO DE DATOS")
print("="*60)
df = pd.read_sql_query("SELECT * FROM ventas_diarias LIMIT 3", conn)
print(df.to_string())

conn.close()

# Revisar Parquet
print("\n" + "="*60)
print("COLUMNAS EN PARQUET")
print("="*60)
df_parquet = pd.read_parquet('data/ventas_diarias.parquet')
print(df_parquet.columns.tolist())
print("\nEjemplo:")
print(df_parquet.head(3).to_string())
