import pandas as pd
import numpy as np

df = pd.read_parquet('data/ventas_diarias.parquet')
df['fecha'] = pd.to_datetime(df['fecha'])
df['dia_semana'] = df['fecha'].dt.dayofweek
df['dia_nombre'] = df['fecha'].dt.day_name()

print("=" * 80)
print("ANÁLISIS DE PATRONES REALES")
print("=" * 80)

print("\n1. VENTAS POR DÍA DE SEMANA:")
print("-" * 80)
dias_nombres = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
for i, dia in enumerate(dias_nombres):
    data_dia = df[df['dia_semana'] == i]
    if len(data_dia) > 0:
        print(f"\n{dia}:")
        print(f"  Ventas:    ${data_dia['total_ventas_dia'].mean():>8,.0f} (min: ${data_dia['total_ventas_dia'].min():,.0f}, max: ${data_dia['total_ventas_dia'].max():,.0f})")
        print(f"  Pizzas:    {data_dia['pizzas_vendidas'].mean():>8.1f} (min: {data_dia['pizzas_vendidas'].min()}, max: {data_dia['pizzas_vendidas'].max()})")
        print(f"  Baguettes: {data_dia['baguettes_vendidas'].mean():>8.1f} (min: {data_dia['baguettes_vendidas'].min()}, max: {data_dia['baguettes_vendidas'].max()})")
        print(f"  Papas:     {data_dia['papas_gajo_vendidas'].mean():>8.1f} (min: {data_dia['papas_gajo_vendidas'].min()}, max: {data_dia['papas_gajo_vendidas'].max()})")

print("\n" + "=" * 80)
print("2. CORRELACIÓN PIZZAS vs VENTAS:")
print("-" * 80)
print(f"Correlación: {df['pizzas_vendidas'].corr(df['total_ventas_dia']):.3f}")
print(f"\nPrecio promedio por pizza: ${df['total_ventas_dia'].sum() / df['pizzas_vendidas'].sum():.2f}")

# Análisis de precio por pizza por día
print("\n3. PRECIO POR PIZZA POR DÍA:")
print("-" * 80)
df['precio_por_pizza'] = df['total_ventas_dia'] / (df['pizzas_vendidas'] + 0.1)
for i, dia in enumerate(dias_nombres):
    data_dia = df[df['dia_semana'] == i]
    if len(data_dia) > 0:
        print(f"{dia}: ${data_dia['precio_por_pizza'].mean():.2f} por pizza")

print("\n" + "=" * 80)
print("4. ÚLTIMOS 20 DÍAS (PATRONES RECIENTES):")
print("-" * 80)
ultimos = df.tail(20)[['fecha', 'dia_nombre', 'total_ventas_dia', 'pizzas_vendidas', 'baguettes_vendidas', 'papas_gajo_vendidas']]
print(ultimos.to_string(index=False))

print("\n" + "=" * 80)
print("5. FIN DE SEMANA vs ENTRE SEMANA:")
print("-" * 80)
fin_semana = df[df['dia_semana'].isin([5, 6])]  # Sábado, Domingo
entre_semana = df[~df['dia_semana'].isin([5, 6])]

print("\nFIN DE SEMANA (Sábado-Domingo):")
print(f"  Ventas promedio: ${fin_semana['total_ventas_dia'].mean():,.0f}")
print(f"  Pizzas promedio: {fin_semana['pizzas_vendidas'].mean():.1f}")
print(f"  Baguettes promedio: {fin_semana['baguettes_vendidas'].mean():.1f}")

print("\nENTRE SEMANA (Lun-Vie):")
print(f"  Ventas promedio: ${entre_semana['total_ventas_dia'].mean():,.0f}")
print(f"  Pizzas promedio: {entre_semana['pizzas_vendidas'].mean():.1f}")
print(f"  Baguettes promedio: {entre_semana['baguettes_vendidas'].mean():.1f}")

print("\nDIFERENCIA:")
print(f"  Ventas: {(fin_semana['total_ventas_dia'].mean() / entre_semana['total_ventas_dia'].mean() - 1) * 100:.1f}% más en fin de semana")
print(f"  Pizzas: {(fin_semana['pizzas_vendidas'].mean() / entre_semana['pizzas_vendidas'].mean() - 1) * 100:.1f}% más en fin de semana")

print("\n" + "=" * 80)
print("6. DÍAS QUE ROZAN 20K:")
print("-" * 80)
dias_20k = df[df['total_ventas_dia'] >= 18000]
print(f"\nTotal de días con ventas >= $18,000: {len(dias_20k)}")
print(dias_20k[['fecha', 'dia_nombre', 'total_ventas_dia', 'pizzas_vendidas']].to_string(index=False))
