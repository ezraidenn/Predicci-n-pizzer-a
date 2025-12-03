"""
Script para entrenar modelos con los nuevos productos
"""

import sys
sys.path.insert(0, '.')

from pathlib import Path
from app.predictor_simple import PredictorSimple

print("="*80)
print("🧠 ENTRENANDO MODELOS CON PRODUCTOS NUEVOS")
print("="*80)

# Rutas
DATA_DIR = Path("data")
MODELS_DIR = Path("models")
data_file = DATA_DIR / "ventas_diarias.parquet"

# Verificar que existe el archivo
if not data_file.exists():
    print(f"❌ No se encontró: {data_file}")
    exit(1)

# Crear predictor y entrenar
predictor = PredictorSimple(MODELS_DIR)

print("\n🔄 Entrenando...")
metrics = predictor.train_models(data_file)

print("\n" + "="*80)
print("✅ ENTRENAMIENTO COMPLETADO")
print("="*80)

# Mostrar predicción de prueba
print("\n📊 Probando predicciones...")
predictions = predictor.predict_next_days(data_file, days=7)

print("\n🔮 PREDICCIONES PRÓXIMOS 7 DÍAS:")
print("-"*80)
for pred in predictions:
    fecha = pred['fecha'].strftime('%Y-%m-%d')
    dia = pred['dia_nombre']
    pizzas = pred['pizzas_vendidas']
    pastor = pred['pizzas_pastor']
    chuleta = pred['pizzas_chuleta']
    alitas = pred['alitas_vendidas']
    ventas = pred['total_ventas_dia']
    evento = pred.get('evento', '')
    
    evento_str = f" 🎉 {evento}" if evento else ""
    print(f"{fecha} ({dia}){evento_str}:")
    print(f"  💰 Ventas: ${ventas:,.0f}")
    print(f"  🍕 Pizzas: {pizzas:.0f} (Pastor: {pastor:.0f}, Chuleta: {chuleta:.0f})")
    print(f"  🍗 Alitas: {alitas:.0f}")
    print()

print("="*80)
print("✅ TODO LISTO - Inicia el backend para ver en el dashboard")
print("="*80)
