import { motion } from 'framer-motion'
import { TrendingUp, Info } from 'lucide-react'

export default function PredictionIntervals({ prediction, title = "Predicción" }) {
  if (!prediction) return null

  const hasIntervals = prediction.total_ventas_dia_lower && prediction.total_ventas_dia_upper
  
  if (!hasIntervals) return null

  const median = prediction.total_ventas_dia
  const lower = prediction.total_ventas_dia_lower
  const upper = prediction.total_ventas_dia_upper
  
  // Calcular porcentaje de posición de la mediana en el rango
  const range = upper - lower
  const medianPosition = ((median - lower) / range) * 100

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-effect rounded-xl p-6 mb-6"
    >
      <div className="flex items-center gap-2 mb-4">
        <TrendingUp className="w-5 h-5 text-primary-600" />
        <h3 className="text-lg font-bold text-gray-800">{title} con Intervalos de Confianza</h3>
      </div>

      {/* Barra de rango */}
      <div className="mb-6">
        <div className="relative h-12 bg-gradient-to-r from-red-100 via-yellow-100 to-green-100 rounded-lg overflow-hidden">
          {/* Marcador de mediana */}
          <div 
            className="absolute top-0 bottom-0 w-1 bg-primary-600 shadow-lg"
            style={{ left: `${medianPosition}%` }}
          >
            <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-primary-600 text-white px-3 py-1 rounded text-xs font-bold whitespace-nowrap">
              ${median.toLocaleString('es-MX', {minimumFractionDigits: 2, maximumFractionDigits: 2})}
            </div>
          </div>
        </div>

        {/* Labels */}
        <div className="flex justify-between mt-2 text-xs">
          <div className="text-left">
            <span className="text-gray-600">Pesimista</span>
            <div className="font-bold text-red-600">
              ${lower.toLocaleString('es-MX', {minimumFractionDigits: 2, maximumFractionDigits: 2})}
            </div>
          </div>
          <div className="text-right">
            <span className="text-gray-600">Optimista</span>
            <div className="font-bold text-green-600">
              ${upper.toLocaleString('es-MX', {minimumFractionDigits: 2, maximumFractionDigits: 2})}
            </div>
          </div>
        </div>
      </div>

      {/* Explicación */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start gap-2">
          <Info className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-blue-800">
            <p className="font-semibold mb-1">¿Qué significa esto?</p>
            <p>
              Hay un <strong>80% de probabilidad</strong> de que las ventas estén entre{' '}
              <strong>${lower.toLocaleString('es-MX', {maximumFractionDigits: 0})}</strong> y{' '}
              <strong>${upper.toLocaleString('es-MX', {maximumFractionDigits: 0})}</strong>.
              {' '}La predicción más probable es{' '}
              <strong>${median.toLocaleString('es-MX', {maximumFractionDigits: 0})}</strong>.
            </p>
          </div>
        </div>
      </div>

      {/* Productos */}
      {prediction.pizzas_vendidas_lower && (
        <div className="grid grid-cols-3 gap-4 mt-4">
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-xs text-gray-600 mb-1">🍕 Pizzas</div>
            <div className="text-sm font-bold text-gray-800">
              {Math.round(prediction.pizzas_vendidas_lower)} - {Math.round(prediction.pizzas_vendidas_upper)}
            </div>
            <div className="text-xs text-primary-600 font-semibold">
              ~{Math.round(prediction.pizzas_vendidas)}
            </div>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-xs text-gray-600 mb-1">🥖 Baguettes</div>
            <div className="text-sm font-bold text-gray-800">
              {Math.round(prediction.baguettes_vendidas_lower)} - {Math.round(prediction.baguettes_vendidas_upper)}
            </div>
            <div className="text-xs text-primary-600 font-semibold">
              ~{Math.round(prediction.baguettes_vendidas)}
            </div>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-xs text-gray-600 mb-1">🍟 Papas</div>
            <div className="text-sm font-bold text-gray-800">
              {Math.round(prediction.papas_gajo_vendidas_lower)} - {Math.round(prediction.papas_gajo_vendidas_upper)}
            </div>
            <div className="text-xs text-primary-600 font-semibold">
              ~{Math.round(prediction.papas_gajo_vendidas)}
            </div>
          </div>
        </div>
      )}
    </motion.div>
  )
}
