"""
Advanced Predictor - Quantile Regression, SHAP, AutoML
"""
import pandas as pd
import numpy as np
import logging
import pickle
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    logging.warning("SHAP no disponible")

try:
    from flaml import AutoML
    FLAML_AVAILABLE = True
except ImportError:
    FLAML_AVAILABLE = False
    logging.warning("FLAML no disponible")

logger = logging.getLogger(__name__)


class AdvancedPredictor:
    """Predictor avanzado con Quantile Regression, SHAP y AutoML"""
    
    def __init__(self, models_dir: Path):
        self.models_dir = models_dir
        self.quantile_models = {}  # {target: {lower, median, upper}}
        self.shap_explainers = {}
        self.automl_models = {}
        
        self.target_vars = [
            'total_ventas_dia',
            'pizzas_vendidas',
            'baguettes_vendidas',
            'papas_gajo_vendidas'
        ]
    
    def train_quantile_models(self, X_train, y_train, target: str) -> Dict[str, Any]:
        """
        Entrena modelos de Quantile Regression para intervalos de confianza
        
        Returns:
            Dict con modelos para percentiles 10, 50, 90
        """
        logger.info(f"Entrenando Quantile Regression para {target}...")
        
        quantiles = {
            'lower': 0.1,   # Percentil 10 (pesimista)
            'median': 0.5,  # Percentil 50 (esperado)
            'upper': 0.9    # Percentil 90 (optimista)
        }
        
        models = {}
        
        for name, alpha in quantiles.items():
            logger.info(f"  Entrenando {name} (α={alpha})...")
            
            model = GradientBoostingRegressor(
                loss='quantile',
                alpha=alpha,
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
            
            pipeline = Pipeline([
                ('scaler', StandardScaler()),
                ('model', model)
            ])
            
            pipeline.fit(X_train, y_train)
            models[name] = pipeline
            
            logger.info(f"  ✓ {name} entrenado")
        
        # Guardar modelos
        for name, model in models.items():
            model_file = self.models_dir / f"quantile_{target}_{name}.pkl"
            with open(model_file, 'wb') as f:
                pickle.dump(model, f)
        
        self.quantile_models[target] = models
        
        return models
    
    def predict_with_intervals(self, X, target: str) -> Dict[str, np.ndarray]:
        """
        Predice con intervalos de confianza
        
        Returns:
            Dict con predicciones: {lower, median, upper} o None si no hay modelos
        """
        if target not in self.quantile_models:
            # Cargar modelos si no están en memoria
            self.load_quantile_models(target)
        
        # Si aún no hay modelos, retornar None
        if target not in self.quantile_models or not self.quantile_models[target]:
            return None
        
        predictions = {}
        for name, model in self.quantile_models[target].items():
            predictions[name] = model.predict(X)
        
        return predictions
    
    def load_quantile_models(self, target: str):
        """Carga modelos de quantile regression"""
        models = {}
        for name in ['lower', 'median', 'upper']:
            model_file = self.models_dir / f"quantile_{target}_{name}.pkl"
            if model_file.exists():
                with open(model_file, 'rb') as f:
                    models[name] = pickle.load(f)
        
        if models:
            self.quantile_models[target] = models
            logger.info(f"Modelos quantile cargados para {target}")
    
    def create_shap_explainer(self, model, X_train, target: str):
        """
        Crea explicador SHAP para el modelo
        """
        if not SHAP_AVAILABLE:
            logger.warning("SHAP no disponible, saltando explicabilidad")
            return None
        
        logger.info(f"Creando explicador SHAP para {target}...")
        
        try:
            # Usar TreeExplainer para modelos de árbol
            explainer = shap.TreeExplainer(model.named_steps['model'])
            
            # Guardar explainer
            explainer_file = self.models_dir / f"shap_explainer_{target}.pkl"
            with open(explainer_file, 'wb') as f:
                pickle.dump(explainer, f)
            
            self.shap_explainers[target] = explainer
            logger.info(f"✓ Explicador SHAP creado para {target}")
            
            return explainer
        except Exception as e:
            logger.error(f"Error creando SHAP explainer: {e}")
            return None
    
    def explain_prediction(self, X, target: str, feature_names: List[str]) -> Dict[str, Any]:
        """
        Explica una predicción usando SHAP
        
        Returns:
            Dict con valores SHAP y explicación en texto
        """
        if not SHAP_AVAILABLE or target not in self.shap_explainers:
            return None
        
        try:
            explainer = self.shap_explainers[target]
            
            # Calcular SHAP values
            X_scaled = self.quantile_models[target]['median'].named_steps['scaler'].transform(X)
            shap_values = explainer.shap_values(X_scaled)
            
            # Si es una sola predicción
            if len(shap_values.shape) == 1 or shap_values.shape[0] == 1:
                shap_values = shap_values.flatten()
                
                # Obtener top features
                top_indices = np.argsort(np.abs(shap_values))[-5:][::-1]
                
                explanations = []
                for idx in top_indices:
                    feature = feature_names[idx]
                    impact = shap_values[idx]
                    value = X[0, idx] if X.shape[0] == 1 else X[idx]
                    
                    # Crear explicación en texto
                    direction = "aumenta" if impact > 0 else "disminuye"
                    explanations.append({
                        'feature': feature,
                        'impact': float(impact),
                        'value': float(value),
                        'text': f"{feature} {direction} la predicción en ${abs(impact):.2f}"
                    })
                
                return {
                    'shap_values': shap_values.tolist(),
                    'feature_names': feature_names,
                    'top_explanations': explanations,
                    'base_value': float(explainer.expected_value)
                }
            
        except Exception as e:
            logger.error(f"Error explicando predicción: {e}")
            return None
    
    def train_automl(self, X_train, y_train, target: str, time_budget: int = 300) -> Any:
        """
        Entrena modelo usando AutoML (FLAML)
        
        Args:
            time_budget: Tiempo en segundos para búsqueda (default: 5 minutos)
        """
        if not FLAML_AVAILABLE:
            logger.warning("FLAML no disponible, saltando AutoML")
            return None
        
        logger.info(f"Entrenando AutoML para {target} (budget: {time_budget}s)...")
        
        try:
            automl = AutoML()
            
            automl.fit(
                X_train, y_train,
                task='regression',
                time_budget=time_budget,
                metric='mae',
                estimator_list=['lgbm', 'xgboost', 'rf', 'extra_tree'],
                ensemble=True,
                verbose=0
            )
            
            logger.info(f"✓ AutoML completado para {target}")
            logger.info(f"  Mejor modelo: {automl.best_estimator}")
            logger.info(f"  Mejor MAE: {automl.best_loss:.2f}")
            
            # Guardar modelo
            model_file = self.models_dir / f"automl_{target}.pkl"
            with open(model_file, 'wb') as f:
                pickle.dump(automl, f)
            
            self.automl_models[target] = automl
            
            return automl
            
        except Exception as e:
            logger.error(f"Error en AutoML: {e}")
            return None
    
    def load_automl_model(self, target: str):
        """Carga modelo AutoML"""
        model_file = self.models_dir / f"automl_{target}.pkl"
        if model_file.exists():
            with open(model_file, 'rb') as f:
                self.automl_models[target] = pickle.load(f)
            logger.info(f"Modelo AutoML cargado para {target}")
    
    def predict_with_automl(self, X, target: str) -> np.ndarray:
        """Predice usando modelo AutoML"""
        if target not in self.automl_models:
            self.load_automl_model(target)
        
        if target in self.automl_models:
            return self.automl_models[target].predict(X)
        
        return None
