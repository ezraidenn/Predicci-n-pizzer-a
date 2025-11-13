import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { motion } from 'framer-motion'

export default function SalesChart({ historicalData, predictions }) {
  // Combinar datos históricos y predicciones
  const chartData = [
    ...(historicalData || []).map(d => ({
      fecha: d.fecha,
      ventas: d.total_ventas_dia,
      tipo: 'real'
    })),
    ...(predictions || []).map(p => ({
      fecha: p.fecha,
      prediccion: p.total_ventas_dia,
      tipo: 'prediccion'
    }))
  ]

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-white rounded-lg p-3 border border-gray-200 shadow-lg">
          <p className="text-sm font-semibold mb-1 text-gray-800">{data.fecha}</p>
          {data.ventas && (
            <p className="text-sm text-primary-600 font-medium">
              Ventas: ${data.ventas.toLocaleString('es-MX', {minimumFractionDigits: 2, maximumFractionDigits: 2})}
            </p>
          )}
          {data.prediccion && (
            <p className="text-sm text-blue-600 font-medium">
              Predicción: ${data.prediccion.toLocaleString('es-MX', {minimumFractionDigits: 2, maximumFractionDigits: 2})}
            </p>
          )}
        </div>
      )
    }
    return null
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-effect rounded-xl p-6"
    >
      <h3 className="text-xl font-bold mb-4 text-gray-800">Ventas: Real vs Predicción</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            dataKey="fecha" 
            stroke="#6b7280"
            tick={{ fill: '#6b7280', fontSize: 12 }}
            tickFormatter={(value) => {
              const date = new Date(value)
              return `${date.getDate()}/${date.getMonth() + 1}`
            }}
          />
          <YAxis 
            stroke="#6b7280"
            tick={{ fill: '#6b7280', fontSize: 12 }}
            tickFormatter={(value) => `$${value.toLocaleString('es-MX')}`}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend 
            wrapperStyle={{ color: '#374151' }}
            iconType="line"
          />
          <Line
            type="monotone"
            dataKey="ventas"
            stroke="#16a34a"
            strokeWidth={3}
            dot={{ fill: '#16a34a', r: 5 }}
            name="Ventas Reales"
            connectNulls
          />
          <Line
            type="monotone"
            dataKey="prediccion"
            stroke="#2563eb"
            strokeWidth={3}
            strokeDasharray="5 5"
            dot={{ fill: '#2563eb', r: 5 }}
            name="Predicción"
            connectNulls
          />
        </LineChart>
      </ResponsiveContainer>
    </motion.div>
  )
}
