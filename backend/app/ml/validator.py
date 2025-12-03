"""
Time Series Validation - Validación correcta para series temporales
NO usar random split (causa data leakage)
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Generator, Any
from sklearn.metrics import mean_absolute_error, mean_squared_error
import logging

logger = logging.getLogger(__name__)


def mean_absolute_percentage_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Calcula MAPE evitando división por cero"""
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    # Evitar división por cero
    mask = y_true != 0
    if mask.sum() == 0:
        return 0.0
    
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100


class TimeSeriesValidator:
    """
    Validación cruzada para series temporales con expanding window
    
    Ejemplo con 5 splits y test_size=14:
    
    Split 1: [====TRAIN====][TEST]................
    Split 2: [======TRAIN======][TEST]............
    Split 3: [========TRAIN========][TEST]........
    Split 4: [==========TRAIN==========][TEST]....
    Split 5: [============TRAIN============][TEST]
    """
    
    def __init__(self, n_splits: int = 5, test_size: int = 14, min_train_size: int = 60):
        """
        Args:
            n_splits: Número de splits de validación
            test_size: Tamaño del conjunto de test en cada split
            min_train_size: Tamaño mínimo de entrenamiento
        """
        self.n_splits = n_splits
        self.test_size = test_size
        self.min_train_size = min_train_size
    
    def split(self, X: pd.DataFrame) -> Generator[Tuple[List[int], List[int]], None, None]:
        """
        Genera índices de train/test para cada split
        
        Args:
            X: DataFrame con los datos
            
        Yields:
            Tupla (train_indices, test_indices)
        """
        n = len(X)
        
        # Calcular tamaño de cada incremento
        total_test = self.n_splits * self.test_size
        available = n - self.min_train_size
        
        if available < total_test:
            logger.warning(f"Datos insuficientes para {self.n_splits} splits. Ajustando...")
            actual_splits = max(1, available // self.test_size)
        else:
            actual_splits = self.n_splits
        
        for i in range(actual_splits):
            # El train crece en cada split
            train_end = self.min_train_size + (i * self.test_size)
            test_start = train_end
            test_end = min(test_start + self.test_size, n)
            
            train_idx = list(range(train_end))
            test_idx = list(range(test_start, test_end))
            
            if len(test_idx) > 0:
                yield train_idx, test_idx
    
    def evaluate(self, model, X: pd.DataFrame, y: pd.Series, 
                 feature_cols: List[str] = None) -> Dict[str, Any]:
        """
        Evalúa un modelo usando validación temporal
        
        Args:
            model: Modelo con métodos fit() y predict()
            X: Features
            y: Target
            feature_cols: Columnas a usar como features (si X tiene más columnas)
            
        Returns:
            Diccionario con métricas promedio y por split
        """
        if feature_cols is None:
            feature_cols = X.columns.tolist()
        
        all_metrics = []
        all_predictions = []
        
        for fold, (train_idx, test_idx) in enumerate(self.split(X)):
            X_train = X.iloc[train_idx][feature_cols]
            X_test = X.iloc[test_idx][feature_cols]
            y_train = y.iloc[train_idx]
            y_test = y.iloc[test_idx]
            
            # Manejar NaN en features
            X_train = X_train.fillna(X_train.mean())
            X_test = X_test.fillna(X_train.mean())
            
            # Entrenar y predecir
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            
            # Calcular métricas
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            mape = mean_absolute_percentage_error(y_test, y_pred)
            
            fold_metrics = {
                'fold': fold + 1,
                'train_size': len(train_idx),
                'test_size': len(test_idx),
                'mae': mae,
                'rmse': rmse,
                'mape': mape
            }
            all_metrics.append(fold_metrics)
            
            # Guardar predicciones para análisis
            all_predictions.extend([
                {'idx': idx, 'y_true': yt, 'y_pred': yp}
                for idx, yt, yp in zip(test_idx, y_test, y_pred)
            ])
            
            logger.info(f"  Fold {fold+1}: MAE={mae:.2f}, RMSE={rmse:.2f}, MAPE={mape:.2f}%")
        
        # Calcular promedios
        metrics_df = pd.DataFrame(all_metrics)
        
        return {
            'mae_mean': metrics_df['mae'].mean(),
            'mae_std': metrics_df['mae'].std(),
            'rmse_mean': metrics_df['rmse'].mean(),
            'rmse_std': metrics_df['rmse'].std(),
            'mape_mean': metrics_df['mape'].mean(),
            'mape_std': metrics_df['mape'].std(),
            'n_splits': len(all_metrics),
            'fold_details': all_metrics,
            'predictions': all_predictions
        }
    
    def evaluate_with_intervals(self, model_point, model_lower, model_upper,
                                 X: pd.DataFrame, y: pd.Series,
                                 feature_cols: List[str] = None) -> Dict[str, Any]:
        """
        Evalúa modelo con intervalos de predicción
        
        Args:
            model_point: Modelo para predicción puntual
            model_lower: Modelo para límite inferior (Q10)
            model_upper: Modelo para límite superior (Q90)
            
        Returns:
            Métricas incluyendo coverage de intervalos
        """
        if feature_cols is None:
            feature_cols = X.columns.tolist()
        
        all_metrics = []
        
        for fold, (train_idx, test_idx) in enumerate(self.split(X)):
            X_train = X.iloc[train_idx][feature_cols].fillna(0)
            X_test = X.iloc[test_idx][feature_cols].fillna(0)
            y_train = y.iloc[train_idx]
            y_test = y.iloc[test_idx]
            
            # Entrenar los 3 modelos
            model_point.fit(X_train, y_train)
            model_lower.fit(X_train, y_train)
            model_upper.fit(X_train, y_train)
            
            # Predecir
            y_pred = model_point.predict(X_test)
            y_lower = model_lower.predict(X_test)
            y_upper = model_upper.predict(X_test)
            
            # Métricas de punto
            mae = mean_absolute_error(y_test, y_pred)
            mape = mean_absolute_percentage_error(y_test, y_pred)
            
            # Coverage: % de valores reales dentro del intervalo
            within_interval = ((y_test >= y_lower) & (y_test <= y_upper)).sum()
            coverage = within_interval / len(y_test) * 100
            
            # Ancho promedio del intervalo
            interval_width = np.mean(y_upper - y_lower)
            
            fold_metrics = {
                'fold': fold + 1,
                'mae': mae,
                'mape': mape,
                'coverage_80': coverage,
                'interval_width': interval_width
            }
            all_metrics.append(fold_metrics)
        
        metrics_df = pd.DataFrame(all_metrics)
        
        return {
            'mae_mean': metrics_df['mae'].mean(),
            'mape_mean': metrics_df['mape'].mean(),
            'coverage_80_mean': metrics_df['coverage_80'].mean(),
            'interval_width_mean': metrics_df['interval_width'].mean(),
            'fold_details': all_metrics
        }


class WalkForwardValidator:
    """
    Walk-forward validation: simula predicción en producción
    Entrena con todos los datos hasta t-1, predice t
    """
    
    def __init__(self, initial_train_size: int = 60, step: int = 1):
        """
        Args:
            initial_train_size: Tamaño inicial del conjunto de entrenamiento
            step: Cuántos días avanzar en cada iteración
        """
        self.initial_train_size = initial_train_size
        self.step = step
    
    def evaluate(self, model, X: pd.DataFrame, y: pd.Series,
                 feature_cols: List[str] = None,
                 retrain_frequency: int = 7) -> Dict[str, Any]:
        """
        Evaluación walk-forward
        
        Args:
            retrain_frequency: Reentrenar cada N días
            
        Returns:
            Métricas y predicciones día a día
        """
        if feature_cols is None:
            feature_cols = X.columns.tolist()
        
        n = len(X)
        predictions = []
        last_train_idx = self.initial_train_size
        
        for i in range(self.initial_train_size, n, self.step):
            # Decidir si reentrenar
            if (i - last_train_idx) >= retrain_frequency or i == self.initial_train_size:
                X_train = X.iloc[:i][feature_cols].fillna(0)
                y_train = y.iloc[:i]
                model.fit(X_train, y_train)
                last_train_idx = i
            
            # Predecir siguiente(s) punto(s)
            end_idx = min(i + self.step, n)
            X_test = X.iloc[i:end_idx][feature_cols].fillna(0)
            y_test = y.iloc[i:end_idx]
            y_pred = model.predict(X_test)
            
            for j, (yt, yp) in enumerate(zip(y_test, y_pred)):
                predictions.append({
                    'idx': i + j,
                    'y_true': yt,
                    'y_pred': yp,
                    'error': abs(yt - yp),
                    'error_pct': abs(yt - yp) / yt * 100 if yt != 0 else 0
                })
        
        pred_df = pd.DataFrame(predictions)
        
        return {
            'mae': pred_df['error'].mean(),
            'mape': pred_df['error_pct'].mean(),
            'predictions': predictions,
            'n_predictions': len(predictions)
        }


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Calcula todas las métricas de evaluación
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mape = mean_absolute_percentage_error(y_true, y_pred)
    
    # R² (coeficiente de determinación)
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
    
    # Error máximo
    max_error = np.max(np.abs(y_true - y_pred))
    
    return {
        'mae': mae,
        'rmse': rmse,
        'mape': mape,
        'r2': r2,
        'max_error': max_error
    }
