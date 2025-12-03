"""
LightGBM Model Wrapper - Modelo principal para predicción
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
import pickle
from pathlib import Path
import logging

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    
from sklearn.linear_model import Ridge, QuantileRegressor
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


class LightGBMModel:
    """
    Wrapper para LightGBM optimizado para predicción de ventas
    
    Features:
    - Entrenamiento con early stopping
    - Predicción de intervalos (quantile regression)
    - Feature importance
    - Serialización/deserialización
    """
    
    # Configuración optimizada para datos pequeños (~300 registros)
    DEFAULT_PARAMS = {
        'objective': 'regression',
        'metric': 'mae',
        'boosting_type': 'gbdt',
        'n_estimators': 500,
        'learning_rate': 0.05,
        'max_depth': 6,
        'num_leaves': 31,
        'min_child_samples': 5,  # Bajo porque tenemos pocos datos
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'reg_alpha': 0.1,
        'reg_lambda': 0.1,
        'random_state': 42,
        'verbose': -1
    }
    
    # Parámetros para quantile regression
    QUANTILE_PARAMS = {
        'objective': 'quantile',
        'metric': 'quantile',
        'boosting_type': 'gbdt',
        'n_estimators': 300,
        'learning_rate': 0.05,
        'max_depth': 5,
        'num_leaves': 20,
        'min_child_samples': 5,
        'random_state': 42,
        'verbose': -1
    }
    
    def __init__(self, name: str = "lgbm", use_quantiles: bool = True):
        """
        Args:
            name: Nombre del modelo (para identificación)
            use_quantiles: Si crear modelos para intervalos de confianza
        """
        self.name = name
        self.use_quantiles = use_quantiles
        
        # Modelo principal
        self.model = None
        
        # Modelos para intervalos
        self.model_q10 = None  # Percentil 10
        self.model_q90 = None  # Percentil 90
        
        # Fallback si LightGBM no está disponible
        self.fallback_model = None
        self.scaler = StandardScaler()
        
        self.feature_names = []
        self.feature_importance_ = {}
        self.is_fitted = False
        
    def fit(self, X: pd.DataFrame, y: pd.Series, 
            eval_set: Tuple[pd.DataFrame, pd.Series] = None) -> 'LightGBMModel':
        """
        Entrena el modelo
        
        Args:
            X: Features de entrenamiento
            y: Target de entrenamiento
            eval_set: (X_val, y_val) para early stopping
        """
        self.feature_names = X.columns.tolist()
        
        # Preprocesar
        X_clean = X.fillna(0).replace([np.inf, -np.inf], 0)
        y_clean = y.fillna(y.mean())
        
        if LIGHTGBM_AVAILABLE:
            self._fit_lightgbm(X_clean, y_clean, eval_set)
        else:
            self._fit_fallback(X_clean, y_clean)
        
        self.is_fitted = True
        logger.info(f"✅ Modelo {self.name} entrenado con {len(X)} registros")
        
        return self
    
    def _fit_lightgbm(self, X: pd.DataFrame, y: pd.Series, 
                      eval_set: Tuple = None):
        """Entrenamiento con LightGBM"""
        
        # Modelo principal (predicción puntual)
        params = self.DEFAULT_PARAMS.copy()
        
        if eval_set:
            X_val, y_val = eval_set
            X_val = X_val.fillna(0).replace([np.inf, -np.inf], 0)
            
            self.model = lgb.LGBMRegressor(**params)
            self.model.fit(
                X, y,
                eval_set=[(X_val, y_val)],
                callbacks=[lgb.early_stopping(50, verbose=False)]
            )
        else:
            self.model = lgb.LGBMRegressor(**params)
            self.model.fit(X, y)
        
        # Feature importance
        self.feature_importance_ = dict(zip(
            self.feature_names,
            self.model.feature_importances_
        ))
        
        # Modelos de quantile para intervalos
        if self.use_quantiles:
            # Q10 (límite inferior)
            params_q10 = self.QUANTILE_PARAMS.copy()
            params_q10['alpha'] = 0.1
            self.model_q10 = lgb.LGBMRegressor(**params_q10)
            self.model_q10.fit(X, y)
            
            # Q90 (límite superior)
            params_q90 = self.QUANTILE_PARAMS.copy()
            params_q90['alpha'] = 0.9
            self.model_q90 = lgb.LGBMRegressor(**params_q90)
            self.model_q90.fit(X, y)
    
    def _fit_fallback(self, X: pd.DataFrame, y: pd.Series):
        """Fallback a Ridge si LightGBM no está disponible"""
        logger.warning("⚠️ LightGBM no disponible, usando Ridge regression")
        
        X_scaled = self.scaler.fit_transform(X)
        
        self.fallback_model = Ridge(alpha=1.0)
        self.fallback_model.fit(X_scaled, y)
        
        # Feature importance (coeficientes)
        self.feature_importance_ = dict(zip(
            self.feature_names,
            np.abs(self.fallback_model.coef_)
        ))
        
        if self.use_quantiles:
            try:
                # Sklearn QuantileRegressor como fallback
                self.model_q10 = QuantileRegressor(quantile=0.1, alpha=0.1)
                self.model_q10.fit(X_scaled, y)
                
                self.model_q90 = QuantileRegressor(quantile=0.9, alpha=0.1)
                self.model_q90.fit(X_scaled, y)
            except Exception as e:
                logger.warning(f"No se pudieron crear modelos de quantile: {e}")
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predicción puntual"""
        if not self.is_fitted:
            raise ValueError("Modelo no entrenado. Llamar fit() primero.")
        
        X_clean = X[self.feature_names].fillna(0).replace([np.inf, -np.inf], 0)
        
        if self.model is not None:
            return self.model.predict(X_clean)
        else:
            X_scaled = self.scaler.transform(X_clean)
            return self.fallback_model.predict(X_scaled)
    
    def predict_interval(self, X: pd.DataFrame) -> Dict[str, np.ndarray]:
        """
        Predicción con intervalos de confianza
        
        Returns:
            Dict con 'prediction', 'lower', 'upper'
        """
        if not self.is_fitted:
            raise ValueError("Modelo no entrenado. Llamar fit() primero.")
        
        X_clean = X[self.feature_names].fillna(0).replace([np.inf, -np.inf], 0)
        
        # Predicción puntual
        if self.model is not None:
            pred = self.model.predict(X_clean)
        else:
            X_scaled = self.scaler.transform(X_clean)
            pred = self.fallback_model.predict(X_scaled)
        
        # Intervalos
        if self.model_q10 is not None and self.model_q90 is not None:
            if self.model is not None:
                lower = self.model_q10.predict(X_clean)
                upper = self.model_q90.predict(X_clean)
            else:
                X_scaled = self.scaler.transform(X_clean)
                lower = self.model_q10.predict(X_scaled)
                upper = self.model_q90.predict(X_scaled)
        else:
            # Fallback: ±15% de la predicción
            lower = pred * 0.85
            upper = pred * 1.15
        
        # Asegurar que lower < upper
        lower = np.minimum(lower, pred * 0.9)
        upper = np.maximum(upper, pred * 1.1)
        
        return {
            'prediction': pred,
            'lower': lower,
            'upper': upper
        }
    
    def get_feature_importance(self, top_n: int = 20) -> List[Dict[str, Any]]:
        """
        Retorna las features más importantes
        
        Args:
            top_n: Número de features a retornar
        """
        sorted_features = sorted(
            self.feature_importance_.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]
        
        total = sum(v for _, v in sorted_features)
        
        return [
            {
                'feature': name,
                'importance': float(importance),
                'importance_pct': float(importance / total * 100) if total > 0 else 0
            }
            for name, importance in sorted_features
        ]
    
    def save(self, path: Path):
        """Guarda el modelo"""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'name': self.name,
            'feature_names': self.feature_names,
            'feature_importance': self.feature_importance_,
            'use_quantiles': self.use_quantiles,
            'is_fitted': self.is_fitted,
            'model': self.model,
            'model_q10': self.model_q10,
            'model_q90': self.model_q90,
            'fallback_model': self.fallback_model,
            'scaler': self.scaler
        }
        
        with open(path, 'wb') as f:
            pickle.dump(data, f)
        
        logger.info(f"✅ Modelo guardado en {path}")
    
    @classmethod
    def load(cls, path: Path) -> 'LightGBMModel':
        """Carga un modelo guardado"""
        with open(path, 'rb') as f:
            data = pickle.load(f)
        
        model = cls(name=data['name'], use_quantiles=data['use_quantiles'])
        model.feature_names = data['feature_names']
        model.feature_importance_ = data['feature_importance']
        model.is_fitted = data['is_fitted']
        model.model = data['model']
        model.model_q10 = data.get('model_q10')
        model.model_q90 = data.get('model_q90')
        model.fallback_model = data.get('fallback_model')
        model.scaler = data.get('scaler', StandardScaler())
        
        logger.info(f"✅ Modelo cargado desde {path}")
        return model
