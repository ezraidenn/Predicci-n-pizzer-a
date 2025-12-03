"""
Anomaly Detection - Detección de días atípicos
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """
    Detecta días con ventas atípicas usando Isolation Forest
    
    Útil para:
    1. No contaminar el entrenamiento con outliers
    2. Alertar al usuario sobre días inusuales
    3. Identificar patrones especiales (eventos no catalogados)
    """
    
    def __init__(self, contamination: float = 0.05):
        """
        Args:
            contamination: Proporción esperada de anomalías (5% por defecto)
        """
        self.contamination = contamination
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        self.is_fitted = False
        
    def fit(self, df: pd.DataFrame) -> 'AnomalyDetector':
        """
        Entrena el detector con datos históricos
        
        Args:
            df: DataFrame con ventas históricas
        """
        features = self._extract_features(df)
        features_scaled = self.scaler.fit_transform(features)
        self.model.fit(features_scaled)
        self.is_fitted = True
        
        logger.info(f"✅ Anomaly detector entrenado con {len(df)} registros")
        return self
    
    def detect(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Detecta anomalías en los datos
        
        Returns:
            Diccionario con:
            - anomaly_mask: Boolean array
            - anomaly_indices: Índices de anomalías
            - anomaly_dates: Fechas anómalas
            - anomaly_scores: Scores de anomalía
            - summary: Resumen estadístico
        """
        if not self.is_fitted:
            self.fit(df)
        
        features = self._extract_features(df)
        features_scaled = self.scaler.transform(features)
        
        # Predicción: 1 = normal, -1 = anomalía
        predictions = self.model.predict(features_scaled)
        scores = self.model.decision_function(features_scaled)
        
        anomaly_mask = predictions == -1
        anomaly_indices = np.where(anomaly_mask)[0].tolist()
        
        # Extraer información de anomalías
        anomalies = df.iloc[anomaly_indices].copy()
        anomalies['anomaly_score'] = scores[anomaly_indices]
        
        # Clasificar tipo de anomalía
        anomaly_details = []
        for idx in anomaly_indices:
            row = df.iloc[idx]
            detail = self._classify_anomaly(row, df)
            detail['fecha'] = str(row['fecha']) if 'fecha' in row else str(idx)
            detail['anomaly_score'] = float(scores[idx])
            anomaly_details.append(detail)
        
        return {
            'anomaly_mask': anomaly_mask,
            'anomaly_indices': anomaly_indices,
            'anomaly_count': len(anomaly_indices),
            'anomaly_pct': len(anomaly_indices) / len(df) * 100,
            'anomaly_details': anomaly_details,
            'summary': {
                'total_records': len(df),
                'anomalies_found': len(anomaly_indices),
                'anomaly_rate': f"{len(anomaly_indices) / len(df) * 100:.1f}%"
            }
        }
    
    def get_clean_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Separa datos limpios de anomalías
        
        Returns:
            (df_clean, df_anomalies)
        """
        result = self.detect(df)
        mask = ~result['anomaly_mask']
        
        return df[mask].copy(), df[~mask].copy()
    
    def _extract_features(self, df: pd.DataFrame) -> np.ndarray:
        """Extrae features para detección de anomalías"""
        features = []
        
        # Ventas
        if 'total_ventas_dia' in df.columns:
            features.append(df['total_ventas_dia'].fillna(0).values)
        
        # Pizzas
        if 'pizzas_vendidas' in df.columns:
            features.append(df['pizzas_vendidas'].fillna(0).values)
        
        # Día de la semana (si hay fecha)
        if 'fecha' in df.columns:
            df_temp = df.copy()
            df_temp['fecha'] = pd.to_datetime(df_temp['fecha'])
            features.append(df_temp['fecha'].dt.dayofweek.values)
            features.append(df_temp['fecha'].dt.day.values)
        
        # Ratio pizzas/ventas
        if 'total_ventas_dia' in df.columns and 'pizzas_vendidas' in df.columns:
            ventas = df['total_ventas_dia'].fillna(1).replace(0, 1)
            pizzas = df['pizzas_vendidas'].fillna(0)
            features.append((pizzas / ventas * 100).values)
        
        return np.column_stack(features) if features else np.zeros((len(df), 1))
    
    def _classify_anomaly(self, row: pd.Series, df: pd.DataFrame) -> Dict[str, Any]:
        """Clasifica el tipo de anomalía"""
        
        result = {
            'type': 'unknown',
            'description': 'Día atípico detectado',
            'severity': 'medium'
        }
        
        if 'total_ventas_dia' not in row:
            return result
        
        ventas = row['total_ventas_dia']
        ventas_mean = df['total_ventas_dia'].mean()
        ventas_std = df['total_ventas_dia'].std()
        
        # Calcular z-score
        z_score = (ventas - ventas_mean) / ventas_std if ventas_std > 0 else 0
        
        if z_score > 2.5:
            result['type'] = 'high_sales'
            result['description'] = f'Ventas muy altas: ${ventas:,.0f} (promedio: ${ventas_mean:,.0f})'
            result['severity'] = 'high' if z_score > 3 else 'medium'
        elif z_score < -2.5:
            result['type'] = 'low_sales'
            result['description'] = f'Ventas muy bajas: ${ventas:,.0f} (promedio: ${ventas_mean:,.0f})'
            result['severity'] = 'high' if z_score < -3 else 'medium'
        elif ventas == 0:
            result['type'] = 'zero_sales'
            result['description'] = 'Día sin ventas (¿cerrado?)'
            result['severity'] = 'low'
        else:
            result['type'] = 'unusual_pattern'
            result['description'] = 'Patrón inusual en la combinación de métricas'
            result['severity'] = 'low'
        
        result['z_score'] = float(z_score)
        result['ventas'] = float(ventas)
        result['ventas_promedio'] = float(ventas_mean)
        
        return result


class StatisticalAnomalyDetector:
    """
    Detector de anomalías basado en estadísticas simples
    Más interpretable que Isolation Forest
    """
    
    def __init__(self, threshold_std: float = 2.5):
        """
        Args:
            threshold_std: Número de desviaciones estándar para considerar anomalía
        """
        self.threshold_std = threshold_std
        self.stats = {}
    
    def fit(self, df: pd.DataFrame, group_by: str = 'dia_semana') -> 'StatisticalAnomalyDetector':
        """
        Calcula estadísticas por grupo
        
        Args:
            group_by: Columna para agrupar (default: día de la semana)
        """
        df = df.copy()
        if 'fecha' in df.columns:
            df['fecha'] = pd.to_datetime(df['fecha'])
            df['dia_semana'] = df['fecha'].dt.dayofweek
        
        # Calcular media y std por grupo
        for col in ['total_ventas_dia', 'pizzas_vendidas']:
            if col in df.columns:
                self.stats[col] = df.groupby(group_by)[col].agg(['mean', 'std']).to_dict()
        
        return self
    
    def detect(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detecta anomalías basadas en desviación del promedio del día"""
        df = df.copy()
        if 'fecha' in df.columns:
            df['fecha'] = pd.to_datetime(df['fecha'])
            df['dia_semana'] = df['fecha'].dt.dayofweek
        
        anomalies = []
        
        for idx, row in df.iterrows():
            dia = row.get('dia_semana', 0)
            
            for col in ['total_ventas_dia', 'pizzas_vendidas']:
                if col in row and col in self.stats:
                    valor = row[col]
                    mean = self.stats[col]['mean'].get(dia, df[col].mean())
                    std = self.stats[col]['std'].get(dia, df[col].std())
                    
                    if std > 0:
                        z_score = (valor - mean) / std
                        
                        if abs(z_score) > self.threshold_std:
                            anomalies.append({
                                'idx': idx,
                                'fecha': str(row.get('fecha', idx)),
                                'variable': col,
                                'valor': float(valor),
                                'esperado': float(mean),
                                'z_score': float(z_score),
                                'tipo': 'alto' if z_score > 0 else 'bajo'
                            })
        
        return anomalies
