# 🍕 Pizzería MAX AI - Sistema de Predicción Inteligente

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![React](https://img.shields.io/badge/react-18.2-61dafb.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

**Sistema completo de predicción de ventas, gestión de clientes y reportes ejecutivos**

</div>

---

## 🎯 Descripción

Sistema integral para pizzerías que incluye:

- 📤 **Carga de datos** desde archivos Excel de ventas
- 🧠 **Predicciones inteligentes** con ajustes por quincena, festivos y tendencias
- 👥 **Gestión de clientes** con historial y métricas de fidelización
- 📊 **Reportes ejecutivos** con insights y recomendaciones
- 📈 **Dashboard interactivo** con KPIs en tiempo real
- 🎨 **Interfaz moderna** con diseño responsive

---

## ✨ Características

### 📊 Dashboard
- KPIs animados (ventas, pizzas, baguettes, papas)
- Predicciones para los próximos 7 días
- Rangos pesimista/optimista
- Detección de eventos especiales (quincenas, festivos)

### 👥 Gestión de Clientes
- Base de datos de clientes extraída automáticamente
- Métricas: total gastado, ticket promedio, frecuencia
- Búsqueda por nombre o teléfono
- Historial de pedidos por cliente

### 📈 Reportes Ejecutivos
- Top 10 clientes por dinero gastado
- Top 10 clientes por cantidad de pedidos
- Análisis de rendimiento por día de semana
- Insights y recomendaciones automáticas
- Resumen ejecutivo con conclusiones

### 🔧 Backend (FastAPI + Python)
- Procesamiento ETL de archivos Excel
- Modelo de predicción con medianas históricas
- Ajustes por quincena (+15-20%) y festivos
- Factor de tendencia reciente
- API RESTful documentada

### 🎨 Frontend (React + TailwindCSS)
- Diseño moderno y profesional
- Animaciones fluidas (Framer Motion)
- Gráficos interactivos (Recharts)
- Responsive (mobile, tablet, desktop)

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
│   │   ├── main.py              # FastAPI app principal
│   │   ├── etl_processor.py     # Procesamiento Excel
│   │   ├── predictor_simple.py  # Predictor con medianas
│   │   ├── database.py          # Gestión SQLite (clientes)
│   │   ├── calendario_comercial.py  # Quincenas y festivos
│   │   └── gpt_insights.py      # Insights con GPT (opcional)
│   ├── data/
│   │   ├── ventas_diarias.parquet
│   │   └── pizzeria_max.db      # Base de datos clientes
│   ├── models/
│   │   └── promedios_simple.pkl # Modelo de predicción
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx    # Panel principal
│   │   │   ├── Analytics.jsx    # Análisis histórico
│   │   │   ├── Clientes.jsx     # Gestión de clientes
│   │   │   ├── Reportes.jsx     # Reportes ejecutivos
│   │   │   └── KPICard.jsx      # Tarjetas de métricas
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── scripts/
│   ├── install.bat              # Instalación automática
│   └── start-all.bat            # Iniciar todo
│
└── README.md
```

---

## 🧠 Sistema de Predicción

### Variables Predichas
- **Total ventas diarias** ($)
- **Pizzas vendidas** (totales, pastor, chuleta)
- **Baguettes vendidos**
- **Papas gajo vendidas**
- **Alitas vendidas**

### Metodología
El sistema usa **medianas históricas por día de semana** ajustadas por:

1. **Quincenas** (+15-20% en días de pago: 1, 15, 30 del mes)
2. **Festivos mexicanos** (Día de las Madres, Navidad, etc.)
3. **Tendencia reciente** (compara últimas 4 semanas vs anteriores)
4. **Variabilidad natural** (±5% por posición en el mes)

### Rangos de Predicción
Cada predicción incluye:
- **Valor base**: Mediana histórica ajustada
- **Rango pesimista**: Percentil 25
- **Rango optimista**: Percentil 75

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

## 🛠️ Tecnologías

### Backend
- **FastAPI** - Framework web moderno
- **Pandas** - Procesamiento de datos
- **SQLite** - Base de datos de clientes
- **Uvicorn** - Servidor ASGI

### Frontend
- **React 18** - Interfaz de usuario
- **Vite** - Build tool
- **TailwindCSS** - Estilos
- **Framer Motion** - Animaciones
- **Recharts** - Gráficos
- **Lucide React** - Iconos
- **Axios** - HTTP client

---

## 📝 API Endpoints

### Datos y Predicciones
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/upload_excel` | Sube y procesa archivo Excel |
| POST | `/train_model` | Entrena modelo de predicción |
| GET | `/predict?days=7` | Obtiene predicciones |
| GET | `/stats` | Estadísticas generales |
| POST | `/reset` | Reinicia base de datos |

### Clientes
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/clientes` | Lista de clientes |
| GET | `/clientes/stats` | Estadísticas de clientes |
| GET | `/clientes/{telefono}` | Detalle de cliente |
| GET | `/clientes/buscar/{query}` | Buscar cliente |

### Reportes
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/reportes/resumen` | Reporte ejecutivo completo |

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

## 📄 Licencia

MIT License - Libre para uso personal y comercial.

---

## 👨‍💻 Autor

Desarrollado con ❤️ para Pizzería MAX

---

<div align="center">

**Pizzería MAX AI v2.0** - Sistema de Predicción Inteligente

</div>
