# 🍕 AGREGAR PRODUCTOS NUEVOS AL SISTEMA

## 📋 **PRODUCTOS A AGREGAR**

1. **Pizzas de Pastor** (Pastorera)
2. **Pizzas de Chuleta** (Chuli)
3. **Alitas** (Complemento)

---

## 🔍 **PASOS PARA IMPLEMENTAR**

### **1. Actualizar ETL (Procesamiento de Excel)**

**Archivo**: `backend/app/etl_processor.py`

```python
# Agregar nuevas columnas al procesar Excel
columnas_esperadas = {
    'pizzas_vendidas': int,
    'baguettes_vendidas': int,
    'papas_gajo_vendidas': int,
    'pizzas_pastor': int,      # NUEVO
    'pizzas_chuleta': int,     # NUEVO
    'alitas_vendidas': int,    # NUEVO
    'total_ventas_dia': float,
    'total_pedidos': int,
}
```

---

### **2. Actualizar Base de Datos**

**Archivo**: `backend/app/database.py`

```sql
ALTER TABLE ventas_diarias 
ADD COLUMN pizzas_pastor INTEGER DEFAULT 0;

ALTER TABLE ventas_diarias 
ADD COLUMN pizzas_chuleta INTEGER DEFAULT 0;

ALTER TABLE ventas_diarias 
ADD COLUMN alitas_vendidas INTEGER DEFAULT 0;
```

---

### **3. Actualizar Predictor**

**Archivo**: `backend/app/predictor_simple.py`

```python
# Agregar a la lista de variables
self.variables = [
    'pizzas_vendidas',
    'baguettes_vendidas', 
    'papas_gajo_vendidas',
    'pizzas_pastor',      # NUEVO
    'pizzas_chuleta',     # NUEVO
    'alitas_vendidas',    # NUEVO
    'total_ventas_dia'
]

# Calcular promedios para cada producto
for variable in self.variables:
    mediana = df_reciente[variable].median()
    p15 = df_reciente[variable].quantile(0.15)
    p85 = df_reciente[variable].quantile(0.85)
    
    self.promedios[dia_num][variable] = {
        'base': float(mediana),
        'min': float(p15),
        'max': float(p85)
    }
```

---

### **4. Actualizar API Response**

**Archivo**: `backend/app/predictor_simple.py` - función `predict`

```python
pred_values = {
    'fecha': pred_date,
    'dia_nombre': dia_nombre,
    
    # Productos base
    'pizzas_vendidas': float(pizzas_base * multiplicador),
    'baguettes_vendidas': float(baguettes_base * multiplicador),
    'papas_gajo_vendidas': float(papas_base * multiplicador),
    
    # NUEVOS PRODUCTOS
    'pizzas_pastor': float(pastor_base * multiplicador),
    'pizzas_chuleta': float(chuleta_base * multiplicador),
    'alitas_vendidas': float(alitas_base * multiplicador),
    
    # Rangos para nuevos productos
    'pastor_min': float(self.promedios[dia_semana]['pizzas_pastor']['min'] * multiplicador),
    'pastor_max': float(self.promedios[dia_semana]['pizzas_pastor']['max'] * multiplicador),
    'chuleta_min': float(self.promedios[dia_semana]['pizzas_chuleta']['min'] * multiplicador),
    'chuleta_max': float(self.promedios[dia_semana]['pizzas_chuleta']['max'] * multiplicador),
    'alitas_min': float(self.promedios[dia_semana]['alitas_vendidas']['min'] * multiplicador),
    'alitas_max': float(self.promedios[dia_semana]['alitas_vendidas']['max'] * multiplicador),
    
    # Ventas
    'total_ventas_dia': float(ventas_base * multiplicador),
    'ventas_min': float(self.promedios[dia_semana]['total_ventas_dia']['min'] * multiplicador),
    'ventas_max': float(self.promedios[dia_semana]['total_ventas_dia']['max'] * multiplicador),
    
    # Evento
    'evento': evento_info['evento'],
    'multiplicador': multiplicador,
}
```

---

### **5. Actualizar Frontend - Modal**

**Archivo**: `frontend/src/components/Dashboard.jsx`

```jsx
{/* Predicción Principal - Expandida */}
<div className="bg-gradient-to-br from-primary-50 to-primary-100 rounded-xl p-6 mb-6">
  <div className="grid grid-cols-3 gap-4">
    <div>
      <p className="text-sm text-gray-600 mb-1">Ventas Esperadas</p>
      <p className="text-2xl font-bold text-primary-600">
        {formatCurrency(selectedPrediction.total_ventas_dia)}
      </p>
    </div>
    <div>
      <p className="text-sm text-gray-600 mb-1">Pizzas Totales</p>
      <p className="text-2xl font-bold text-primary-600">
        {Math.round(selectedPrediction.pizzas_vendidas)}
      </p>
    </div>
    <div>
      <p className="text-sm text-gray-600 mb-1">Alitas</p>
      <p className="text-2xl font-bold text-primary-600">
        {Math.round(selectedPrediction.alitas_vendidas || 0)}
      </p>
    </div>
  </div>
  
  {/* Desglose de Pizzas */}
  <div className="mt-4 pt-4 border-t border-primary-200">
    <p className="text-xs text-gray-600 mb-2 font-semibold">Desglose de Pizzas:</p>
    <div className="grid grid-cols-3 gap-3 text-sm">
      <div>
        <p className="text-gray-600">🍕 Normales</p>
        <p className="font-bold">{Math.round(selectedPrediction.pizzas_vendidas - (selectedPrediction.pizzas_pastor || 0) - (selectedPrediction.pizzas_chuleta || 0))}</p>
      </div>
      <div>
        <p className="text-gray-600">🌮 Pastor</p>
        <p className="font-bold">{Math.round(selectedPrediction.pizzas_pastor || 0)}</p>
        <p className="text-xs text-gray-500">({Math.round(selectedPrediction.pastor_min || 0)}-{Math.round(selectedPrediction.pastor_max || 0)})</p>
      </div>
      <div>
        <p className="text-gray-600">🥩 Chuleta</p>
        <p className="font-bold">{Math.round(selectedPrediction.pizzas_chuleta || 0)}</p>
        <p className="text-xs text-gray-500">({Math.round(selectedPrediction.chuleta_min || 0)}-{Math.round(selectedPrediction.chuleta_max || 0)})</p>
      </div>
    </div>
  </div>
</div>

{/* Recomendaciones Actualizadas */}
<div className="bg-green-50 border border-green-200 rounded-lg p-4">
  <div className="flex items-start gap-3">
    <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center text-white font-bold flex-shrink-0">
      💡
    </div>
    <div className="flex-1">
      <p className="font-semibold text-gray-800 mb-1">Recomendaciones para este día</p>
      <ul className="text-sm text-gray-600 space-y-1">
        <li>• <strong>Pizzas normales:</strong> {Math.round((selectedPrediction.pizzas_vendidas - (selectedPrediction.pizzas_pastor || 0) - (selectedPrediction.pizzas_chuleta || 0)) * 1.1)} unidades</li>
        <li>• <strong>Pastor:</strong> {Math.round((selectedPrediction.pizzas_pastor || 0) * 1.1)} kg de carne al pastor</li>
        <li>• <strong>Chuleta:</strong> {Math.round((selectedPrediction.pizzas_chuleta || 0) * 1.1)} kg de chuleta</li>
        <li>• <strong>Alitas:</strong> {Math.round((selectedPrediction.alitas_vendidas || 0) * 1.1)} órdenes (aprox {Math.round((selectedPrediction.alitas_vendidas || 0) * 6)} piezas)</li>
        <li>• Personal recomendado: <strong>{Math.round(selectedPrediction.pizzas_vendidas / 25)} personas</strong></li>
        {selectedPrediction.evento && (
          <li className="text-orange-700 font-semibold">• ⚠️ Día especial: considera tener personal extra disponible</li>
        )}
      </ul>
    </div>
  </div>
</div>
```

---

### **6. Actualizar Tabla Principal (Opcional)**

**Archivo**: `frontend/src/components/Dashboard.jsx`

```jsx
<thead>
  <tr className="border-b-2 border-gray-300 bg-gray-50">
    <th className="text-left py-3 px-4">Fecha</th>
    <th className="text-right py-3 px-4">Ventas</th>
    <th className="text-right py-3 px-4">Pizzas</th>
    <th className="text-right py-3 px-4">Pastor</th>    {/* NUEVO */}
    <th className="text-right py-3 px-4">Chuleta</th>   {/* NUEVO */}
    <th className="text-right py-3 px-4">Alitas</th>    {/* NUEVO */}
    <th className="text-right py-3 px-4">Baguettes</th>
    <th className="text-right py-3 px-4">Papas</th>
  </tr>
</thead>
```

---

## 📊 **FORMATO ESPERADO EN EXCEL**

```
Fecha       | Pizzas | Pastor | Chuleta | Alitas | Baguettes | Papas | Ventas
------------|--------|--------|---------|--------|-----------|-------|--------
2025-11-01  |   50   |   12   |    8    |   15   |     9     |   1   | 12,678
2025-11-02  |   44   |   10   |    6    |   12   |     8     |   3   | 11,045
```

**Nombres de columnas aceptados**:
- Pastor: `pastor`, `pastorera`, `pizzas_pastor`, `pizza_pastor`
- Chuleta: `chuleta`, `chuli`, `pizzas_chuleta`, `pizza_chuleta`
- Alitas: `alitas`, `alitas_vendidas`, `ordenes_alitas`

---

## ✅ **CHECKLIST DE IMPLEMENTACIÓN**

- [ ] Subir Excel con columnas nuevas
- [ ] Actualizar ETL para procesar nuevas columnas
- [ ] Migrar base de datos (agregar columnas)
- [ ] Actualizar predictor para incluir nuevos productos
- [ ] Actualizar API response
- [ ] Actualizar frontend - modal
- [ ] Actualizar frontend - tabla (opcional)
- [ ] Reentrenar modelos
- [ ] Probar predicciones
- [ ] Validar rangos
- [ ] Subir a GitHub

---

## 🎯 **PRÓXIMOS PASOS**

1. **Compartir archivo Excel** con las columnas de pastor, chuleta y alitas
2. **Revisar formato** y nombres de columnas
3. **Implementar cambios** en el código
4. **Probar** con datos reales
5. **Desplegar** a producción

---

**📝 Nota**: Una vez que tengas el Excel con los datos históricos de estos productos, podré implementar todo el sistema automáticamente.
