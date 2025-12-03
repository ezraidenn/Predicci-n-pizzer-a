# 🚀 Plan de Mejoras Profesionales - Pizzería MAX AI

## 📊 Datos Descubiertos No Utilizados

### 1. ⏰ Hora del Día (ALTA PRIORIDAD)
**Estado actual:** Se ignora la hora del pedido
**Oportunidad:** 
- Pico de ventas: 19:00-21:00 (70% de pedidos)
- Valle: 14:00-16:00 (10% de pedidos)

**Mejora propuesta:**
- Agregar columnas: `pedidos_hora_pico`, `pedidos_almuerzo`, `pedidos_tarde`
- Feature: `es_hora_pico` (19-22)
- Predicción por franja horaria

### 2. 🚗 Tipo de Servicio (ALTA PRIORIDAD)
**Estado actual:** Solo se guarda porcentaje general
**Datos reales:**
- Domicilio: $228 ticket promedio
- Para llevar: $194 ticket promedio

**Mejora propuesta:**
- Separar predicciones por tipo de servicio
- `ventas_domicilio`, `ventas_local`
- `ticket_promedio_domicilio`, `ticket_promedio_local`

### 3. 💳 Método de Pago (MEDIA PRIORIDAD)
**Oportunidad:** Correlación con ticket promedio
- Tarjeta suele tener tickets más altos
- Efectivo más frecuente en llevar

### 4. 👁️ Visitas y Conversión (MEDIA PRIORIDAD)
**Datos disponibles:**
- Menús vistos
- Pedidos iniciados
- Pedidos creados
- Tasa de conversión (~15%)

**Mejora propuesta:**
- Feature: `tasa_conversion_reciente`
- Predicción basada en visitas del día anterior

### 5. 🍕 Productos Específicos (MEDIA PRIORIDAD)
**Top productos:**
1. Pizza Pastorera (56 unidades)
2. Paquete Baguette (52)
3. Pizza de 3 ingredientes (43)

**Mejora propuesta:**
- Tracking de productos estrella
- Alertas de tendencias

### 6. 📦 Modificadores/Extras (BAJA PRIORIDAD)
**Datos disponibles:**
- Ingredientes extra más pedidos
- Ganancia por modificador

---

## 🔧 Mejoras al ETL Processor

### Cambios Requeridos:

```python
# NUEVAS COLUMNAS A EXTRAER
- hora_pedido (int 0-23)
- franja_horaria (almuerzo/tarde/cena/noche)
- ventas_domicilio (float)
- ventas_local (float)
- pedidos_domicilio (int)
- pedidos_local (int)
- ticket_promedio (float)
- visitas_dia (int)
- conversion_rate (float)
- productos_estrella (JSON)
```

### Nuevas Features para ML:
```python
# FEATURES TEMPORALES ADICIONALES
- es_hora_pico (bool)
- es_hora_almuerzo (bool)
- hora_peak_anterior (int)

# FEATURES DE SERVICIO
- ratio_domicilio (float 0-1)
- ticket_promedio_7d (float)

# FEATURES DE CONVERSIÓN
- conversion_rate_7d (float)
- visitas_promedio_7d (float)
```

---

## 📅 Plan de Implementación

### Fase 1: ETL Mejorado (Inmediato)
- [ ] Agregar extracción de hora del pedido
- [ ] Separar ventas por tipo de servicio
- [ ] Calcular ticket promedio diario
- [ ] Agregar datos de visitas

### Fase 2: Features Adicionales
- [ ] Feature de franja horaria
- [ ] Feature de ratio domicilio
- [ ] Feature de conversión

### Fase 3: ML Avanzado
- [ ] Modelo por franja horaria
- [ ] Predicción de tipo de servicio
- [ ] Alertas de productos

---

## 📈 Impacto Esperado

| Mejora | Impacto en Precisión |
|--------|---------------------|
| Hora del día | +5-10% |
| Tipo de servicio | +3-5% |
| Tasa de conversión | +2-3% |
| Ticket promedio | +2-3% |

**Total esperado: +12-20% mejora en MAPE**
