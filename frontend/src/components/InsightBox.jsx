import { motion } from 'framer-motion'
import { Sparkles, Loader2 } from 'lucide-react'

export default function InsightBox({ insight, loading }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="glass-effect rounded-xl p-6 border-primary/20 glow-effect"
    >
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center flex-shrink-0">
          {loading ? (
            <Loader2 className="w-6 h-6 text-primary animate-spin" />
          ) : (
            <Sparkles className="w-6 h-6 text-primary" />
          )}
        </div>
        
        <div className="flex-1">
          <h3 className="text-lg font-bold mb-2 flex items-center gap-2">
            <span>Análisis Inteligente</span>
            <span className="text-xs px-2 py-1 bg-primary/20 text-primary rounded-full">
              GPT-4
            </span>
          </h3>
          
          {loading ? (
            <div className="space-y-2">
              <div className="h-4 bg-white/10 rounded animate-pulse w-full"></div>
              <div className="h-4 bg-white/10 rounded animate-pulse w-5/6"></div>
              <div className="h-4 bg-white/10 rounded animate-pulse w-4/6"></div>
            </div>
          ) : (
            <div className="text-gray-300 leading-relaxed whitespace-pre-line">
              {insight}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  )
}
