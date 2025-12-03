"""
ML Pipeline - Orquestador principal del sistema de predicción
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import time
import logging

from .feature_engineer import AdvancedFeatureEngineer
from .models.lgbm_model import LightGBMModel
from .models.ensemble import EnsembleModel
from .validator import TimeSeriesValidator, calculate_metrics
from .anomaly_detector import AnomalyDetector
from .tracker import PredictionTracker

logger = logging.getLogger(__name__)


class MLPipeline:
    """
    Pipeline completo de ML para predicción de ventas
    
    Componentes:
    1. Feature Engineering avanzado
    2. Modelo Ensemble (LightGBM + Ridge + Historical)
    3. Validación temporal
    4. Detección de anomalías
    5. Tracking de predicciones
    """
    
    VERSION = "2.0.0"
    
    # Variables a predecir
    TARGET_VARIABLES = [
        'total_ventas_dia',
        'pizzas_vendidas',
        'pizzas_pastor',
        'pizzas_chuleta',
        'alitas_vendidas',
        'baguettes_vendidas',
        'papas_gajo_vendidas'
    ]
    
    def __init__(self, models_dir: Path, data_dir: Path):
        """
        Args:
            models_dir: Directorio para guardar modelos
            data_dir: Directorio de datos (para tracker)
        """
        self.models_dir = Path(models_dir)
        self.data_dir = Path(data_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Componentes
        self.feature_engineer = AdvancedFeatureEngineer()
        self.models = {}  # Un modelo por variable
        self.anomaly_detector = AnomalyDetector(contamination=0.05)
        self.tracker = PredictionTracker(self.data_dir / "pizzeria_max.db")
        self.validator = TimeSeriesValidator(n_splits=5, test_size=14)
        
        # Metadata
        self.metadata = {
            'version': self.VERSION,
            'last_trained': None,
            'n_registros': 0,
            'metrics': {},
            'feature_importance': {}
        }
        
        self.is_fitted = False
    
    def train(self, df: pd.DataFrame, validate: bool = True) -> Dict[str, Any]:
        """
        Entrena todos los modelos del pipeline
        
        Args:
            df: DataFrame con datos históricos
            validate: Si hacer validación cruzada
            
        Returns:
            Diccionario con métricas de entrenamiento
        """
        start_time = time.time()
        logger.info("="*60)
        logger.info("🚀 INICIANDO ENTRENAMIENTO ML PROFESIONAL")
        logger.info("="*60)
        
        # Preparar datos
        df = df.copy()
        df['fecha'] = pd.to_datetime(df['fecha'])
        df = df.sort_values('fecha').reset_index(drop=True)
        
        logger.info(f"📊 Datos: {len(df)} registros")
        logger.info(f"📅 Rango: {df['fecha'].min().date()} a {df['fecha'].max().date()}")
        
        # 1. Detectar anomalías
        logger.info("\n🔍 Detectando anomalías...")
        anomaly_result = self.anomaly_detector.fit(df).detect(df)
        logger.info(f"   Anomalías encontradas: {anomaly_result['anomaly_count']} ({anomaly_result['anomaly_pct']:.1f}%)")
        
        # Opcionalmente excluir anomalías del entrenamiento
        # df_clean, df_anomalies = self.anomaly_detector.get_clean_data(df)
        # Por ahora usamos todos los datos
        df_clean = df
        
        # 2. Generar features
        logger.info("\n🔧 Generando features...")
        X = self.feature_engineer.fit_transform(df_clean)
        logger.info(f"   Features generadas: {len(self.feature_engineer.feature_names)}")
        
        # 3. Entrenar modelo para cada variable
        all_metrics = {}
        
        for target_var in self.TARGET_VARIABLES:
            if target_var not in df_clean.columns:
                logger.warning(f"   ⚠️ Variable {target_var} no encontrada, saltando...")
                continue
            
            logger.info(f"\n📈 Entrenando modelo para: {target_var}")
            
            y = df_clean[target_var].fillna(0)
            
            # Crear y entrenar ensemble
            ensemble = EnsembleModel(name=f"ensemble_{target_var}")
            ensemble.fit(X, y, df_original=df_clean)
            
            # Validación
            if validate and len(df_clean) >= 90:
                logger.info(f"   🔄 Validando con TimeSeriesSplit...")
                
                # Crear modelo simple para validación
                lgbm_val = LightGBMModel(name=f"val_{target_var}", use_quantiles=False)
                metrics = self.validator.evaluate(
                    lgbm_val, X, y,
                    feature_cols=self.feature_engineer.feature_names
                )
                
                all_metrics[target_var] = {
                    'mae': metrics['mae_mean'],
                    'rmse': metrics['rmse_mean'],
                    'mape': metrics['mape_mean']
                }
                
                logger.info(f"   ✅ MAPE: {metrics['mape_mean']:.2f}% | MAE: ${metrics['mae_mean']:,.0f}")
            else:
                all_metrics[target_var] = {'mape': None, 'mae': None, 'rmse': None}
            
            # Guardar modelo
            self.models[target_var] = ensemble
        
        # 4. Guardar feature importance (del modelo de ventas)
        if 'total_ventas_dia' in self.models:
            self.metadata['feature_importance'] = self.models['total_ventas_dia'].get_feature_importance(20)
        
        # 5. Guardar modelos
        self._save_models()
        
        # 6. Actualizar metadata
        duration = time.time() - start_time
        self.metadata.update({
            'last_trained': datetime.now().isoformat(),
            'n_registros': len(df_clean),
            'fecha_inicio': str(df_clean['fecha'].min().date()),
            'fecha_fin': str(df_clean['fecha'].max().date()),
            'metrics': all_metrics,
            'anomalies_detected': anomaly_result['anomaly_count'],
            'training_duration_seconds': duration
        })
        
        # Guardar feature_names en metadata
        self.metadata['feature_names'] = self.feature_engineer.feature_names
        
        self._save_metadata()
        
        # 7. Registrar entrenamiento en tracker
        self.tracker.log_training({
            'version': self.VERSION,
            'n_registros': len(df_clean),
            'fecha_inicio': str(df_clean['fecha'].min().date()),
            'fecha_fin': str(df_clean['fecha'].max().date()),
            'metricas': all_metrics,
            'feature_importance': self.metadata['feature_importance'],
            'duracion': duration
        })
        
        self.is_fitted = True
        
        logger.info("\n" + "="*60)
        logger.info(f"✅ ENTRENAMIENTO COMPLETADO en {duration:.1f}s")
        logger.info("="*60)
        
        return {
            'success': True,
            'version': self.VERSION,
            'metrics': all_metrics,
            'n_features': len(self.feature_engineer.feature_names),
            'n_registros': len(df_clean),
            'anomalies': anomaly_result['anomaly_count'],
            'duration_seconds': duration
        }
    
    def predict(self, df_historical: pd.DataFrame, 
                days: int = 7) -> List[Dict[str, Any]]:
        """
        Genera predicciones para los próximos N días
        
        Args:
            df_historical: Datos históricos para calcular lags
            days: Número de días a predecir
            
        Returns:
            Lista de predicciones con intervalos
        """
        if not self.is_fitted:
            self.load_models()
        
        df_historical = df_historical.copy()
        df_historical['fecha'] = pd.to_datetime(df_historical['fecha'])
        df_historical = df_historical.sort_values('fecha')
        
        # Fechas a predecir (desde mañana)
        today = datetime.now().date()
        future_dates = []
        
        for i in range(1, days + 15):  # Pedir más días para saltar martes
            fecha = today + timedelta(days=i)
            dia_semana = fecha.weekday()
            
            # Saltar martes (cerrado)
            if dia_semana == 1:
                continue
            
            future_dates.append(fecha)
            
            if len(future_dates) >= days:
                break
        
        # Crear DataFrame de fechas futuras
        df_future = pd.DataFrame({'fecha': pd.to_datetime(future_dates)})
        
        # Generar features para fechas futuras
        X_future = self.feature_engineer.transform(df_future, historical_df=df_historical)
        
        # Predecir cada variable
        predictions = []
        dias_nombres = {
            0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves',
            4: 'Viernes', 5: 'Sábado', 6: 'Domingo'
        }
        
        for i, fecha in enumerate(future_dates):
            pred_row = {
                'fecha': fecha,
                'dia_semana': fecha.weekday(),
                'dia_nombre': dias_nombres[fecha.weekday()]
            }
            
            X_single = X_future.iloc[[i]]
            dia_semana = np.array([fecha.weekday()])
            
            for target_var in self.TARGET_VARIABLES:
                if target_var in self.models:
                    model = self.models[target_var]
                    result = model.predict_interval(X_single, dia_semana=dia_semana)
                    
                    pred_row[target_var] = float(max(0, result['prediction'][0]))
                    pred_row[f'{target_var}_min'] = float(max(0, result['lower'][0]))
                    pred_row[f'{target_var}_max'] = float(max(0, result['upper'][0]))
            
            # Detectar eventos especiales
            pred_row['evento'] = self._detect_evento(fecha)
            pred_row['multiplicador'] = self._get_multiplicador(fecha)
            
            predictions.append(pred_row)
        
        # Registrar predicciones en tracker
        for pred in predictions:
            self.tracker.log_prediction(pred, self.VERSION)
        
        logger.info(f"✅ Generadas {len(predictions)} predicciones")
        
        return predictions
    
    def _detect_evento(self, fecha) -> Optional[str]:
        """Detecta si hay un evento especial"""
        dia = fecha.day
        mes = fecha.month
        
        # Quincenas
        if dia in [1, 15]:
            return "Quincena (día_pago)"
        elif dia in [2, 16]:
            return "Quincena (día_pico)"
        elif dia in [3, 17]:
            return "Quincena (día_alto)"
        elif dia in [4, 18]:
            return "Quincena (dia_moderado)"
        
        # Festivos fijos
        festivos = {
            (12, 25): "Navidad",
            (12, 24): "Nochebuena",
            (12, 31): "Fin de Año",
            (1, 1): "Año Nuevo",
            (9, 16): "Independencia",
            (11, 2): "Día de Muertos"
        }
        
        return festivos.get((mes, dia))
    
    def _get_multiplicador(self, fecha) -> float:
        """Calcula multiplicador por eventos"""
        dia = fecha.day
        
        multiplicador = 1.0
        
        # Quincenas
        if dia in [1, 15]:
            multiplicador *= 1.30
        elif dia in [2, 16]:
            multiplicador *= 1.40
        elif dia in [3, 17]:
            multiplicador *= 1.25
        elif dia in [4, 18]:
            multiplicador *= 1.10
        
        # Festivos (adicional)
        mes = fecha.month
        if (mes, dia) in [(12, 25), (12, 24), (12, 31)]:
            multiplicador *= 1.20
        
        return multiplicador
    
    def get_model_info(self) -> Dict[str, Any]:
        """Retorna información del modelo"""
        return {
            'version': self.VERSION,
            'is_fitted': self.is_fitted,
            'last_trained': self.metadata.get('last_trained'),
            'n_registros': self.metadata.get('n_registros'),
            'metrics': self.metadata.get('metrics', {}),
            'feature_importance': self.metadata.get('feature_importance', [])[:10],
            'n_features': len(self.feature_engineer.feature_names) if self.feature_engineer.feature_names else 0
        }
    
    def get_accuracy_report(self, days: int = 30) -> Dict[str, Any]:
        """Obtiene reporte de precisión del tracker"""
        return self.tracker.get_accuracy_metrics(days)
    
    def should_retrain(self) -> Dict[str, Any]:
        """Evalúa si el modelo necesita reentrenamiento"""
        return self.tracker.should_retrain()
    
    def _save_models(self):
        """Guarda todos los modelos"""
        for var_name, model in self.models.items():
            path = self.models_dir / f"model_{var_name}.pkl"
            model.save(path)
    
    def _save_metadata(self):
        """Guarda metadata del pipeline"""
        path = self.models_dir / "pipeline_metadata.json"
        
        # Asegurar que feature_names esté en metadata
        if self.feature_engineer.feature_names:
            self.metadata['feature_names'] = self.feature_engineer.feature_names
        
        with open(path, 'w') as f:
            json.dump(self.metadata, f, indent=2, default=str)
        
        logger.info(f"✅ Metadata guardado con {len(self.metadata.get('feature_names', []))} features")
    
    def load_models(self):
        """Carga modelos guardados"""
        metadata_path = self.models_dir / "pipeline_metadata.json"
        
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                self.metadata = json.load(f)
        
        for target_var in self.TARGET_VARIABLES:
            model_path = self.models_dir / f"model_{target_var}.pkl"
            if model_path.exists():
                try:
                    self.models[target_var] = EnsembleModel.load(model_path)
                except Exception as e:
                    logger.warning(f"Error cargando modelo {target_var}: {e}")
        
        # Cargar feature names del metadata o reconstruir
        if 'feature_names' in self.metadata:
            self.feature_engineer.feature_names = self.metadata['feature_names']
        
        self.is_fitted = len(self.models) > 0
        
        if self.is_fitted:
            logger.info(f"✅ Cargados {len(self.models)} modelos")
        else:
            logger.warning("⚠️ No se encontraron modelos guardados")
