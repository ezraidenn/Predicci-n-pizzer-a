"""
PREDICTOR ULTRA SIMPLE - Basado en Promedios Históricos
Sin complicaciones, sin ML excesivo
"""

import pandas as pd
import numpy as np
import logging
import pickle
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

from app.calendar_events import CalendarioEventos

logger = logging.getLogger(__name__)


class PredictorSimple:
    """
    Predictor ultra simple: usa promedios históricos por tipo de día
    """
    
    def __init__(self, models_dir: Path = Path("models")):
        self.models_dir = models_dir
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.promedios = {}  # Promedios por tipo de día
        self.calendario = CalendarioEventos()  # Sistema de eventos especiales
        
    def train_models(self, data_file: Path):
        """
        Calcular promedios históricos por tipo de día
        """
        logger.info("\n" + "="*80)
        logger.info("🎯 SISTEMA ULTRA SIMPLE - PROMEDIOS HISTÓRICOS")
        logger.info("="*80 + "\n")
        
        try:
            # Cargar datos
            df = pd.read_parquet(data_file)
            df['fecha'] = pd.to_datetime(df['fecha'])
            df['dia_semana'] = df['fecha'].dt.dayofweek
            
            # Log de columnas disponibles
            logger.info(f"Columnas cargadas: {df.columns.tolist()}")
            logger.info(f"Total filas: {len(df)}")
        except Exception as e:
            logger.error(f"Error cargando datos: {e}")
            import traceback
            traceback.print_exc()
            raise
        
        # Calcular promedios POR CADA DÍA DE LA SEMANA (7 promedios independientes)
        dias_nombres = {
            0: 'Lunes',
            1: 'Martes', 
            2: 'Miércoles',
            3: 'Jueves',
            4: 'Viernes',
            5: 'Sábado',
            6: 'Domingo'
        }
        
        for dia_num in range(7):
            try:
                # MARTES (1) siempre está CERRADO - forzar a 0
                if dia_num == 1:
                    logger.warning(f"⚠️ {dias_nombres[dia_num]} - Pizzería CERRADA (día fijo)")
                    self.promedios[dia_num] = {}
                    for variable in ['pizzas_vendidas', 'pizzas_pastor', 'pizzas_chuleta', 'alitas_vendidas', 'baguettes_vendidas', 'papas_gajo_vendidas', 'total_ventas_dia']:
                        self.promedios[dia_num][variable] = {
                            'base': 0.0,
                            'min': 0.0,
                            'max': 0.0
                        }
                    continue
                
                df_dia = df[df['dia_semana'] == dia_num]
                
                if len(df_dia) > 0:
                    # Últimos 40-60 días de este día específico
                    cantidad = min(len(df_dia), 40)
                    df_reciente = df_dia.tail(cantidad)
                    
                    # Calcular mediana (central) y percentiles (rangos)
                    self.promedios[dia_num] = {}
                    
                    for variable in ['pizzas_vendidas', 'pizzas_pastor', 'pizzas_chuleta', 'alitas_vendidas', 'baguettes_vendidas', 'papas_gajo_vendidas', 'total_ventas_dia']:
                        mediana = df_reciente[variable].median()
                        p15 = df_reciente[variable].quantile(0.15)  # Percentil 15 (rango amplio para crecimiento)
                        p85 = df_reciente[variable].quantile(0.85)  # Percentil 85 (rango amplio para crecimiento)
                        
                        self.promedios[dia_num][variable] = {
                            'base': float(mediana),
                            'min': float(p15),
                            'max': float(p85)
                        }
                    
                    logger.info(f"\n{dias_nombres[dia_num].upper()}:")
                    logger.info(f"  Pizzas: {self.promedios[dia_num]['pizzas_vendidas']['base']:.0f} (rango: {self.promedios[dia_num]['pizzas_vendidas']['min']:.0f}-{self.promedios[dia_num]['pizzas_vendidas']['max']:.0f})")
                    logger.info(f"  Ventas: ${self.promedios[dia_num]['total_ventas_dia']['base']:,.0f} (rango: ${self.promedios[dia_num]['total_ventas_dia']['min']:,.0f}-${self.promedios[dia_num]['total_ventas_dia']['max']:,.0f})")
                else:
                    # Si no hay datos para este día, asumir que está CERRADO
                    logger.warning(f"⚠️ No hay datos para {dias_nombres[dia_num]} - Pizzería CERRADA")
                    self.promedios[dia_num] = {}
                    for variable in ['pizzas_vendidas', 'pizzas_pastor', 'pizzas_chuleta', 'alitas_vendidas', 'baguettes_vendidas', 'papas_gajo_vendidas', 'total_ventas_dia']:
                        self.promedios[dia_num][variable] = {
                            'base': 0.0,
                            'min': 0.0,
                            'max': 0.0
                        }
            except Exception as e:
                logger.error(f"Error procesando {dias_nombres[dia_num]}: {e}")
                import traceback
                traceback.print_exc()
                raise
        
        # Guardar
        with open(self.models_dir / "promedios_simple.pkl", 'wb') as f:
            pickle.dump(self.promedios, f)
        
        logger.info("\n" + "="*80)
        logger.info("✅ PROMEDIOS CALCULADOS Y GUARDADOS")
        logger.info("="*80 + "\n")
        
        return {'modelos_entrenados': {'simple': 3}, 'total_modelos': 3}
    
    def predict_next_days(self, data_file: Path, days: int = 7) -> List[Dict]:
        """
        Predecir usando promedios históricos
        """
        logger.info(f"\n🔮 Prediciendo próximos {days} días (SIMPLE)...")
        
        # Cargar promedios
        self.cargar_modelos()
        
        # Cargar datos para contexto
        df = pd.read_parquet(data_file)
        df['fecha'] = pd.to_datetime(df['fecha'])
        
        # Usar la fecha actual como punto de partida (no la última fecha de datos)
        from datetime import datetime
        today = datetime.now().date()
        last_date = pd.Timestamp(today)
        
        logger.info(f"Prediciendo desde: {last_date.date()}")
        
        predictions = []
        
        dias_nombres = {
            0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves',
            4: 'Viernes', 5: 'Sábado', 6: 'Domingo'
        }
        
        for day in range(1, days + 1):
            pred_date = last_date + timedelta(days=day)
            dia_semana = pred_date.dayofweek
            dia_nombre = dias_nombres[dia_semana]
            
            # SALTAR MARTES - Pizzería cerrada
            if dia_semana == 1:
                logger.info(f"{pred_date.date()} ({dia_nombre}): CERRADO - Saltando predicción")
                continue
            
            # Obtener predicción base del día
            pizzas_base = float(self.promedios[dia_semana]['pizzas_vendidas']['base'])
            pastor_base = float(self.promedios[dia_semana]['pizzas_pastor']['base'])
            chuleta_base = float(self.promedios[dia_semana]['pizzas_chuleta']['base'])
            alitas_base = float(self.promedios[dia_semana]['alitas_vendidas']['base'])
            baguettes_base = float(self.promedios[dia_semana]['baguettes_vendidas']['base'])
            papas_base = float(self.promedios[dia_semana]['papas_gajo_vendidas']['base'])
            ventas_base = float(self.promedios[dia_semana]['total_ventas_dia']['base'])
            
            # Aplicar multiplicadores por quincenas/festivos
            evento_info = self.calendario.get_multiplicador_total(pred_date)
            multiplicador = evento_info['multiplicador']
            
            # Aplicar multiplicador a predicciones
            pred_values = {
                'fecha': pred_date,
                'dia_nombre': dia_nombre,
                
                # Base ajustada por eventos
                'pizzas_vendidas': float(pizzas_base * multiplicador),
                'pizzas_pastor': float(pastor_base * multiplicador),
                'pizzas_chuleta': float(chuleta_base * multiplicador),
                'alitas_vendidas': float(alitas_base * multiplicador),
                'baguettes_vendidas': float(baguettes_base * multiplicador),
                'papas_gajo_vendidas': float(papas_base * multiplicador),
                'total_ventas_dia': float(ventas_base * multiplicador),
                
                # Rangos pizzas totales
                'pizzas_min': float(self.promedios[dia_semana]['pizzas_vendidas']['min'] * multiplicador),
                'pizzas_max': float(self.promedios[dia_semana]['pizzas_vendidas']['max'] * multiplicador),
                
                # Rangos pizzas pastor
                'pastor_min': float(self.promedios[dia_semana]['pizzas_pastor']['min'] * multiplicador),
                'pastor_max': float(self.promedios[dia_semana]['pizzas_pastor']['max'] * multiplicador),
                
                # Rangos pizzas chuleta
                'chuleta_min': float(self.promedios[dia_semana]['pizzas_chuleta']['min'] * multiplicador),
                'chuleta_max': float(self.promedios[dia_semana]['pizzas_chuleta']['max'] * multiplicador),
                
                # Rangos alitas
                'alitas_min': float(self.promedios[dia_semana]['alitas_vendidas']['min'] * multiplicador),
                'alitas_max': float(self.promedios[dia_semana]['alitas_vendidas']['max'] * multiplicador),
                
                # Rangos baguettes
                'baguettes_min': float(self.promedios[dia_semana]['baguettes_vendidas']['min'] * multiplicador),
                'baguettes_max': float(self.promedios[dia_semana]['baguettes_vendidas']['max'] * multiplicador),
                
                # Rangos papas
                'papas_min': float(self.promedios[dia_semana]['papas_gajo_vendidas']['min'] * multiplicador),
                'papas_max': float(self.promedios[dia_semana]['papas_gajo_vendidas']['max'] * multiplicador),
                
                # Rangos ventas
                'ventas_min': float(self.promedios[dia_semana]['total_ventas_dia']['min'] * multiplicador),
                'ventas_max': float(self.promedios[dia_semana]['total_ventas_dia']['max'] * multiplicador),
                
                # Info del evento
                'evento': evento_info['evento'],
                'multiplicador': multiplicador,
            }
            
            predictions.append(pred_values)
            
            # Log con info de evento
            evento_str = f" 🎉 {evento_info['evento']} (+{(multiplicador-1)*100:.0f}%)" if evento_info['evento'] else ""
            logger.info(f"{pred_date.date()} ({dia_nombre}){evento_str}: {pred_values['pizzas_vendidas']:.0f} pizzas ({pred_values['pizzas_min']:.0f}-{pred_values['pizzas_max']:.0f}), ${pred_values['total_ventas_dia']:,.0f} (${pred_values['ventas_min']:,.0f}-${pred_values['ventas_max']:,.0f})")
        
        return predictions
    
    def cargar_modelos(self):
        """Cargar promedios guardados"""
        archivo = self.models_dir / "promedios_simple.pkl"
        if archivo.exists():
            with open(archivo, 'rb') as f:
                self.promedios = pickle.load(f)
