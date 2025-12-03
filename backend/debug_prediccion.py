"""
Debug detallado de las predicciones
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys
sys.path.insert(0, '.')

from app.predictor_pro import PredictorPro

# Cargar datos
df = pd.read_parquet('data/ventas_diarias.parquet')
df['fecha'] = pd.to_datetime(df['fecha'])
df['dia_semana'] = df['fecha'].dt.dayofweek

dias = {0:'Lunes', 1:'Martes', 2:'Miércoles', 3:'Jueves', 4:'Viernes', 5:'Sábado', 6:'Domingo'}

print("="*80)
print("DATOS HISTÓRICOS REALES (últimos 90 días)")
print("="*80)

# Filtrar anomalías
umbral = df['total_ventas_dia'].mean() * 0.30
df_clean = df[df['total_ventas_dia'] >= umbral].tail(90)

for dia in [5, 6, 4, 3, 0, 2]:  # Sábado, Domingo, Viernes, etc
    if dia == 1:
        continue
    subset = df_clean[df_clean['dia_semana'] == dia]
    if len(subset) > 0:
        print(f"\n{dias[dia]}:")
        print(f"  Ventas mediana: ${subset['total_ventas_dia'].median():,.0f}")
        print(f"  Pizzas mediana: {subset['pizzas_vendidas'].median():.0f}")
        print(f"  Pizzas promedio: {subset['pizzas_vendidas'].mean():.0f}")
        print(f"  Pizzas max: {subset['pizzas_vendidas'].max():.0f}")

print("\n" + "="*80)
print("PREDICCIONES DEL MODELO")
print("="*80)

predictor = PredictorPro(Path("models"), Path("data"))
predictor.cargar_modelos()

predictions = predictor.predict_next_days(Path("data/ventas_diarias.parquet"), days=7)

for pred in predictions:
    dia = pred['dia_nombre']
    print(f"\n{dia}:")
    print(f"  Ventas: ${pred['total_ventas_dia']:,.0f}")
    print(f"  Pizzas: {pred['pizzas_vendidas']:.0f}")
    print(f"  Pastor: {pred.get('pizzas_pastor', 0):.0f}")
    print(f"  Chuleta: {pred.get('pizzas_chuleta', 0):.0f}")

print("\n" + "="*80)
print("COMPARACIÓN DIRECTA")
print("="*80)

predicciones_por_dia = {}
for pred in predictions:
    dia_semana = pred['fecha'].weekday() if hasattr(pred['fecha'], 'weekday') else 0
    if dia_semana not in predicciones_por_dia:
        predicciones_por_dia[dia_semana] = pred

print(f"\n{'Día':<12} | {'Pizzas Pred':>12} | {'Pizzas Real':>12} | {'Diff':>8}")
print("-"*50)

for dia in [5, 6, 4, 3, 0, 2]:
    if dia == 1:
        continue
    subset = df_clean[df_clean['dia_semana'] == dia]
    real = subset['pizzas_vendidas'].median() if len(subset) > 0 else 0
    
    pred_val = predicciones_por_dia.get(dia, {}).get('pizzas_vendidas', 0) if dia in predicciones_por_dia else 0
    diff = ((pred_val - real) / real * 100) if real > 0 else 0
    
    status = "✅" if abs(diff) < 10 else "⚠️" if abs(diff) < 20 else "❌"
    print(f"{dias[dia]:<12} | {pred_val:>12.0f} | {real:>12.0f} | {diff:>+7.1f}% {status}")
