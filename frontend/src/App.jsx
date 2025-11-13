import { useState, useEffect } from 'react'
import axios from 'axios'
import Navbar from './components/Navbar'
import Hero from './components/Hero'
import Dashboard from './components/Dashboard'
import Analytics from './components/Analytics'
import { motion } from 'framer-motion'
import { BarChart3, Home } from 'lucide-react'

const API_URL = '/api'

function App() {
  const [data, setData] = useState(null)
  const [predictions, setPredictions] = useState([])
  const [insight, setInsight] = useState('')
  const [loading, setLoading] = useState(false)
  const [hasHistoricalData, setHasHistoricalData] = useState(false)
  const [currentView, setCurrentView] = useState('dashboard') // 'dashboard' o 'analytics'

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
            <div className="flex gap-4 mb-6">
              <button
                onClick={() => setCurrentView('dashboard')}
                className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all ${
                  currentView === 'dashboard'
                    ? 'text-white shadow-lg'
                    : 'bg-white text-gray-700 hover:bg-gray-100 border-2 border-gray-300'
                }`}
                style={currentView === 'dashboard' ? {backgroundColor: '#16a34a'} : {}}
              >
                <Home className="w-5 h-5" />
                Dashboard
              </button>
              <button
                onClick={() => setCurrentView('analytics')}
                className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all ${
                  currentView === 'analytics'
                    ? 'text-white shadow-lg'
                    : 'bg-white text-gray-700 hover:bg-gray-100 border-2 border-gray-300'
                }`}
                style={currentView === 'analytics' ? {backgroundColor: '#16a34a'} : {}}
              >
                <BarChart3 className="w-5 h-5" />
                Análisis Detallado
              </button>
            </div>

            {/* Content */}
            <motion.div
              key={currentView}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              {currentView === 'dashboard' ? (
                <Dashboard 
                  data={data}
                  predictions={predictions}
                  insight={insight}
                  loading={loading}
                />
              ) : (
                <Analytics />
              )}
            </motion.div>
          </>
        )}
      </main>
    </div>
  )
}

export default App
