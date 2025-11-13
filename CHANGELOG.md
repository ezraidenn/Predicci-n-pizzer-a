# Changelog

Todos los cambios notables en este proyecto serán documentados aquí.

## [1.0.0] - 2024-01-12

### ✨ Añadido
- Sistema completo de predicción de ventas con IA
- Backend FastAPI con procesamiento ETL de Excel
- Modelos de Machine Learning (XGBoost/GradientBoosting)
- Frontend React con diseño Tesla-style
- Integración con OpenAI GPT-4 para insights
- Dashboard interactivo con KPIs animados
- Gráficos de ventas y productos (Recharts)
- Drag & Drop para subir archivos Excel
- Predicciones para 7 días
- Validación cruzada de modelos
- Documentación completa (README, QUICKSTART)
- Scripts de instalación y ejecución automática

### 🎨 Diseño
- Paleta de colores cian (#00ffc3) y negro (#0f0f10)
- Efectos glass morphism y glow
- Animaciones con Framer Motion
- Responsive design (mobile, tablet, desktop)
- Tipografía Inter de Google Fonts

### 🧠 Machine Learning
- Features: medias móviles, lags, one-hot encoding
- Predicción de 4 variables: ventas, pizzas, baguettes, papas
- Métricas: MAE, RMSE, R², CV MAE
- Guardado automático de modelos (.pkl)

### 📊 Visualización
- KPI Cards con CountUp animado
- Gráfico de líneas (Real vs Predicción)
- Gráfico de dona (Distribución de productos)
- Tabla de predicciones
- Insight box con análisis GPT

### 🔧 Configuración
- Variables de entorno (.env)
- CORS configurado
- Proxy Vite para desarrollo
- Logging estructurado

---

## Próximas Versiones

### [1.1.0] - Planificado
- [ ] Autenticación de usuarios
- [ ] Base de datos PostgreSQL
- [ ] Exportar reportes PDF
- [ ] Comparación de períodos
- [ ] Alertas personalizadas
- [ ] Modo oscuro/claro toggle
- [ ] Soporte multi-idioma
- [ ] Tests unitarios y e2e

### [1.2.0] - Planificado
- [ ] Dashboard de administración
- [ ] Gestión de múltiples locales
- [ ] Predicción de inventario
- [ ] Análisis de rentabilidad
- [ ] Integración con POS
- [ ] App móvil (React Native)

---

**Formato basado en [Keep a Changelog](https://keepachangelog.com/)**
