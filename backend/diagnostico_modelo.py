"""
Diagnóstico detallado del modelo
"""
import pandas as pd
import numpy as np
from pathlib import Path

# Cargar datos
df = pd.read_parquet('data/ventas_diarias.parquet')
df['fecha'] = pd.to_datetime(df['fecha'])
df['dia_semana'] = df['fecha'].dt.dayofweek

dias = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}

print("="*80)
print("🔍 DIAGNÓSTICO DETALLADO")
print("="*80)

# Filtrar anomalías primero
umbral = df['total_ventas_dia'].mean() * 0.30
df_clean = df[df['total_ventas_dia'] >= umbral]
print(f"\nDatos limpios: {len(df_clean)} de {len(df)} registros")
print(f"Umbral de anomalía: ${umbral:,.0f}")

# Últimos 90 días limpios
df_recent = df_clean.tail(90)

print("\n" + "="*80)
print("📊 MEDIANAS HISTÓRICAS POR DÍA (últimos 90 días limpios)")
print("="*80)

for dia in range(7):
    if dia == 1:  # Martes cerrado
        continue
    subset = df_recent[df_recent['dia_semana'] == dia]
    if len(subset) > 0:
        ventas_median = subset['total_ventas_dia'].median()
        pizzas_median = subset['pizzas_vendidas'].median()
        print(f"{dias[dia]:12} | n={len(subset):2} | Ventas: ${ventas_median:,.0f} | Pizzas: {pizzas_median:.0f}")

print("\n" + "="*80)
print("🎯 LO QUE DEBERÍA PREDECIR EL MODELO")
print("="*80)
print("Si el modelo está bien calibrado, debería predecir CERCA de las medianas:")

for dia in [3, 4, 5, 6, 0, 2]:  # Jueves a Miércoles
    subset = df_recent[df_recent['dia_semana'] == dia]
    if len(subset) > 0:
        ventas_median = subset['total_ventas_dia'].median()
        pizzas_median = subset['pizzas_vendidas'].median()
        ventas_p25 = subset['total_ventas_dia'].quantile(0.25)
        ventas_p75 = subset['total_ventas_dia'].quantile(0.75)
        print(f"{dias[dia]:12} | Esperado: ${ventas_median:,.0f} (rango: ${ventas_p25:,.0f}-${ventas_p75:,.0f}) | Pizzas: {pizzas_median:.0f}")

print("\n" + "="*80)
print("❌ PROBLEMA IDENTIFICADO")
print("="*80)
print("""
El modelo ML (LightGBM + Ridge) está prediciendo valores muy bajos porque:
1. Promedia TODOS los días, no solo el día específico de la semana
2. Los días débiles (Lunes, Miércoles, Jueves) jalan el promedio hacia abajo
3. El ensemble da 50% al histórico, pero 50% a modelos que predicen bajo

SOLUCIÓN: Usar 100% el histórico por día de semana (como hacía predictor_simple)
y solo usar ML para ajustes por eventos especiales.
""")
