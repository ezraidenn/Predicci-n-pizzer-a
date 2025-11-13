import { useState, useCallback } from 'react'
import { Upload, Pizza, Loader2, RefreshCw } from 'lucide-react'
import { useDropzone } from 'react-dropzone'
import axios from 'axios'
import { motion, AnimatePresence } from 'framer-motion'

const API_URL = '/api'

export default function Navbar({ onDataUpdate, onPredictionsUpdate, onInsightUpdate, setLoading, setHasHistoricalData }) {
  const [uploading, setUploading] = useState(false)
  const [retraining, setRetraining] = useState(false)
  const [showDropzone, setShowDropzone] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return

    const file = acceptedFiles[0]
    setUploading(true)
    setLoading(true)
    setUploadProgress(0)

    try {
      // 1. Subir archivo
      const formData = new FormData()
      formData.append('file', file)

      setUploadProgress(25)
      const uploadResponse = await axios.post(`${API_URL}/upload_excel`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      // Cargar datos históricos completos
      const historicalResponse = await axios.get(`${API_URL}/historical`)
      onDataUpdate(historicalResponse.data)
      setHasHistoricalData(true)
      
      // Mostrar mensaje si hay duplicados
      if (uploadResponse.data.message && uploadResponse.data.message.includes('duplicadas')) {
        alert(uploadResponse.data.message)
      }
      
      setUploadProgress(50)

      // 2. Entrenar modelos
      await axios.post(`${API_URL}/train_model`)
      setUploadProgress(75)

      // 3. Obtener predicciones
      const predResponse = await axios.get(`${API_URL}/predict?days=7`)
      onPredictionsUpdate(predResponse.data.predictions)
      setUploadProgress(90)

      // 4. Generar insights
      const insightResponse = await axios.post(`${API_URL}/insight`)
      onInsightUpdate(insightResponse.data.insight)
      setUploadProgress(100)

      setShowDropzone(false)
    } catch (error) {
      console.error('Error procesando archivo:', error)
      alert('Error procesando archivo: ' + (error.response?.data?.detail || error.message))
    } finally {
      setUploading(false)
      setLoading(false)
      setTimeout(() => setUploadProgress(0), 1000)
    }
  }, [onDataUpdate, onPredictionsUpdate, onInsightUpdate, setLoading])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls']
    },
    maxFiles: 1,
    disabled: uploading
  })

  const handleRetrain = async () => {
    if (retraining) return
    
    const confirmed = window.confirm(
      '¿Reentrenar el modelo con todos los datos actuales?\n\n' +
      'Esto aplicará las últimas optimizaciones y mejoras de tendencia.\n' +
      'Tomará aproximadamente 3-5 minutos.'
    )
    
    if (!confirmed) return
    
    setRetraining(true)
    setLoading(true)
    setUploadProgress(0)
    
    try {
      setUploadProgress(20)
      
      // 1. Entrenar modelos con datos existentes
      await axios.post(`${API_URL}/train_model`)
      setUploadProgress(70)
      
      // 2. Obtener nuevas predicciones
      const predResponse = await axios.get(`${API_URL}/predict?days=7`)
      onPredictionsUpdate(predResponse.data.predictions)
      setUploadProgress(90)
      
      // 3. Recargar datos históricos
      const historicalResponse = await axios.get(`${API_URL}/historical`)
      onDataUpdate(historicalResponse.data)
      
      setUploadProgress(100)
      
      alert('✅ Modelo reentrenado exitosamente!\n\nLas predicciones ahora reflejan las últimas optimizaciones.')
      
    } catch (error) {
      console.error('Error reentrenando:', error)
      alert('Error reentrenando modelo: ' + (error.response?.data?.detail || error.message))
    } finally {
      setRetraining(false)
      setLoading(false)
      setTimeout(() => setUploadProgress(0), 1000)
    }
  }

  return (
    <>
      <nav className="glass-effect border-b border-gray-200 sticky top-0 z-50 bg-white">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
                <Pizza className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-800">Pizzería MAX AI</h1>
                <p className="text-xs text-gray-600">Predicción Inteligente</p>
              </div>
            </div>

            {/* Buttons */}
            <div className="flex items-center gap-3">
              {/* Retrain Button */}
              <button
                onClick={handleRetrain}
                disabled={retraining || uploading}
                className="flex items-center gap-2 px-4 py-3 text-white font-semibold rounded-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl"
                style={{backgroundColor: retraining ? '#9ca3af' : '#2563eb'}}
                onMouseEnter={(e) => !retraining && !uploading && (e.currentTarget.style.backgroundColor = '#1d4ed8')}
                onMouseLeave={(e) => !retraining && !uploading && (e.currentTarget.style.backgroundColor = '#2563eb')}
                title="Reentrenar modelo con datos actuales"
              >
                {retraining ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Reentrenando...
                  </>
                ) : (
                  <>
                    <RefreshCw className="w-5 h-5" />
                    Reentrenar
                  </>
                )}
              </button>

              {/* Upload Button */}
              <button
                onClick={() => setShowDropzone(true)}
                disabled={uploading || retraining}
                className="flex items-center gap-2 px-6 py-3 text-white font-semibold rounded-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl"
                style={{backgroundColor: uploading ? '#9ca3af' : '#16a34a'}}
                onMouseEnter={(e) => !uploading && !retraining && (e.currentTarget.style.backgroundColor = '#15803d')}
                onMouseLeave={(e) => !uploading && !retraining && (e.currentTarget.style.backgroundColor = '#16a34a')}
              >
                {uploading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Procesando...
                  </>
                ) : (
                  <>
                    <Upload className="w-5 h-5" />
                    Subir Excel
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Progress Bar */}
          {uploadProgress > 0 && uploadProgress < 100 && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="mt-4"
            >
              <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                <motion.div
                  className="h-full bg-primary-600"
                  initial={{ width: 0 }}
                  animate={{ width: `${uploadProgress}%` }}
                  transition={{ duration: 0.3 }}
                />
              </div>
              <p className="text-xs text-gray-600 mt-2 text-center">
                {retraining ? (
                  <>
                    {uploadProgress < 30 && 'Preparando reentrenamiento...'}
                    {uploadProgress >= 30 && uploadProgress < 80 && 'Entrenando modelos con optimizaciones...'}
                    {uploadProgress >= 80 && 'Generando nuevas predicciones...'}
                  </>
                ) : (
                  <>
                    {uploadProgress < 30 && 'Subiendo archivo...'}
                    {uploadProgress >= 30 && uploadProgress < 60 && 'Procesando datos...'}
                    {uploadProgress >= 60 && uploadProgress < 85 && 'Entrenando modelos...'}
                    {uploadProgress >= 85 && 'Generando predicciones...'}
                  </>
                )}
              </p>
            </motion.div>
          )}
        </div>
      </nav>

      {/* Dropzone Modal */}
      <AnimatePresence>
        {showDropzone && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-gray-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => !uploading && setShowDropzone(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-2xl p-8 max-w-lg w-full shadow-2xl border border-gray-200">
              <h2 className="text-2xl font-bold mb-4 text-gray-800">Subir Archivo Excel</h2>
              <p className="text-gray-600 mb-6">
                Arrastra tu archivo Excel o haz clic para seleccionarlo
              </p>

              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all duration-300 ${
                  isDragActive
                    ? 'border-primary-600 bg-primary-50'
                    : 'border-gray-300 hover:border-primary-400 bg-gray-50'
                } ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <input {...getInputProps()} />
                <Upload className="w-16 h-16 mx-auto mb-4 text-primary-600" />
                {isDragActive ? (
                  <p className="text-primary-600 font-semibold">Suelta el archivo aquí...</p>
                ) : (
                  <>
                    <p className="text-gray-800 font-semibold mb-2">
                      Arrastra y suelta tu archivo Excel
                    </p>
                    <p className="text-gray-600 text-sm">
                      o haz clic para seleccionar (.xlsx, .xls)
                    </p>
                  </>
                )}
              </div>

              {!uploading && (
                <button
                  onClick={() => setShowDropzone(false)}
                  className="mt-6 w-full py-3 bg-gray-200 text-gray-800 font-semibold rounded-lg hover:bg-gray-300 transition-colors"
                >
                  Cancelar
                </button>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
