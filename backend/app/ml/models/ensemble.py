"""
Ensemble Model - Combina múltiples modelos para predicción robusta
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from pathlib import Path
import pickle
import logging

from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

from .lgbm_model import LightGBMModel

logger = logging.getLogger(__name__)


class EnsembleModel:
    """
    Ensemble de modelos para predicción robusta
    
    Combina:
    1. LightGBM - Captura patrones no lineales
    2. Ridge - Baseline lineal robusto
    3. Historical Average - Promedio por día de semana (fallback)
    
    Los pesos se ajustan basándose en validación cruzada
    """
    
    def __init__(self, name: str = "ensemble"):
        """
        Args:
            name: Nombre del ensemble
        """
        self.name = name
        
        # Modelos
        self.lgbm = LightGBMModel(name=f"{name}_lgbm", use_quantiles=True)
        self.ridge = None
        self.ridge_scaler = StandardScaler()
        
        # Promedios históricos por día de semana
        self.historical_avg = {}
        
        # Pesos del ensemble (ajustados para mejor captura de estacionalidad)
        # Historical captura bien la estacionalidad semanal
        # LightGBM captura tendencias y eventos especiales
        self.weights = {
            'lgbm': 0.35,
            'ridge': 0.15,
            'historical': 0.50  # Mayor peso a histórico por día de semana
        }
        
        self.feature_names = []
        self.is_fitted = False
        
    def fit(self, X: pd.DataFrame, y: pd.Series, 
            df_original: pd.DataFrame = None) -> 'EnsembleModel':
        """
        Entrena todos los modelos del ensemble
        
        Args:
            X: Features
            y: Target
            df_original: DataFrame original para calcular promedios históricos
        """
        self.feature_names = X.columns.tolist()
        
        # 1. Entrenar LightGBM
        logger.info("Entrenando LightGBM...")
        self.lgbm.fit(X, y)
        
        # 2. Entrenar Ridge
        logger.info("Entrenando Ridge...")
        X_clean = X.fillna(0).replace([np.inf, -np.inf], 0)
        X_scaled = self.ridge_scaler.fit_transform(X_clean)
        self.ridge = Ridge(alpha=1.0)
        self.ridge.fit(X_scaled, y)
        
        # 3. Calcular promedios históricos por día de semana
        if df_original is not None and 'fecha' in df_original.columns:
            logger.info("Calculando promedios históricos por día de semana...")
            df_temp = df_original.copy().reset_index(drop=True)
            df_temp['fecha'] = pd.to_datetime(df_temp['fecha'])
            df_temp['dia_semana'] = df_temp['fecha'].dt.dayofweek
            
            # Agregar el target al df_temp para calcular correctamente
            y_reset = y.reset_index(drop=True)
            df_temp['target'] = y_reset.values
            
            # === FILTRAR ANOMALÍAS (días atípicos como cortes de luz, etc.) ===
            # Calcular estadísticas globales para detectar outliers
            global_mean = df_temp['target'].mean()
            global_std = df_temp['target'].std()
            
            # Umbral: menos del 30% del promedio global = día anómalo (cerrado parcial, etc.)
            umbral_minimo = global_mean * 0.30
            
            # También filtrar días extremadamente altos (>3 std)
            umbral_maximo = global_mean + (3 * global_std)
            
            # Filtrar anomalías
            df_clean = df_temp[
                (df_temp['target'] >= umbral_minimo) & 
                (df_temp['target'] <= umbral_maximo)
            ].copy()
            
            anomalias_filtradas = len(df_temp) - len(df_clean)
            if anomalias_filtradas > 0:
                logger.warning(f"  ⚠️ Filtrados {anomalias_filtradas} días anómalos (ventas < ${umbral_minimo:,.0f})")
                # Mostrar cuáles se filtraron
                anomalias = df_temp[df_temp['target'] < umbral_minimo]
                for _, row in anomalias.iterrows():
                    logger.warning(f"    - {row['fecha'].strftime('%Y-%m-%d')}: ${row['target']:,.0f}")
            
            # Usar solo los últimos 90 días para promedios más recientes (aumentado de 60)
            if len(df_clean) > 90:
                df_clean = df_clean.tail(90)
            
            for dia in range(7):
                subset = df_clean[df_clean['dia_semana'] == dia]
                if len(subset) > 0:
                    # Usar mediana en lugar de media para ser más robusto a outliers
                    self.historical_avg[dia] = {
                        'mean': float(subset['target'].median()),  # Mediana es más estable
                        'std': float(subset['target'].std()) if len(subset) > 1 else float(y.std())
                    }
                    logger.info(f"  Día {dia}: mediana=${subset['target'].median():,.0f}, n={len(subset)}")
                else:
                    self.historical_avg[dia] = {
                        'mean': float(y.mean()),
                        'std': float(y.std())
                    }
        else:
            # Fallback: usar promedio global
            for dia in range(7):
                self.historical_avg[dia] = {
                    'mean': float(y.mean()),
                    'std': float(y.std())
                }
        
        self.is_fitted = True
        logger.info(f"✅ Ensemble {self.name} entrenado")
        
        return self
    
    def predict(self, X: pd.DataFrame, dia_semana: np.ndarray = None) -> np.ndarray:
        """
        Predicción combinada del ensemble
        
        Args:
            X: Features
            dia_semana: Array con día de la semana para cada observación
        """
        if not self.is_fitted:
            raise ValueError("Ensemble no entrenado")
        
        X_clean = X[self.feature_names].fillna(0).replace([np.inf, -np.inf], 0)
        
        # Predicciones individuales
        pred_lgbm = self.lgbm.predict(X_clean)
        
        X_scaled = self.ridge_scaler.transform(X_clean)
        pred_ridge = self.ridge.predict(X_scaled)
        
        # Predicción histórica
        if dia_semana is not None:
            pred_hist = np.array([
                self.historical_avg.get(d, {'mean': pred_lgbm[i]})['mean']
                for i, d in enumerate(dia_semana)
            ])
        else:
            # Intentar extraer día de semana de features
            if 'dia_semana' in X.columns:
                pred_hist = X['dia_semana'].apply(
                    lambda d: self.historical_avg.get(int(d), {'mean': 0})['mean']
                ).values
            else:
                pred_hist = pred_lgbm  # Fallback
        
        # Combinación ponderada
        final = (
            self.weights['lgbm'] * pred_lgbm +
            self.weights['ridge'] * pred_ridge +
            self.weights['historical'] * pred_hist
        )
        
        return final
    
    def predict_interval(self, X: pd.DataFrame, 
                         dia_semana: np.ndarray = None) -> Dict[str, np.ndarray]:
        """
        Predicción con intervalos de confianza
        """
        if not self.is_fitted:
            raise ValueError("Ensemble no entrenado")
        
        X_clean = X[self.feature_names].fillna(0).replace([np.inf, -np.inf], 0)
        
        # Usar intervalos de LightGBM (más sofisticados)
        lgbm_intervals = self.lgbm.predict_interval(X_clean)
        
        # Predicción del ensemble
        pred_ensemble = self.predict(X, dia_semana)
        
        # Ajustar intervalos basados en ensemble
        # Mantener el ancho relativo de LightGBM pero centrar en ensemble
        lgbm_center = lgbm_intervals['prediction']
        lgbm_lower_offset = lgbm_center - lgbm_intervals['lower']
        lgbm_upper_offset = lgbm_intervals['upper'] - lgbm_center
        
        return {
            'prediction': pred_ensemble,
            'lower': pred_ensemble - lgbm_lower_offset,
            'upper': pred_ensemble + lgbm_upper_offset
        }
    
    def get_feature_importance(self, top_n: int = 20) -> List[Dict[str, Any]]:
        """Feature importance del modelo LightGBM (el más interpretable)"""
        return self.lgbm.get_feature_importance(top_n)
    
    def adjust_weights(self, validation_errors: Dict[str, float]):
        """
        Ajusta los pesos basándose en errores de validación
        
        Args:
            validation_errors: Dict con errores por modelo {'lgbm': mae, 'ridge': mae, ...}
        """
        # Inversamente proporcional al error
        total_inv_error = sum(1 / e for e in validation_errors.values() if e > 0)
        
        if total_inv_error > 0:
            for model_name, error in validation_errors.items():
                if model_name in self.weights and error > 0:
                    self.weights[model_name] = (1 / error) / total_inv_error
        
        logger.info(f"Pesos ajustados: {self.weights}")
    
    def save(self, path: Path):
        """Guarda el ensemble completo"""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Guardar LightGBM por separado
        lgbm_path = path.parent / f"{path.stem}_lgbm.pkl"
        self.lgbm.save(lgbm_path)
        
        data = {
            'name': self.name,
            'feature_names': self.feature_names,
            'weights': self.weights,
            'historical_avg': self.historical_avg,
            'ridge': self.ridge,
            'ridge_scaler': self.ridge_scaler,
            'is_fitted': self.is_fitted,
            'lgbm_path': str(lgbm_path)
        }
        
        with open(path, 'wb') as f:
            pickle.dump(data, f)
        
        logger.info(f"✅ Ensemble guardado en {path}")
    
    @classmethod
    def load(cls, path: Path) -> 'EnsembleModel':
        """Carga un ensemble guardado"""
        with open(path, 'rb') as f:
            data = pickle.load(f)
        
        ensemble = cls(name=data['name'])
        ensemble.feature_names = data['feature_names']
        ensemble.weights = data['weights']
        ensemble.historical_avg = data['historical_avg']
        ensemble.ridge = data['ridge']
        ensemble.ridge_scaler = data['ridge_scaler']
        ensemble.is_fitted = data['is_fitted']
        
        # Cargar LightGBM
        lgbm_path = Path(data['lgbm_path'])
        if lgbm_path.exists():
            ensemble.lgbm = LightGBMModel.load(lgbm_path)
        
        logger.info(f"✅ Ensemble cargado desde {path}")
        return ensemble
