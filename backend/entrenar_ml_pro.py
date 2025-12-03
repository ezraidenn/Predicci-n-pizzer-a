"""
Script para entrenar el modelo ML profesional
"""

import sys
sys.path.insert(0, '.')

from pathlib import Path
from app.predictor_pro import PredictorPro

print("="*80)
print("🧠 ENTRENAMIENTO ML PROFESIONAL")
print("="*80)

# Rutas
DATA_DIR = Path("data")
MODELS_DIR = Path("models")
data_file = DATA_DIR / "ventas_diarias.parquet"

# Verificar archivo
if not data_file.exists():
    print(f"❌ No se encontró: {data_file}")
    exit(1)

# Crear predictor
print("\n📦 Inicializando PredictorPro...")
predictor = PredictorPro(MODELS_DIR, DATA_DIR)

# Entrenar
print("\n🚀 Iniciando entrenamiento...")
try:
    metrics = predictor.train_models(data_file)
    
    print("\n" + "="*80)
    print("📊 MÉTRICAS DE VALIDACIÓN")
    print("="*80)
    
    for var, m in metrics.get('metrics', {}).items():
        if m.get('mape'):
            print(f"  {var}:")
            print(f"    MAPE: {m['mape']:.2f}%")
            print(f"    MAE:  ${m['mae']:,.0f}")
    
    print("\n" + "="*80)
    print("✅ ENTRENAMIENTO COMPLETADO")
    print("="*80)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Probar predicciones
print("\n🔮 PROBANDO PREDICCIONES...")
print("-"*80)

try:
    predictions = predictor.predict_next_days(data_file, days=7)
    
    for pred in predictions:
        fecha = pred['fecha'].strftime('%Y-%m-%d') if hasattr(pred['fecha'], 'strftime') else str(pred['fecha'])
        dia = pred['dia_nombre']
        ventas = pred['total_ventas_dia']
        ventas_min = pred['ventas_min']
        ventas_max = pred['ventas_max']
        pizzas = pred['pizzas_vendidas']
        evento = pred.get('evento', '')
        
        evento_str = f" 🎉 {evento}" if evento else ""
        print(f"{fecha} ({dia}){evento_str}:")
        print(f"  💰 Ventas: ${ventas:,.0f} (${ventas_min:,.0f} - ${ventas_max:,.0f})")
        print(f"  🍕 Pizzas: {pizzas:.0f}")
        print()

except Exception as e:
    print(f"\n❌ Error en predicciones: {e}")
    import traceback
    traceback.print_exc()

print("="*80)
print("✅ ML PROFESIONAL LISTO")
print("="*80)
