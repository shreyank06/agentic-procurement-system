import { useState, useEffect } from 'react'
import axios from 'axios'
import RequestForm from './components/RequestForm'
import CandidatesList from './components/CandidatesList'
import SelectedItem from './components/SelectedItem'
import ExecutionTrace from './components/ExecutionTrace'
import MetricsPanel from './components/MetricsPanel'
import NegotiationPanel from './components/NegotiationPanel'
import InteractiveCostChat from './components/InteractiveCostChat'
import InteractiveNegotiationChat from './components/InteractiveNegotiationChat'

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
  const [activeChat, setActiveChat] = useState(null)  // 'cost' or 'negotiation'
  const [error, setError] = useState(null)
  const [currentStep, setCurrentStep] = useState('form')  // 'form', 'results', 'analysis'
  const [sidebarOpen, setSidebarOpen] = useState(true)

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
    setCurrentStep('results')

    try {
      const response = await axios.post(`${API_BASE}/api/procurement`, requestData)
      setResult(response.data)

      // If negotiate is enabled, run negotiation
      if (requestData.negotiate && response.data.selected) {
        const negResponse = await axios.post(`${API_BASE}/api/negotiate/start`, {
          selected_item: response.data.selected,
          request: response.data.request,
          llm_provider: requestData.llm_provider,
          api_key: requestData.api_key
        })
        setNegotiation(negResponse.data)
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'An error occurred')
      setCurrentStep('form')
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setResult(null)
    setNegotiation(null)
    setActiveChat(null)
    setError(null)
    setCurrentStep('form')
  }

  const handleCostOptimize = () => {
    setActiveChat('cost')
  }

  const handleNegotiate = () => {
    setActiveChat('negotiation')
  }

  const handleCloseChat = () => {
    setActiveChat(null)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Header */}
      <header className="bg-white/95 backdrop-blur shadow-lg border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600">
                <span className="text-white text-xl font-bold">⚡</span>
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  Procurement Agent
                </h1>
                <p className="text-gray-600 text-sm mt-0.5">
                  AI-powered hardware procurement system
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 bg-green-50 px-4 py-2 rounded-lg border border-green-200">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm font-medium text-green-700">System Active</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Step Indicator */}
        {result && (
          <div className="mb-8">
            <div className="flex justify-between items-center">
              <div className={`flex items-center gap-3 p-4 rounded-lg transition-all ${currentStep === 'form' ? 'bg-blue-100 border border-blue-300' : 'bg-white/80 border border-gray-200'}`}>
                <div className={`flex items-center justify-center w-8 h-8 rounded-full font-bold ${currentStep === 'form' || result ? 'bg-green-500 text-white' : 'bg-gray-300 text-white'}`}>✓</div>
                <span className="font-medium text-gray-900">Search Results</span>
              </div>
              <div className="flex-1 h-1 mx-4 bg-gradient-to-r from-green-500 to-blue-500 rounded"></div>
              <div className={`flex items-center gap-3 p-4 rounded-lg transition-all ${activeChat === 'cost' || activeChat === 'negotiation' ? 'bg-blue-100 border border-blue-300' : 'bg-white/80 border border-gray-200'}`}>
                <div className={`flex items-center justify-center w-8 h-8 rounded-full font-bold ${activeChat ? 'bg-blue-500 text-white' : 'bg-gray-300 text-white'}`}>{activeChat ? '●' : '2'}</div>
                <span className="font-medium text-gray-900">Analysis</span>
              </div>
            </div>
          </div>
        )}

        {/* Error Alert */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 rounded-lg flex items-start gap-3">
            <svg className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" />
            </svg>
            <div>
              <h3 className="text-lg font-semibold text-red-900">Error</h3>
              <p className="text-red-700 text-sm mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="card bg-white/95 backdrop-blur p-12 text-center rounded-2xl shadow-2xl">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-blue-100 to-indigo-100 mb-6">
              <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-600 border-t-transparent"></div>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Analyzing Components...</h2>
            <p className="text-gray-600 text-sm max-w-md mx-auto">Evaluating options, comparing specifications, and calculating optimal solutions</p>
            <div className="mt-6 flex justify-center gap-1">
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{animationDelay: '0ms'}}></div>
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{animationDelay: '150ms'}}></div>
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{animationDelay: '300ms'}}></div>
            </div>
          </div>
        )}

        {/* Results View */}
        {result && !loading && (
          <>
            {/* Chat Views */}
            {activeChat === 'cost' ? (
              <InteractiveCostChat
                selected={result.selected}
                request={result.request}
                onClose={handleCloseChat}
              />
            ) : activeChat === 'negotiation' ? (
              <InteractiveNegotiationChat
                selected={result.selected}
                request={result.request}
                onClose={handleCloseChat}
              />
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left Sidebar - Navigation */}
                <div className="lg:col-span-1">
                  <div className="sticky top-8 space-y-4">
                    {/* Back Button */}
                    <button
                      onClick={handleReset}
                      className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-white/80 hover:bg-white border border-gray-200 hover:border-gray-300 transition text-gray-900 font-medium"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                      </svg>
                      New Search
                    </button>

                    {/* Selected Item Card */}
                    <SelectedItem
                      selected={result.selected}
                      justification={result.justification}
                      onOptimize={handleCostOptimize}
                      onNegotiate={handleNegotiate}
                    />
                  </div>
                </div>

                {/* Main Content */}
                <div className="lg:col-span-2 space-y-6">
                  {/* Candidates */}
                  <CandidatesList candidates={result.candidates} />

                  {/* Negotiation Panel */}
                  {negotiation && <NegotiationPanel negotiation={negotiation} />}

                  {/* Metrics */}
                  {result.metrics && <MetricsPanel metrics={result.metrics} />}

                  {/* Execution Trace */}
                  <ExecutionTrace trace={result.trace} />
                </div>
              </div>
            )}
          </>
        )}

        {/* Empty State */}
        {!result && !loading && !error && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Form */}
            <div className="lg:col-span-1">
              <RequestForm
                components={components}
                vendors={vendors}
                onSubmit={handleSubmit}
                onReset={handleReset}
                loading={loading}
              />
            </div>

            {/* Welcome Message */}
            <div className="lg:col-span-2">
              <div className="card bg-white/95 backdrop-blur p-12 rounded-2xl shadow-2xl text-center">
                <div className="inline-flex items-center justify-center w-24 h-24 rounded-full bg-gradient-to-br from-blue-100 to-indigo-100 mb-8">
                  <svg className="w-12 h-12 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <h2 className="text-3xl font-bold text-gray-900 mb-4">Smart Procurement</h2>
                <p className="text-gray-600 max-w-lg mx-auto mb-8 leading-relaxed">
                  Define your component requirements and let our AI analyze thousands of options. We'll find the optimal match based on your specifications, budget, and delivery timeline.
                </p>

                {/* Feature List */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-12">
                  <div className="p-4 rounded-lg bg-blue-50 border border-blue-200">
                    <div className="text-2xl mb-2">⚡</div>
                    <p className="font-semibold text-gray-900 mb-1">Fast Analysis</p>
                    <p className="text-sm text-gray-600">AI-powered evaluation in seconds</p>
                  </div>
                  <div className="p-4 rounded-lg bg-blue-50 border border-blue-200">
                    <div className="text-2xl mb-2">🎯</div>
                    <p className="font-semibold text-gray-900 mb-1">Accurate Matching</p>
                    <p className="text-sm text-gray-600">Find components that fit your needs</p>
                  </div>
                  <div className="p-4 rounded-lg bg-blue-50 border border-blue-200">
                    <div className="text-2xl mb-2">💬</div>
                    <p className="font-semibold text-gray-900 mb-1">Smart Negotiation</p>
                    <p className="text-sm text-gray-600">Dynamic vendor interaction</p>
                  </div>
                </div>

                {/* Steps */}
                <div className="mt-12 pt-8 border-t border-gray-200">
                  <p className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-6">How It Works</p>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div className="flex flex-col items-center">
                      <div className="flex items-center justify-center w-12 h-12 rounded-full bg-blue-600 text-white font-bold mb-3">1</div>
                      <p className="font-medium text-gray-900">Choose Component</p>
                      <p className="text-sm text-gray-600 mt-1">Select what you need</p>
                    </div>
                    <div className="flex flex-col items-center">
                      <div className="flex items-center justify-center w-12 h-12 rounded-full bg-indigo-600 text-white font-bold mb-3">2</div>
                      <p className="font-medium text-gray-900">Set Constraints</p>
                      <p className="text-sm text-gray-600 mt-1">Budget, specs, timeline</p>
                    </div>
                    <div className="flex flex-col items-center">
                      <div className="flex items-center justify-center w-12 h-12 rounded-full bg-purple-600 text-white font-bold mb-3">3</div>
                      <p className="font-medium text-gray-900">Get Results</p>
                      <p className="text-sm text-gray-600 mt-1">Ranked best options</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
