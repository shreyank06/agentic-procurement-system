import { useState, useRef, useEffect } from 'react'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function InteractiveNegotiationChat({ selected, request, onClose }) {
  const [conversation, setConversation] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [userMessage, setUserMessage] = useState('')
  const messagesEndRef = useRef(null)

  // Start negotiation on mount
  useEffect(() => {
    startNegotiation()
  }, [])

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [conversation])

  const startNegotiation = async () => {
    setLoading(true)
    setError(null)

    try {
      console.log('Starting negotiation with:', {
        selected_item: selected,
        llm_provider: 'openai',
        api_base: API_BASE
      })

      const response = await axios.post(`${API_BASE}/api/negotiate/start`, {
        selected_item: selected,
        request: request,
        llm_provider: 'openai',
        api_key: process.env.REACT_APP_OPENAI_API_KEY || ''
      })

      console.log('Negotiation response:', response.data)
      setConversation(response.data.conversation)
    } catch (err) {
      let errorMsg = 'Unknown error'

      if (err.response?.data) {
        const detail = err.response.data.detail
        errorMsg = typeof detail === 'string' ? detail : JSON.stringify(detail)
      } else if (err.message) {
        errorMsg = err.message
      }

      console.error('Negotiation error:', errorMsg, err)
      setError(`Error: ${errorMsg}`)
    } finally {
      setLoading(false)
    }
  }

  const sendMessage = async (e) => {
    e.preventDefault()
    if (!userMessage.trim()) return

    // Add user message to conversation
    const userMsg = { role: 'buyer', message: userMessage, timestamp: new Date().toISOString() }
    setConversation([...conversation, userMsg])
    setUserMessage('')
    setLoading(true)
    setError(null)

    try {
      const response = await axios.post(`${API_BASE}/api/negotiate/chat`, {
        user_message: userMessage,
        conversation: [...conversation, userMsg],
        selected_item: selected,
        request: request,
        llm_provider: 'openai',
        api_key: process.env.REACT_APP_OPENAI_API_KEY || ''
      })

      // Add vendor response
      setConversation(prev => [...prev, {
        role: 'vendor',
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

      console.error('Negotiation chat error:', errorMsg, err)
      setError(`Error: ${errorMsg}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card h-full flex flex-col">
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-gray-200">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Vendor Negotiation</h2>
          <p className="text-sm text-gray-600 mt-1">
            Negotiating with <span className="font-semibold">{selected.vendor}</span> for {selected.id}
          </p>
        </div>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 text-xl font-bold"
        >
          ✕
        </button>
      </div>

      {/* Item Summary */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 mb-6 border border-blue-200">
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div>
            <p className="text-blue-700 font-semibold">Current Price</p>
            <p className="text-lg font-bold text-blue-900">${selected.price}</p>
          </div>
          <div>
            <p className="text-blue-700 font-semibold">Lead Time</p>
            <p className="text-lg font-bold text-blue-900">{selected.lead_time_days} days</p>
          </div>
          <div>
            <p className="text-blue-700 font-semibold">Reliability</p>
            <p className="text-lg font-bold text-blue-900">{(selected.reliability * 100).toFixed(1)}%</p>
          </div>
        </div>
      </div>

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
            className={`flex ${msg.role === 'buyer' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${
                msg.role === 'buyer'
                  ? 'bg-indigo-500 text-white rounded-br-none'
                  : 'bg-amber-50 text-gray-900 border border-amber-200 rounded-bl-none'
              }`}
            >
              <p className={`text-xs font-semibold mb-1 ${msg.role === 'buyer' ? 'text-indigo-100' : 'text-amber-700'}`}>
                {msg.role === 'buyer' ? 'You' : 'Vendor'}
              </p>
              <p className="text-sm leading-relaxed">{msg.message}</p>
              <p className={`text-xs mt-1 ${msg.role === 'buyer' ? 'text-indigo-100' : 'text-amber-600'}`}>
                {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-amber-50 text-gray-900 px-4 py-3 rounded-lg rounded-bl-none border border-amber-200">
              <div className="flex gap-2">
                <div className="w-2 h-2 bg-amber-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-amber-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-amber-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
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
          placeholder="Make an offer or ask a question..."
          disabled={loading}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={loading || !userMessage.trim()}
          className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed font-semibold transition-colors"
        >
          Send
        </button>
      </form>
    </div>
  )
}
