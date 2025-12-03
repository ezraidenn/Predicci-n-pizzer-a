import { useState, useEffect } from 'react'
import axios from 'axios'
import Navbar from './components/Navbar'
import Hero from './components/Hero'
import Dashboard from './components/Dashboard'
import Analytics from './components/Analytics'
import Clientes from './components/Clientes'
import Reportes from './components/Reportes'
import { motion } from 'framer-motion'
import { BarChart3, Home, Users, FileText } from 'lucide-react'

const API_URL = '/api'

function App() {
  const [data, setData] = useState(null)
  const [predictions, setPredictions] = useState([])
  const [insight, setInsight] = useState('')
  const [loading, setLoading] = useState(false)
  const [hasHistoricalData, setHasHistoricalData] = useState(false)
  const [currentView, setCurrentView] = useState('dashboard') // 'dashboard', 'analytics', 'clientes', 'reportes'

  // Cargar datos históricos al iniciar
  useEffect(() => {
    const loadHistoricalData = async () => {
      try {
        const response = await axios.get(`${API_URL}/historical`)
        if (response.data.success && response.data.data.length > 0) {
          setData(response.data)
          setHasHistoricalData(true)
          
          // Cargar predicciones si hay datos
          try {
            const predResponse = await axios.get(`${API_URL}/predict?days=7`)
            setPredictions(predResponse.data.predictions)
          } catch (err) {
            console.log('No hay modelos entrenados aún')
          }
        }
      } catch (error) {
        console.log('No hay datos históricos aún')
      }
    }
    
    loadHistoricalData()
  }, [])

  return (
    <div className="min-h-screen gradient-bg">
      <Navbar 
        onDataUpdate={setData}
        onPredictionsUpdate={setPredictions}
        onInsightUpdate={setInsight}
        setLoading={setLoading}
        setHasHistoricalData={setHasHistoricalData}
      />
      
      <main className="container mx-auto px-4 py-8">
        {!data || !hasHistoricalData ? (
          <Hero />
        ) : (
          <>
            {/* Navigation Tabs */}
            <div className="flex flex-wrap gap-3 mb-6">
              <button
                onClick={() => setCurrentView('dashboard')}
                className={`flex items-center gap-2 px-5 py-2.5 rounded-lg font-semibold transition-all ${
                  currentView === 'dashboard'
                    ? 'bg-green-600 text-white shadow-lg'
                    : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
                }`}
              >
                <Home className="w-4 h-4" />
                Dashboard
              </button>
              <button
                onClick={() => setCurrentView('analytics')}
                className={`flex items-center gap-2 px-5 py-2.5 rounded-lg font-semibold transition-all ${
                  currentView === 'analytics'
                    ? 'bg-blue-600 text-white shadow-lg'
                    : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
                }`}
              >
                <BarChart3 className="w-4 h-4" />
                Análisis
              </button>
              <button
                onClick={() => setCurrentView('clientes')}
                className={`flex items-center gap-2 px-5 py-2.5 rounded-lg font-semibold transition-all ${
                  currentView === 'clientes'
                    ? 'bg-purple-600 text-white shadow-lg'
                    : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
                }`}
              >
                <Users className="w-4 h-4" />
                Clientes
              </button>
              <button
                onClick={() => setCurrentView('reportes')}
                className={`flex items-center gap-2 px-5 py-2.5 rounded-lg font-semibold transition-all ${
                  currentView === 'reportes'
                    ? 'bg-indigo-600 text-white shadow-lg'
                    : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
                }`}
              >
                <FileText className="w-4 h-4" />
                Reportes
              </button>
            </div>

            {/* Content */}
            <motion.div
              key={currentView}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              {currentView === 'dashboard' && (
                <Dashboard 
                  data={data}
                  predictions={predictions}
                  insight={insight}
                  loading={loading}
                />
              )}
              {currentView === 'analytics' && <Analytics />}
              {currentView === 'clientes' && <Clientes />}
              {currentView === 'reportes' && <Reportes />}
            </motion.div>
          </>
        )}
      </main>
    </div>
  )
}

export default App
