# 🍕 Pizzería MAX - Backend API

Backend FastAPI para el sistema de predicción de ventas inteligente.

## 🚀 Instalación

1. **Crear entorno virtual:**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

2. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno:**
```bash
copy .env.example .env
# Editar .env y añadir tu OPENAI_API_KEY (opcional)
```

## 🎯 Ejecutar servidor

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

El servidor estará disponible en: `http://localhost:8000`

## 📚 Documentación API

Una vez ejecutado el servidor, accede a:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 Endpoints principales

### `POST /upload_excel`
Sube archivo Excel y procesa datos de ventas.

**Body:** `multipart/form-data` con archivo Excel

**Response:**
```json
{
  "success": true,
  "message": "Archivo procesado exitosamente",
  "stats": {
    "total_dias": 365,
    "ventas_totales": 150000.50,
    "promedio_ventas_dia": 410.96,
    ...
  },
  "recent_data": [...]
}
```

### `POST /train_model`
Entrena modelos de predicción con los datos procesados.

**Response:**
```json
{
  "success": true,
  "message": "Modelos entrenados exitosamente",
  "metrics": {
    "total_ventas_dia": {
      "mae": 45.23,
      "rmse": 67.89,
      "r2": 0.85
    },
    ...
  }
}
```

### `GET /predict?days=7`
Obtiene predicciones para los próximos días.

**Query params:**
- `days`: Número de días a predecir (default: 7)

**Response:**
```json
{
  "success": true,
  "predictions": [
    {
      "fecha": "2024-01-15",
      "total_ventas_dia": 450.30,
      "pizzas_vendidas": 25,
      "baguettes_vendidas": 18,
      "papas_gajo_vendidas": 12
    },
    ...
  ]
}
```

### `POST /insight`
Genera análisis en lenguaje natural usando GPT.

**Response:**
```json
{
  "success": true,
  "insight": "Las proyecciones indican un crecimiento del 12% en ventas..."
}
```

## 📁 Estructura del proyecto

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app principal
│   ├── etl_processor.py     # Procesamiento de Excel
│   ├── predictor.py         # Modelos ML
│   └── gpt_insights.py      # Generador de insights
├── data/                    # Datos procesados (generado)
├── models/                  # Modelos entrenados (generado)
├── requirements.txt
├── .env.example
└── README.md
```

## 🧠 Modelos de Machine Learning

El sistema entrena modelos para predecir:
- ✅ Ventas totales diarias
- ✅ Pizzas vendidas
- ✅ Baguettes vendidos
- ✅ Papas gajo vendidas

**Algoritmo:** XGBoost (o GradientBoosting como fallback)

**Features utilizadas:**
- Día de la semana (one-hot encoded)
- Visitas, pedidos iniciados, pedidos creados
- Medias móviles de 3 y 7 días
- Tipo de servicio (domicilio/llevar)
- Lags de 1 y 7 días

## 🔐 Seguridad

- CORS configurado (ajustar en producción)
- Validación de archivos Excel
- Manejo de errores robusto
- Logging detallado

## 📝 Notas

- Los modelos se guardan en `/models` como archivos `.pkl`
- Los datos procesados se guardan en `/data` como `.parquet`
- GPT insights requiere `OPENAI_API_KEY` configurada
- Sin API key, se generan insights predeterminados
