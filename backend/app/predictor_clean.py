"""
PREDICTOR LIMPIO Y SIMPLE
Sistema de predicción por tipo de día: Fuerte, Medio Fuerte, Normal
"""

import pandas as pd
import numpy as np
import logging
import pickle
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any

from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

logger = logging.getLogger(__name__)


class PredictorClean:
    """
    Predictor simple y limpio con modelos separados por tipo de día
    """
    
    def __init__(self, models_dir: Path = Path("models")):
        self.models_dir = models_dir
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Variables a predecir
        self.variables = [
            'pizzas_vendidas',
            'baguettes_vendidas',
            'papas_gajo_vendidas',
            'total_ventas_dia'
        ]
        
        # Modelos separados por tipo de día
        self.modelos_normal = {}      # Lunes-Jueves
        self.modelos_medio_fuerte = {}  # Viernes
        self.modelos_fuerte = {}        # Sábado-Domingo
        
        self.scalers_normal = {}
        self.scalers_medio_fuerte = {}
        self.scalers_fuerte = {}
        
    def clasificar_dia(self, dia_semana: int) -> str:
        """
        Clasificar día según intensidad
        0=Lun, 1=Mar, 2=Mié, 3=Jue, 4=Vie, 5=Sáb, 6=Dom
        """
        if dia_semana in [5, 6]:  # Sábado, Domingo
            return 'fuerte'
        elif dia_semana == 4:  # Viernes
            return 'medio_fuerte'
        else:  # Lunes-Jueves
            return 'normal'
    
    def crear_features_simples(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Features simples y limpios - SOLO temporales
        """
        df = df.copy()
        df['fecha'] = pd.to_datetime(df['fecha'])
        df = df.sort_values('fecha')
        
        # Temporales básicos
        df['dia_semana'] = df['fecha'].dt.dayofweek
        df['dia_mes'] = df['fecha'].dt.day
        df['mes'] = df['fecha'].dt.month
        df['semana_anio'] = df['fecha'].dt.isocalendar().week
        
        # Patrones de restaurante
        df['es_quincena'] = ((df['dia_mes'] <= 2) | ((df['dia_mes'] >= 15) & (df['dia_mes'] <= 16))).astype(int)
        df['es_fin_mes'] = (df['dia_mes'] >= 28).astype(int)
        
        # Clasificar tipo de día
        df['tipo_dia'] = df['dia_semana'].apply(self.clasificar_dia)
        
        # Lags por variable (simple y estable)
        for var in self.variables:
            if var in df.columns:
                # Lag del mismo día de semana (hace 7 días) - MÁS CONFIABLE
                df[f'{var}_lag7'] = df[var].shift(7)
                
                # Lag de hace 14 días (para estabilidad)
                df[f'{var}_lag14'] = df[var].shift(14)
                
                # Media móvil simple (más estable que exponencial)
                df[f'{var}_ma7'] = df[var].rolling(window=7, min_periods=1).mean()
                df[f'{var}_ma14'] = df[var].rolling(window=14, min_periods=1).mean()
        
        df = df.fillna(0)
        return df
    
    def get_features_lista(self) -> List[str]:
        """Features temporales simples"""
        features = [
            'dia_mes',
            'mes',
            'semana_anio',
            'es_quincena',
            'es_fin_mes'
        ]
        return features
    
    def train_models(self, data_file: Path):
        """
        Entrenar modelos separados por tipo de día
        """
        logger.info("\n" + "="*80)
        logger.info("🚀 ENTRENAMIENTO LIMPIO - MODELOS POR TIPO DE DÍA")
        logger.info("="*80 + "\n")
        
        try:
            # Cargar y preparar datos
            df = pd.read_parquet(data_file)
            df = self.crear_features_simples(df)
        except Exception as e:
            logger.error(f"Error cargando datos: {e}")
            raise ValueError(f"No se pudieron cargar los datos: {e}")
        
        logger.info(f"📊 Datos cargados: {len(df)} días")
        logger.info(f"   Período: {df['fecha'].min().date()} a {df['fecha'].max().date()}")
        
        # Contar días por tipo
        tipos = df['tipo_dia'].value_counts()
        logger.info(f"\n📈 Distribución:")
        logger.info(f"   Normal (Lun-Jue): {tipos.get('normal', 0)} días")
        logger.info(f"   Medio Fuerte (Vie): {tipos.get('medio_fuerte', 0)} días")
        logger.info(f"   Fuerte (Sáb-Dom): {tipos.get('fuerte', 0)} días")
        
        # Features base
        features_base = self.get_features_lista()
        
        # Entrenar para cada tipo de día
        for tipo_dia in ['normal', 'medio_fuerte', 'fuerte']:
            logger.info(f"\n{'='*60}")
            logger.info(f"📚 Entrenando modelos para días: {tipo_dia.upper()}")
            logger.info(f"{'='*60}")
            
            # Filtrar datos de este tipo de día
            df_tipo = df[df['tipo_dia'] == tipo_dia].copy()
            
            if len(df_tipo) < 10:
                logger.warning(f"⚠️ Pocos datos para {tipo_dia}: {len(df_tipo)} días")
                continue
            
            # Entrenar modelo para cada variable
            for variable in self.variables:
                try:
                    logger.info(f"\n  🎯 {variable}:")
                    
                    # Features: base + lags estables de esta variable
                    features = features_base + [
                        f'{variable}_lag7',   # Mismo día semana anterior (MÁS IMPORTANTE)
                        f'{variable}_lag14',  # Hace 2 semanas (estabilidad)
                        f'{variable}_ma7',    # Promedio últimos 7 días
                        f'{variable}_ma14'    # Promedio últimos 14 días (tendencia)
                    ]
                    
                    # Verificar que las columnas existan
                    missing_cols = [f for f in features if f not in df_tipo.columns]
                    if missing_cols:
                        logger.error(f"     ❌ Columnas faltantes: {missing_cols}")
                        continue
                    
                    # Preparar datos
                    X = df_tipo[features].values
                    y = df_tipo[variable].values
                except Exception as e:
                    logger.error(f"     ❌ Error preparando datos: {e}")
                    continue
                
                try:
                    # Split
                    X_train, X_test, y_train, y_test = train_test_split(
                        X, y, test_size=0.2, shuffle=False, random_state=42
                    )
                    
                    # Scaler
                    scaler = StandardScaler()
                    X_train_scaled = scaler.fit_transform(X_train)
                    X_test_scaled = scaler.transform(X_test)
                    
                    # Modelo Ridge con alpha balanceado (estabilidad + variación)
                    modelo = Ridge(alpha=0.5, random_state=42)
                    modelo.fit(X_train_scaled, y_train)
                    
                    # Evaluar
                    y_pred = modelo.predict(X_test_scaled)
                    mae = mean_absolute_error(y_test, y_pred)
                    y_mean = y_test.mean()
                    # Evitar división por cero
                    if y_mean > 0:
                        error_pct = (mae / y_mean) * 100
                    else:
                        error_pct = 0
                    
                    logger.info(f"     MAE: {mae:.2f} ({error_pct:.1f}% error)")
                    logger.info(f"     Datos train: {len(X_train)}, test: {len(X_test)}")
                    
                    # Guardar según tipo
                    if tipo_dia == 'normal':
                        self.modelos_normal[variable] = modelo
                        self.scalers_normal[variable] = scaler
                    elif tipo_dia == 'medio_fuerte':
                        self.modelos_medio_fuerte[variable] = modelo
                        self.scalers_medio_fuerte[variable] = scaler
                    else:  # fuerte
                        self.modelos_fuerte[variable] = modelo
                        self.scalers_fuerte[variable] = scaler
                        
                except Exception as e:
                    logger.error(f"     ❌ Error entrenando modelo: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
        
        # Guardar modelos
        self.guardar_modelos()
        
        logger.info("\n" + "="*80)
        logger.info("✅ ENTRENAMIENTO COMPLETADO")
        logger.info("="*80 + "\n")
        
        # Devolver métricas básicas
        return {
            'modelos_entrenados': {
                'normal': len(self.modelos_normal),
                'medio_fuerte': len(self.modelos_medio_fuerte),
                'fuerte': len(self.modelos_fuerte)
            },
            'total_modelos': len(self.modelos_normal) + len(self.modelos_medio_fuerte) + len(self.modelos_fuerte)
        }
    
    def predict_next_days(self, data_file: Path, days: int = 7) -> List[Dict]:
        """
        Predecir próximos días usando el modelo apropiado según tipo de día
        """
        logger.info("\n" + "="*80)
        logger.info(f"🔮 PREDICIENDO PRÓXIMOS {days} DÍAS")
        logger.info("="*80 + "\n")
        
        # Cargar datos históricos
        df = pd.read_parquet(data_file)
        df = self.crear_features_simples(df)
        
        predictions = []
        last_date = df['fecha'].max()
        
        # DataFrame para ir acumulando predicciones
        df_pred = df.copy()
        
        for day in range(1, days + 1):
            pred_date = last_date + timedelta(days=day)
            dia_semana = pred_date.dayofweek
            tipo_dia = self.clasificar_dia(dia_semana)
            
            logger.info(f"📅 Día {day}: {pred_date.date()} ({pred_date.strftime('%A')}) - Tipo: {tipo_dia}")
            
            # Seleccionar modelos según tipo de día
            if tipo_dia == 'normal':
                modelos = self.modelos_normal
                scalers = self.scalers_normal
            elif tipo_dia == 'medio_fuerte':
                modelos = self.modelos_medio_fuerte
                scalers = self.scalers_medio_fuerte
            else:  # fuerte
                modelos = self.modelos_fuerte
                scalers = self.scalers_fuerte
            
            # Crear features para este día
            features_dia = {
                'dia_mes': pred_date.day,
                'mes': pred_date.month,
                'semana_anio': pred_date.isocalendar().week,
                'es_quincena': 1 if (pred_date.day <= 2 or (pred_date.day >= 15 and pred_date.day <= 16)) else 0,
                'es_fin_mes': 1 if pred_date.day >= 28 else 0
            }
            
            pred_values = {'fecha': pred_date}
            
            # Predecir cada variable
            for variable in self.variables:
                if variable not in modelos:
                    logger.warning(f"  ⚠️ No hay modelo para {variable} tipo {tipo_dia}")
                    pred_values[variable] = 0
                    continue
                
                # Agregar lags estables
                if variable in df_pred.columns:
                    features_dia[f'{variable}_lag7'] = df_pred[variable].iloc[-7] if len(df_pred) >= 7 else df_pred[variable].iloc[-1]
                    features_dia[f'{variable}_lag14'] = df_pred[variable].iloc[-14] if len(df_pred) >= 14 else df_pred[variable].iloc[-1]
                    features_dia[f'{variable}_ma7'] = df_pred[variable].tail(7).mean()
                    features_dia[f'{variable}_ma14'] = df_pred[variable].tail(14).mean() if len(df_pred) >= 14 else df_pred[variable].mean()
                else:
                    features_dia[f'{variable}_lag7'] = 0
                    features_dia[f'{variable}_lag14'] = 0
                    features_dia[f'{variable}_ma7'] = 0
                    features_dia[f'{variable}_ma14'] = 0
                
                # Preparar X
                features_orden = self.get_features_lista() + [
                    f'{variable}_lag7',
                    f'{variable}_lag14',
                    f'{variable}_ma7',
                    f'{variable}_ma14'
                ]
                X_pred = np.array([[features_dia[f] for f in features_orden]])
                
                # Predecir
                X_pred_scaled = scalers[variable].transform(X_pred)
                pred = modelos[variable].predict(X_pred_scaled)[0]
                pred = max(0, pred)  # No negativos
                
                pred_values[variable] = float(pred)
                logger.info(f"   {variable}: {pred:.1f}")
                
                # Agregar a histórico para próximas predicciones
                features_dia[variable] = pred
            
            # Validar consistencia ventas
            ventas_calculadas = (
                pred_values['pizzas_vendidas'] * 232 +
                pred_values['baguettes_vendidas'] * 98 +
                pred_values['papas_gajo_vendidas'] * 85
            )
            
            # Evitar división por cero
            if ventas_calculadas > 0:
                diferencia_pct = abs(pred_values['total_ventas_dia'] - ventas_calculadas) / ventas_calculadas
                if diferencia_pct > 0.30:
                    logger.info(f"   ⚖️ Ajustando ventas: ${pred_values['total_ventas_dia']:.2f} → ${ventas_calculadas:.2f}")
                    pred_values['total_ventas_dia'] = ventas_calculadas
            else:
                # Si ventas calculadas son 0, usar la predicción del modelo
                pass
            
            predictions.append(pred_values)
            
            # Agregar al histórico
            nueva_fila = pd.DataFrame([{
                'fecha': pred_date,
                **features_dia
            }])
            df_pred = pd.concat([df_pred, nueva_fila], ignore_index=True)
        
        return predictions
    
    def guardar_modelos(self):
        """Guardar todos los modelos"""
        # Normal
        for var in self.modelos_normal:
            with open(self.models_dir / f"normal_{var}_model.pkl", 'wb') as f:
                pickle.dump(self.modelos_normal[var], f)
            with open(self.models_dir / f"normal_{var}_scaler.pkl", 'wb') as f:
                pickle.dump(self.scalers_normal[var], f)
        
        # Medio fuerte
        for var in self.modelos_medio_fuerte:
            with open(self.models_dir / f"medio_fuerte_{var}_model.pkl", 'wb') as f:
                pickle.dump(self.modelos_medio_fuerte[var], f)
            with open(self.models_dir / f"medio_fuerte_{var}_scaler.pkl", 'wb') as f:
                pickle.dump(self.scalers_medio_fuerte[var], f)
        
        # Fuerte
        for var in self.modelos_fuerte:
            with open(self.models_dir / f"fuerte_{var}_model.pkl", 'wb') as f:
                pickle.dump(self.modelos_fuerte[var], f)
            with open(self.models_dir / f"fuerte_{var}_scaler.pkl", 'wb') as f:
                pickle.dump(self.scalers_fuerte[var], f)
        
        logger.info("💾 Modelos guardados")
    
    def cargar_modelos(self):
        """Cargar modelos guardados"""
        for tipo in ['normal', 'medio_fuerte', 'fuerte']:
            for var in self.variables:
                model_file = self.models_dir / f"{tipo}_{var}_model.pkl"
                scaler_file = self.models_dir / f"{tipo}_{var}_scaler.pkl"
                
                if model_file.exists() and scaler_file.exists():
                    with open(model_file, 'rb') as f:
                        modelo = pickle.load(f)
                    with open(scaler_file, 'rb') as f:
                        scaler = pickle.load(f)
                    
                    if tipo == 'normal':
                        self.modelos_normal[var] = modelo
                        self.scalers_normal[var] = scaler
                    elif tipo == 'medio_fuerte':
                        self.modelos_medio_fuerte[var] = modelo
                        self.scalers_medio_fuerte[var] = scaler
                    else:
                        self.modelos_fuerte[var] = modelo
                        self.scalers_fuerte[var] = scaler
