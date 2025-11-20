import { useState, useRef, useEffect } from 'react'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function InteractiveNegotiationChat({ selected, request, onClose }) {
  const [conversation, setConversation] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [userMessage, setUserMessage] = useState('')
  const [orderConfirmed, setOrderConfirmed] = useState(false)
  const [receipt, setReceipt] = useState(null)
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

      // Check if order was confirmed
      if (response.data.order_status === 'confirmed') {
        setOrderConfirmed(true)
        setReceipt(response.data.receipt)
      }
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

      {/* Receipt Display */}
      {orderConfirmed && receipt && (
        <div className="bg-gradient-to-b from-green-50 to-green-100 border-2 border-green-500 rounded-lg p-6 mb-4 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <span className="text-3xl">✓</span>
              <div>
                <h3 className="text-2xl font-bold text-green-900">Order Confirmed!</h3>
                <p className="text-sm text-green-700">Order #{receipt.order_number}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-4 space-y-3 mb-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs uppercase font-semibold text-gray-500">Item</p>
                <p className="text-lg font-bold text-gray-900">{receipt.item_id}</p>
                <p className="text-sm text-gray-600">{receipt.vendor}</p>
              </div>
              <div>
                <p className="text-xs uppercase font-semibold text-gray-500">Quantity</p>
                <p className="text-lg font-bold text-gray-900">{receipt.quantity} unit{receipt.quantity > 1 ? 's' : ''}</p>
              </div>
            </div>

            <hr className="border-gray-200" />

            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs uppercase font-semibold text-gray-500">Unit Price</p>
                <p className="text-lg font-bold text-blue-600">${receipt.unit_price.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-xs uppercase font-semibold text-gray-500">Total Price</p>
                <p className="text-lg font-bold text-green-600">${receipt.total_price.toLocaleString()}</p>
              </div>
            </div>

            <hr className="border-gray-200" />

            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs uppercase font-semibold text-gray-500">Lead Time</p>
                <p className="text-lg font-bold text-gray-900">{receipt.lead_time_days} days</p>
              </div>
              <div>
                <p className="text-xs uppercase font-semibold text-gray-500">Estimated Delivery</p>
                <p className="text-lg font-bold text-gray-900">{receipt.estimated_delivery}</p>
              </div>
            </div>

            <hr className="border-gray-200" />

            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs uppercase font-semibold text-gray-500">Order Date</p>
                <p className="text-sm text-gray-700">{receipt.order_date}</p>
              </div>
              <div>
                <p className="text-xs uppercase font-semibold text-gray-500">Reliability</p>
                <p className="text-sm text-gray-700">{(receipt.reliability * 100).toFixed(0)}%</p>
              </div>
            </div>
          </div>

          <div className="bg-green-100 border border-green-400 rounded-lg p-3 text-sm text-green-800">
            <p className="font-semibold">✓ Order successfully submitted!</p>
            <p className="mt-1">A confirmation email will be sent to you shortly with all order details.</p>
          </div>
        </div>
      )}

      {/* Input Area */}
      {!orderConfirmed && (
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
      )}

      {orderConfirmed && (
        <div className="pt-4 border-t border-gray-200 text-center">
          <button
            onClick={onClose}
            className="bg-green-600 hover:bg-green-700 text-white px-8 py-2 rounded-lg font-semibold transition-colors"
          >
            Done
          </button>
        </div>
      )}
    </div>
  )
}
