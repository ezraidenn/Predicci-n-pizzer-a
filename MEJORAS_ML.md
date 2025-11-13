# Mejoras al Sistema de Machine Learning

## 📊 Cambios Implementados

### 1. **Nuevas Features Temporales**

#### Features de Quincena y Días de Pago
- `es_primera_quincena`: Identifica días 1-15 del mes
- `es_segunda_quincena`: Identifica días 16-fin de mes
- `dias_desde_quincena`: Contador de días desde inicio de quincena
- `es_inicio_mes`: Días 1-5 (días de pago típicos)
- `es_fin_mes`: Días 25-fin (días de pago de quincena)
- `es_dia_pago`: Días 1-5, 13-17, 25-fin (días con mayor poder adquisitivo)

#### Features de Fin de Semana Mejoradas
- `es_viernes`: Específico para viernes (día de alta demanda)
- `es_sabado`: Específico para sábado
- `es_domingo`: Específico para domingo
- `es_fin_semana`: Sábado y domingo combinados

#### Features Estacionales
- `trimestre`: Trimestre del año (1-4)
- `semana_año`: Semana del año (1-52)

### 2. **Medias Móviles Extendidas**

Ahora se calculan ventanas de:
- **3 días**: Tendencia inmediata
- **7 días**: Tendencia semanal
- **14 días**: Tendencia quincenal (NUEVO)

### 3. **Lags Extendidos**

Se agregó:
- `lag14`: Valor de hace 14 días (para capturar patrones quincenales)

### 4. **Predicción desde HOY**

**Antes**: Solo predecía desde mañana
**Ahora**: 
- Si la última fecha de datos es HOY o posterior → predice desde mañana
- Si la última fecha es anterior a HOY → predice desde HOY
- Siempre muestra 7 días de predicción

### 5. **Mejora en Promedios de Visitas**

**Antes**: Usaba promedio simple de últimos 7 días
**Ahora**: Usa promedio del **mismo día de la semana** en las últimas 4 semanas
- Ejemplo: Para predecir un viernes, usa el promedio de los últimos 4 viernes
- Esto captura mejor los patrones semanales

## 🎯 Impacto Esperado

### Mejor Captura de Patrones
1. **Quincenas**: El modelo ahora entiende que las ventas suelen aumentar en días de pago
2. **Fin de Semana**: Diferencia entre viernes (preparación), sábado (pico) y domingo
3. **Estacionalidad**: Captura patrones mensuales y trimestrales

### Predicciones Más Precisas
- Con 7 meses de datos, el modelo tiene suficiente información para:
  - Identificar patrones quincenales
  - Reconocer días de alta demanda
  - Ajustar por estacionalidad

### Validación Recomendada
Después de reentrenar el modelo:
1. Comparar predicciones con datos reales de los últimos 30 días
2. Verificar que las predicciones de fin de semana sean mayores
3. Confirmar que los días de pago (1-5, 15, 25-fin) tengan predicciones más altas

## 🔄 Próximos Pasos

### Para Reentrenar el Modelo:
1. Sube un archivo Excel con datos actualizados
2. El sistema automáticamente:
   - Procesará los datos con las nuevas features
   - Entrenará los modelos con los patrones mejorados
   - Generará predicciones más precisas

### Monitoreo:
- Observa las predicciones durante 1-2 semanas
- Compara con ventas reales
- Si las predicciones están consistentemente altas/bajas, el modelo se auto-ajustará con más datos

## 📈 Features Totales del Modelo

### Temporales (18)
- dia_semana, dia_mes, mes, trimestre, semana_año
- es_fin_semana, es_viernes, es_sabado, es_domingo
- es_primera_quincena, es_segunda_quincena, dias_desde_quincena
- es_inicio_mes, es_fin_mes, es_dia_pago
- dia_0 a dia_6 (one-hot encoding)

### Operacionales (5)
- total_visitas, pedidos_iniciados, pedidos_creados
- tipo_servicio_domicilio, tipo_servicio_llevar
- conversion_rate

### Históricas por Variable (7 x 4 variables = 28)
- ma3, ma7, ma14 (medias móviles)
- std7 (desviación estándar)
- lag1, lag7, lag14 (valores anteriores)

**Total: ~51 features** (vs ~30 anteriores)

## ⚠️ Notas Importantes

1. **Reentrenamiento Necesario**: Las nuevas features requieren reentrenar el modelo
2. **Datos Mínimos**: Se recomienda tener al menos 60 días de datos para capturar patrones quincenales
3. **Actualización Continua**: Sube datos nuevos regularmente para mantener el modelo actualizado
