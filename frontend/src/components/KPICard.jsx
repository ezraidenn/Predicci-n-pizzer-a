import { motion } from 'framer-motion'
import CountUp from 'react-countup'
import { TrendingUp, TrendingDown } from 'lucide-react'

const colorMap = {
  primary: 'text-primary-600',
  green: 'text-primary-600',
  orange: 'text-orange-600',
  yellow: 'text-yellow-600',
  amber: 'text-amber-600',
  blue: 'text-blue-600',
}

const bgColorMap = {
  primary: 'bg-primary-50',
  green: 'bg-primary-50',
  orange: 'bg-orange-50',
  yellow: 'bg-yellow-50',
  amber: 'bg-amber-50',
  blue: 'bg-blue-50',
}

export default function KPICard({ 
  title, 
  value, 
  format = 'number', 
  icon: Icon, 
  color = 'primary',
  subtitle,
  prediction,
  avgDaily,
  predictionLabel = 'Predicción hoy'
}) {
  const textColor = colorMap[color] || colorMap.primary
  const bgColor = bgColorMap[color] || bgColorMap.primary

  // Calcular cambio si hay predicción
  let change = null
  if (prediction && avgDaily) {
    // Comparar predicción de mañana vs promedio diario histórico
    change = ((prediction - avgDaily) / avgDaily) * 100
  }

  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -5 }}
      transition={{ type: 'spring', stiffness: 300 }}
      className="glass-effect rounded-xl p-6 hover:border-primary-300 hover:shadow-xl transition-all duration-300"
    >
      <div className="flex items-start justify-between mb-4">
        <div className={`w-12 h-12 ${bgColor} rounded-lg flex items-center justify-center`}>
          <Icon className={`w-6 h-6 ${textColor}`} />
        </div>
        {change !== null && (
          <div className={`flex items-center gap-1 text-sm ${change >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
            {change >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
            <span className="font-semibold">{Math.abs(change).toFixed(1)}%</span>
          </div>
        )}
      </div>

      <h3 className="text-gray-600 text-sm mb-2 font-medium">{title}</h3>
      
      <div className={`text-3xl font-bold ${textColor} mb-1`}>
        {format === 'currency' && '$'}
        <CountUp
          end={value}
          duration={2}
          separator=","
          decimals={format === 'currency' ? 2 : 0}
        />
      </div>

      {subtitle && (
        <p className="text-xs text-gray-600">{subtitle}</p>
      )}

      {prediction && (
        <div className="mt-3 pt-3 border-t border-gray-200">
          <p className="text-xs text-gray-600 mb-1">
            {predictionLabel}:
          </p>
          <p className={`text-sm font-semibold ${textColor}`}>
            {format === 'currency' && '$'}
            {format === 'currency' ? prediction.toLocaleString('es-MX', {minimumFractionDigits: 2, maximumFractionDigits: 2}) : Math.round(prediction).toLocaleString('es-MX')}
          </p>
          {change !== null && (
            <div className="flex items-center gap-1 mt-1">
              {change > 0 ? (
                <TrendingUp className="w-3 h-3 text-green-600" />
              ) : (
                <TrendingDown className="w-3 h-3 text-red-600" />
              )}
              <span className={`text-xs font-medium ${change > 0 ? 'text-green-600' : 'text-red-600'}`}>
                {change > 0 ? '+' : ''}{change.toFixed(1)}% vs promedio
              </span>
            </div>
          )}
        </div>
      )}
    </motion.div>
  )
}
