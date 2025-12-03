"""
Script para verificar que las predicciones tengan sentido
Compara con datos históricos
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
print("📊 ANÁLISIS DE DATOS HISTÓRICOS")
print("="*80)
print(f"Total registros: {len(df)}")
print(f"Rango: {df['fecha'].min().date()} a {df['fecha'].max().date()}")

print("\n" + "="*80)
print("📅 PROMEDIOS POR DÍA DE LA SEMANA (últimos 60 días)")
print("="*80)

df_recent = df.tail(60)

promedios_historicos = {}
for dia in range(7):
    subset = df_recent[df_recent['dia_semana'] == dia]
    if len(subset) > 0:
        ventas_mean = subset['total_ventas_dia'].mean()
        ventas_median = subset['total_ventas_dia'].median()
        ventas_std = subset['total_ventas_dia'].std()
        pizzas_mean = subset['pizzas_vendidas'].mean()
        n = len(subset)
        promedios_historicos[dia] = {
            'ventas_mean': ventas_mean,
            'ventas_median': ventas_median,
            'pizzas_mean': pizzas_mean
        }
        print(f"{dias[dia]:12} | n={n:2} | Ventas: ${ventas_mean:,.0f} (mediana: ${ventas_median:,.0f}) | Pizzas: {pizzas_mean:.0f}")
    else:
        print(f"{dias[dia]:12} | CERRADO (sin datos)")

print("\n" + "="*80)
print("📈 ESTADÍSTICAS GLOBALES")
print("="*80)
print(f"Ventas promedio: ${df['total_ventas_dia'].mean():,.0f}")
print(f"Ventas mediana:  ${df['total_ventas_dia'].median():,.0f}")
print(f"Ventas min:      ${df['total_ventas_dia'].min():,.0f}")
print(f"Ventas max:      ${df['total_ventas_dia'].max():,.0f}")
print(f"Pizzas promedio: {df['pizzas_vendidas'].mean():.0f}")

print("\n" + "="*80)
print("📆 ÚLTIMOS 10 DÍAS DE DATOS REALES")
print("="*80)
for _, row in df.tail(10).iterrows():
    fecha = row['fecha'].strftime('%Y-%m-%d')
    dia = dias[row['dia_semana']]
    ventas = row['total_ventas_dia']
    pizzas = row['pizzas_vendidas']
    print(f"{fecha} ({dia:10}) | Ventas: ${ventas:,.0f} | Pizzas: {pizzas:.0f}")

# Ahora cargar predicciones del modelo
print("\n" + "="*80)
print("🔮 PREDICCIONES DEL MODELO ML")
print("="*80)

import sys
sys.path.insert(0, '.')
from app.predictor_pro import PredictorPro

predictor = PredictorPro(Path("models"), Path("data"))
predictor.cargar_modelos()

predictions = predictor.predict_next_days(Path("data/ventas_diarias.parquet"), days=7)

for pred in predictions:
    fecha = pred['fecha'].strftime('%Y-%m-%d') if hasattr(pred['fecha'], 'strftime') else str(pred['fecha'])
    dia = pred['dia_nombre']
    ventas = pred['total_ventas_dia']
    ventas_min = pred['ventas_min']
    ventas_max = pred['ventas_max']
    pizzas = pred['pizzas_vendidas']
    
    print(f"{fecha} ({dia:10}) | Ventas: ${ventas:,.0f} (${ventas_min:,.0f}-${ventas_max:,.0f}) | Pizzas: {pizzas:.0f}")

# Comparar predicciones con históricos
print("\n" + "="*80)
print("⚖️ COMPARACIÓN: PREDICCIÓN vs HISTÓRICO")
print("="*80)

errores = []
for pred in predictions:
    dia_semana = pred['fecha'].weekday() if hasattr(pred['fecha'], 'weekday') else 0
    dia_nombre = pred['dia_nombre']
    pred_ventas = pred['total_ventas_dia']
    
    if dia_semana in promedios_historicos:
        hist = promedios_historicos[dia_semana]
        hist_ventas = hist['ventas_median']  # Usar mediana para comparar
        diff_pct = (pred_ventas - hist_ventas) / hist_ventas * 100 if hist_ventas > 0 else 0
        errores.append(abs(diff_pct))
        
        status = "✅" if abs(diff_pct) < 20 else "⚠️" if abs(diff_pct) < 40 else "❌"
        print(f"{dia_nombre:10} | Pred: ${pred_ventas:,.0f} | Hist: ${hist_ventas:,.0f} | Diff: {diff_pct:+.1f}% {status}")

print("\n" + "="*80)
print("📋 DIAGNÓSTICO")
print("="*80)

avg_error = np.mean(errores) if errores else 0
print(f"Error promedio vs histórico: {avg_error:.1f}%")

if avg_error < 15:
    print("✅ Las predicciones están BIEN calibradas con los datos históricos")
elif avg_error < 30:
    print("⚠️ Las predicciones tienen desviación MODERADA - revisar features")
else:
    print("❌ Las predicciones tienen desviación ALTA - el modelo necesita ajuste")

# Verificar si las predicciones son razonables
print("\n" + "="*80)
print("🔍 VERIFICACIÓN DE RANGOS")
print("="*80)

ventas_historicas_mean = df['total_ventas_dia'].mean()
ventas_historicas_std = df['total_ventas_dia'].std()

for pred in predictions:
    ventas = pred['total_ventas_dia']
    dia = pred['dia_nombre']
    
    # ¿Está dentro de 3 desviaciones estándar?
    z_score = (ventas - ventas_historicas_mean) / ventas_historicas_std if ventas_historicas_std > 0 else 0
    
    if abs(z_score) > 3:
        print(f"❌ {dia}: ${ventas:,.0f} - FUERA DE RANGO (z={z_score:.1f})")
    elif abs(z_score) > 2:
        print(f"⚠️ {dia}: ${ventas:,.0f} - Algo alto/bajo (z={z_score:.1f})")
    else:
        print(f"✅ {dia}: ${ventas:,.0f} - Dentro del rango normal (z={z_score:.1f})")
