"""
Online Learning Predictor - Aprendizaje Incremental Día a Día
El modelo se entrena inicialmente con 6 meses, luego aprende día a día
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from datetime import datetime, timedelta
from sklearn.linear_model import SGDRegressor  # Permite aprendizaje incremental
from sklearn.preprocessing import StandardScaler
import pickle

logger = logging.getLogger(__name__)


class OnlinePredictor:
    """
    Predictor con aprendizaje incremental día a día
    """
    
    def __init__(self, models_dir: Path = Path("models")):
        self.models_dir = models_dir
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.target_vars = [
            'pizzas_vendidas',
            'baguettes_vendidas', 
            'papas_gajo_vendidas',
            'total_ventas_dia'
        ]
        
        # Modelos que soportan partial_fit (aprendizaje incremental)
        self.models = {}
        self.scalers = {}
        self.training_history = []  # Historial de errores
        
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Crear features temporales simples pero efectivos"""
        df = df.copy()
        df['fecha'] = pd.to_datetime(df['fecha'])
        df = df.sort_values('fecha')
        
        # ===== FEATURES TEMPORALES =====
        df['dia_semana'] = df['fecha'].dt.dayofweek
        df['dia_mes'] = df['fecha'].dt.day
        df['mes'] = df['fecha'].dt.month
        df['es_fin_semana'] = (df['dia_semana'] >= 5).astype(int)
        
        # One-hot días
        for i in range(7):
            df[f'dia_{i}'] = (df['dia_semana'] == i).astype(int)
        
        # Patrones de restaurante
        df['es_quincena'] = ((df['dia_mes'] <= 2) | ((df['dia_mes'] >= 15) & (df['dia_mes'] <= 16))).astype(int)
        df['es_fin_mes'] = (df['dia_mes'] >= 28).astype(int)
        df['es_primera_quincena'] = (df['dia_mes'] <= 15).astype(int)
        
        # ===== LAGS Y ROLLING =====
        for var in self.target_vars:
            if var in df.columns:
                # Lags
                df[f'{var}_lag1'] = df[var].shift(1)
                df[f'{var}_lag7'] = df[var].shift(7)
                
                # Rolling means
                df[f'{var}_ma3'] = df[var].rolling(window=3, min_periods=1).mean()
                df[f'{var}_ma7'] = df[var].rolling(window=7, min_periods=1).mean()
                
                # Trend
                recent_7 = df[var].rolling(window=7, min_periods=1).mean()
                recent_30 = df[var].rolling(window=30, min_periods=7).mean()
                df[f'{var}_trend'] = ((recent_7 - recent_30) / (recent_30 + 1)) * 100
        
        df = df.fillna(0)
        return df
    
    def get_feature_columns(self) -> list:
        """Features para el modelo"""
        feature_cols = [
            'dia_semana', 'dia_mes', 'mes', 'es_fin_semana',
            'dia_0', 'dia_1', 'dia_2', 'dia_3', 'dia_4', 'dia_5', 'dia_6',
            'es_quincena', 'es_fin_mes', 'es_primera_quincena'
        ]
        
        # Features de cada variable
        for var in self.target_vars:
            feature_cols.extend([
                f'{var}_lag1',
                f'{var}_lag7',
                f'{var}_ma3',
                f'{var}_ma7',
                f'{var}_trend'
            ])
        
        return feature_cols
    
    def train_initial(self, data_file: Path, initial_days: int = 180):
        """
        Entrenamiento inicial con los primeros N días (default 180 = 6 meses)
        """
        logger.info(f"\n{'='*80}")
        logger.info("🚀 ENTRENAMIENTO INICIAL - ONLINE LEARNING")
        logger.info(f"{'='*80}\n")
        
        # Cargar datos
        df = pd.read_parquet(data_file)
        df = self.create_features(df)
        
        # Tomar primeros N días para entrenamiento inicial
        df_train = df.head(initial_days).copy()
        
        logger.info(f"📊 Datos iniciales:")
        logger.info(f"  Período: {df_train['fecha'].min().date()} a {df_train['fecha'].max().date()}")
        logger.info(f"  Días: {len(df_train)}")
        
        feature_cols = self.get_feature_columns()
        
        # Entrenar modelo para cada variable
        for target in self.target_vars:
            logger.info(f"\n📈 Entrenando modelo inicial para: {target}")
            
            X = df_train[feature_cols].values
            y = df_train[target].values
            
            # Scaler
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # SGDRegressor permite aprendizaje incremental con partial_fit
            model = SGDRegressor(
                loss='squared_error',
                penalty='l2',
                alpha=0.001,  # Regularización ligera
                learning_rate='adaptive',
                eta0=0.01,  # Learning rate inicial
                max_iter=1000,
                random_state=42,
                warm_start=True  # Permite continuar entrenamiento
            )
            
            model.fit(X_scaled, y)
            
            self.models[target] = model
            self.scalers[target] = scaler
            
            # Evaluar en datos de entrenamiento
            y_pred = model.predict(X_scaled)
            mae = np.mean(np.abs(y - y_pred))
            
            logger.info(f"  ✓ MAE inicial: {mae:.2f}")
        
        # Guardar modelos iniciales
        self._save_models()
        
        logger.info(f"\n{'='*80}")
        logger.info("✅ Entrenamiento inicial completado")
        logger.info(f"{'='*80}\n")
        
        return {
            'initial_days': initial_days,
            'train_period': f"{df_train['fecha'].min().date()} a {df_train['fecha'].max().date()}"
        }
    
    def predict_and_learn(self, data_file: Path, initial_days: int = 180):
        """
        Predicción incremental día a día:
        1. Predecir día siguiente
        2. Obtener valor real
        3. Calcular error
        4. Reentrenar con nuevo dato (partial_fit)
        5. Repetir
        """
        logger.info(f"\n{'='*80}")
        logger.info("🧠 APRENDIZAJE INCREMENTAL DÍA A DÍA")
        logger.info(f"{'='*80}\n")
        
        # Cargar datos
        df = pd.read_parquet(data_file)
        df = self.create_features(df)
        
        feature_cols = self.get_feature_columns()
        
        # Historial de errores por día
        errors_by_day = []
        
        # Iterar desde día initial_days+1 hasta el final
        for day_idx in range(initial_days, len(df)):
            current_date = df.iloc[day_idx]['fecha']
            
            # Datos hasta ayer (para predecir hoy)
            df_history = df.iloc[:day_idx].copy()
            
            # Dato real de hoy (para evaluar y aprender)
            real_data = df.iloc[day_idx]
            
            logger.info(f"\n📅 Día {day_idx - initial_days + 1}/{len(df) - initial_days}: {current_date.date()}")
            
            day_errors = {'fecha': current_date}
            
            # Para cada variable
            for target in self.target_vars:
                # 1. PREDECIR usando datos hasta ayer
                X_pred = df_history[feature_cols].tail(1).values
                X_pred_scaled = self.scalers[target].transform(X_pred)
                
                pred = self.models[target].predict(X_pred_scaled)[0]
                pred = max(0, pred)  # No negativos
                
                # 2. OBTENER VALOR REAL
                real = real_data[target]
                
                # 3. CALCULAR ERROR
                error = abs(pred - real)
                error_pct = (error / (real + 1)) * 100
                
                day_errors[f'{target}_pred'] = pred
                day_errors[f'{target}_real'] = real
                day_errors[f'{target}_error'] = error
                day_errors[f'{target}_error_pct'] = error_pct
                
                logger.info(f"  {target}:")
                logger.info(f"    Predicción: {pred:.2f}")
                logger.info(f"    Real: {real:.2f}")
                logger.info(f"    Error: {error:.2f} ({error_pct:.1f}%)")
                
                # 4. REENTRENAR con nuevo dato (partial_fit)
                # Incluir el nuevo dato real en features
                df_updated = df.iloc[:day_idx+1].copy()
                X_new = df_updated[feature_cols].tail(1).values
                y_new = np.array([real])
                
                X_new_scaled = self.scalers[target].transform(X_new)
                
                # Actualizar modelo incrementalmente
                self.models[target].partial_fit(X_new_scaled, y_new)
            
            errors_by_day.append(day_errors)
            
            # Guardar modelos cada 7 días
            if (day_idx - initial_days) % 7 == 0:
                self._save_models()
        
        # Guardar modelos finales
        self._save_models()
        
        # Convertir historial a DataFrame
        errors_df = pd.DataFrame(errors_by_day)
        
        logger.info(f"\n{'='*80}")
        logger.info("📊 RESUMEN DE APRENDIZAJE")
        logger.info(f"{'='*80}\n")
        
        for target in self.target_vars:
            error_col = f'{target}_error_pct'
            if error_col in errors_df.columns:
                mean_error = errors_df[error_col].mean()
                logger.info(f"{target}:")
                logger.info(f"  Error promedio: {mean_error:.2f}%")
                logger.info(f"  Error primeros 30 días: {errors_df[error_col].head(30).mean():.2f}%")
                logger.info(f"  Error últimos 30 días: {errors_df[error_col].tail(30).mean():.2f}%\n")
        
        # Guardar historial
        errors_df.to_csv(self.models_dir / 'online_learning_history.csv', index=False)
        
        return {
            'errors_df': errors_df,
            'total_days_learned': len(df) - initial_days
        }
    
    def predict_next_days(self, data_file: Path, days: int = 7):
        """Predecir próximos N días usando modelos entrenados"""
        df = pd.read_parquet(data_file)
        df = self.create_features(df)
        
        feature_cols = self.get_feature_columns()
        predictions = []
        
        # Crear DataFrame para predicción iterativa
        df_pred = df.copy()
        last_date = df['fecha'].max()
        
        for day in range(1, days + 1):
            pred_date = last_date + timedelta(days=day)
            
            # Crear fila con features temporales
            new_row = pd.DataFrame({
                'fecha': [pred_date],
                'dia_semana': [pred_date.dayofweek],
                'dia_mes': [pred_date.day],
                'mes': [pred_date.month],
                'es_fin_semana': [1 if pred_date.dayofweek >= 5 else 0],
                'es_quincena': [1 if pred_date.day <= 2 or (pred_date.day >= 15 and pred_date.day <= 16) else 0],
                'es_fin_mes': [1 if pred_date.day >= 28 else 0],
                'es_primera_quincena': [1 if pred_date.day <= 15 else 0]
            })
            
            # One-hot días
            for i in range(7):
                new_row[f'dia_{i}'] = [1 if pred_date.dayofweek == i else 0]
            
            pred_values = {'fecha': pred_date}
            
            # Predecir cada variable
            for target in self.target_vars:
                # Calcular features basados en datos históricos
                if target in df_pred.columns:
                    new_row[f'{target}_lag1'] = [df_pred[target].iloc[-1]]
                    new_row[f'{target}_lag7'] = [df_pred[target].iloc[-7] if len(df_pred) >= 7 else df_pred[target].iloc[-1]]
                    new_row[f'{target}_ma3'] = [df_pred[target].tail(3).mean()]
                    new_row[f'{target}_ma7'] = [df_pred[target].tail(7).mean()]
                    
                    if len(df_pred) >= 30:
                        recent_7 = df_pred[target].tail(7).mean()
                        recent_30 = df_pred[target].tail(30).mean()
                        new_row[f'{target}_trend'] = [((recent_7 - recent_30) / (recent_30 + 1)) * 100]
                    else:
                        new_row[f'{target}_trend'] = [0]
                else:
                    new_row[f'{target}_lag1'] = [0]
                    new_row[f'{target}_lag7'] = [0]
                    new_row[f'{target}_ma3'] = [0]
                    new_row[f'{target}_ma7'] = [0]
                    new_row[f'{target}_trend'] = [0]
                
                new_row = new_row.fillna(0)
                
                # Predecir
                X_pred = new_row[feature_cols].values
                X_pred_scaled = self.scalers[target].transform(X_pred)
                
                pred = self.models[target].predict(X_pred_scaled)[0]
                pred = max(0, pred)
                
                pred_values[target] = float(pred)
                new_row[target] = [pred]
            
            # Agregar predicción al histórico
            df_pred = pd.concat([df_pred, new_row], ignore_index=True)
            predictions.append(pred_values)
        
        return predictions
    
    def _save_models(self):
        """Guardar modelos y scalers"""
        for target in self.target_vars:
            model_file = self.models_dir / f"{target}_online_model.pkl"
            scaler_file = self.models_dir / f"{target}_online_scaler.pkl"
            
            with open(model_file, 'wb') as f:
                pickle.dump(self.models[target], f)
            
            with open(scaler_file, 'wb') as f:
                pickle.dump(self.scalers[target], f)
    
    def load_models(self):
        """Cargar modelos guardados"""
        for target in self.target_vars:
            model_file = self.models_dir / f"{target}_online_model.pkl"
            scaler_file = self.models_dir / f"{target}_online_scaler.pkl"
            
            if model_file.exists() and scaler_file.exists():
                with open(model_file, 'rb') as f:
                    self.models[target] = pickle.load(f)
                
                with open(scaler_file, 'rb') as f:
                    self.scalers[target] = pickle.load(f)
