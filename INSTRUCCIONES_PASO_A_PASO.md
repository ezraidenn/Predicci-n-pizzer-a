# 📖 Instrucciones Paso a Paso - Pizzería MAX

## 🎯 Objetivo
Configurar y ejecutar el sistema de predicción de ventas en tu computadora.

---

## ⚙️ PASO 1: Verificar Requisitos

### ✅ Checklist de Software Necesario

**Python 3.9 o superior:**
```bash
python --version
# Debe mostrar: Python 3.9.x o superior
```

**Node.js 18 o superior:**
```bash
node --version
# Debe mostrar: v18.x.x o superior

npm --version
# Debe mostrar: 9.x.x o superior
```

### 📥 Si no los tienes instalados:
- **Python:** https://www.python.org/downloads/
- **Node.js:** https://nodejs.org/

---

## 🔧 PASO 2: Instalación del Proyecto

### Opción A: Instalación Automática (MÁS FÁCIL) ⭐

1. **Abrir terminal en la carpeta del proyecto:**
   - Navegar a: `C:\Users\raulc\Downloads\Proyecto prediccion MAX`
   - Shift + Click derecho → "Abrir PowerShell aquí"

2. **Ejecutar script de instalación:**
   ```bash
   .\scripts\install.bat
   ```

3. **Esperar a que termine** (puede tomar 3-5 minutos)

4. **¡Listo!** Pasar al PASO 3.

---

### Opción B: Instalación Manual

#### 2.1 Configurar Backend

```bash
# 1. Ir a carpeta backend
cd backend

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno virtual
venv\Scripts\activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Volver a carpeta raíz
cd ..
```

#### 2.2 Configurar Frontend

```bash
# 1. Ir a carpeta frontend
cd frontend

# 2. Instalar dependencias
npm install

# 3. Volver a carpeta raíz
cd ..
```

---

## 🚀 PASO 3: Iniciar el Sistema

### Opción A: Inicio Automático (MÁS FÁCIL) ⭐

1. **Ejecutar script de inicio:**
   ```bash
   .\scripts\start-all.bat
   ```

2. **Se abrirán 2 ventanas:**
   - Ventana 1: Backend (puerto 8000)
   - Ventana 2: Frontend (puerto 3000)

3. **Esperar mensajes de confirmación:**
   - Backend: "Application startup complete"
   - Frontend: "Local: http://localhost:3000"

4. **¡Listo!** Pasar al PASO 4.

---

### Opción B: Inicio Manual

#### 3.1 Iniciar Backend

**Terminal 1:**
```bash
cd backend
venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Esperar mensaje:**
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### 3.2 Iniciar Frontend

**Terminal 2 (nueva terminal):**
```bash
cd frontend
npm run dev
```

**Esperar mensaje:**
```
  VITE v5.0.11  ready in XXX ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

---

## 🌐 PASO 4: Abrir la Aplicación

1. **Abrir navegador** (Chrome, Edge, Firefox)

2. **Ir a:** http://localhost:3000

3. **Deberías ver:**
   - Pantalla de bienvenida con fondo oscuro
   - Logo "Pizzería MAX AI"
   - Botón "Subir Excel" en la esquina superior derecha
   - 4 tarjetas con características del sistema

---

## 📤 PASO 5: Subir Archivo Excel

### 5.1 Preparar tu Excel

Tu archivo Excel **DEBE** tener 3 hojas con estos nombres exactos:

1. **Pedidos**
   - Columnas: `Fecha de creación`, `Total`, `Estado`, `Tipo de servicio`

2. **Detalles**
   - Columnas: `Fecha de creación`, `Nombre`, `Cantidad`, `Categoría`

3. **Visitas**
   - Columnas: `Fecha`, `Total de visitas`, `Pedidos iniciados`, `Pedidos creados`

### 5.2 Subir el Archivo

1. **Hacer clic en "Subir Excel"** (botón verde superior derecho)

2. **Arrastrar tu archivo** a la zona de drop o hacer clic para seleccionar

3. **Esperar procesamiento** (30-60 segundos):
   - ✅ Subiendo archivo...
   - ✅ Procesando datos...
   - ✅ Entrenando modelos...
   - ✅ Generando predicciones...

4. **Ver barra de progreso** en la parte superior

---

## 📊 PASO 6: Visualizar Resultados

Una vez procesado, verás:

### 6.1 KPI Cards (4 tarjetas superiores)
- 💰 **Ventas Totales** - Total en dinero
- 🍕 **Pizzas Vendidas** - Cantidad de pizzas
- 🥖 **Baguettes** - Cantidad de baguettes
- 🍟 **Papas Gajo** - Cantidad de papas

Cada tarjeta muestra:
- Valor total histórico
- Promedio diario
- Predicción para mañana
- Cambio porcentual

### 6.2 Insight Box (Análisis GPT)
- Caja con icono de estrella
- Análisis en lenguaje natural
- Tendencias y recomendaciones

### 6.3 Gráficos
- **Izquierda:** Ventas Real vs Predicción (líneas)
- **Derecha:** Distribución de Productos (dona)

### 6.4 Tabla de Predicciones
- 7 filas (próximos 7 días)
- Columnas: Fecha, Ventas, Pizzas, Baguettes, Papas

---

## 🎨 PASO 7: Explorar Funcionalidades

### Interactividad
- **Hover sobre gráficos** → Ver valores exactos
- **Hover sobre KPI cards** → Efecto de elevación
- **Scroll** → Animaciones suaves

### Subir Nuevo Archivo
- Hacer clic en "Subir Excel" nuevamente
- El sistema reemplazará los datos anteriores

---

## 🔧 PASO 8: Configuración Opcional - GPT Insights

### Sin GPT (Predeterminado)
- El sistema genera insights básicos automáticamente
- **No requiere configuración**

### Con GPT-4 (Avanzado)
Si quieres análisis más detallados con IA:

1. **Obtener API Key de OpenAI:**
   - Ir a: https://platform.openai.com/api-keys
   - Crear cuenta (si no tienes)
   - Generar nueva API key
   - Copiar la clave (empieza con `sk-...`)

2. **Configurar en el proyecto:**
   ```bash
   # Ir a carpeta backend
   cd backend
   
   # Copiar archivo de ejemplo
   copy .env.example .env
   
   # Editar .env con Notepad
   notepad .env
   ```

3. **Pegar tu API key:**
   ```env
   OPENAI_API_KEY=sk-tu-clave-aqui
   ```

4. **Guardar y cerrar**

5. **Reiniciar backend:**
   - Cerrar ventana del backend (Ctrl+C)
   - Ejecutar nuevamente: `.\scripts\start-backend.bat`

---

## ❌ PASO 9: Detener el Sistema

### Opción A: Cerrar Ventanas
- Simplemente cerrar las 2 ventanas de terminal

### Opción B: Detener con Ctrl+C
- En cada ventana de terminal, presionar `Ctrl+C`
- Confirmar con `Y` si pregunta

---

## 🐛 SOLUCIÓN DE PROBLEMAS COMUNES

### ❌ Error: "Puerto 8000 ya en uso"

**Solución:**
```bash
# Encontrar proceso
netstat -ano | findstr :8000

# Matar proceso (reemplazar XXXX con el PID)
taskkill /PID XXXX /F

# O usar otro puerto
python -m uvicorn app.main:app --reload --port 8001
```

---

### ❌ Error: "ModuleNotFoundError"

**Solución:**
```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt --force-reinstall
```

---

### ❌ Error: "npm ERR!"

**Solución:**
```bash
cd frontend
npm cache clean --force
rmdir /s /q node_modules
del package-lock.json
npm install
```

---

### ❌ Error al subir Excel: "Faltan hojas requeridas"

**Solución:**
- Verificar que el Excel tenga exactamente 3 hojas
- Nombres exactos: `Pedidos`, `Detalles`, `Visitas`
- Revisar que las columnas coincidan con el formato

---

### ❌ Página en blanco en http://localhost:3000

**Solución:**
1. Verificar que el frontend esté corriendo (ver terminal)
2. Refrescar página (F5)
3. Limpiar cache del navegador (Ctrl+Shift+Del)
4. Probar en modo incógnito

---

### ❌ "Cannot connect to backend"

**Solución:**
1. Verificar que backend esté corriendo en puerto 8000
2. Ir a http://localhost:8000 (debe mostrar JSON)
3. Revisar firewall/antivirus
4. Reiniciar ambos servicios

---

## 📞 AYUDA ADICIONAL

### Documentación
- **README principal:** `README.md`
- **Guía rápida:** `QUICKSTART.md`
- **Resumen proyecto:** `PROYECTO_RESUMEN.md`

### Verificar Estado del Sistema

**Backend:**
```bash
# Abrir en navegador
http://localhost:8000
# Debe mostrar: {"status":"online","service":"Pizzería MAX..."}

# Documentación API
http://localhost:8000/docs
```

**Frontend:**
```bash
# Abrir en navegador
http://localhost:3000
# Debe mostrar la interfaz
```

---

## ✅ CHECKLIST FINAL

Antes de usar el sistema, verifica:

- [ ] Python 3.9+ instalado
- [ ] Node.js 18+ instalado
- [ ] Dependencias backend instaladas
- [ ] Dependencias frontend instaladas
- [ ] Backend corriendo en puerto 8000
- [ ] Frontend corriendo en puerto 3000
- [ ] Navegador abierto en http://localhost:3000
- [ ] Archivo Excel preparado con 3 hojas
- [ ] (Opcional) API Key de OpenAI configurada

---

## 🎉 ¡LISTO PARA USAR!

Si completaste todos los pasos, tu sistema está funcionando correctamente.

**Próximo paso:** Subir tu archivo Excel y ver las predicciones.

---

<div align="center">

**¿Necesitas ayuda?**

Revisa la sección de **Solución de Problemas** arriba

o consulta la documentación completa en `README.md`

---

**¡Disfruta prediciendo tus ventas! 🍕📊🚀**

</div>
