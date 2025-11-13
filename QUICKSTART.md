# 🚀 Guía de Inicio Rápido - Pizzería MAX

## ⚡ Instalación en 5 Minutos

### Paso 1: Backend

```bash
# Navegar a backend
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno (Windows)
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 2: Frontend

```bash
# Abrir nueva terminal
cd frontend

# Instalar dependencias
npm install
```

### Paso 3: Ejecutar

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Paso 4: Usar

1. Abrir navegador: `http://localhost:3000`
2. Clic en **"Subir Excel"**
3. Arrastrar tu archivo Excel
4. ¡Listo! Ver predicciones y análisis

---

## 📋 Checklist de Instalación

- [ ] Python 3.9+ instalado
- [ ] Node.js 18+ instalado
- [ ] Backend corriendo en puerto 8000
- [ ] Frontend corriendo en puerto 3000
- [ ] Archivo Excel con hojas: Pedidos, Detalles, Visitas

---

## 🔧 Configuración Opcional

### Habilitar Insights GPT

1. Obtener API Key de OpenAI: https://platform.openai.com/api-keys
2. Crear archivo `backend/.env`:
```env
OPENAI_API_KEY=sk-tu-clave-aqui
```
3. Reiniciar backend

---

## 🎯 Comandos Útiles

### Backend
```bash
# Ver documentación API
http://localhost:8000/docs

# Ver logs
python -m uvicorn app.main:app --reload --log-level debug
```

### Frontend
```bash
# Build para producción
npm run build

# Preview build
npm run preview
```

---

## ❓ Problemas Comunes

### "Puerto 8000 ya en uso"
```bash
# Windows: Matar proceso
netstat -ano | findstr :8000
taskkill /PID [número] /F

# Usar otro puerto
python -m uvicorn app.main:app --reload --port 8001
```

### "ModuleNotFoundError"
```bash
# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

### "npm ERR!"
```bash
# Limpiar cache
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

---

## 📞 Soporte

Si tienes problemas, revisa:
1. README.md principal
2. backend/README.md
3. frontend/README.md

---

**¡Disfruta prediciendo tus ventas! 🍕📊**
