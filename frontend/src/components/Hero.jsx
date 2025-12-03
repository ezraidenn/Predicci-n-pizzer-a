import { motion } from 'framer-motion'
import { TrendingUp, BarChart3, Brain, Sparkles } from 'lucide-react'

export default function Hero() {
  const features = [
    {
      icon: TrendingUp,
      title: 'Predicciones Precisas',
      description: 'Algoritmos de ML entrenados con tus datos históricos'
    },
    {
      icon: BarChart3,
      title: 'Visualización Intuitiva',
      description: 'Gráficos interactivos y KPIs en tiempo real'
    },
    {
      icon: Brain,
      title: 'Insights con IA',
      description: 'Análisis automático con GPT para decisiones inteligentes'
    },
    {
      icon: Sparkles,
      title: 'Interfaz Moderna',
      description: 'Diseño elegante y experiencia de usuario fluida'
    }
  ]

  return (
    <div className="min-h-[80vh] flex items-center justify-center">
      <div className="max-w-5xl mx-auto text-center">
        {/* Hero Title */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <h1 className="text-6xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-gray-900 via-primary-600 to-gray-900 bg-clip-text text-transparent">
            Predicción de Ventas
            <br />
            Inteligente
          </h1>
          <p className="text-xl md:text-2xl text-gray-600 mb-12 max-w-3xl mx-auto">
            Analiza tus ventas diarias y predice tu futuro con IA.
            <br />
            Toma decisiones basadas en datos, no en intuición.
          </p>
        </motion.div>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="mb-16"
        >
          <div className="inline-flex items-center gap-2 px-6 py-3 bg-primary/10 border border-primary/30 rounded-full text-primary">
            <Sparkles className="w-5 h-5" />
            <span className="font-semibold">Haz clic en "Subir Excel" para comenzar</span>
          </div>
        </motion.div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 + index * 0.1 }}
              className="glass-effect rounded-xl p-6 hover:border-primary/50 transition-all duration-300"
            >
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4 mx-auto">
                <feature.icon className="w-6 h-6 text-primary" />
              </div>
              <h3 className="font-semibold mb-2 text-gray-800">{feature.title}</h3>
              <p className="text-sm text-gray-600">{feature.description}</p>
            </motion.div>
          ))}
        </div>

        {/* Animated Background Elements */}
        <div className="absolute inset-0 -z-10 overflow-hidden pointer-events-none">
          <motion.div
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.1, 0.2, 0.1],
            }}
            transition={{
              duration: 8,
              repeat: Infinity,
              ease: "easeInOut"
            }}
            className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-3xl"
          />
          <motion.div
            animate={{
              scale: [1.2, 1, 1.2],
              opacity: [0.1, 0.2, 0.1],
            }}
            transition={{
              duration: 10,
              repeat: Infinity,
              ease: "easeInOut"
            }}
            className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl"
          />
        </div>
      </div>
    </div>
  )
}
