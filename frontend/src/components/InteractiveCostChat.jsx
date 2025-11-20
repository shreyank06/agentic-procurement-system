import { useState, useRef, useEffect } from 'react'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function InteractiveCostChat({ selected, request, onClose }) {
  const [conversation, setConversation] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [userMessage, setUserMessage] = useState('')
  const [analysis, setAnalysis] = useState(null)
  const messagesEndRef = useRef(null)

  // Start analysis on mount
  useEffect(() => {
    startAnalysis()
  }, [])

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [conversation])

  const startAnalysis = async () => {
    setLoading(true)
    setError(null)

    try {
      console.log('Starting cost analysis with:', {
        selected_item: selected,
        llm_provider: 'openai',
        api_base: API_BASE
      })

      const response = await axios.post(`${API_BASE}/api/cost-optimize/start`, {
        selected_item: selected,
        request: request,
        llm_provider: 'openai',
        api_key: process.env.REACT_APP_OPENAI_API_KEY || ''
      })

      console.log('Analysis response:', response.data)
      setAnalysis(response.data.estimated_savings)
      setConversation(response.data.conversation)
    } catch (err) {
      let errorMsg = 'Unknown error'

      if (err.response?.data) {
        const detail = err.response.data.detail
        errorMsg = typeof detail === 'string' ? detail : JSON.stringify(detail)
      } else if (err.message) {
        errorMsg = err.message
      }

      console.error('Analysis error:', errorMsg, err)
      setError(`Error: ${errorMsg}`)
    } finally {
      setLoading(false)
    }
  }

  const sendMessage = async (e) => {
    e.preventDefault()
    if (!userMessage.trim()) return

    // Add user message to conversation
    const userMsg = { role: 'user', message: userMessage, timestamp: new Date().toISOString() }
    setConversation([...conversation, userMsg])
    setUserMessage('')
    setLoading(true)
    setError(null)

    try {
      const response = await axios.post(`${API_BASE}/api/cost-optimize/chat`, {
        user_message: userMessage,
        conversation: [...conversation, userMsg],
        selected_item: selected,
        request: request,
        llm_provider: 'openai',
        api_key: process.env.REACT_APP_OPENAI_API_KEY || ''
      })

      // Add agent response
      setConversation(prev => [...prev, {
        role: 'agent',
        message: response.data.message,
        timestamp: response.data.timestamp
      }])
    } catch (err) {
      let errorMsg = 'Unknown error'

      if (err.response?.data) {
        const detail = err.response.data.detail
        errorMsg = typeof detail === 'string' ? detail : JSON.stringify(detail)
      } else if (err.message) {
        errorMsg = err.message
      }

      console.error('Chat error:', errorMsg, err)
      setError(`Error: ${errorMsg}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card h-full flex flex-col bg-gradient-to-b from-white to-gray-50">
      <div className="flex items-center justify-between mb-6 pb-4 border-b-2 border-green-200">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <span>💰</span> Cost Optimization
          </h2>
          <p className="text-sm text-gray-600 mt-1">Explore ways to reduce costs</p>
        </div>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 hover:bg-gray-100 p-2 rounded-lg transition-colors"
          title="Close"
        >
          ✕
        </button>
      </div>

      {/* Savings Summary */}
      {analysis && (
        <div className="bg-gradient-to-r from-green-500 to-emerald-500 rounded-lg p-4 mb-6 text-white shadow-lg">
          <div className="grid grid-cols-2 gap-6">
            <div>
              <p className="text-green-100 text-sm font-semibold uppercase">Current Cost</p>
              <p className="text-3xl font-bold mt-2">${analysis.current_cost.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-green-100 text-sm font-semibold uppercase">Potential Savings</p>
              <p className="text-3xl font-bold mt-2">${analysis.total_potential_savings.toLocaleString()}</p>
              <p className="text-green-100 text-xs mt-1">{analysis.savings_percentage}% savings</p>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4 text-red-700 text-sm">
          {error}
        </div>
      )}

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto mb-4 space-y-4 min-h-[300px] px-2">
        {conversation.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl shadow-sm ${
                msg.role === 'user'
                  ? 'bg-green-600 text-white rounded-br-none'
                  : 'bg-white text-gray-900 rounded-bl-none border border-gray-200'
              }`}
            >
              <p className="text-sm leading-relaxed">{msg.message}</p>
              <p className={`text-xs mt-2 opacity-70`}>
                {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white text-gray-900 px-4 py-3 rounded-2xl rounded-bl-none border border-gray-200">
              <div className="flex gap-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <form onSubmit={sendMessage} className="flex gap-2 pt-4 border-t border-gray-200">
        <input
          type="text"
          value={userMessage}
          onChange={(e) => setUserMessage(e.target.value)}
          placeholder="Ask about cost reduction strategies..."
          disabled={loading}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50 bg-white"
        />
        <button
          type="submit"
          disabled={loading || !userMessage.trim()}
          className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed font-semibold transition-colors"
        >
          Send
        </button>
      </form>
    </div>
  )
}
