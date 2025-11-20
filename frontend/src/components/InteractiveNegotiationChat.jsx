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
    <div className="card h-full flex flex-col bg-gradient-to-b from-white to-gray-50">
      <div className="flex items-center justify-between mb-6 pb-4 border-b-2 border-blue-200">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <span>🤝</span> Vendor Negotiation
          </h2>
          <p className="text-sm text-gray-600 mt-1">
            Negotiate terms with <span className="font-semibold">{selected.vendor}</span>
          </p>
        </div>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 hover:bg-gray-100 p-2 rounded-lg transition-colors"
          title="Close"
        >
          ✕
        </button>
      </div>

      {/* Item Summary */}
      <div className="bg-gradient-to-r from-blue-500 to-indigo-500 rounded-lg p-4 mb-6 text-white shadow-lg">
        <p className="text-xs font-semibold uppercase text-blue-100 mb-3">{selected.id} • {selected.vendor}</p>
        <div className="grid grid-cols-3 gap-6 text-sm">
          <div>
            <p className="text-blue-100 text-xs uppercase font-semibold">Price</p>
            <p className="text-2xl font-bold mt-1">${selected.price.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-blue-100 text-xs uppercase font-semibold">Lead Time</p>
            <p className="text-2xl font-bold mt-1">{selected.lead_time_days}d</p>
          </div>
          <div>
            <p className="text-blue-100 text-xs uppercase font-semibold">Reliability</p>
            <p className="text-2xl font-bold mt-1">{(selected.reliability * 100).toFixed(0)}%</p>
          </div>
        </div>
      </div>

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
            className={`flex ${msg.role === 'buyer' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl shadow-sm ${
                msg.role === 'buyer'
                  ? 'bg-blue-600 text-white rounded-br-none'
                  : 'bg-white text-gray-900 border border-gray-200 rounded-bl-none'
              }`}
            >
              <p className={`text-xs font-semibold mb-2 uppercase opacity-70`}>
                {msg.role === 'buyer' ? 'You' : 'Vendor'}
              </p>
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
          placeholder="Make an offer or ask a question..."
          disabled={loading}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 bg-white"
        />
        <button
          type="submit"
          disabled={loading || !userMessage.trim()}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed font-semibold transition-colors"
        >
          Send
        </button>
      </form>
    </div>
  )
}
