import pandas as pd

df = pd.read_parquet('data/ventas_diarias.parquet')

print("=== BAGUETTES ===")
print("\nUltimos 14 dias:")
print(df.tail(14)[['fecha', 'baguettes_vendidas', 'total_ventas_dia']].to_string(index=False))

print("\n=== ESTADISTICAS BAGUETTES ===")
print(f"Min: {df['baguettes_vendidas'].min()}")
print(f"Max: {df['baguettes_vendidas'].max()}")
print(f"Promedio: {df['baguettes_vendidas'].mean():.2f}")
print(f"Std: {df['baguettes_vendidas'].std():.2f}")

print("\n=== ESTADISTICAS VENTAS ===")
print(f"Min: ${df['total_ventas_dia'].min():.2f}")
print(f"Max: ${df['total_ventas_dia'].max():.2f}")
print(f"Promedio: ${df['total_ventas_dia'].mean():.2f}")
print(f"Std: ${df['total_ventas_dia'].std():.2f}")

print("\n=== VARIACION POR DIA DE SEMANA ===")
df['dia_semana'] = pd.to_datetime(df['fecha']).dt.dayofweek
dias = ['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab', 'Dom']
for i, dia in enumerate(dias):
    data_dia = df[df['dia_semana'] == i]
    print(f"{dia}: Baguettes={data_dia['baguettes_vendidas'].mean():.1f}, Ventas=${data_dia['total_ventas_dia'].mean():.0f}")
