"""
Prediction Tracker - Almacena predicciones y calcula precisión real
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import json

logger = logging.getLogger(__name__)


class PredictionTracker:
    """
    Rastrea predicciones y las compara con valores reales
    
    Funcionalidades:
    1. Guardar cada predicción con su intervalo de confianza
    2. Actualizar con valores reales cuando estén disponibles
    3. Calcular métricas de precisión histórica
    4. Detectar cuando el modelo necesita reentrenamiento
    """
    
    def __init__(self, db_path: Path):
        """
        Args:
            db_path: Ruta a la base de datos SQLite
        """
        self.db_path = db_path
        self._init_tables()
    
    def _init_tables(self):
        """Crea las tablas necesarias"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabla de predicciones
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ml_predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha_prediccion DATE NOT NULL,
                    fecha_objetivo DATE NOT NULL,
                    variable TEXT NOT NULL,
                    valor_predicho REAL NOT NULL,
                    intervalo_lower REAL,
                    intervalo_upper REAL,
                    valor_real REAL,
                    error_absoluto REAL,
                    error_porcentual REAL,
                    dentro_intervalo BOOLEAN,
                    modelo_version TEXT,
                    features_hash TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP,
                    UNIQUE(fecha_objetivo, variable, modelo_version)
                )
            """)
            
            # Tabla de métricas del modelo
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ml_model_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha DATE NOT NULL,
                    variable TEXT NOT NULL,
                    mape REAL,
                    mae REAL,
                    rmse REAL,
                    coverage_80 REAL,
                    n_predictions INTEGER,
                    modelo_version TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de entrenamientos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ml_training_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha_entrenamiento TIMESTAMP NOT NULL,
                    modelo_version TEXT NOT NULL,
                    n_registros_train INTEGER,
                    fecha_inicio_datos DATE,
                    fecha_fin_datos DATE,
                    metricas_validacion TEXT,
                    feature_importance TEXT,
                    duracion_segundos REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            logger.info("✅ Tablas de tracking inicializadas")
    
    def log_prediction(self, prediction: Dict[str, Any], modelo_version: str = "2.0.0"):
        """
        Guarda una predicción
        
        Args:
            prediction: Diccionario con la predicción
            modelo_version: Versión del modelo usado
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            fecha_objetivo = prediction.get('fecha_objetivo') or prediction.get('fecha')
            
            for variable in ['total_ventas_dia', 'pizzas_vendidas', 'pizzas_pastor', 
                           'pizzas_chuleta', 'alitas_vendidas']:
                if variable in prediction:
                    valor = prediction[variable]
                    lower = prediction.get(f'{variable}_lower', prediction.get('lower_80'))
                    upper = prediction.get(f'{variable}_upper', prediction.get('upper_80'))
                    
                    try:
                        cursor.execute("""
                            INSERT OR REPLACE INTO ml_predictions 
                            (fecha_prediccion, fecha_objetivo, variable, valor_predicho,
                             intervalo_lower, intervalo_upper, modelo_version, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            date.today().isoformat(),
                            str(fecha_objetivo),
                            variable,
                            float(valor) if isinstance(valor, dict) else float(valor),
                            float(lower) if lower else None,
                            float(upper) if upper else None,
                            modelo_version,
                            datetime.now().isoformat()
                        ))
                    except Exception as e:
                        logger.warning(f"Error guardando predicción para {variable}: {e}")
            
            conn.commit()
    
    def log_predictions_batch(self, predictions: List[Dict[str, Any]], modelo_version: str = "2.0.0"):
        """Guarda múltiples predicciones"""
        for pred in predictions:
            self.log_prediction(pred, modelo_version)
    
    def update_with_actual(self, fecha: str, variable: str, valor_real: float):
        """
        Actualiza una predicción con el valor real
        
        Args:
            fecha: Fecha de la predicción
            variable: Variable predicha
            valor_real: Valor real observado
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Obtener predicción
            cursor.execute("""
                SELECT valor_predicho, intervalo_lower, intervalo_upper
                FROM ml_predictions
                WHERE fecha_objetivo = ? AND variable = ? AND valor_real IS NULL
                ORDER BY created_at DESC LIMIT 1
            """, (fecha, variable))
            
            row = cursor.fetchone()
            if row:
                valor_predicho, lower, upper = row
                error_abs = abs(valor_real - valor_predicho)
                error_pct = (error_abs / valor_real * 100) if valor_real != 0 else 0
                dentro = lower <= valor_real <= upper if (lower and upper) else None
                
                cursor.execute("""
                    UPDATE ml_predictions
                    SET valor_real = ?,
                        error_absoluto = ?,
                        error_porcentual = ?,
                        dentro_intervalo = ?,
                        updated_at = ?
                    WHERE fecha_objetivo = ? AND variable = ? AND valor_real IS NULL
                """, (
                    valor_real, error_abs, error_pct, dentro,
                    datetime.now().isoformat(), fecha, variable
                ))
                
                conn.commit()
                logger.info(f"✅ Actualizada predicción {variable} para {fecha}: error={error_pct:.1f}%")
    
    def update_actuals_from_data(self, df: pd.DataFrame):
        """
        Actualiza todas las predicciones pendientes con datos reales
        
        Args:
            df: DataFrame con datos reales (debe tener 'fecha' y variables)
        """
        df = df.copy()
        df['fecha'] = pd.to_datetime(df['fecha']).dt.date.astype(str)
        
        variables = ['total_ventas_dia', 'pizzas_vendidas', 'pizzas_pastor',
                    'pizzas_chuleta', 'alitas_vendidas']
        
        updated = 0
        for _, row in df.iterrows():
            fecha = row['fecha']
            for var in variables:
                if var in row and pd.notna(row[var]):
                    self.update_with_actual(fecha, var, float(row[var]))
                    updated += 1
        
        logger.info(f"✅ Actualizados {updated} valores reales")
    
    def get_accuracy_metrics(self, days: int = 30, variable: str = None) -> Dict[str, Any]:
        """
        Calcula métricas de precisión de los últimos N días
        
        Args:
            days: Número de días a considerar
            variable: Variable específica (None = todas)
            
        Returns:
            Diccionario con métricas
        """
        with sqlite3.connect(self.db_path) as conn:
            query = f"""
                SELECT 
                    variable,
                    COUNT(*) as n_predictions,
                    AVG(error_absoluto) as mae,
                    AVG(error_porcentual) as mape,
                    SUM(CASE WHEN dentro_intervalo = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as coverage_80,
                    MIN(error_porcentual) as best_prediction,
                    MAX(error_porcentual) as worst_prediction
                FROM ml_predictions
                WHERE valor_real IS NOT NULL
                  AND fecha_objetivo >= date('now', '-{days} days')
            """
            
            if variable:
                query += f" AND variable = '{variable}'"
            
            query += " GROUP BY variable"
            
            df = pd.read_sql_query(query, conn)
            
            if len(df) == 0:
                return {'message': 'No hay predicciones con valores reales aún'}
            
            result = {
                'period_days': days,
                'by_variable': df.to_dict('records'),
                'overall': {
                    'mape': df['mape'].mean(),
                    'mae': df['mae'].mean(),
                    'coverage_80': df['coverage_80'].mean(),
                    'total_predictions': df['n_predictions'].sum()
                }
            }
            
            # Tendencia (últimos 7 días vs anteriores)
            query_recent = f"""
                SELECT AVG(error_porcentual) as mape
                FROM ml_predictions
                WHERE valor_real IS NOT NULL
                  AND fecha_objetivo >= date('now', '-7 days')
            """
            query_older = f"""
                SELECT AVG(error_porcentual) as mape
                FROM ml_predictions
                WHERE valor_real IS NOT NULL
                  AND fecha_objetivo < date('now', '-7 days')
                  AND fecha_objetivo >= date('now', '-{days} days')
            """
            
            mape_recent = pd.read_sql_query(query_recent, conn)['mape'].iloc[0]
            mape_older = pd.read_sql_query(query_older, conn)['mape'].iloc[0]
            
            if mape_recent and mape_older:
                if mape_recent < mape_older:
                    result['trend'] = 'improving'
                elif mape_recent > mape_older * 1.2:
                    result['trend'] = 'degrading'
                else:
                    result['trend'] = 'stable'
            else:
                result['trend'] = 'insufficient_data'
            
            return result
    
    def get_predictions_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """Obtiene historial de predicciones"""
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(f"""
                SELECT fecha_objetivo, variable, valor_predicho, valor_real,
                       error_porcentual, dentro_intervalo
                FROM ml_predictions
                WHERE fecha_objetivo >= date('now', '-{days} days')
                ORDER BY fecha_objetivo DESC, variable
            """, conn)
            
            return df.to_dict('records')
    
    def log_training(self, training_info: Dict[str, Any]):
        """
        Registra un entrenamiento del modelo
        
        Args:
            training_info: Información del entrenamiento
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO ml_training_history
                (fecha_entrenamiento, modelo_version, n_registros_train,
                 fecha_inicio_datos, fecha_fin_datos, metricas_validacion,
                 feature_importance, duracion_segundos)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                training_info.get('version', '2.0.0'),
                training_info.get('n_registros'),
                training_info.get('fecha_inicio'),
                training_info.get('fecha_fin'),
                json.dumps(training_info.get('metricas', {})),
                json.dumps(training_info.get('feature_importance', {})),
                training_info.get('duracion')
            ))
            
            conn.commit()
    
    def should_retrain(self, mape_threshold: float = 20.0, 
                       coverage_threshold: float = 60.0) -> Dict[str, Any]:
        """
        Determina si el modelo necesita reentrenamiento
        
        Args:
            mape_threshold: MAPE máximo aceptable
            coverage_threshold: Coverage mínimo aceptable
            
        Returns:
            Diccionario con recomendación y razón
        """
        metrics = self.get_accuracy_metrics(days=14)
        
        if 'message' in metrics:
            return {
                'should_retrain': False,
                'reason': 'Datos insuficientes para evaluar',
                'metrics': None
            }
        
        overall = metrics['overall']
        
        reasons = []
        
        if overall['mape'] > mape_threshold:
            reasons.append(f"MAPE ({overall['mape']:.1f}%) > threshold ({mape_threshold}%)")
        
        if overall['coverage_80'] < coverage_threshold:
            reasons.append(f"Coverage ({overall['coverage_80']:.1f}%) < threshold ({coverage_threshold}%)")
        
        if metrics['trend'] == 'degrading':
            reasons.append("Tendencia de precisión degradándose")
        
        return {
            'should_retrain': len(reasons) > 0,
            'reasons': reasons,
            'metrics': overall,
            'trend': metrics['trend']
        }
