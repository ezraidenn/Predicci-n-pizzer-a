# 📊 Formato de Excel - Ejemplo Detallado

## 📋 Estructura General

Tu archivo Excel debe tener **exactamente 3 hojas** con estos nombres:

1. **Pedidos**
2. **Detalles**
3. **Visitas**

---

## 📄 HOJA 1: "Pedidos"

### Columnas Requeridas:
- `Fecha de creación` - Fecha y hora del pedido
- `Total` - Monto total en dinero
- `Estado` - Estado del pedido (debe contener "Finalizado")
- `Tipo de servicio` - A domicilio, Para llevar, etc.

### Ejemplo de Datos:

| Fecha de creación | Total | Estado | Tipo de servicio |
|-------------------|-------|--------|------------------|
| 2024-01-01 10:30:00 | 450.50 | Finalizado | A domicilio |
| 2024-01-01 11:15:00 | 320.00 | Finalizado | Para llevar |
| 2024-01-01 12:45:00 | 580.75 | Finalizado | A domicilio |
| 2024-01-01 14:20:00 | 290.00 | Finalizado | Para llevar |
| 2024-01-01 18:30:00 | 650.25 | Finalizado | A domicilio |
| 2024-01-02 10:00:00 | 380.00 | Finalizado | Para llevar |
| 2024-01-02 11:30:00 | 520.50 | Finalizado | A domicilio |

### Notas Importantes:
- ✅ `Fecha de creación` debe ser formato fecha/hora válido
- ✅ `Total` debe ser número (puede tener decimales)
- ✅ `Estado` debe contener la palabra "Finalizado" (mayúsculas/minúsculas no importan)
- ✅ `Tipo de servicio` puede ser cualquier texto

---

## 📄 HOJA 2: "Detalles"

### Columnas Requeridas:
- `Fecha de creación` - Fecha y hora del pedido
- `Nombre` - Nombre del producto
- `Cantidad` - Cantidad vendida
- `Categoría` - (Opcional) Categoría del producto

### Ejemplo de Datos:

| Fecha de creación | Nombre | Cantidad | Categoría |
|-------------------|--------|----------|-----------|
| 2024-01-01 10:30:00 | Pizza Margarita | 2 | Pizzas |
| 2024-01-01 10:30:00 | Baguette Jamón | 1 | Baguette |
| 2024-01-01 10:30:00 | Papas Gajo | 1 | Acompañamientos |
| 2024-01-01 11:15:00 | Pizza Pepperoni | 1 | Pizzas |
| 2024-01-01 11:15:00 | Pizza Hawaiana | 1 | Pizzas |
| 2024-01-01 12:45:00 | Baguette Pollo | 2 | Baguette |
| 2024-01-01 12:45:00 | Papas Gajo | 2 | Acompañamientos |
| 2024-01-01 14:20:00 | Pizza Vegetariana | 1 | Pizzas |
| 2024-01-01 18:30:00 | Pizza 4 Quesos | 2 | Pizzas |
| 2024-01-01 18:30:00 | Baguette Atún | 1 | Baguette |

### Notas Importantes:
- ✅ `Fecha de creación` debe coincidir con fechas de la hoja Pedidos
- ✅ `Nombre` es texto libre - el sistema detecta automáticamente:
  - **Pizzas:** Si contiene "pizza" o categoría es "Pizzas"
  - **Baguettes:** Si contiene "baguette"
  - **Papas Gajo:** Si contiene "papas gajo" o "papa gajo"
- ✅ `Cantidad` debe ser número entero
- ✅ `Categoría` es opcional pero ayuda a la clasificación

---

## 📄 HOJA 3: "Visitas"

### Columnas Requeridas:
- `Fecha` - Fecha (sin hora)
- `Total de visitas` - Número de visitas al sitio/local
- `Pedidos iniciados` - Pedidos que se comenzaron
- `Pedidos creados` - Pedidos que se completaron

### Ejemplo de Datos:

| Fecha | Total de visitas | Pedidos iniciados | Pedidos creados |
|-------|------------------|-------------------|-----------------|
| 2024-01-01 | 150 | 45 | 30 |
| 2024-01-02 | 180 | 52 | 38 |
| 2024-01-03 | 165 | 48 | 35 |
| 2024-01-04 | 200 | 60 | 42 |
| 2024-01-05 | 175 | 50 | 36 |
| 2024-01-06 | 220 | 65 | 48 |
| 2024-01-07 | 190 | 55 | 40 |

### Notas Importantes:
- ✅ `Fecha` solo fecha, sin hora
- ✅ Todos los valores numéricos deben ser números enteros
- ✅ Una fila por día
- ✅ Las fechas deben coincidir con las de Pedidos y Detalles

---

## 📊 EJEMPLO COMPLETO - Día Típico

### Día: 2024-01-15

**Hoja Pedidos:**
| Fecha de creación | Total | Estado | Tipo de servicio |
|-------------------|-------|--------|------------------|
| 2024-01-15 12:00 | 450.00 | Finalizado | A domicilio |
| 2024-01-15 13:30 | 320.50 | Finalizado | Para llevar |
| 2024-01-15 19:00 | 580.00 | Finalizado | A domicilio |

**Hoja Detalles:**
| Fecha de creación | Nombre | Cantidad | Categoría |
|-------------------|--------|----------|-----------|
| 2024-01-15 12:00 | Pizza Margarita | 2 | Pizzas |
| 2024-01-15 12:00 | Papas Gajo | 1 | Acompañamientos |
| 2024-01-15 13:30 | Baguette Jamón | 2 | Baguette |
| 2024-01-15 13:30 | Pizza Pepperoni | 1 | Pizzas |
| 2024-01-15 19:00 | Pizza 4 Quesos | 2 | Pizzas |
| 2024-01-15 19:00 | Baguette Pollo | 1 | Baguette |

**Hoja Visitas:**
| Fecha | Total de visitas | Pedidos iniciados | Pedidos creados |
|-------|------------------|-------------------|-----------------|
| 2024-01-15 | 200 | 60 | 45 |

**Resultado Procesado:**
- **Fecha:** 2024-01-15
- **Total ventas día:** $1,350.50
- **Total pedidos:** 3
- **Pizzas vendidas:** 5 unidades
- **Baguettes vendidas:** 3 unidades
- **Papas gajo vendidas:** 1 unidad
- **Total visitas:** 200
- **Pedidos iniciados:** 60
- **Pedidos creados:** 45
- **% A domicilio:** 66.67%
- **% Para llevar:** 33.33%

---

## ✅ VALIDACIONES DEL SISTEMA

El sistema validará automáticamente:

### ✓ Estructura
- [x] Archivo es formato Excel (.xlsx o .xls)
- [x] Existen las 3 hojas requeridas
- [x] Nombres de hojas son exactos

### ✓ Columnas
- [x] Todas las columnas requeridas están presentes
- [x] Nombres de columnas coinciden (mayúsculas/minúsculas no importan)

### ✓ Datos
- [x] Fechas son válidas y parseables
- [x] Números son válidos
- [x] No hay filas completamente vacías
- [x] Estados contienen "Finalizado"

---

## ❌ ERRORES COMUNES

### Error: "Faltan hojas requeridas"
**Causa:** Nombres de hojas incorrectos
**Solución:** Renombrar hojas exactamente como: `Pedidos`, `Detalles`, `Visitas`

### Error: "Falta columna 'Fecha de creación'"
**Causa:** Nombre de columna incorrecto
**Solución:** Verificar nombres exactos de columnas (ver arriba)

### Error: "No hay datos procesados"
**Causa:** No hay pedidos con estado "Finalizado"
**Solución:** Verificar que la columna Estado contenga "Finalizado"

### Error: "Fechas inválidas"
**Causa:** Formato de fecha no reconocido
**Solución:** Usar formato: `YYYY-MM-DD HH:MM:SS` o `DD/MM/YYYY HH:MM:SS`

---

## 💡 CONSEJOS

### Para Mejores Resultados:
1. **Datos históricos:** Mínimo 30 días, ideal 90+ días
2. **Consistencia:** Mantener mismo formato en todas las filas
3. **Completitud:** Incluir todos los pedidos finalizados
4. **Precisión:** Verificar que totales coincidan con detalles

### Datos Opcionales que Mejoran Predicciones:
- Más días históricos
- Categorías detalladas en productos
- Datos de visitas precisos
- Tipos de servicio consistentes

---

## 📥 PLANTILLA DESCARGABLE

Para crear tu propio archivo, puedes:

1. **Copiar estructura** de los ejemplos arriba
2. **Usar Excel/Google Sheets** para crear las 3 hojas
3. **Llenar con tus datos** reales
4. **Guardar como .xlsx**
5. **Subir al sistema**

---

## 🔍 VERIFICACIÓN ANTES DE SUBIR

Checklist rápido:

- [ ] Archivo es .xlsx o .xls
- [ ] Tiene exactamente 3 hojas
- [ ] Hojas se llaman: Pedidos, Detalles, Visitas
- [ ] Todas las columnas requeridas están presentes
- [ ] Hay al menos 30 días de datos
- [ ] Fechas están en formato válido
- [ ] Números son válidos (sin texto)
- [ ] Estados dicen "Finalizado"

---

<div align="center">

**¿Listo para subir tu Excel?**

Sigue las instrucciones en `INSTRUCCIONES_PASO_A_PASO.md`

---

**¡Buena suerte con tus predicciones! 🍕📊**

</div>
