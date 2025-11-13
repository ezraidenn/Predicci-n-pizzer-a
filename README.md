# 🍕 Pizzería MAX - Sistema de Predicción de Ventas con IA

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![React](https://img.shields.io/badge/react-18.2-61dafb.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

**Plataforma inteligente de predicción de ventas con Machine Learning y análisis GPT**

[Características](#-características) • [Instalación](#-instalación-rápida) • [Uso](#-uso) • [Arquitectura](#-arquitectura) • [Screenshots](#-screenshots)

</div>

---

## 🎯 Descripción

Sistema completo de predicción de ventas que permite:

- 📤 **Subir archivos Excel** de ventas diarias
- 🧠 **Entrenar modelos ML** automáticamente (XGBoost/GradientBoosting)
- 📊 **Visualizar datos** con gráficos interactivos y animados
- 🤖 **Predicciones precisas** para los próximos 7 días
- 💡 **Insights con GPT-4** en lenguaje natural
- 🎨 **Interfaz Tesla-style** moderna y elegante

---

## ✨ Características

### Backend (FastAPI + Python)
- ✅ Procesamiento ETL de archivos Excel
- ✅ Modelos de Machine Learning (XGBoost, Scikit-learn)
- ✅ Predicción de ventas, pizzas, baguettes y papas gajo
- ✅ Features: medias móviles, lags, one-hot encoding
- ✅ Validación cruzada y métricas de rendimiento
- ✅ Integración con OpenAI GPT-4 para insights
- ✅ API RESTful documentada (Swagger/ReDoc)

### Frontend (React + TailwindCSS)
- ✅ Diseño futurista tipo Tesla
- ✅ Drag & Drop para subir archivos
- ✅ KPI cards animados con CountUp
- ✅ Gráficos interactivos (Recharts)
- ✅ Efectos glass morphism y glow
- ✅ Animaciones fluidas (Framer Motion)
- ✅ Responsive design (mobile, tablet, desktop)

---

## 🚀 Instalación Rápida

### Prerrequisitos
- Python 3.9+
- Node.js 18+
- npm o yarn

### 1️⃣ Clonar/Descargar proyecto

```bash
cd "Proyecto prediccion MAX"
```

### 2️⃣ Configurar Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno (opcional)
copy .env.example .env
# Editar .env y añadir OPENAI_API_KEY si deseas insights GPT
```

### 3️⃣ Configurar Frontend

```bash
cd ../frontend

# Instalar dependencias
npm install
```

---

## 🎮 Uso

### Iniciar Backend

```bash
cd backend
venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend disponible en:** `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Iniciar Frontend

```bash
cd frontend
npm run dev
```

**Frontend disponible en:** `http://localhost:3000`

---

## 📖 Flujo de Trabajo

1. **Abrir aplicación** en `http://localhost:3000`
2. **Hacer clic en "Subir Excel"** en la barra superior
3. **Arrastrar archivo Excel** con hojas: `Pedidos`, `Detalles`, `Visitas`
4. **Esperar procesamiento** (automático):
   - ✅ Carga y validación de datos
   - ✅ Procesamiento ETL
   - ✅ Entrenamiento de modelos ML
   - ✅ Generación de predicciones
   - ✅ Análisis con GPT (si está configurado)
5. **Visualizar resultados**:
   - KPIs animados
   - Gráficos de tendencias
   - Tabla de predicciones
   - Insights inteligentes

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                            │
│  React + TailwindCSS + Framer Motion + Recharts            │
│                    (Port 3000)                              │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP REST API
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                         BACKEND                             │
│              FastAPI + Python (Port 8000)                   │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ ETL Processor│  │  ML Predictor│  │ GPT Insights │     │
│  │   (Pandas)   │  │  (XGBoost)   │  │  (OpenAI)    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATA STORAGE                             │
│  ┌──────────────────┐  ┌──────────────────────────────┐    │
│  │ ventas_diarias   │  │ Modelos ML (.pkl)            │    │
│  │   (.parquet)     │  │ - model_total_ventas_dia.pkl │    │
│  └──────────────────┘  │ - model_pizzas_vendidas.pkl  │    │
│                        │ - model_baguettes_vendidas...│    │
│                        └──────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Estructura del Proyecto

```
Proyecto prediccion MAX/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app
│   │   ├── etl_processor.py     # Procesamiento Excel
│   │   ├── predictor.py         # Modelos ML
│   │   └── gpt_insights.py      # Generador insights
│   ├── data/                    # Datos procesados (auto-generado)
│   ├── models/                  # Modelos entrenados (auto-generado)
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── Hero.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── KPICard.jsx
│   │   │   ├── SalesChart.jsx
│   │   │   ├── ProductsChart.jsx
│   │   │   └── InsightBox.jsx
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── README.md
│
└── README.md                    # Este archivo
```

---

## 🧠 Modelos de Machine Learning

### Variables Predichas
- **Total ventas diarias** ($)
- **Pizzas vendidas** (unidades)
- **Baguettes vendidos** (unidades)
- **Papas gajo vendidas** (unidades)

### Features Utilizadas
- Día de la semana (one-hot encoded)
- Día del mes, mes
- Es fin de semana (binario)
- Total visitas, pedidos iniciados, pedidos creados
- Tipo de servicio (% domicilio, % llevar)
- Medias móviles de 3 y 7 días
- Desviación estándar de 7 días
- Lags de 1 y 7 días
- Tasa de conversión

### Algoritmo
- **XGBoost** (si está instalado)
- **GradientBoosting** (fallback)

### Métricas
- MAE (Mean Absolute Error)
- RMSE (Root Mean Squared Error)
- R² Score
- Cross-validation MAE

---

## 🔑 Variables de Entorno

Crear archivo `.env` en `/backend`:

```env
# OpenAI API Key (opcional - para insights GPT)
OPENAI_API_KEY=sk-your-api-key-here

# Configuración del servidor
HOST=0.0.0.0
PORT=8000
```

**Nota:** Sin `OPENAI_API_KEY`, el sistema generará insights predeterminados (sin GPT).

---

## 📊 Formato del Excel

El archivo Excel debe contener 3 hojas:

### Hoja "Pedidos"
| Fecha de creación | Total | Estado | Tipo de servicio |
|-------------------|-------|--------|------------------|
| 2024-01-01        | 450.5 | Finalizado | A domicilio |

### Hoja "Detalles"
| Fecha de creación | Nombre | Cantidad | Categoría |
|-------------------|--------|----------|-----------|
| 2024-01-01        | Pizza Margarita | 2 | Pizzas |

### Hoja "Visitas"
| Fecha | Total de visitas | Pedidos iniciados | Pedidos creados |
|-------|------------------|-------------------|-----------------|
| 2024-01-01 | 150 | 45 | 30 |

---

## 🎨 Paleta de Colores

- **Primary (Cian):** `#00ffc3`
- **Dark Background:** `#0f0f10`
- **Dark Card:** `#18181b`
- **Text Primary:** `#ffffff`
- **Text Secondary:** `#9ca3af`

---

## 🛠️ Tecnologías

### Backend
- FastAPI 0.109.0
- Pandas 2.1.4
- Scikit-learn 1.4.0
- XGBoost 2.0.3
- OpenAI 1.10.0
- Uvicorn 0.27.0

### Frontend
- React 18.2
- Vite 5.0
- TailwindCSS 3.4
- Framer Motion 10.18
- Recharts 2.10
- Lucide React 0.303
- React Dropzone 14.2
- React CountUp 6.5

---

## 📝 API Endpoints

### `POST /upload_excel`
Sube y procesa archivo Excel.

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_dias": 365,
    "ventas_totales": 150000.50,
    "promedio_ventas_dia": 410.96
  },
  "recent_data": [...]
}
```

### `POST /train_model`
Entrena modelos ML.

### `GET /predict?days=7`
Obtiene predicciones.

### `POST /insight`
Genera análisis GPT.

---

## 🐛 Troubleshooting

### Backend no inicia
```bash
# Verificar que el puerto 8000 esté libre
netstat -ano | findstr :8000

# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

### Frontend no compila
```bash
# Limpiar cache y reinstalar
rm -rf node_modules package-lock.json
npm install
```

### Error al subir Excel
- Verificar que el archivo tenga las 3 hojas: Pedidos, Detalles, Visitas
- Revisar que las columnas coincidan con el formato esperado
- Comprobar logs del backend en consola

---

## 🚀 Despliegue en Producción

### Backend (Railway, Render, Heroku)
```bash
# Añadir Procfile
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Frontend (Vercel, Netlify)
```bash
npm run build
# Subir carpeta dist/
```

---

## 📄 Licencia

MIT License - Libre para uso personal y comercial.

---

## 👨‍💻 Autor

Desarrollado con ❤️ para Pizzería MAX

---

## 🙏 Agradecimientos

- OpenAI por GPT-4
- Comunidad de React y FastAPI
- Tailwind Labs por TailwindCSS
- Recharts por gráficos hermosos

---

<div align="center">

**¿Preguntas o sugerencias?**

[Reportar Bug](https://github.com/tu-repo/issues) • [Solicitar Feature](https://github.com/tu-repo/issues)

⭐ **Si te gusta este proyecto, dale una estrella!** ⭐

</div>
