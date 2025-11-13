import pandas as pd
import numpy as np

df = pd.read_parquet('data/ventas_diarias.parquet')
df['dias_desde_inicio'] = (pd.to_datetime(df['fecha']) - pd.to_datetime(df['fecha']).min()).dt.days
max_days = df['dias_desde_inicio'].max()

# Calcular pesos con diferentes decays
df['peso_15'] = np.exp((df['dias_desde_inicio'] - max_days) / 15)
df['peso_30'] = np.exp((df['dias_desde_inicio'] - max_days) / 30)

print("=== ANÁLISIS DE PESOS ===\n")
print("Con decay/15 (actual):")
print(f"  Último día: {df['peso_15'].iloc[-1]:.4f}")
print(f"  Hace 7 días: {df['peso_15'].iloc[-7]:.4f}")
print(f"  Hace 14 días: {df['peso_15'].iloc[-14]:.4f}")
print(f"  Hace 30 días: {df['peso_15'].iloc[-30]:.4f}")
print(f"  Mínimo: {df['peso_15'].min():.6f}")

print("\nCon decay/30 (anterior):")
print(f"  Último día: {df['peso_30'].iloc[-1]:.4f}")
print(f"  Hace 7 días: {df['peso_30'].iloc[-7]:.4f}")
print(f"  Hace 14 días: {df['peso_30'].iloc[-14]:.4f}")
print(f"  Hace 30 días: {df['peso_30'].iloc[-30]:.4f}")
print(f"  Mínimo: {df['peso_30'].min():.6f}")

print("\n=== ÚLTIMOS 7 DÍAS ===")
recent = df.tail(7)[['fecha', 'pizzas_vendidas', 'peso_15', 'peso_30']]
print(recent.to_string(index=False))

print(f"\nPromedio últimos 7 días: {df.tail(7)['pizzas_vendidas'].mean():.2f}")
print(f"Promedio ponderado (peso_15): {np.average(df.tail(7)['pizzas_vendidas'], weights=df.tail(7)['peso_15']):.2f}")
print(f"Promedio ponderado (peso_30): {np.average(df.tail(7)['pizzas_vendidas'], weights=df.tail(7)['peso_30']):.2f}")
