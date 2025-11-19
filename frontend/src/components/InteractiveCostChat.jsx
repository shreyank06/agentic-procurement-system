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
      const response = await axios.post(`${API_BASE}/api/cost-optimize/start`, {
        selected_item: selected,
        request: request
      })

      setAnalysis(response.data.estimated_savings)
      setConversation(response.data.conversation)
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
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
        llm_provider: 'mock'
      })

      // Add agent response
      setConversation(prev => [...prev, {
        role: 'agent',
        message: response.data.message,
        timestamp: response.data.timestamp
      }])
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card h-full flex flex-col">
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-gray-200">
        <h2 className="text-2xl font-bold text-gray-900">Cost Optimization Agent</h2>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 text-xl font-bold"
        >
          ✕
        </button>
      </div>

      {/* Savings Summary */}
      {analysis && (
        <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-4 mb-6 border border-green-200">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-green-700 font-semibold">Current Cost</p>
              <p className="text-lg font-bold text-green-900">${analysis.current_cost}</p>
            </div>
            <div>
              <p className="text-green-700 font-semibold">Potential Savings</p>
              <p className="text-lg font-bold text-emerald-600">${analysis.total_potential_savings}</p>
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
      <div className="flex-1 overflow-y-auto mb-4 space-y-4 min-h-[300px]">
        {conversation.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${
                msg.role === 'user'
                  ? 'bg-blue-500 text-white rounded-br-none'
                  : 'bg-gray-100 text-gray-900 rounded-bl-none'
              }`}
            >
              <p className="text-sm leading-relaxed">{msg.message}</p>
              <p className={`text-xs mt-1 ${msg.role === 'user' ? 'text-blue-100' : 'text-gray-500'}`}>
                {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-900 px-4 py-3 rounded-lg rounded-bl-none">
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
          placeholder="Ask about cost optimization strategies..."
          disabled={loading}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={loading || !userMessage.trim()}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-semibold transition-colors"
        >
          Send
        </button>
      </form>
    </div>
  )
}
