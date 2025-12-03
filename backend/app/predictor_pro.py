"""
PREDICTOR PROFESIONAL - ML Avanzado para Pizzería MAX
Versión 2.0 con técnicas profesionales de Machine Learning

Features:
- Ensemble (LightGBM + Ridge + Historical)
- 50+ features automáticos
- Intervalos de confianza reales (Quantile Regression)
- Validación temporal (no random split)
- Tracking de predicciones
- Detección de anomalías
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

from app.ml import MLPipeline
from app.calendar_events import CalendarioEventos

logger = logging.getLogger(__name__)


class PredictorPro:
    """
    Predictor profesional con ML avanzado
    
    Mejoras sobre predictor_simple:
    1. Modelo Ensemble en lugar de promedios simples
    2. 50+ features vs 7 features
    3. Intervalos de confianza reales vs percentiles fijos
    4. Validación temporal vs ninguna validación
    5. Tracking de precisión vs sin tracking
    """
    
    def __init__(self, models_dir: Path = Path("models"), 
                 data_dir: Path = Path("data")):
        """
        Args:
            models_dir: Directorio para modelos
            data_dir: Directorio de datos
        """
        self.models_dir = Path(models_dir)
        self.data_dir = Path(data_dir)
        
        # Pipeline de ML
        self.pipeline = MLPipeline(self.models_dir, self.data_dir)
        
        # Sistema de eventos (quincenas, festivos)
        self.calendario = CalendarioEventos()
        
        # Estado
        self.is_trained = False
        self.last_training_metrics = None
    
    def train_models(self, data_file: Path) -> Dict[str, Any]:
        """
        Entrena los modelos con datos históricos
        
        Args:
            data_file: Ruta al archivo parquet con datos
            
        Returns:
            Métricas de entrenamiento
        """
        logger.info("\n" + "="*80)
        logger.info("🧠 SISTEMA ML PROFESIONAL - ENTRENAMIENTO")
        logger.info("="*80 + "\n")
        
        try:
            # Cargar datos
            df = pd.read_parquet(data_file)
            df['fecha'] = pd.to_datetime(df['fecha'])
            
            logger.info(f"📊 Datos cargados: {len(df)} registros")
            logger.info(f"📅 Período: {df['fecha'].min().date()} → {df['fecha'].max().date()}")
            logger.info(f"📋 Columnas: {df.columns.tolist()}")
            
            # Entrenar pipeline
            metrics = self.pipeline.train(df, validate=True)
            
            self.is_trained = True
            self.last_training_metrics = metrics
            
            logger.info("\n" + "="*80)
            logger.info("✅ ENTRENAMIENTO COMPLETADO")
            logger.info("="*80)
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Error en entrenamiento: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def predict_next_days(self, data_file: Path, days: int = 7) -> List[Dict[str, Any]]:
        """
        Predice los próximos N días
        
        Args:
            data_file: Ruta al archivo parquet
            days: Días a predecir
            
        Returns:
            Lista de predicciones con intervalos
        """
        logger.info(f"\n🔮 Generando predicciones para {days} días...")
        
        # Cargar modelos si es necesario
        if not self.is_trained:
            self.cargar_modelos()
        
        # Cargar datos históricos
        df = pd.read_parquet(data_file)
        df['fecha'] = pd.to_datetime(df['fecha'])
        
        # Generar predicciones con el pipeline
        predictions_raw = self.pipeline.predict(df, days=days)
        
        # Formatear predicciones para el frontend
        predictions = []
        
        for pred in predictions_raw:
            # Aplicar multiplicador adicional del calendario
            evento_info = self.calendario.get_multiplicador_total(pred['fecha'])
            multiplicador_adicional = evento_info['multiplicador']
            
            # Formatear predicción
            pred_formatted = {
                'fecha': pred['fecha'],
                'dia_nombre': pred['dia_nombre'],
                
                # Predicciones principales
                'total_ventas_dia': float(pred.get('total_ventas_dia', 0)),
                'pizzas_vendidas': float(pred.get('pizzas_vendidas', 0)),
                'pizzas_pastor': float(pred.get('pizzas_pastor', 0)),
                'pizzas_chuleta': float(pred.get('pizzas_chuleta', 0)),
                'alitas_vendidas': float(pred.get('alitas_vendidas', 0)),
                'baguettes_vendidas': float(pred.get('baguettes_vendidas', 0)),
                'papas_gajo_vendidas': float(pred.get('papas_gajo_vendidas', 0)),
                
                # Rangos de ventas
                'ventas_min': float(pred.get('total_ventas_dia_min', pred.get('total_ventas_dia', 0) * 0.85)),
                'ventas_max': float(pred.get('total_ventas_dia_max', pred.get('total_ventas_dia', 0) * 1.15)),
                
                # Rangos de pizzas
                'pizzas_min': float(pred.get('pizzas_vendidas_min', pred.get('pizzas_vendidas', 0) * 0.85)),
                'pizzas_max': float(pred.get('pizzas_vendidas_max', pred.get('pizzas_vendidas', 0) * 1.15)),
                
                # Rangos de pastor
                'pastor_min': float(pred.get('pizzas_pastor_min', pred.get('pizzas_pastor', 0) * 0.80)),
                'pastor_max': float(pred.get('pizzas_pastor_max', pred.get('pizzas_pastor', 0) * 1.20)),
                
                # Rangos de chuleta
                'chuleta_min': float(pred.get('pizzas_chuleta_min', pred.get('pizzas_chuleta', 0) * 0.80)),
                'chuleta_max': float(pred.get('pizzas_chuleta_max', pred.get('pizzas_chuleta', 0) * 1.20)),
                
                # Rangos de alitas
                'alitas_min': float(pred.get('alitas_vendidas_min', pred.get('alitas_vendidas', 0) * 0.80)),
                'alitas_max': float(pred.get('alitas_vendidas_max', pred.get('alitas_vendidas', 0) * 1.20)),
                
                # Rangos de baguettes
                'baguettes_min': float(pred.get('baguettes_vendidas_min', pred.get('baguettes_vendidas', 0) * 0.85)),
                'baguettes_max': float(pred.get('baguettes_vendidas_max', pred.get('baguettes_vendidas', 0) * 1.15)),
                
                # Rangos de papas
                'papas_min': float(pred.get('papas_gajo_vendidas_min', pred.get('papas_gajo_vendidas', 0) * 0.85)),
                'papas_max': float(pred.get('papas_gajo_vendidas_max', pred.get('papas_gajo_vendidas', 0) * 1.15)),
                
                # Evento y multiplicador
                'evento': pred.get('evento') or evento_info.get('evento'),
                'multiplicador': pred.get('multiplicador', 1.0)
            }
            
            predictions.append(pred_formatted)
            
            # Log
            logger.info(
                f"  {pred['fecha']} ({pred['dia_nombre']}): "
                f"${pred_formatted['total_ventas_dia']:,.0f} | "
                f"{pred_formatted['pizzas_vendidas']:.0f} pizzas"
                f"{' 🎉 ' + pred_formatted['evento'] if pred_formatted['evento'] else ''}"
            )
        
        return predictions
    
    def cargar_modelos(self):
        """Carga modelos guardados"""
        try:
            self.pipeline.load_models()
            self.is_trained = self.pipeline.is_fitted
            
            if self.is_trained:
                logger.info("✅ Modelos ML cargados correctamente")
            else:
                logger.warning("⚠️ No hay modelos entrenados")
                
        except Exception as e:
            logger.error(f"Error cargando modelos: {e}")
            self.is_trained = False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Retorna información del modelo"""
        return self.pipeline.get_model_info()
    
    def get_accuracy_report(self, days: int = 30) -> Dict[str, Any]:
        """Obtiene reporte de precisión"""
        return self.pipeline.get_accuracy_report(days)
    
    def should_retrain(self) -> Dict[str, Any]:
        """Evalúa si necesita reentrenamiento"""
        return self.pipeline.should_retrain()
    
    def get_feature_importance(self, top_n: int = 20) -> List[Dict[str, Any]]:
        """Obtiene las features más importantes"""
        if 'total_ventas_dia' in self.pipeline.models:
            return self.pipeline.models['total_ventas_dia'].get_feature_importance(top_n)
        return []


# Mantener compatibilidad con el nombre anterior
class PredictorSimple(PredictorPro):
    """Alias para compatibilidad"""
    pass
