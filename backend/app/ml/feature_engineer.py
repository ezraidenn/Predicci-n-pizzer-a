"""
Advanced Feature Engineering para Series Temporales de Ventas
Genera 50+ features para capturar patrones complejos
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class AdvancedFeatureEngineer:
    """
    Genera features avanzados para predicción de ventas:
    - Temporales (día, mes, año, etc.)
    - Fourier (captura estacionalidad)
    - Lags (valores pasados)
    - Rolling windows (promedios móviles)
    - Eventos especiales (quincenas, festivos)
    """
    
    # Festivos mexicanos fijos
    FESTIVOS_FIJOS = {
        (1, 1): "Año Nuevo",
        (2, 5): "Día de la Constitución",
        (3, 21): "Natalicio de Benito Juárez", 
        (5, 1): "Día del Trabajo",
        (9, 16): "Día de la Independencia",
        (11, 2): "Día de Muertos",
        (11, 20): "Revolución Mexicana",
        (12, 25): "Navidad",
        (12, 31): "Fin de Año"
    }
    
    def __init__(self, target_cols: List[str] = None):
        """
        Args:
            target_cols: Columnas objetivo para calcular lags
        """
        self.target_cols = target_cols or [
            'total_ventas_dia', 'pizzas_vendidas', 'pizzas_pastor',
            'pizzas_chuleta', 'alitas_vendidas', 'baguettes_vendidas',
            'papas_gajo_vendidas'
        ]
        self.feature_names = []
        
    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Genera todas las features para el DataFrame
        
        Args:
            df: DataFrame con columna 'fecha' y targets
            
        Returns:
            DataFrame con todas las features generadas
        """
        df = df.copy()
        df['fecha'] = pd.to_datetime(df['fecha'])
        df = df.sort_values('fecha').reset_index(drop=True)
        
        logger.info(f"Generando features para {len(df)} registros...")
        
        features = pd.DataFrame(index=df.index)
        
        # 1. Features temporales básicos
        features = self._add_temporal_features(df, features)
        
        # 2. Features de Fourier (estacionalidad)
        features = self._add_fourier_features(df, features)
        
        # 3. Features de quincena
        features = self._add_quincena_features(df, features)
        
        # 4. Features de festivos
        features = self._add_holiday_features(df, features)
        
        # 5. Lags (valores pasados)
        features = self._add_lag_features(df, features)
        
        # 6. Rolling windows
        features = self._add_rolling_features(df, features)
        
        # 7. Features de tendencia
        features = self._add_trend_features(df, features)
        
        # 8. Interacciones
        features = self._add_interaction_features(features)
        
        # Guardar nombres de features
        self.feature_names = features.columns.tolist()
        
        logger.info(f"✅ Generadas {len(self.feature_names)} features")
        
        return features
    
    def transform(self, df: pd.DataFrame, historical_df: pd.DataFrame = None) -> pd.DataFrame:
        """
        Transforma nuevos datos usando features ya definidas
        Útil para predicción de fechas futuras
        
        Args:
            df: DataFrame con fechas a predecir
            historical_df: Datos históricos para calcular lags
        """
        df = df.copy()
        df['fecha'] = pd.to_datetime(df['fecha'])
        
        features = pd.DataFrame(index=df.index)
        
        # Features que no requieren histórico
        features = self._add_temporal_features(df, features)
        features = self._add_fourier_features(df, features)
        features = self._add_quincena_features(df, features)
        features = self._add_holiday_features(df, features)
        features = self._add_trend_features(df, features)
        
        # Lags y rolling necesitan histórico
        if historical_df is not None:
            features = self._add_lag_features_for_future(df, features, historical_df)
            features = self._add_rolling_features_for_future(df, features, historical_df)
        
        features = self._add_interaction_features(features)
        
        # Asegurar mismas columnas que en entrenamiento
        for col in self.feature_names:
            if col not in features.columns:
                features[col] = 0
        
        return features[self.feature_names]
    
    def _add_temporal_features(self, df: pd.DataFrame, features: pd.DataFrame) -> pd.DataFrame:
        """Features temporales básicos"""
        fecha = df['fecha']
        
        features['dia_semana'] = fecha.dt.dayofweek  # 0=Lunes, 6=Domingo
        features['dia_mes'] = fecha.dt.day
        features['mes'] = fecha.dt.month
        features['semana_año'] = fecha.dt.isocalendar().week.astype(int)
        features['dia_año'] = fecha.dt.dayofyear
        features['año'] = fecha.dt.year
        
        # One-hot para días de la semana
        for i in range(7):
            features[f'es_dia_{i}'] = (features['dia_semana'] == i).astype(int)
        
        # Es fin de semana
        features['es_fin_semana'] = features['dia_semana'].isin([4, 5, 6]).astype(int)
        
        # Es inicio de semana
        features['es_inicio_semana'] = features['dia_semana'].isin([0, 2]).astype(int)
        
        return features
    
    def _add_fourier_features(self, df: pd.DataFrame, features: pd.DataFrame) -> pd.DataFrame:
        """Features de Fourier para capturar estacionalidad"""
        
        # Estacionalidad semanal (período = 7 días)
        for k in range(1, 4):  # 3 armónicos
            features[f'sin_week_{k}'] = np.sin(2 * np.pi * k * features['dia_semana'] / 7)
            features[f'cos_week_{k}'] = np.cos(2 * np.pi * k * features['dia_semana'] / 7)
        
        # Estacionalidad mensual (período ≈ 30 días)
        for k in range(1, 3):  # 2 armónicos
            features[f'sin_month_{k}'] = np.sin(2 * np.pi * k * features['dia_mes'] / 30.5)
            features[f'cos_month_{k}'] = np.cos(2 * np.pi * k * features['dia_mes'] / 30.5)
        
        # Estacionalidad anual (período = 365 días)
        for k in range(1, 3):
            features[f'sin_year_{k}'] = np.sin(2 * np.pi * k * features['dia_año'] / 365.25)
            features[f'cos_year_{k}'] = np.cos(2 * np.pi * k * features['dia_año'] / 365.25)
        
        return features
    
    def _add_quincena_features(self, df: pd.DataFrame, features: pd.DataFrame) -> pd.DataFrame:
        """Features de quincena (crítico para México)"""
        dia_mes = features['dia_mes']
        
        # Es período de quincena (días 1-4 y 15-18)
        features['es_quincena'] = (
            ((dia_mes >= 1) & (dia_mes <= 4)) | 
            ((dia_mes >= 15) & (dia_mes <= 18))
        ).astype(int)
        
        # Intensidad de quincena (4=máximo, 0=no quincena)
        features['intensidad_quincena'] = 0
        features.loc[dia_mes.isin([1, 15]), 'intensidad_quincena'] = 4  # Día de pago
        features.loc[dia_mes.isin([2, 16]), 'intensidad_quincena'] = 3  # Día siguiente
        features.loc[dia_mes.isin([3, 17]), 'intensidad_quincena'] = 2  # Efecto residual
        features.loc[dia_mes.isin([4, 18]), 'intensidad_quincena'] = 1  # Final
        
        # Distancia al día de pago más cercano
        features['dias_desde_quincena'] = dia_mes.apply(
            lambda d: min(abs(d - 1), abs(d - 15), abs(d - 16) if d < 16 else abs(d - 15))
        )
        
        return features
    
    def _add_holiday_features(self, df: pd.DataFrame, features: pd.DataFrame) -> pd.DataFrame:
        """Features de festivos mexicanos"""
        fecha = df['fecha']
        
        # Es festivo
        features['es_festivo'] = fecha.apply(
            lambda d: 1 if (d.month, d.day) in self.FESTIVOS_FIJOS else 0
        )
        
        # Días hasta Navidad
        features['dias_para_navidad'] = fecha.apply(
            lambda d: self._dias_hasta_fecha(d, d.year, 12, 25)
        )
        
        # Días hasta Año Nuevo  
        features['dias_para_año_nuevo'] = fecha.apply(
            lambda d: self._dias_hasta_fecha(d, d.year + 1, 1, 1)
        )
        
        # Es temporada navideña (Dic 15 - Ene 6)
        features['es_temporada_navidad'] = fecha.apply(
            lambda d: 1 if (d.month == 12 and d.day >= 15) or (d.month == 1 and d.day <= 6) else 0
        )
        
        # Es víspera de festivo
        features['es_vispera_festivo'] = fecha.apply(
            lambda d: 1 if ((d + timedelta(days=1)).month, (d + timedelta(days=1)).day) in self.FESTIVOS_FIJOS else 0
        )
        
        return features
    
    def _add_lag_features(self, df: pd.DataFrame, features: pd.DataFrame) -> pd.DataFrame:
        """Lags de variables objetivo"""
        
        # Lags principales: mismo día hace N semanas
        lag_days = [1, 7, 14, 21, 28]
        
        for col in ['total_ventas_dia', 'pizzas_vendidas']:
            if col in df.columns:
                for lag in lag_days:
                    features[f'{col}_lag_{lag}'] = df[col].shift(lag)
        
        return features
    
    def _add_lag_features_for_future(self, df: pd.DataFrame, features: pd.DataFrame, 
                                     historical_df: pd.DataFrame) -> pd.DataFrame:
        """Calcular lags para fechas futuras usando histórico"""
        
        historical_df = historical_df.copy()
        historical_df['fecha'] = pd.to_datetime(historical_df['fecha'])
        historical_df = historical_df.sort_values('fecha')
        
        lag_days = [1, 7, 14, 21, 28]
        
        for col in ['total_ventas_dia', 'pizzas_vendidas']:
            if col in historical_df.columns:
                for lag in lag_days:
                    values = []
                    for fecha in df['fecha']:
                        fecha_lag = fecha - timedelta(days=lag)
                        match = historical_df[historical_df['fecha'] == fecha_lag]
                        if len(match) > 0:
                            values.append(match[col].iloc[0])
                        else:
                            # Usar promedio si no hay dato exacto
                            values.append(historical_df[col].mean())
                    features[f'{col}_lag_{lag}'] = values
        
        return features
    
    def _add_rolling_features(self, df: pd.DataFrame, features: pd.DataFrame) -> pd.DataFrame:
        """Promedios móviles y desviación estándar"""
        
        windows = [7, 14, 28]
        
        for col in ['total_ventas_dia', 'pizzas_vendidas']:
            if col in df.columns:
                for window in windows:
                    features[f'{col}_ma_{window}'] = df[col].rolling(window, min_periods=1).mean()
                    features[f'{col}_std_{window}'] = df[col].rolling(window, min_periods=1).std().fillna(0)
                    
                # Ratio actual vs promedio móvil
                features[f'{col}_ratio_ma7'] = df[col] / features[f'{col}_ma_7'].replace(0, 1)
        
        return features
    
    def _add_rolling_features_for_future(self, df: pd.DataFrame, features: pd.DataFrame,
                                          historical_df: pd.DataFrame) -> pd.DataFrame:
        """Rolling features para fechas futuras"""
        
        historical_df = historical_df.copy()
        historical_df['fecha'] = pd.to_datetime(historical_df['fecha'])
        
        windows = [7, 14, 28]
        
        for col in ['total_ventas_dia', 'pizzas_vendidas']:
            if col in historical_df.columns:
                # Usar los últimos N días del histórico
                for window in windows:
                    last_values = historical_df[col].tail(window)
                    features[f'{col}_ma_{window}'] = last_values.mean()
                    features[f'{col}_std_{window}'] = last_values.std()
                
                features[f'{col}_ratio_ma7'] = 1.0  # Neutral para futuro
        
        return features
    
    def _add_trend_features(self, df: pd.DataFrame, features: pd.DataFrame) -> pd.DataFrame:
        """Features de tendencia"""
        fecha = df['fecha']
        
        # Días desde el inicio de los datos
        fecha_min = fecha.min()
        features['dias_desde_inicio'] = (fecha - fecha_min).dt.days
        
        # Normalizado (0-1)
        max_dias = features['dias_desde_inicio'].max()
        if max_dias > 0:
            features['tendencia_normalizada'] = features['dias_desde_inicio'] / max_dias
        else:
            features['tendencia_normalizada'] = 0
        
        return features
    
    def _add_interaction_features(self, features: pd.DataFrame) -> pd.DataFrame:
        """Features de interacción entre variables"""
        
        # Quincena + Fin de semana (combo poderoso)
        if 'es_quincena' in features.columns and 'es_fin_semana' in features.columns:
            features['quincena_x_finsemana'] = features['es_quincena'] * features['es_fin_semana']
        
        # Festivo + Fin de semana
        if 'es_festivo' in features.columns and 'es_fin_semana' in features.columns:
            features['festivo_x_finsemana'] = features['es_festivo'] * features['es_fin_semana']
        
        # Intensidad quincena * día específico
        if 'intensidad_quincena' in features.columns:
            for i in [4, 5, 6]:  # Viernes, Sábado, Domingo
                if f'es_dia_{i}' in features.columns:
                    features[f'quincena_x_dia_{i}'] = features['intensidad_quincena'] * features[f'es_dia_{i}']
        
        return features
    
    def _dias_hasta_fecha(self, fecha_actual, año_target, mes_target, dia_target) -> int:
        """Calcula días hasta una fecha específica"""
        try:
            fecha_target = datetime(año_target, mes_target, dia_target)
            if fecha_target < fecha_actual:
                fecha_target = datetime(año_target + 1, mes_target, dia_target)
            return (fecha_target - fecha_actual).days
        except:
            return 365
    
    def get_feature_names(self) -> List[str]:
        """Retorna nombres de features generadas"""
        return self.feature_names
    
    def get_feature_importance_groups(self) -> Dict[str, List[str]]:
        """Agrupa features por categoría para análisis"""
        groups = {
            'temporal': [f for f in self.feature_names if any(x in f for x in ['dia_', 'mes', 'año', 'semana'])],
            'fourier': [f for f in self.feature_names if any(x in f for x in ['sin_', 'cos_'])],
            'quincena': [f for f in self.feature_names if 'quincena' in f],
            'festivos': [f for f in self.feature_names if any(x in f for x in ['festivo', 'navidad', 'año_nuevo'])],
            'lags': [f for f in self.feature_names if 'lag_' in f],
            'rolling': [f for f in self.feature_names if any(x in f for x in ['_ma_', '_std_', 'ratio'])],
            'tendencia': [f for f in self.feature_names if 'tendencia' in f or 'dias_desde' in f],
            'interacciones': [f for f in self.feature_names if '_x_' in f]
        }
        return groups
