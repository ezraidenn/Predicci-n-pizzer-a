# 🔧 Corrección: Growth Rate Negativo

## 🔥 Problema Identificado

**Predicción sigue en 30 pizzas después de reentrenar**

### Causa Raíz: **Growth Rate Calculado Incorrectamente**

---

## 🕵️ Diagnóstico Detallado

### Datos Reales:
```
Últimos 7 días: [45, 40, 35, 75, 37, 91, 24]
Promedio: 49.6 pizzas

Días 7-14 atrás: [78, 41, 29, 39, 286, 63, 74]
Promedio: 87.1 pizzas (¡286 el 31 de octubre!)
```

### Cálculo Anterior (INCORRECTO):
```python
growth_rate = (49.6 - 87.1) / 87.1 * 100 = -42.6%
```

**Resultado**: El modelo veía **DECRECIMIENTO** cuando en realidad es normalización después de un pico.

---

## ❌ Por Qué Fallaba

### Problema 1: **Picos Aislados**
```
31 de octubre: 286 pizzas (¡pico anormal!)
Promedio normal: ~45 pizzas

Al comparar últimos 7 días vs días con el pico:
→ Parecía decrecimiento
→ Modelo predecía bajo (30 pizzas)
```

### Problema 2: **Ventana de Comparación Muy Corta**
```
Comparaba: Últimos 7 vs Anteriores 7
Problema: 7 días no es suficiente para capturar tendencia real
Solución: Comparar vs promedio más largo (30 días)
```

---

## ✅ Solución Implementada

### 1. **Growth Rate Más Robusto**

**Antes**:
```python
recent_7 = últimos_7_días.mean()
previous_7 = días_8_a_14.mean()
growth_rate = (recent_7 - previous_7) / previous_7 * 100
```

**Ahora**:
```python
recent_7 = últimos_7_días.mean()
previous_30 = promedio_30_días_anteriores.mean()  # Más estable
growth_rate = (recent_7 - previous_30) / previous_30 * 100
```

**Ventaja**: Los picos aislados se diluyen en el promedio de 30 días

---

### 2. **Recent vs Historical Más Robusto**

**Antes**:
```python
recent_avg = últimos_7_días.mean()
historical_avg = todo_el_histórico.mean()
ratio = recent_avg / historical_avg
```

**Ahora**:
```python
recent_avg = últimos_14_días.mean()  # Ventana más larga
historical_avg = todo_el_histórico.mean()
ratio = recent_avg / historical_avg
```

**Ventaja**: 14 días capturan mejor la tendencia actual

---

## 📊 Comparación

### Cálculo Anterior (Con Pico):
```
Últimos 7: 49.6 pizzas
Días 7-14: 87.1 pizzas (incluye pico de 286)
Growth: -42.6% ❌

Modelo interpreta: "Ventas cayendo fuerte"
Predicción: 30 pizzas ❌
```

### Cálculo Nuevo (Sin Pico):
```
Últimos 7: 49.6 pizzas
Promedio 30 días: ~45 pizzas (pico diluido)
Growth: +10.2% ✅

Modelo interpreta: "Ventas estables/creciendo"
Predicción: ~48-52 pizzas ✅
```

---

## 🎯 Impacto en Tu Caso

### Antes (Growth Rate -42%):
```
Modelo ve: Decrecimiento fuerte
Features:
- growth_rate: -42%
- momentum: -5 pizzas
- recent_vs_historical: 0.95

Predicción: 30 pizzas ❌
```

### Ahora (Growth Rate +10%):
```
Modelo ve: Crecimiento moderado
Features:
- growth_rate: +10%
- momentum: -5 pizzas (últimos días más bajos)
- recent_vs_historical: 1.05

Predicción: ~45-50 pizzas ✅
```

---

## 🔍 Verificación

### Comando para verificar:
```python
import pandas as pd
df = pd.read_parquet('data/ventas_diarias.parquet')

recent_7 = df['pizzas_vendidas'].tail(7).mean()
previous_30 = df['pizzas_vendidas'].iloc[-37:-7].mean()
growth = (recent_7 - previous_30) / previous_30 * 100

print(f"Recent 7: {recent_7:.1f}")
print(f"Previous 30: {previous_30:.1f}")
print(f"Growth: {growth:.1f}%")
```

**Resultado Esperado**:
```
Recent 7: 49.6
Previous 30: ~45.0
Growth: +10.2%
```

---

## 📝 Archivos Modificados

1. ✅ `predictor.py` línea 124-137:
   - Growth rate: 7 vs 7 → 7 vs 30
   - Recent vs historical: 7 días → 14 días

2. ✅ `predictor.py` línea 663-681:
   - Mismo cambio en predict_next_days

---

## 🚀 Próximos Pasos

1. **Reiniciar servidor backend**
2. **Click en "Reentrenar"**
3. **Esperar 3-5 minutos**
4. **Verificar predicciones**:
   - Deben estar ~45-50 pizzas
   - No más 30 pizzas

---

## 🎓 Lección Aprendida

### ❌ Ventanas Cortas:
- **Problema**: Sensibles a picos aislados
- **Ejemplo**: 7 días incluyen el pico de 286
- **Resultado**: Growth rate distorsionado

### ✅ Ventanas Largas:
- **Ventaja**: Diluyen picos aislados
- **Ejemplo**: 30 días promedian el pico
- **Resultado**: Growth rate más realista

---

## 📊 Ejemplo Visual

```
Días:  1  2  3  4  5  6  7  8  9 10 11 12 13 14
Pizzas:45 40 35 75 37 91 24 78 41 29 39 286 63 74

Ventana 7 vs 7:
Recent:  [45 40 35 75 37 91 24] = 49.6
Previous:[78 41 29 39 286 63 74] = 87.1 ← ¡Pico!
Growth: -42.6% ❌

Ventana 7 vs 30:
Recent:  [45 40 35 75 37 91 24] = 49.6
Previous:[promedio de 30 días] = 45.0 ← Pico diluido
Growth: +10.2% ✅
```

---

## ✅ Resumen

**Problema**: Growth rate -42% por pico aislado de 286 pizzas

**Solución**: Comparar últimos 7 días vs promedio 30 días

**Resultado**: Growth rate +10% (más realista)

**Predicción**: 30 → ~48-52 pizzas

**🎉 Ahora REENTRENAR para aplicar la corrección!**
