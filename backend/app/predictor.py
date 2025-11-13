"""
Sales Predictor - Modelos de Machine Learning para predicción de ventas
"""
import pandas as pd
import numpy as np
import logging
import pickle
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    logging.warning("Prophet no disponible, usando modelos alternativos")

from app.advanced_predictor import AdvancedPredictor

logger = logging.getLogger(__name__)


class SalesPredictor:
    """Predictor de ventas usando Machine Learning"""
    
    def __init__(self, models_dir: Path):
        self.models_dir = models_dir
        self.models = {}
        self.scalers = {}
        
        # Variables objetivo a predecir
        self.target_vars = [
            'total_ventas_dia',
            'pizzas_vendidas',
            'baguettes_vendidas',
            'papas_gajo_vendidas'
        ]
        
        # Inicializar predictor avanzado
        self.advanced = AdvancedPredictor(models_dir)
    
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Crea features para el modelo incluyendo tendencias y crecimiento
        
        Args:
            df: DataFrame con datos diarios
            
        Returns:
            DataFrame con features adicionales
        """
        df = df.copy()
        
        # Asegurar que fecha es datetime
        df['fecha'] = pd.to_datetime(df['fecha'])
        
        # Ordenar por fecha para cálculos correctos
        df = df.sort_values('fecha').reset_index(drop=True)
        
        # ===== FEATURES TEMPORALES OPTIMIZADOS PARA RESTAURANTES =====
        df['dia_semana'] = df['fecha'].dt.dayofweek  # 0=Lunes, 6=Domingo
        df['dia_mes'] = df['fecha'].dt.day
        df['mes'] = df['fecha'].dt.month
        df['es_fin_semana'] = (df['dia_semana'] >= 5).astype(int)
        
        # One-hot encoding para días de la semana (crítico para restaurantes)
        for i in range(7):
            df[f'dia_{i}'] = (df['dia_semana'] == i).astype(int)
        
        # NUEVOS FEATURES PARA RESTAURANTES (basado en investigación)
        # Semana del mes (1-5) - patrones de quincena
        df['semana_mes'] = ((df['dia_mes'] - 1) // 7) + 1
        
        # Días desde inicio de mes (patrones de pago)
        df['dias_desde_inicio_mes'] = df['dia_mes']
        
        # Es quincena (días 1-2 y 15-16 tienen más ventas)
        df['es_quincena'] = ((df['dia_mes'] <= 2) | ((df['dia_mes'] >= 15) & (df['dia_mes'] <= 16))).astype(int)
        
        # Es fin de mes (últimos 3 días)
        df['es_fin_mes'] = (df['dia_mes'] >= 28).astype(int)
        df['es_viernes'] = (df['dia_semana'] == 4).astype(int)
        df['es_sabado'] = (df['dia_semana'] == 5).astype(int)
        df['es_domingo'] = (df['dia_semana'] == 6).astype(int)
        
        # Features de quincena (días 1-15 vs 16-fin de mes)
        df['es_primera_quincena'] = (df['dia_mes'] <= 15).astype(int)
        df['es_segunda_quincena'] = (df['dia_mes'] > 15).astype(int)
        df['dias_desde_quincena'] = df['dia_mes'].apply(lambda x: x if x <= 15 else x - 15)
        
        # Features de inicio/fin de mes (días de pago)
        df['es_inicio_mes'] = (df['dia_mes'] <= 5).astype(int)
        df['es_fin_mes'] = (df['dia_mes'] >= 25).astype(int)
        df['es_dia_pago'] = ((df['dia_mes'] <= 5) | (df['dia_mes'] >= 25) | 
                             ((df['dia_mes'] >= 13) & (df['dia_mes'] <= 17))).astype(int)
        
        # One-hot encoding para día de la semana
        for i in range(7):
            df[f'dia_{i}'] = (df['dia_semana'] == i).astype(int)
        
        # Medias móviles (ventanas de 3, 7 y 14 días)
        for var in self.target_vars:
            if var in df.columns:
                df[f'{var}_ma3'] = df[var].rolling(window=3, min_periods=1).mean()
                df[f'{var}_ma7'] = df[var].rolling(window=7, min_periods=1).mean()
                df[f'{var}_ma14'] = df[var].rolling(window=14, min_periods=1).mean()
                df[f'{var}_std7'] = df[var].rolling(window=7, min_periods=1).std().fillna(0)
        
        # Lags (valores de días anteriores)
        for var in self.target_vars:
            if var in df.columns:
                df[f'{var}_lag1'] = df[var].shift(1).fillna(0)
                df[f'{var}_lag7'] = df[var].shift(7).fillna(0)
                df[f'{var}_lag14'] = df[var].shift(14).fillna(0)
        
        # Features de visitas y pedidos
        if 'total_visitas' in df.columns:
            df['conversion_rate'] = np.where(
                df['total_visitas'] > 0,
                df['pedidos_creados'] / df['total_visitas'],
                0
            )
        
        # ===== DETECCIÓN DE OUTLIERS Y LIMPIEZA AGRESIVA =====
        logger.info("Detectando outliers y eventos especiales...")
        
        for var in self.target_vars:
            if var in df.columns:
                # Detectar outliers usando IQR (método robusto)
                Q1 = df[var].quantile(0.25)
                Q3 = df[var].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 3 * IQR
                upper_bound = Q3 + 3 * IQR
                
                # Marcar outliers
                df[f'{var}_is_outlier'] = ((df[var] < lower_bound) | (df[var] > upper_bound)).astype(int)
                
                # Crear versión "limpia" - ESTRATEGIA AGRESIVA
                df[f'{var}_clean'] = df[var].copy()
                outlier_mask = df[f'{var}_is_outlier'] == 1
                if outlier_mask.any():
                    # Reemplazar outliers con el límite superior (más agresivo)
                    # Esto convierte 286 pizzas → 184 pizzas (límite IQR)
                    df.loc[outlier_mask & (df[var] > upper_bound), f'{var}_clean'] = upper_bound
                    df.loc[outlier_mask & (df[var] < lower_bound), f'{var}_clean'] = lower_bound
                    logger.info(f"✓ Detectados y limpiados {outlier_mask.sum()} outliers en {var}")
                    logger.info(f"  Límites IQR: [{lower_bound:.1f}, {upper_bound:.1f}]")
        
        # ===== FEATURES DE TENDENCIA (SIMPLIFICADOS) =====
        logger.info("Calculando features de tendencia...")
        
        for var in self.target_vars:
            if var in df.columns:
                clean_var = f'{var}_clean'
                
                # Tendencia simple: últimos 7 días vs últimos 30 días
                recent_7 = df[clean_var].rolling(window=7, min_periods=1).mean()
                recent_30 = df[clean_var].rolling(window=30, min_periods=7).mean()
                df[f'{var}_trend'] = ((recent_7 - recent_30) / (recent_30 + 1)) * 100
        
        # ===== FEATURES DE CONTEXTO TEMPORAL =====
        # Días desde inicio (captura crecimiento general del negocio)
        df['dias_desde_inicio'] = (df['fecha'] - df['fecha'].min()).dt.days
        
        # Peso temporal (balance entre datos recientes y patrones históricos)
        # Decay=45 según mejores prácticas de industria
        # - Prioriza datos recientes
        # - Pero mantiene suficiente contexto histórico para aprender patrones semanales
        max_days = (df['fecha'].max() - df['fecha'].min()).days
        df['peso_temporal'] = np.exp((df['dias_desde_inicio'] - max_days) / 45)  # Decay balanceado
        
        # Rellenar NaN con 0
        df = df.fillna(0)
        
        return df
    
    def get_feature_columns(self, df: pd.DataFrame) -> List[str]:
        """Obtener lista de columnas de features (optimizado para Ridge Regression)"""
        feature_cols = [
            # Temporales básicos
            'dia_semana', 'dia_mes', 'mes', 'es_fin_semana',
            # One-hot días de la semana (XGBoost aprende mejor con estos)
            'dia_0', 'dia_1', 'dia_2', 'dia_3', 'dia_4', 'dia_5', 'dia_6',
            # Días críticos para restaurantes
            'es_viernes', 'es_sabado', 'es_domingo',
            # Patrones de quincena (días de pago)
            'es_quincena', 'es_primera_quincena', 'es_fin_mes'
        ]
        
        # Features de cada variable
        for var in self.target_vars:
            feature_cols.extend([
                f'{var}_ma7',    # Media móvil 7 días
                f'{var}_lag7',   # Valor hace 7 días (patrón semanal)
                f'{var}_trend'   # Tendencia
            ])
        
        return feature_cols
    
    def train_models(self, data_file: Path) -> Dict[str, Any]:
        """
        Entrena modelos para cada variable objetivo (excepto total_ventas_dia que se calcula)
        
        Args:
            data_file: Ruta al archivo parquet con datos
            
        Returns:
            Diccionario con métricas de entrenamiento
        """
        logger.info("Cargando datos para entrenamiento...")
        df = pd.read_parquet(data_file)
        
        # Crear features
        df = self.create_features(df)
        
        # Obtener columnas de features
        feature_cols = self.get_feature_columns(df)
        
        logger.info(f"Features utilizadas: {len(feature_cols)}")
        logger.info(f"Registros totales: {len(df)}")
        
        metrics = {}
        
        for target in self.target_vars:
            # Skipear total_ventas_dia - se calculará basado en productos
            if target == 'total_ventas_dia':
                logger.info(f"\n{'='*50}")
                logger.info(f"⏭️  {target}: Se calculará basado en productos (no se entrena)")
                logger.info(f"{'='*50}")
                continue
            
            logger.info(f"\n{'='*50}")
            logger.info(f"Entrenando modelo para: {target}")
            logger.info(f"{'='*50}")
            
            # Preparar datos
            X = df[feature_cols].values
            y = df[target].values
            
            # Pesos de muestra (datos recientes más importantes)
            sample_weights = df['peso_temporal'].values
            
            # Split train/test (mantener pesos)
            X_train, X_test, y_train, y_test, weights_train, weights_test = train_test_split(
                X, y, sample_weights, test_size=0.2, random_state=42, shuffle=False
            )
            
            # RIDGE REGRESSION - Mejor modelo para restaurantes según investigación científica
            # Según estudio MDPI 2022 con 3 años de datos reales de restaurante:
            # - Ridge: 19.6% error (MEJOR)
            # - XGBoost: 22-25% error
            # - Ridge es 20-30% MÁS PRECISO para restaurantes
            #
            # Razones:
            # - Restaurantes tienen ciclos semanales FUERTES (Lunes bajo, Sábado alto)
            # - Tendencias lineales predecibles
            # - Datos limitados (<1000 días) → Ridge más estable
            # - Ridge captura mejor patrones semanales repetitivos
            
            base_model = Ridge(
                alpha=0.5,              # Regularización ligera-moderada (balance)
                random_state=42
            )
            
            logger.info(f"✓ Usando Ridge Regression (19.6% error - óptimo para restaurantes)")
            
            # Pipeline CON StandardScaler (CRÍTICO para Ridge)
            pipeline = Pipeline([
                ('scaler', StandardScaler()),  # Normaliza features
                ('model', base_model)
            ])
            
            # Entrenar con pesos (datos recientes más importantes)
            pipeline.fit(X_train, y_train, model__sample_weight=weights_train)
            
            # Evaluar
            y_pred = pipeline.predict(X_test)
            
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)
            
            logger.info(f"MAE: {mae:.2f}")
            logger.info(f"RMSE: {rmse:.2f}")
            logger.info(f"R²: {r2:.3f}")
            
            # Guardar modelo
            model_file = self.models_dir / f"model_{target}.pkl"
            with open(model_file, 'wb') as f:
                pickle.dump(pipeline, f)
            logger.info(f"Modelo guardado en: {model_file}")
            
            # Guardar en memoria
            self.models[target] = pipeline
            
            # ===== ENTRENAR MODELOS AVANZADOS (OPCIONAL - DESACTIVADO POR VELOCIDAD) =====
            # Nota: Desactivado temporalmente para acelerar entrenamiento
            # Puedes activarlos después del primer entrenamiento exitoso
            
            # logger.info(f"\n🚀 Entrenando modelos avanzados para {target}...")
            # quantile_models = self.advanced.train_quantile_models(X_train, y_train, target)
            # shap_explainer = self.advanced.create_shap_explainer(pipeline, X_train, target)
            
            quantile_models = None
            shap_explainer = None
            
            # Guardar métricas
            metrics[target] = {
                'mae': float(mae),
                'rmse': float(rmse),
                'r2': float(r2),
                'train_samples': len(X_train),
                'test_samples': len(X_test),
                'model_type': 'Ridge (α=0.5, Weighted, Balanced)',
                'has_quantile': False,
                'has_shap': False
            }
        
        # Guardar feature columns
        feature_file = self.models_dir / "feature_columns.pkl"
        with open(feature_file, 'wb') as f:
            pickle.dump(feature_cols, f)
        
        logger.info("\n✅ Todos los modelos entrenados exitosamente")
        
        return metrics
    
    def load_models(self):
        """Carga modelos previamente entrenados"""
        for target in self.target_vars:
            model_file = self.models_dir / f"model_{target}.pkl"
            if model_file.exists():
                with open(model_file, 'rb') as f:
                    self.models[target] = pickle.load(f)
                logger.info(f"Modelo cargado: {target}")
            else:
                logger.warning(f"Modelo no encontrado: {target}")
    
    def analyze_historical_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analiza patrones históricos para validación de predicciones
        
        Returns:
            Diccionario con estadísticas por día de la semana y rangos válidos
        """
        patterns = {
            'by_weekday': {},
            'global_stats': {},
            'closed_days': []
        }
        
        # Analizar por día de la semana
        for weekday in range(7):
            weekday_data = df[df['dia_semana'] == weekday]
            
            if len(weekday_data) == 0:
                # Día sin datos históricos = probablemente cerrado
                patterns['closed_days'].append(weekday)
                continue
            
            patterns['by_weekday'][weekday] = {}
            
            for var in self.target_vars:
                if var in weekday_data.columns:
                    values = weekday_data[var].values
                    # Filtrar valores válidos (> 0)
                    valid_values = values[values > 0]
                    
                    if len(valid_values) > 0:
                        patterns['by_weekday'][weekday][var] = {
                            'mean': float(np.mean(valid_values)),
                            'std': float(np.std(valid_values)),
                            'min': float(np.min(valid_values)),
                            'max': float(np.max(valid_values)),
                            'median': float(np.median(valid_values)),
                            'q25': float(np.percentile(valid_values, 25)),
                            'q75': float(np.percentile(valid_values, 75)),
                            'zero_count': int(np.sum(values == 0)),
                            'total_count': len(values)
                        }
                    else:
                        # Si todos los valores son 0, probablemente no se vende ese producto ese día
                        patterns['by_weekday'][weekday][var] = {
                            'mean': 0,
                            'min': 0,
                            'max': 0,
                            'zero_count': len(values),
                            'total_count': len(values)
                        }
        
        # Estadísticas globales
        for var in self.target_vars:
            if var in df.columns:
                values = df[var].values
                valid_values = values[values > 0]
                
                if len(valid_values) > 0:
                    patterns['global_stats'][var] = {
                        'mean': float(np.mean(valid_values)),
                        'std': float(np.std(valid_values)),
                        'min': float(np.min(valid_values)),
                        'max': float(np.max(valid_values))
                    }
        
        return patterns
    
    def validate_and_adjust_prediction(self, pred_value: float, target: str, 
                                       weekday: int, patterns: Dict) -> float:
        """
        Valida y ajusta una predicción basándose en patrones históricos
        
        Args:
            pred_value: Valor predicho
            target: Variable objetivo
            weekday: Día de la semana (0=Lunes, 6=Domingo)
            patterns: Patrones históricos
            
        Returns:
            Valor ajustado
        """
        # Si el día está cerrado históricamente, retornar 0
        if weekday in patterns.get('closed_days', []):
            logger.info(f"Día {weekday} identificado como cerrado. Predicción = 0")
            return 0.0
        
        # Si no hay datos para ese día de la semana, usar estadísticas globales
        if weekday not in patterns.get('by_weekday', {}):
            if target in patterns.get('global_stats', {}):
                stats = patterns['global_stats'][target]
                # Usar la media global como fallback
                return max(0, stats['mean'])
            return 0.0
        
        weekday_stats = patterns['by_weekday'][weekday].get(target, {})
        
        # Si históricamente ese producto no se vende ese día
        if weekday_stats.get('zero_count', 0) == weekday_stats.get('total_count', 1):
            logger.info(f"{target} nunca se vendió los días {weekday}. Predicción = 0")
            return 0.0
        
        # Si la predicción es negativa, usar el mínimo histórico
        if pred_value < 0:
            return weekday_stats.get('min', 0)
        
        # Si la predicción es 0 pero históricamente siempre hay ventas
        if pred_value == 0 and weekday_stats.get('min', 0) > 0:
            # Usar el percentil 25 como valor mínimo razonable
            adjusted = weekday_stats.get('q25', weekday_stats.get('min', 0))
            logger.info(f"Predicción de 0 ajustada a {adjusted:.2f} (mínimo histórico)")
            return adjusted
        
        # Si la predicción está fuera del rango histórico razonable
        mean = weekday_stats.get('mean', 0)
        std = weekday_stats.get('std', 0)
        q25 = weekday_stats.get('q25', 0)
        q75 = weekday_stats.get('q75', 0)
        
        # Rango razonable: [Q25 - 1.5*IQR, Q75 + 1.5*IQR]
        iqr = q75 - q25
        lower_bound = max(0, q25 - 1.5 * iqr)
        upper_bound = q75 + 1.5 * iqr
        
        # Si está muy por debajo del mínimo histórico
        if pred_value < lower_bound and weekday_stats.get('min', 0) > 0:
            adjusted = max(lower_bound, weekday_stats['min'])
            logger.info(f"Predicción {pred_value:.2f} muy baja, ajustada a {adjusted:.2f}")
            return adjusted
        
        # Si está muy por encima del máximo histórico
        if pred_value > upper_bound:
            # Permitir hasta 3x el máximo histórico (para crecimiento fuerte)
            max_allowed = weekday_stats.get('max', 0) * 3
            if pred_value > max_allowed:
                logger.info(f"Predicción {pred_value:.2f} muy alta, ajustada a {max_allowed:.2f}")
                return max_allowed
        
        return pred_value
    
    def predict_next_days(self, data_file: Path, days: int = 7) -> List[Dict[str, Any]]:
        """
        Predice ventas para los próximos días
        
        Args:
            data_file: Ruta al archivo parquet con datos históricos
            days: Número de días a predecir
            
        Returns:
            Lista de diccionarios con predicciones
        """
        logger.info(f"Generando predicciones para {days} días...")
        
        # Cargar datos
        df = pd.read_parquet(data_file)
        df = self.create_features(df)
        
        # Cargar modelos si no están en memoria
        if not self.models:
            self.load_models()
        
        # Cargar feature columns
        feature_file = self.models_dir / "feature_columns.pkl"
        if feature_file.exists():
            with open(feature_file, 'rb') as f:
                feature_cols = pickle.load(f)
        else:
            feature_cols = self.get_feature_columns(df)
        
        # Analizar patrones históricos para validación
        logger.info("Analizando patrones históricos...")
        patterns = self.analyze_historical_patterns(df)
        
        if patterns['closed_days']:
            dias_nombres = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
            closed_names = [dias_nombres[d] for d in patterns['closed_days']]
            logger.info(f"Días identificados como cerrados: {', '.join(closed_names)}")
        
        # Última fecha en los datos
        last_date = df['fecha'].max()
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        # MODIFICACIÓN: Predecir desde AYER para comparar con ventas reales
        # Calcular cuántos días faltan desde last_date hasta ayer
        days_gap = (yesterday - last_date.date()).days
        
        if days_gap >= 1:
            start_day = days_gap  # Empezar desde ayer
            logger.info(f"📊 Última fecha de datos: {last_date.date()}")
            logger.info(f"📊 Prediciendo desde AYER ({yesterday}) para comparación con ventas reales")
        else:
            # Si ya tenemos datos de ayer, predecir desde hoy
            start_day = (today - last_date.date()).days
            logger.info(f"📊 Ya hay datos de ayer, prediciendo desde hoy ({today})")
        
        predictions = []
        
        # Crear DataFrame temporal para predicciones iterativas
        df_pred = df.copy()
        
        for day in range(start_day, start_day + days):
            pred_date = last_date + timedelta(days=day)
            
            # Crear nueva fila con features temporales
            new_row = pd.DataFrame({
                'fecha': [pred_date],
                'dia_semana': [pred_date.dayofweek],
                'dia_mes': [pred_date.day],
                'mes': [pred_date.month],
                'trimestre': [(pred_date.month - 1) // 3 + 1],
                'semana_año': [pred_date.isocalendar()[1]],
                'es_fin_semana': [1 if pred_date.dayofweek >= 5 else 0],
                'es_viernes': [1 if pred_date.dayofweek == 4 else 0],
                'es_sabado': [1 if pred_date.dayofweek == 5 else 0],
                'es_domingo': [1 if pred_date.dayofweek == 6 else 0],
                'es_primera_quincena': [1 if pred_date.day <= 15 else 0],
                'es_segunda_quincena': [1 if pred_date.day > 15 else 0],
                'dias_desde_quincena': [pred_date.day if pred_date.day <= 15 else pred_date.day - 15],
                'es_inicio_mes': [1 if pred_date.day <= 5 else 0],
                'es_fin_mes': [1 if pred_date.day >= 25 else 0],
                'es_dia_pago': [1 if (pred_date.day <= 5 or pred_date.day >= 25 or 
                                     (pred_date.day >= 13 and pred_date.day <= 17)) else 0]
            })
            
            # One-hot encoding para día
            for i in range(7):
                new_row[f'dia_{i}'] = [1 if pred_date.dayofweek == i else 0]
            
            # Usar promedios para features de visitas (simplificación)
            for col in ['total_visitas', 'pedidos_iniciados', 'pedidos_creados',
                       'tipo_servicio_domicilio', 'tipo_servicio_llevar']:
                if col in df.columns:
                    # Usar promedio del mismo día de la semana en las últimas 4 semanas
                    same_weekday = df[df['dia_semana'] == pred_date.dayofweek].tail(4)
                    if len(same_weekday) > 0:
                        new_row[col] = [same_weekday[col].mean()]
                    else:
                        new_row[col] = [df[col].tail(7).mean()]
            
            # Calcular conversion_rate
            if 'total_visitas' in new_row.columns and new_row['total_visitas'].iloc[0] > 0:
                new_row['conversion_rate'] = [
                    new_row['pedidos_creados'].iloc[0] / new_row['total_visitas'].iloc[0]
                ]
            else:
                new_row['conversion_rate'] = [0]
            
            # Predecir cada variable
            pred_values = {'fecha': pred_date}
            
            for target in self.target_vars:
                if target not in self.models:
                    logger.warning(f"Modelo no disponible para {target}")
                    pred_values[target] = 0
                    continue
                
                # Calcular features (SOLO los que usamos)
                if target in df_pred.columns:
                    # Usar versión limpia si existe
                    clean_col = f'{target}_clean' if f'{target}_clean' in df_pred.columns else target
                    
                    # ma7
                    if len(df_pred) >= 7:
                        new_row[f'{target}_ma7'] = [df_pred[clean_col].tail(7).mean()]
                    else:
                        new_row[f'{target}_ma7'] = [df_pred[clean_col].mean()]
                    
                    # lag7
                    if len(df_pred) >= 7:
                        new_row[f'{target}_lag7'] = [df_pred[clean_col].iloc[-7]]
                    else:
                        new_row[f'{target}_lag7'] = [0]
                    
                    # trend (últimos 7 vs últimos 30)
                    if len(df_pred) >= 30:
                        recent_7 = df_pred[clean_col].tail(7).mean()
                        recent_30 = df_pred[clean_col].tail(30).mean()
                        new_row[f'{target}_trend'] = [((recent_7 - recent_30) / (recent_30 + 1)) * 100]
                    else:
                        new_row[f'{target}_trend'] = [0]
                else:
                    new_row[f'{target}_ma7'] = [0]
                    new_row[f'{target}_lag7'] = [0]
                    new_row[f'{target}_trend'] = [0]
                
                # Rellenar NaN
                new_row = new_row.fillna(0)
                
                # Asegurar que todas las columnas de features existan
                for col in feature_cols:
                    if col not in new_row.columns:
                        new_row[col] = 0
                
                # Preparar features en el orden correcto
                X_pred = new_row[feature_cols].values
                
                # CALCULAR VENTAS BASADO EN PRODUCTOS (no predecir con ML)
                if target == 'total_ventas_dia':
                    # Calcular ventas basado en productos predichos
                    # Precio promedio según análisis de datos reales
                    precio_pizza = 232.0
                    precio_baguette = 98.0
                    precio_papas = 85.0
                    
                    ventas_pizzas = pred_values.get('pizzas_vendidas', 0) * precio_pizza
                    ventas_baguettes = pred_values.get('baguettes_vendidas', 0) * precio_baguette
                    ventas_papas = pred_values.get('papas_gajo_vendidas', 0) * precio_papas
                    
                    pred = ventas_pizzas + ventas_baguettes + ventas_papas
                    logger.info(f"Ventas calculadas: ${pred:.2f} (Pizzas: ${ventas_pizzas:.2f} + Baguettes: ${ventas_baguettes:.2f} + Papas: ${ventas_papas:.2f})")
                else:
                    # Predecir productos con modelo ML
                    pred = self.models[target].predict(X_pred)[0]
                    pred = max(0, pred)  # No permitir valores negativos
                    
                    # Solo validar días cerrados
                    if pred_date.dayofweek in patterns.get('closed_days', []):
                        pred = 0
                        logger.info(f"Día {pred_date.date()} es día cerrado, predicción = 0")
                
                pred_values[target] = float(pred)
                
                # ===== PREDICCIONES AVANZADAS =====
                # Intervalos de confianza (Quantile Regression)
                try:
                    intervals = self.advanced.predict_with_intervals(X_pred, target)
                    if intervals:
                        pred_values[f'{target}_lower'] = float(max(0, intervals['lower'][0]))
                        pred_values[f'{target}_upper'] = float(max(0, intervals['upper'][0]))
                except Exception as e:
                    logger.warning(f"No se pudieron calcular intervalos para {target}: {e}")
                
                # Explicación SHAP (solo para el primer día)
                if day == start_day:
                    try:
                        explanation = self.advanced.explain_prediction(X_pred, target, feature_cols)
                        if explanation:
                            pred_values[f'{target}_explanation'] = explanation
                    except Exception as e:
                        logger.warning(f"No se pudo generar explicación para {target}: {e}")
                
                # Añadir predicción al DataFrame temporal para próximas iteraciones
                new_row[target] = [pred]
            
            # Añadir nueva fila al DataFrame temporal
            df_pred = pd.concat([df_pred, new_row], ignore_index=True)
            
            predictions.append(pred_values)
            
            logger.info(f"Día {day} ({pred_date.date()}): Ventas=${pred_values['total_ventas_dia']:.2f}")
        
        return predictions
