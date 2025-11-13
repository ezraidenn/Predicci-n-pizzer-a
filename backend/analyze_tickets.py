import pandas as pd
import numpy as np

df = pd.read_parquet('data/ventas_diarias.parquet')
df['fecha'] = pd.to_datetime(df['fecha'])
df['dia_semana'] = df['fecha'].dt.dayofweek
df['dia_nombre'] = df['fecha'].dt.day_name()

print("=" * 80)
print("ANÁLISIS DE COMPOSICIÓN DE TICKETS")
print("=" * 80)

# Calcular tickets promedio y ticket promedio
df['ticket_promedio'] = df['total_ventas_dia'] / (df['pizzas_vendidas'] + df['baguettes_vendidas'] + df['papas_gajo_vendidas'] + 0.1)

print("\n1. COMPOSICIÓN PROMEDIO:")
print("-" * 80)
print(f"Pizzas por día: {df['pizzas_vendidas'].mean():.1f}")
print(f"Baguettes por día: {df['baguettes_vendidas'].mean():.1f}")
print(f"Papas por día: {df['papas_gajo_vendidas'].mean():.1f}")
print(f"Total productos por día: {(df['pizzas_vendidas'] + df['baguettes_vendidas'] + df['papas_gajo_vendidas']).mean():.1f}")
print(f"Ventas por día: ${df['total_ventas_dia'].mean():,.0f}")
print(f"Ticket promedio: ${df['ticket_promedio'].mean():.2f}")

print("\n2. RELACIÓN ENTRE PRODUCTOS:")
print("-" * 80)
print(f"Correlación Pizzas-Ventas: {df['pizzas_vendidas'].corr(df['total_ventas_dia']):.3f}")
print(f"Correlación Baguettes-Ventas: {df['baguettes_vendidas'].corr(df['total_ventas_dia']):.3f}")
print(f"Correlación Papas-Ventas: {df['papas_gajo_vendidas'].corr(df['total_ventas_dia']):.3f}")
print(f"Correlación Pizzas-Baguettes: {df['pizzas_vendidas'].corr(df['baguettes_vendidas']):.3f}")
print(f"Correlación Pizzas-Papas: {df['pizzas_vendidas'].corr(df['papas_gajo_vendidas']):.3f}")

print("\n3. PROPORCIONES POR DÍA DE SEMANA:")
print("-" * 80)
dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
for i, dia in enumerate(dias):
    data_dia = df[df['dia_semana'] == i]
    if len(data_dia) > 0:
        total_productos = data_dia['pizzas_vendidas'] + data_dia['baguettes_vendidas'] + data_dia['papas_gajo_vendidas']
        pct_pizzas = (data_dia['pizzas_vendidas'] / total_productos * 100).mean()
        pct_baguettes = (data_dia['baguettes_vendidas'] / total_productos * 100).mean()
        pct_papas = (data_dia['papas_gajo_vendidas'] / total_productos * 100).mean()
        
        print(f"\n{dia}:")
        print(f"  Pizzas: {data_dia['pizzas_vendidas'].mean():.1f} ({pct_pizzas:.1f}%)")
        print(f"  Baguettes: {data_dia['baguettes_vendidas'].mean():.1f} ({pct_baguettes:.1f}%)")
        print(f"  Papas: {data_dia['papas_gajo_vendidas'].mean():.1f} ({pct_papas:.1f}%)")
        print(f"  Ventas: ${data_dia['total_ventas_dia'].mean():,.0f}")

print("\n4. ÚLTIMOS 20 DÍAS (DATOS ACTUALES):")
print("-" * 80)
ultimos = df.tail(20)[['fecha', 'dia_nombre', 'pizzas_vendidas', 'baguettes_vendidas', 'papas_gajo_vendidas', 'total_ventas_dia']]
ultimos['total_prods'] = ultimos['pizzas_vendidas'] + ultimos['baguettes_vendidas'] + ultimos['papas_gajo_vendidas']
print(ultimos.to_string(index=False))

print("\n5. ¿SON INDEPENDIENTES LAS VARIABLES?")
print("-" * 80)
print("Si correlación baja → Son independientes → Entrenar por separado")
print("Si correlación alta → Están relacionadas → Pueden compartir features")
print(f"\nPizzas-Baguettes: {df['pizzas_vendidas'].corr(df['baguettes_vendidas']):.3f} ", end="")
print("(Baja → Independientes)" if abs(df['pizzas_vendidas'].corr(df['baguettes_vendidas'])) < 0.5 else "(Alta → Relacionadas)")

print(f"Pizzas-Papas: {df['pizzas_vendidas'].corr(df['papas_gajo_vendidas']):.3f} ", end="")
print("(Baja → Independientes)" if abs(df['pizzas_vendidas'].corr(df['papas_gajo_vendidas'])) < 0.5 else "(Alta → Relacionadas)")

print(f"Baguettes-Papas: {df['baguettes_vendidas'].corr(df['papas_gajo_vendidas']):.3f} ", end="")
print("(Baja → Independientes)" if abs(df['baguettes_vendidas'].corr(df['papas_gajo_vendidas'])) < 0.5 else "(Alta → Relacionadas)")

print("\n6. PRECIOS IMPLÍCITOS:")
print("-" * 80)
# Calcular precios dividiendo ventas entre productos
df_clean = df[df['pizzas_vendidas'] > 0].copy()
precio_impl_pizza = (df_clean['total_ventas_dia'] / df_clean['pizzas_vendidas']).median()
print(f"Precio implícito pizza (mediana): ${precio_impl_pizza:.2f}")

df_clean = df[df['baguettes_vendidas'] > 0].copy()
precio_impl_baguette = (df_clean['total_ventas_dia'] / df_clean['baguettes_vendidas']).median()
print(f"Precio implícito baguette (mediana): ${precio_impl_baguette:.2f}")

df_clean = df[df['papas_gajo_vendidas'] > 0].copy()
precio_impl_papas = (df_clean['total_ventas_dia'] / df_clean['papas_gajo_vendidas']).median()
print(f"Precio implícito papas (mediana): ${precio_impl_papas:.2f}")

print("\n" + "=" * 80)
