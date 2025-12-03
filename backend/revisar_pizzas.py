"""
Revisar datos de pizzas en detalle
"""
import pandas as pd

df = pd.read_parquet('data/ventas_diarias.parquet')
df['fecha'] = pd.to_datetime(df['fecha'])
df['dia_semana'] = df['fecha'].dt.dayofweek

dias = {0:'Lunes', 1:'Martes', 2:'Miércoles', 3:'Jueves', 4:'Viernes', 5:'Sábado', 6:'Domingo'}

# Solo ultimos 90 dias
df_recent = df.tail(90)

print("="*80)
print("ÚLTIMOS 90 DÍAS - PIZZAS POR DÍA DE SEMANA")
print("="*80)

for dia in [5, 6, 4, 0, 2, 3]:  # Sábado, Domingo, Viernes, etc
    subset = df_recent[df_recent['dia_semana'] == dia]
    if len(subset) > 0:
        print(f"\n{dias[dia].upper()}:")
        print(f"  Mediana: {subset['pizzas_vendidas'].median():.0f} pizzas")
        print(f"  Promedio: {subset['pizzas_vendidas'].mean():.0f} pizzas")
        print(f"  Min: {subset['pizzas_vendidas'].min():.0f}")
        print(f"  Max: {subset['pizzas_vendidas'].max():.0f}")
        print(f"  Últimos 5:")
        for _, row in subset.tail(5).iterrows():
            print(f"    {row['fecha'].strftime('%Y-%m-%d')}: {row['pizzas_vendidas']:.0f} pizzas (${row['total_ventas_dia']:,.0f})")

print("\n" + "="*80)
print("RELACIÓN PEDIDOS vs PIZZAS")
print("="*80)

# Ver si pedidos != pizzas (paquetes de 2)
df_recent['ratio'] = df_recent['pizzas_vendidas'] / df_recent['total_pedidos'].replace(0, 1)
print(f"Ratio promedio pizzas/pedidos: {df_recent['ratio'].mean():.2f}")
print("(Si es ~1 significa 1 pizza por pedido, si es >1 hay paquetes)")

# Revisar algunos dias especificos con alto volumen
print("\n" + "="*80)
print("DÍAS CON MÁS DE 80 PIZZAS (toda la historia)")
print("="*80)
df_high = df[df['pizzas_vendidas'] >= 80].sort_values('pizzas_vendidas', ascending=False)
print(f"Total días con 80+ pizzas: {len(df_high)}")
for _, row in df_high.head(15).iterrows():
    dia_nombre = dias[row['fecha'].weekday()]
    print(f"  {row['fecha'].strftime('%Y-%m-%d')} ({dia_nombre}): {row['pizzas_vendidas']:.0f} pizzas, {row['total_pedidos']:.0f} pedidos, ${row['total_ventas_dia']:,.0f}")

print("\n" + "="*80)
print("ANÁLISIS: ¿LOS DATOS TIENEN SENTIDO?")
print("="*80)

# Calcular precio promedio por pizza
df_recent['precio_por_pizza'] = df_recent['total_ventas_dia'] / df_recent['pizzas_vendidas'].replace(0, 1)
print(f"Precio promedio por pizza: ${df_recent['precio_por_pizza'].median():,.0f}")

# Ver si el total de ventas / pizzas es razonable
print("\nSi una pizza cuesta ~$200-300 promedio:")
print(f"  Con 67 pizzas x $250 = ${67*250:,}")
print(f"  Ventas reales domingo típico: ${df_recent[df_recent['dia_semana']==6]['total_ventas_dia'].median():,.0f}")

# Diferencia entre pizzas_vendidas y suma de tipos
print("\n" + "="*80)
print("VERIFICACIÓN: pizzas_vendidas vs suma de tipos")
print("="*80)
df_recent['suma_tipos'] = df_recent['pizzas_pastor'] + df_recent['pizzas_chuleta']
# Las pizzas normales no están desglosadas, solo pastor y chuleta
print("Nota: pizzas_vendidas incluye TODAS las pizzas")
print("      pizzas_pastor + pizzas_chuleta son solo algunos tipos")
print(f"Promedio pizzas totales: {df_recent['pizzas_vendidas'].mean():.0f}")
print(f"Promedio pastor+chuleta: {df_recent['suma_tipos'].mean():.0f}")
print(f"Diferencia (pizzas normales): {df_recent['pizzas_vendidas'].mean() - df_recent['suma_tipos'].mean():.0f}")
