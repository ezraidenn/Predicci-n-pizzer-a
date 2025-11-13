import { motion } from 'framer-motion'
import { DollarSign, Pizza, Croissant, Beef } from 'lucide-react'
import KPICard from './KPICard'
import SalesChart from './SalesChart'
import ProductsChart from './ProductsChart'
import InsightBox from './InsightBox'
import DataQualityAlert from './DataQualityAlert'
import PredictionIntervals from './PredictionIntervals'
import PredictionExplanation from './PredictionExplanation'
import { formatNumber, formatCurrency } from '../utils/formatters'

export default function Dashboard({ data, predictions, insight, loading }) {
  if (!data) return null

  const stats = data?.stats || {}
  const historicalData = data?.data || []
  const recentData = data.recent_data || []

  // Calcular KPIs
  const totalVentas = stats.ventas_totales || 0
  const promedioVentas = stats.promedio_ventas_dia || 0
  const totalPizzas = stats.total_pizzas || 0
  const totalBaguettes = stats.total_baguettes || 0
  const totalPapas = stats.total_papas_gajo || 0

  // Predicciones: primera es de AYER, segunda es de HOY
  const yesterdayPrediction = predictions && predictions.length > 0 ? predictions[0] : null
  const todayPrediction = predictions && predictions.length > 1 ? predictions[1] : null
  
  // Determinar fechas
  const lastDataDate = stats.fecha_fin ? new Date(stats.fecha_fin) : null
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-8"
    >
      {/* Header */}
      <motion.div variants={itemVariants}>
        <h2 className="text-3xl font-bold mb-2 text-gray-800">Dashboard de Ventas</h2>
        <p className="text-gray-600">
          Datos desde {stats.fecha_inicio} hasta {stats.fecha_fin} ({formatNumber(stats.total_dias)} días)
        </p>
      </motion.div>

      {/* Data Quality Alert */}
      <motion.div variants={itemVariants}>
        <DataQualityAlert stats={stats} />
      </motion.div>

      {/* KPI Cards */}
      <motion.div
        variants={itemVariants}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
      >
        <KPICard
          title="Ventas Totales"
          value={totalVentas}
          format="currency"
          icon={DollarSign}
          color="green"
          subtitle={`Promedio: ${formatCurrency(promedioVentas)}/día`}
          prediction={yesterdayPrediction?.total_ventas_dia}
          avgDaily={promedioVentas}
          predictionLabel="Predicción ayer (12/11)"
        />
        <KPICard
          title="Pizzas Vendidas"
          value={totalPizzas}
          format="number"
          icon={Pizza}
          color="blue"
          subtitle={`${formatNumber((totalPizzas / stats.total_dias).toFixed(1))}/día`}
          prediction={yesterdayPrediction?.pizzas_vendidas}
          avgDaily={totalPizzas / stats.total_dias}
          predictionLabel="Predicción ayer (12/11)"
        />
        <KPICard
          title="Baguettes"
          value={totalBaguettes}
          format="number"
          icon={Croissant}
          color="amber"
          subtitle={`${formatNumber((totalBaguettes / stats.total_dias).toFixed(1))}/día`}
          prediction={yesterdayPrediction?.baguettes_vendidas}
          avgDaily={totalBaguettes / stats.total_dias}
          predictionLabel="Predicción ayer (12/11)"
        />
        <KPICard
          title="Papas Gajo"
          value={totalPapas}
          format="number"
          icon={Beef}
          color="orange"
          subtitle={`${formatNumber((totalPapas / stats.total_dias).toFixed(1))}/día`}
          prediction={yesterdayPrediction?.papas_gajo_vendidas}
          avgDaily={totalPapas / stats.total_dias}
          predictionLabel="Predicción ayer (12/11)"
        />
      </motion.div>

      {/* Insight Box */}
      {insight && (
        <motion.div variants={itemVariants}>
          <InsightBox insight={insight} loading={loading} />
        </motion.div>
      )}

      {/* Prediction Intervals - DESACTIVADO (modelos quantile no entrenados) */}
      {/* {nextDayPrediction && (
        <motion.div variants={itemVariants}>
          <PredictionIntervals 
            prediction={nextDayPrediction} 
            title={isPredictingToday ? "Predicción para Hoy" : "Predicción para Mañana"}
          />
        </motion.div>
      )} */}

      {/* Prediction Explanation - DESACTIVADO (SHAP no entrenado) */}
      {/* {nextDayPrediction && (
        <motion.div variants={itemVariants}>
          <PredictionExplanation prediction={nextDayPrediction} />
        </motion.div>
      )} */}

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div variants={itemVariants}>
          <SalesChart
            historicalData={recentData}
            predictions={predictions}
          />
        </motion.div>
        <motion.div variants={itemVariants}>
          <ProductsChart
            pizzas={totalPizzas}
            baguettes={totalBaguettes}
            papas={totalPapas}
          />
        </motion.div>
      </div>

      {/* Predictions Table */}
      {predictions && predictions.length > 0 && (
        <motion.div variants={itemVariants} className="glass-effect rounded-xl p-6">
          <h3 className="text-xl font-bold mb-4 text-gray-800">Predicciones Próximos 7 Días</h3>
          <p className="text-sm text-gray-600 mb-4">
            Predicción base con rangos realistas (pesimista - optimista)
          </p>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b-2 border-gray-300 bg-gray-50">
                  <th className="text-left py-3 px-4 text-gray-700 font-semibold">Fecha</th>
                  <th className="text-right py-3 px-4 text-gray-700 font-semibold">Ventas</th>
                  <th className="text-right py-3 px-4 text-gray-700 font-semibold">Pizzas</th>
                  <th className="text-right py-3 px-4 text-gray-700 font-semibold">Baguettes</th>
                  <th className="text-right py-3 px-4 text-gray-700 font-semibold">Papas</th>
                </tr>
              </thead>
              <tbody>
                {predictions.map((pred, index) => (
                  <motion.tr
                    key={pred.fecha}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="border-b border-gray-200 hover:bg-primary-50 transition-colors"
                  >
                    <td className="py-3 px-4">
                      <div className="font-medium text-gray-800">{pred.fecha}</div>
                      {pred.dia_nombre && (
                        <div className="text-xs text-gray-500">{pred.dia_nombre}</div>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="text-primary-600 font-semibold">
                        {formatCurrency(pred.total_ventas_dia)}
                      </div>
                      {pred.ventas_min && pred.ventas_max && (
                        <div className="text-xs text-gray-500">
                          {formatCurrency(pred.ventas_min)} - {formatCurrency(pred.ventas_max)}
                        </div>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="text-gray-700 font-medium">
                        {formatNumber(Math.round(pred.pizzas_vendidas))}
                      </div>
                      {pred.pizzas_min && pred.pizzas_max && (
                        <div className="text-xs text-gray-500">
                          {Math.round(pred.pizzas_min)} - {Math.round(pred.pizzas_max)}
                        </div>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="text-gray-700 font-medium">
                        {formatNumber(Math.round(pred.baguettes_vendidas))}
                      </div>
                      {pred.baguettes_min && pred.baguettes_max && (
                        <div className="text-xs text-gray-500">
                          {Math.round(pred.baguettes_min)} - {Math.round(pred.baguettes_max)}
                        </div>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="text-gray-700 font-medium">
                        {formatNumber(Math.round(pred.papas_gajo_vendidas))}
                      </div>
                      {pred.papas_min && pred.papas_max && (
                        <div className="text-xs text-gray-500">
                          {Math.round(pred.papas_min)} - {Math.round(pred.papas_max)}
                        </div>
                      )}
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {/* Leyenda */}
          <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
            <div className="text-sm text-gray-700">
              <span className="font-semibold">💡 Cómo interpretar:</span>
              <ul className="mt-2 space-y-1 text-xs">
                <li><strong>Valor principal:</strong> Predicción más probable (mediana histórica)</li>
                <li><strong>Rango inferior:</strong> Escenario pesimista (15% de días son peores)</li>
                <li><strong>Rango superior:</strong> Escenario optimista (15% de días son mejores)</li>
                <li className="text-gray-600 italic">Rangos amplios para capturar crecimiento y variabilidad</li>
              </ul>
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  )
}
