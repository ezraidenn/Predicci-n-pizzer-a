"""
Script para entrenar el modelo con aprendizaje incremental
"""

import sys
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

from app.online_predictor import OnlinePredictor

def main():
    print("\n" + "="*80)
    print("🧠 SISTEMA DE APRENDIZAJE INCREMENTAL")
    print("="*80 + "\n")
    
    data_file = Path("data/ventas_diarias.parquet")
    
    if not data_file.exists():
        print(f"❌ Error: No se encontró {data_file}")
        return
    
    # Crear predictor
    predictor = OnlinePredictor()
    
    # Paso 1: Entrenamiento inicial con primeros 6 meses
    print("PASO 1: Entrenamiento inicial con primeros 6 meses...")
    initial_info = predictor.train_initial(data_file, initial_days=180)
    print(f"✓ Entrenado con: {initial_info['train_period']}")
    
    # Paso 2: Aprendizaje incremental día a día
    print("\nPASO 2: Aprendizaje incremental día a día...")
    print("(Esto puede tomar un momento...)\n")
    
    learn_info = predictor.predict_and_learn(data_file, initial_days=180)
    print(f"\n✓ Aprendió de {learn_info['total_days_learned']} días adicionales")
    
    # Paso 3: Predicción de próximos 7 días
    print("\nPASO 3: Predicción de próximos 7 días...")
    predictions = predictor.predict_next_days(data_file, days=7)
    
    print("\n" + "="*80)
    print("📊 PREDICCIONES PRÓXIMOS 7 DÍAS")
    print("="*80 + "\n")
    
    for pred in predictions:
        print(f"Fecha: {pred['fecha'].date()}")
        print(f"  Ventas: ${pred['total_ventas_dia']:>10,.2f}")
        print(f"  Pizzas: {pred['pizzas_vendidas']:>10.0f}")
        print(f"  Baguettes: {pred['baguettes_vendidas']:>7.0f}")
        print(f"  Papas: {pred['papas_gajo_vendidas']:>10.0f}")
        print()
    
    # Mostrar historial de errores
    errors_df = learn_info['errors_df']
    
    print("="*80)
    print("📈 EVOLUCIÓN DEL ERROR (Primeros vs Últimos 30 días)")
    print("="*80 + "\n")
    
    for var in ['pizzas_vendidas', 'total_ventas_dia']:
        error_col = f'{var}_error_pct'
        if error_col in errors_df.columns:
            first_30 = errors_df[error_col].head(30).mean()
            last_30 = errors_df[error_col].tail(30).mean()
            improvement = ((first_30 - last_30) / first_30) * 100
            
            print(f"{var}:")
            print(f"  Primeros 30 días: {first_30:.2f}% error")
            print(f"  Últimos 30 días:  {last_30:.2f}% error")
            print(f"  Mejora: {improvement:.1f}%\n")
    
    print("="*80)
    print("✅ ENTRENAMIENTO COMPLETO")
    print("="*80)
    print("\nLos modelos ahora aprenderán continuamente de cada nuevo día.")
    print(f"Historial guardado en: models/online_learning_history.csv\n")

if __name__ == "__main__":
    main()
