"""
Script para entrenar el nuevo sistema limpio
"""

import sys
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

from app.predictor_clean import PredictorClean

def main():
    print("\n" + "="*80)
    print("🎯 SISTEMA LIMPIO - MODELOS POR TIPO DE DÍA")
    print("="*80)
    print("\n📋 Estrategia:")
    print("   • Normal (Lun-Jue): Días regulares")
    print("   • Medio Fuerte (Vie): Transición al fin de semana")
    print("   • Fuerte (Sáb-Dom): Días con más ventas")
    print("\n")
    
    data_file = Path("data/ventas_diarias.parquet")
    
    if not data_file.exists():
        print(f"❌ Error: No se encontró {data_file}")
        return
    
    # Crear predictor
    predictor = PredictorClean()
    
    # Entrenar
    predictor.train_models(data_file)
    
    # Predecir próximos 7 días
    predictions = predictor.predict_next_days(data_file, days=7)
    
    print("\n" + "="*80)
    print("📊 PREDICCIONES PRÓXIMOS 7 DÍAS")
    print("="*80 + "\n")
    
    for pred in predictions:
        fecha = pred['fecha']
        dia_nombre = fecha.strftime('%A')
        dia_semana = fecha.weekday()
        
        # Determinar tipo
        if dia_semana in [5, 6]:
            tipo = "FUERTE"
        elif dia_semana == 4:
            tipo = "MEDIO"
        else:
            tipo = "NORMAL"
        
        print(f"{fecha.date()} ({dia_nombre}) - {tipo}")
        print(f"  💰 Ventas: ${pred['total_ventas_dia']:>10,.2f}")
        print(f"  🍕 Pizzas: {pred['pizzas_vendidas']:>10.0f}")
        print(f"  🥖 Baguettes: {pred['baguettes_vendidas']:>7.0f}")
        print(f"  🍟 Papas: {pred['papas_gajo_vendidas']:>10.0f}")
        print()
    
    print("="*80)
    print("✅ SISTEMA LISTO")
    print("="*80)
    print("\n📝 Ventajas del nuevo sistema:")
    print("   ✓ Modelos especializados por tipo de día")
    print("   ✓ Sábados/Domingos usan solo datos de fines de semana")
    print("   ✓ Viernes tiene su propio modelo (transición)")
    print("   ✓ Lunes-Jueves comparten patrón similar")
    print("   ✓ Sin interferencia entre tipos de día")
    print("   ✓ Validación de consistencia en ventas")
    print()

if __name__ == "__main__":
    main()
