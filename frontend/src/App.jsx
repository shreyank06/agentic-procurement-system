import { useState, useEffect } from 'react'
import axios from 'axios'
import RequestForm from './components/RequestForm'
import CandidatesList from './components/CandidatesList'
import SelectedItem from './components/SelectedItem'
import ExecutionTrace from './components/ExecutionTrace'
import MetricsPanel from './components/MetricsPanel'
import NegotiationPanel from './components/NegotiationPanel'
import CostOptimizationPanel from './components/CostOptimizationPanel'

// Get API base URL - use env var if available, otherwise construct from current window location
const getAPIBase = () => {
  // For development
  if (import.meta.env.DEV) {
    return import.meta.env.VITE_API_URL || 'http://localhost:8000'
  }

  // For production on Render: if VITE_API_URL is set, use it
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
  }

  // Fallback: use the backend service URL based on current hostname
  // On Render, both services share the same domain/subdomain pattern
  const currentHost = window.location.hostname
  if (currentHost.includes('onrender.com')) {
    return `https://procurement-agent-api.onrender.com`
  }

  return 'http://localhost:8000'
}

const API_BASE = getAPIBase()

function App() {
  const [components, setComponents] = useState([])
  const [vendors, setVendors] = useState([])
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [negotiation, setNegotiation] = useState(null)
  const [costOptimization, setCostOptimization] = useState(null)
  const [error, setError] = useState(null)

  // Fetch available components and vendors on mount
  useEffect(() => {
    fetchCatalogData()
  }, [])

  const fetchCatalogData = async () => {
    try {
      const [compRes, vendorRes] = await Promise.all([
        axios.get(`${API_BASE}/api/catalog/components`),
        axios.get(`${API_BASE}/api/catalog/vendors`)
      ])
      setComponents(compRes.data.components)
      setVendors(vendorRes.data.vendors)
    } catch (err) {
      console.error('Failed to fetch catalog data:', err)
    }
  }

  const handleSubmit = async (requestData) => {
    setLoading(true)
    setError(null)
    setResult(null)
    setNegotiation(null)

    try {
      const response = await axios.post(`${API_BASE}/api/procurement`, requestData)
      setResult(response.data)

      // If negotiate is enabled, run negotiation
      if (requestData.negotiate && response.data.selected) {
        const negResponse = await axios.post(`${API_BASE}/api/negotiate`, {
          selected_item: response.data.selected,
          request: response.data.request
        })
        setNegotiation(negResponse.data)
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setResult(null)
    setNegotiation(null)
    setCostOptimization(null)
    setError(null)
  }

  const handleCostOptimize = () => {
    setCostOptimization(true)
  }

  const handleCloseCostOptimization = () => {
    setCostOptimization(null)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Procurement Agent System
              </h1>
              <p className="text-gray-600 mt-1">
                Intelligent hardware selection for mission-critical systems
              </p>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span>API Connected</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Request Form */}
          <div className="lg:col-span-1">
            <RequestForm
              components={components}
              vendors={vendors}
              onSubmit={handleSubmit}
              onReset={handleReset}
              loading={loading}
            />
          </div>

          {/* Right Column - Results */}
          <div className="lg:col-span-2 space-y-6">
            {error && (
              <div className="card bg-red-50 border border-red-200">
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0">
                    <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-red-900">Error</h3>
                    <p className="text-red-700 mt-1">{error}</p>
                  </div>
                </div>
              </div>
            )}

            {loading && (
              <div className="card text-center py-12">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent"></div>
                <p className="text-gray-600 mt-4">Processing procurement request...</p>
              </div>
            )}

            {result && !loading && (
              <>
                {/* Cost Optimization Panel */}
                {costOptimization ? (
                  <CostOptimizationPanel
                    selected={result.selected}
                    request={result.request}
                    onClose={handleCloseCostOptimization}
                  />
                ) : (
                  <>
                    {/* Selected Item */}
                    <SelectedItem
                      selected={result.selected}
                      justification={result.justification}
                      onOptimize={handleCostOptimize}
                    />

                    {/* Candidates List */}
                    <CandidatesList candidates={result.candidates} />

                    {/* Negotiation */}
                    {negotiation && <NegotiationPanel negotiation={negotiation} />}

                    {/* Execution Trace */}
                    <ExecutionTrace trace={result.trace} />

                    {/* Metrics */}
                    {result.metrics && <MetricsPanel metrics={result.metrics} />}
                  </>
                )}
              </>
            )}

            {!result && !loading && !error && (
              <div className="card text-center py-12">
                <svg className="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Results Yet</h3>
                <p className="text-gray-600">
                  Configure your procurement request and click "Run Procurement" to get started.
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
