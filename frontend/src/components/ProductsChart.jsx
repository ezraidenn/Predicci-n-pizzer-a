import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'
import { motion } from 'framer-motion'

const COLORS = ['#16a34a', '#d97706', '#ea580c']  // Verde, Ámbar, Naranja

export default function ProductsChart({ pizzas, baguettes, papas }) {
  const data = [
    { name: 'Pizzas', value: pizzas },
    { name: 'Baguettes', value: baguettes },
    { name: 'Papas Gajo', value: papas },
  ]

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0]
      return (
        <div className="bg-white rounded-lg p-3 border border-gray-200 shadow-lg">
          <p className="text-sm font-semibold mb-1 text-gray-800">{data.name}</p>
          <p className="text-sm font-medium" style={{ color: data.payload.fill }}>
            {data.value.toLocaleString('es-MX')} unidades
          </p>
          <p className="text-xs text-gray-600">
            {((data.value / (pizzas + baguettes + papas)) * 100).toFixed(1)}%
          </p>
        </div>
      )
    }
    return null
  }

  const renderCustomLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }) => {
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5
    const x = cx + radius * Math.cos(-midAngle * Math.PI / 180)
    const y = cy + radius * Math.sin(-midAngle * Math.PI / 180)

    return (
      <text
        x={x}
        y={y}
        fill="#ffffff"
        textAnchor={x > cx ? 'start' : 'end'}
        dominantBaseline="central"
        className="font-bold text-sm drop-shadow-lg"
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-effect rounded-xl p-6"
    >
      <h3 className="text-xl font-bold mb-4 text-gray-800">Distribución de Productos</h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={renderCustomLabel}
            outerRadius={100}
            fill="#8884d8"
            dataKey="value"
            animationBegin={0}
            animationDuration={800}
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ color: '#374151' }}
            iconType="circle"
          />
        </PieChart>
      </ResponsiveContainer>

      {/* Stats below chart */}
      <div className="grid grid-cols-3 gap-4 mt-6 pt-6 border-t border-gray-200">
        {data.map((item, index) => (
          <div key={item.name} className="text-center">
            <div
              className="w-3 h-3 rounded-full mx-auto mb-2"
              style={{ backgroundColor: COLORS[index] }}
            />
            <p className="text-xs text-gray-600 mb-1 font-medium">{item.name}</p>
            <p className="text-lg font-bold" style={{ color: COLORS[index] }}>
              {item.value.toLocaleString('es-MX')}
            </p>
          </div>
        ))}
      </div>
    </motion.div>
  )
}
