# 🧠 DISEÑO ML PROFESIONAL - Pizzería MAX

## 📊 Análisis del Problema

### Tipo de Problema
- **Series temporales multivariadas** con estacionalidad múltiple
- **Forecasting** a corto plazo (1-14 días)
- **Multi-target**: Predecir múltiples productos simultáneamente

### Datos Disponibles
```
Registros: ~300 días
Período: Nov 2024 - Nov 2025
Frecuencia: Diaria
Targets: 7 (ventas, pizzas, pastor, chuleta, alitas, baguettes, papas)
```

### Patrones a Capturar

| Patrón | Descripción | Técnica |
|--------|-------------|---------|
| **Estacionalidad semanal** | Viernes/Sábado > Lunes | Fourier features |
| **Estacionalidad mensual** | Quincenas (+15-40%) | Features de día del mes |
| **Tendencia** | Crecimiento/decrecimiento | Trend decomposition |
| **Eventos** | Festivos mexicanos | Regresores externos |
| **Anomalías** | Días atípicos | Isolation Forest |

---

## 🏗️ ARQUITECTURA PROPUESTA

```
┌─────────────────────────────────────────────────────────────┐
│                    PIPELINE DE ML                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   DATA      │───▶│  FEATURE    │───▶│   MODEL     │     │
│  │  INGESTION  │    │ ENGINEERING │    │  TRAINING   │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                  │                  │             │
│         ▼                  ▼                  ▼             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │  ANOMALY    │    │  FEATURE    │    │  ENSEMBLE   │     │
│  │  DETECTION  │    │   STORE     │    │   MODEL     │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│                                               │             │
│                                               ▼             │
│                          ┌─────────────────────────────┐   │
│                          │      PREDICTION ENGINE      │   │
│                          │  - Point estimates          │   │
│                          │  - Confidence intervals     │   │
│                          │  - Feature importance       │   │
│                          └─────────────────────────────┘   │
│                                               │             │
│                                               ▼             │
│                          ┌─────────────────────────────┐   │
│                          │    PREDICTION TRACKER       │   │
│                          │  - Store predictions        │   │
│                          │  - Calculate accuracy       │   │
│                          │  - Auto-retrain triggers    │   │
│                          └─────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 TÉCNICAS IMPLEMENTADAS

### 1. Feature Engineering Avanzado

```python
class AdvancedFeatureEngineer:
    """
    Genera 50+ features para cada observación
    """
    
    def generate_features(self, df):
        features = {}
        
        # === TEMPORALES BÁSICOS ===
        features['dia_semana'] = df['fecha'].dt.dayofweek          # 0-6
        features['dia_mes'] = df['fecha'].dt.day                    # 1-31
        features['mes'] = df['fecha'].dt.month                      # 1-12
        features['semana_año'] = df['fecha'].dt.isocalendar().week  # 1-53
        features['dia_año'] = df['fecha'].dt.dayofyear              # 1-365
        
        # === ONE-HOT DÍAS ===
        for i in range(7):
            features[f'dia_{i}'] = (features['dia_semana'] == i).astype(int)
        
        # === FOURIER (ESTACIONALIDAD SEMANAL) ===
        for k in range(1, 4):  # 3 armónicos
            features[f'sin_week_{k}'] = np.sin(2 * np.pi * k * features['dia_semana'] / 7)
            features[f'cos_week_{k}'] = np.cos(2 * np.pi * k * features['dia_semana'] / 7)
        
        # === FOURIER (ESTACIONALIDAD MENSUAL) ===
        for k in range(1, 3):  # 2 armónicos
            features[f'sin_month_{k}'] = np.sin(2 * np.pi * k * features['dia_mes'] / 30.5)
            features[f'cos_month_{k}'] = np.cos(2 * np.pi * k * features['dia_mes'] / 30.5)
        
        # === QUINCENAS (CRÍTICO PARA ESTE NEGOCIO) ===
        features['es_quincena'] = ((features['dia_mes'] >= 1) & (features['dia_mes'] <= 4)) | \
                                  ((features['dia_mes'] >= 15) & (features['dia_mes'] <= 18))
        features['tipo_quincena'] = 0
        features.loc[features['dia_mes'].isin([1, 15]), 'tipo_quincena'] = 4  # Pico
        features.loc[features['dia_mes'].isin([2, 16]), 'tipo_quincena'] = 3  # Alto
        features.loc[features['dia_mes'].isin([3, 17]), 'tipo_quincena'] = 2  # Medio
        features.loc[features['dia_mes'].isin([4, 18]), 'tipo_quincena'] = 1  # Bajo
        
        # === LAGS (VALORES PASADOS) ===
        for lag in [1, 7, 14, 21, 28]:  # Mismo día hace 1,2,3,4 semanas
            features[f'ventas_lag_{lag}'] = df['total_ventas_dia'].shift(lag)
            features[f'pizzas_lag_{lag}'] = df['pizzas_vendidas'].shift(lag)
        
        # === ROLLING WINDOWS (PROMEDIOS MÓVILES) ===
        for window in [7, 14, 28]:
            features[f'ventas_ma_{window}'] = df['total_ventas_dia'].rolling(window).mean()
            features[f'ventas_std_{window}'] = df['total_ventas_dia'].rolling(window).std()
            features[f'pizzas_ma_{window}'] = df['pizzas_vendidas'].rolling(window).mean()
        
        # === TENDENCIA ===
        features['dias_desde_inicio'] = (df['fecha'] - df['fecha'].min()).dt.days
        
        # === EVENTOS MEXICANOS ===
        features['es_festivo'] = self._detectar_festivos(df['fecha'])
        features['dias_para_navidad'] = self._dias_para_evento(df['fecha'], mes=12, dia=25)
        features['dias_para_año_nuevo'] = self._dias_para_evento(df['fecha'], mes=1, dia=1)
        
        return pd.DataFrame(features)
```

### 2. Modelo Ensemble (3 modelos)

```python
class EnsemblePredictor:
    """
    Combina 3 modelos para predicción robusta:
    1. LightGBM - Captura patrones no lineales
    2. Prophet - Maneja estacionalidad y eventos
    3. Ridge - Baseline lineal robusto
    """
    
    def __init__(self):
        self.models = {
            'lgbm': LGBMRegressor(
                n_estimators=500,
                learning_rate=0.05,
                max_depth=6,
                num_leaves=31,
                min_child_samples=10,
                subsample=0.8,
                colsample_bytree=0.8,
                reg_alpha=0.1,
                reg_lambda=0.1,
                random_state=42
            ),
            'prophet': Prophet(
                yearly_seasonality=False,  # No hay año completo
                weekly_seasonality=True,
                daily_seasonality=False,
                seasonality_mode='multiplicative',
                changepoint_prior_scale=0.05
            ),
            'ridge': Ridge(alpha=1.0)
        }
        
        # Pesos del ensemble (ajustados por validación)
        self.weights = {'lgbm': 0.5, 'prophet': 0.3, 'ridge': 0.2}
    
    def predict(self, X):
        predictions = {}
        for name, model in self.models.items():
            predictions[name] = model.predict(X)
        
        # Weighted average
        final = sum(
            predictions[name] * self.weights[name] 
            for name in self.models.keys()
        )
        return final
```

### 3. Quantile Regression (Intervalos de Confianza)

```python
class QuantilePredictor:
    """
    Predice percentiles para intervalos de confianza REALES
    No fake min/max basados en ±20%
    """
    
    def __init__(self):
        self.quantiles = [0.1, 0.25, 0.5, 0.75, 0.9]
        self.models = {
            q: LGBMRegressor(
                objective='quantile',
                alpha=q,
                n_estimators=300,
                learning_rate=0.05
            )
            for q in self.quantiles
        }
    
    def predict_intervals(self, X):
        results = {}
        for q, model in self.models.items():
            results[f'q{int(q*100)}'] = model.predict(X)
        
        return {
            'prediction': results['q50'],           # Mediana
            'lower_80': results['q10'],             # P10
            'upper_80': results['q90'],             # P90
            'lower_50': results['q25'],             # P25
            'upper_50': results['q75'],             # P75
        }
```

### 4. Validación Temporal (Time Series Split)

```python
class TimeSeriesValidator:
    """
    Validación correcta para series temporales
    NO usar random split (data leakage)
    """
    
    def __init__(self, n_splits=5, test_size=14):
        self.n_splits = n_splits
        self.test_size = test_size
    
    def split(self, df):
        """
        Expanding window validation:
        
        Split 1: [========TRAIN========][TEST]
        Split 2: [==========TRAIN==========][TEST]
        Split 3: [============TRAIN============][TEST]
        """
        n = len(df)
        min_train = n - (self.n_splits * self.test_size)
        
        for i in range(self.n_splits):
            train_end = min_train + (i * self.test_size)
            test_end = train_end + self.test_size
            
            train_idx = list(range(train_end))
            test_idx = list(range(train_end, min(test_end, n)))
            
            yield train_idx, test_idx
    
    def evaluate(self, model, df, target):
        metrics = []
        
        for train_idx, test_idx in self.split(df):
            X_train = df.iloc[train_idx]
            X_test = df.iloc[test_idx]
            y_train = target.iloc[train_idx]
            y_test = target.iloc[test_idx]
            
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            
            metrics.append({
                'mae': mean_absolute_error(y_test, y_pred),
                'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
                'mape': mean_absolute_percentage_error(y_test, y_pred) * 100
            })
        
        return pd.DataFrame(metrics).mean().to_dict()
```

### 5. Detección de Anomalías

```python
class AnomalyDetector:
    """
    Detecta días atípicos para:
    1. No contaminar el entrenamiento
    2. Alertar al usuario
    """
    
    def __init__(self, contamination=0.05):
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42
        )
    
    def fit_detect(self, df):
        features = df[['total_ventas_dia', 'pizzas_vendidas', 
                       'dia_semana', 'dia_mes']].values
        
        predictions = self.model.fit_predict(features)
        anomalies = df[predictions == -1]
        
        return {
            'anomaly_dates': anomalies['fecha'].tolist(),
            'anomaly_count': len(anomalies),
            'anomaly_pct': len(anomalies) / len(df) * 100
        }
```

### 6. Prediction Tracker

```python
class PredictionTracker:
    """
    Guarda predicciones y calcula precisión real
    """
    
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_table()
    
    def _init_table(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS prediction_history (
                    id INTEGER PRIMARY KEY,
                    fecha_prediccion DATE,
                    fecha_objetivo DATE,
                    variable TEXT,
                    valor_predicho REAL,
                    intervalo_lower REAL,
                    intervalo_upper REAL,
                    valor_real REAL,
                    error_absoluto REAL,
                    dentro_intervalo BOOLEAN,
                    modelo_version TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
    
    def log_prediction(self, pred):
        """Guardar predicción cuando se hace"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO prediction_history 
                (fecha_prediccion, fecha_objetivo, variable, valor_predicho,
                 intervalo_lower, intervalo_upper, modelo_version)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', pred)
    
    def update_actual(self, fecha, variable, valor_real):
        """Actualizar con valor real cuando esté disponible"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                UPDATE prediction_history 
                SET valor_real = ?,
                    error_absoluto = ABS(valor_predicho - ?),
                    dentro_intervalo = ? BETWEEN intervalo_lower AND intervalo_upper
                WHERE fecha_objetivo = ? AND variable = ? AND valor_real IS NULL
            ''', (valor_real, valor_real, valor_real, fecha, variable))
    
    def get_accuracy_metrics(self, days=30):
        """Métricas de precisión de los últimos N días"""
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(f'''
                SELECT variable,
                       AVG(error_absoluto) as mae,
                       AVG(error_absoluto / valor_real * 100) as mape,
                       SUM(dentro_intervalo) * 100.0 / COUNT(*) as coverage
                FROM prediction_history
                WHERE valor_real IS NOT NULL
                  AND fecha_objetivo >= date('now', '-{days} days')
                GROUP BY variable
            ''', conn)
            return df.to_dict('records')
```

---

## 📈 MÉTRICAS DE EVALUACIÓN

| Métrica | Descripción | Target |
|---------|-------------|--------|
| **MAPE** | Error porcentual medio | < 15% |
| **MAE** | Error absoluto medio | < $2,000 |
| **RMSE** | Raíz del error cuadrático | < $3,000 |
| **Coverage 80%** | % predicciones dentro del intervalo 80% | > 75% |
| **Coverage 50%** | % predicciones dentro del intervalo 50% | > 45% |

---

## 🗂️ ESTRUCTURA DE ARCHIVOS

```
backend/
├── app/
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── feature_engineer.py      # Feature engineering
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── lgbm_model.py        # LightGBM wrapper
│   │   │   ├── prophet_model.py     # Prophet wrapper
│   │   │   ├── ridge_model.py       # Ridge wrapper
│   │   │   └── ensemble.py          # Ensemble combiner
│   │   ├── quantile_predictor.py    # Intervalos de confianza
│   │   ├── anomaly_detector.py      # Detección de anomalías
│   │   ├── validator.py             # Time series validation
│   │   ├── tracker.py               # Prediction tracking
│   │   └── pipeline.py              # Orchestrator principal
│   ├── predictor_pro.py             # Nueva clase principal
│   └── ...
├── models/
│   ├── lgbm_ventas.pkl
│   ├── lgbm_pizzas.pkl
│   ├── prophet_ventas.json
│   ├── feature_scaler.pkl
│   └── model_metadata.json
└── ...
```

---

## 🚀 API ENDPOINTS NUEVOS

```python
# Predicciones con intervalos de confianza
GET /api/v1/predict/advanced?days=7
Response: {
    "predictions": [
        {
            "fecha": "2025-12-04",
            "ventas": {
                "prediction": 18500,
                "lower_80": 15200,
                "upper_80": 21800,
                "lower_50": 16800,
                "upper_50": 20200
            },
            "pizzas": {...},
            "confidence_score": 0.85,
            "anomaly_risk": 0.02
        }
    ],
    "model_info": {
        "version": "2.0.0",
        "last_trained": "2025-12-03",
        "mape_validation": 12.3
    }
}

# Métricas de precisión histórica
GET /api/v1/predictions/accuracy
Response: {
    "overall_mape": 11.2,
    "by_variable": {
        "ventas": {"mape": 10.5, "coverage_80": 82},
        "pizzas": {"mape": 12.1, "coverage_80": 78}
    },
    "by_day_of_week": {...},
    "trend": "improving"
}

# Feature importance
GET /api/v1/model/importance
Response: {
    "top_features": [
        {"name": "dia_semana_5", "importance": 0.23},
        {"name": "es_quincena", "importance": 0.18},
        {"name": "ventas_lag_7", "importance": 0.15}
    ]
}

# Forzar reentrenamiento
POST /api/v1/model/retrain
Response: {
    "status": "success",
    "metrics": {
        "mape_before": 14.2,
        "mape_after": 11.8,
        "improvement": "17%"
    }
}
```

---

## 📋 CHECKLIST DE IMPLEMENTACIÓN

### Fase 1: Core ML (Hoy)
- [ ] Crear estructura `backend/app/ml/`
- [ ] Implementar `feature_engineer.py`
- [ ] Implementar `lgbm_model.py`
- [ ] Implementar `validator.py`
- [ ] Implementar `pipeline.py`
- [ ] Crear `predictor_pro.py`

### Fase 2: Avanzado
- [ ] Agregar Prophet
- [ ] Implementar Ensemble
- [ ] Agregar Quantile Regression
- [ ] Implementar Anomaly Detection
- [ ] Crear Prediction Tracker

### Fase 3: API
- [ ] Endpoint `/predict/advanced`
- [ ] Endpoint `/predictions/accuracy`
- [ ] Endpoint `/model/importance`
- [ ] Actualizar frontend

---

## 🎯 RESULTADO ESPERADO

**Antes (predictor_simple.py):**
```
Técnica: Mediana histórica por día
MAPE estimado: 20-25%
Intervalos: Fake (percentiles fijos)
Tracking: Ninguno
```

**Después (predictor_pro.py):**
```
Técnica: Ensemble (LightGBM + Prophet + Ridge)
MAPE esperado: 10-15%
Intervalos: Reales (Quantile Regression)
Tracking: Completo con métricas
```

---

*Documento de diseño - ML Profesional Pizzería MAX*
*Versión 1.0 - Diciembre 2025*
