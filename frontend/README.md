# 🎨 Pizzería MAX - Frontend

Frontend React con diseño Tesla-style para el sistema de predicción de ventas.

## 🚀 Instalación

1. **Instalar dependencias:**
```bash
cd frontend
npm install
```

2. **Configurar backend:**
Asegúrate de que el backend esté corriendo en `http://localhost:8000`

## 🎯 Ejecutar en desarrollo

```bash
npm run dev
```

La aplicación estará disponible en: `http://localhost:3000`

## 🏗️ Build para producción

```bash
npm run build
npm run preview
```

## 🎨 Stack Tecnológico

- **React 18** - Framework UI
- **Vite** - Build tool ultra-rápido
- **TailwindCSS** - Styling utility-first
- **Framer Motion** - Animaciones fluidas
- **Recharts** - Gráficos interactivos
- **Lucide React** - Iconos minimalistas
- **React Dropzone** - Upload de archivos
- **React CountUp** - Animación de números
- **Axios** - Cliente HTTP

## 📁 Estructura

```
frontend/
├── src/
│   ├── components/
│   │   ├── Navbar.jsx          # Barra superior + upload
│   │   ├── Hero.jsx            # Pantalla inicial
│   │   ├── Dashboard.jsx       # Dashboard principal
│   │   ├── KPICard.jsx         # Tarjetas de métricas
│   │   ├── SalesChart.jsx      # Gráfico de ventas
│   │   ├── ProductsChart.jsx   # Gráfico de productos
│   │   └── InsightBox.jsx      # Caja de insights GPT
│   ├── App.jsx                 # Componente raíz
│   ├── main.jsx               # Entry point
│   └── index.css              # Estilos globales
├── index.html
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## 🎨 Diseño

### Paleta de Colores
- **Primary**: `#00ffc3` (Cian brillante)
- **Dark**: `#0f0f10` (Negro profundo)
- **Dark Card**: `#18181b` (Gris oscuro)

### Tipografía
- **Font**: Inter (Google Fonts)
- **Weights**: 300, 400, 500, 600, 700, 800

### Efectos
- **Glass effect**: Fondo translúcido con blur
- **Glow effect**: Sombras luminosas en elementos destacados
- **Animaciones**: Transiciones suaves con Framer Motion

## 🔌 Integración con Backend

El frontend se comunica con el backend a través de:

```javascript
// Proxy configurado en vite.config.js
'/api' -> 'http://localhost:8000'
```

### Endpoints utilizados:
- `POST /api/upload_excel` - Subir archivo
- `POST /api/train_model` - Entrenar modelos
- `GET /api/predict?days=7` - Obtener predicciones
- `POST /api/insight` - Generar insights GPT

## 📊 Componentes Principales

### Dashboard
Muestra:
- 4 KPI cards animados (Ventas, Pizzas, Baguettes, Papas)
- Gráfico de líneas (Real vs Predicción)
- Gráfico de dona (Distribución de productos)
- Tabla de predicciones
- Insight box con análisis GPT

### Navbar
- Logo animado
- Botón de upload con drag & drop
- Barra de progreso durante procesamiento

### Hero
- Pantalla de bienvenida
- 4 features destacadas
- Efectos de fondo animados

## 🎭 Animaciones

Todas las animaciones usan Framer Motion:
- **Fade in**: Aparición suave
- **Slide up**: Deslizamiento desde abajo
- **Stagger children**: Animación secuencial de elementos
- **Hover effects**: Escalado y elevación
- **CountUp**: Números animados en KPIs

## 🌐 Responsive Design

- **Mobile**: 1 columna
- **Tablet**: 2 columnas
- **Desktop**: 4 columnas (KPIs), 2 columnas (gráficos)

## 🔐 Notas de Seguridad

- CORS configurado en backend
- Validación de archivos Excel
- Manejo de errores con mensajes claros
- Loading states durante operaciones async

## 🎯 Próximas Mejoras

- [ ] Autenticación de usuarios
- [ ] Guardar configuraciones
- [ ] Exportar reportes PDF
- [ ] Comparación de períodos
- [ ] Alertas personalizadas
- [ ] Modo oscuro/claro toggle
