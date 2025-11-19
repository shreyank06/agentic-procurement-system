import { useState } from 'react'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function CostOptimizationPanel({ selected, request, onClose }) {
  const [loading, setLoading] = useState(false)
  const [discussion, setDiscussion] = useState(null)
  const [error, setError] = useState(null)

  const handleOptimize = async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await axios.post(`${API_BASE}/api/cost-optimize`, {
        selected_item: selected,
        request: request
      })

      setDiscussion(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to run cost optimization')
    } finally {
      setLoading(false)
    }
  }

  if (!selected) {
    return null
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Cost Optimization Analysis</h2>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 text-xl font-bold"
        >
          ✕
        </button>
      </div>

      {!discussion ? (
        <div className="space-y-4">
          <p className="text-gray-600">
            Launch a multi-agent discussion to explore cost optimization strategies for{' '}
            <span className="font-semibold">{selected.id}</span> from{' '}
            <span className="font-semibold">{selected.vendor}</span> (${selected.price})
          </p>

          <p className="text-sm text-gray-500">
            Four specialized agents will discuss:
          </p>
          <ul className="space-y-2 ml-4 text-sm text-gray-600">
            <li>💰 <strong>Cost Analyst:</strong> Cheaper alternatives and price opportunities</li>
            <li>📦 <strong>Supply Chain Manager:</strong> Bulk deals and long-term contracts</li>
            <li>📋 <strong>Requirements Engineer:</strong> Spec relaxation opportunities</li>
            <li>🚚 <strong>Logistics Officer:</strong> Delivery optimization strategies</li>
          </ul>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 text-sm">
              {error}
            </div>
          )}

          <button
            onClick={handleOptimize}
            disabled={loading}
            className="mt-6 w-full bg-gradient-to-r from-green-600 to-emerald-600 text-white font-semibold py-3 rounded-lg hover:from-green-700 hover:to-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            {loading ? 'Running analysis...' : 'Analyze Cost Optimization'}
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Savings Summary */}
          <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-6 border border-green-200">
            <h3 className="font-bold text-green-900 mb-4">Estimated Cost Savings</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-green-700">Current Cost</p>
                <p className="text-2xl font-bold text-green-900">
                  ${discussion.estimated_savings.current_cost}
                </p>
              </div>
              <div>
                <p className="text-sm text-green-700">After Optimization</p>
                <p className="text-2xl font-bold text-emerald-600">
                  ${discussion.estimated_savings.cost_after_optimization}
                </p>
              </div>
              <div>
                <p className="text-sm text-green-700">Total Potential Savings</p>
                <p className="text-2xl font-bold text-green-600">
                  ${discussion.estimated_savings.total_potential_savings}
                </p>
              </div>
              <div>
                <p className="text-sm text-green-700">Savings Percentage</p>
                <p className="text-2xl font-bold text-green-600">
                  {(
                    (discussion.estimated_savings.total_potential_savings /
                      discussion.estimated_savings.current_cost) *
                    100
                  ).toFixed(1)}
                  %
                </p>
              </div>
            </div>
          </div>

          {/* Discussion Thread */}
          <div className="space-y-4">
            <h3 className="font-bold text-gray-900">Multi-Agent Discussion</h3>
            {discussion.discussion.map((msg, idx) => (
              <div
                key={idx}
                className={`p-4 rounded-lg ${
                  msg.agent === 'Optimization Summary'
                    ? 'bg-blue-50 border border-blue-200'
                    : 'bg-gray-50 border border-gray-200'
                }`}
              >
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-12 h-12 rounded-full bg-gradient-to-br from-blue-400 to-purple-400 flex items-center justify-center text-white font-bold text-sm">
                    {msg.agent.charAt(0)}
                  </div>
                  <div className="flex-grow">
                    <h4 className="font-semibold text-gray-900">{msg.agent}</h4>
                    <p className="text-xs text-gray-500 mb-2">{msg.role}</p>
                    <p className="text-gray-700 text-sm leading-relaxed whitespace-pre-wrap">
                      {msg.message}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4">
            <button
              onClick={handleOptimize}
              disabled={loading}
              className="flex-1 bg-gradient-to-r from-green-600 to-emerald-600 text-white font-semibold py-2 rounded-lg hover:from-green-700 hover:to-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              Run Analysis Again
            </button>
            <button
              onClick={onClose}
              className="flex-1 bg-gray-200 text-gray-900 font-semibold py-2 rounded-lg hover:bg-gray-300 transition-all"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
