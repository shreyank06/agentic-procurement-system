import { useState } from 'react'

function RequestForm({ components, vendors, onSubmit, onReset, loading }) {
  const [formData, setFormData] = useState({
    component: '',
    spec_filters: {},
    max_cost: '',
    latest_delivery_days: '',
    weights: {
      price: 0.4,
      lead_time: 0.3,
      reliability: 0.3
    },
    top_k: 3,
    investigate: false,
    negotiate: false,
    llm_provider: 'mock',
    api_key: ''
  })

  const [specKey, setSpecKey] = useState('')
  const [specValue, setSpecValue] = useState('')

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleWeightChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      weights: {
        ...prev.weights,
        [name]: parseFloat(value) || 0
      }
    }))
  }

  const handleAddSpec = () => {
    if (specKey && specValue) {
      setFormData(prev => ({
        ...prev,
        spec_filters: {
          ...prev.spec_filters,
          [specKey]: parseFloat(specValue)
        }
      }))
      setSpecKey('')
      setSpecValue('')
    }
  }

  const handleRemoveSpec = (key) => {
    setFormData(prev => {
      const newSpecs = { ...prev.spec_filters }
      delete newSpecs[key]
      return { ...prev, spec_filters: newSpecs }
    })
  }

  const handleSubmit = (e) => {
    e.preventDefault()

    const requestData = {
      ...formData,
      max_cost: formData.max_cost ? parseFloat(formData.max_cost) : null,
      latest_delivery_days: formData.latest_delivery_days ? parseInt(formData.latest_delivery_days) : null,
      top_k: parseInt(formData.top_k)
    }

    onSubmit(requestData)
  }

  const handleReset = () => {
    setFormData({
      component: '',
      spec_filters: {},
      max_cost: '',
      latest_delivery_days: '',
      weights: { price: 0.4, lead_time: 0.3, reliability: 0.3 },
      top_k: 3,
      investigate: false,
      negotiate: false,
      llm_provider: 'mock',
      api_key: ''
    })
    onReset()
  }

  return (
    <div className="card sticky top-8">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Procurement Request</h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Component Selection */}
        <div>
          <label className="label">Component Type *</label>
          <select
            name="component"
            value={formData.component}
            onChange={handleChange}
            required
            className="input-field"
          >
            <option value="">Select a component...</option>
            {components.map(comp => (
              <option key={comp} value={comp}>{comp.replace('_', ' ')}</option>
            ))}
          </select>
        </div>

        {/* Spec Filters */}
        <div>
          <label className="label">Technical Specifications</label>
          <div className="space-y-2">
            {Object.entries(formData.spec_filters).map(([key, value]) => (
              <div key={key} className="flex items-center gap-2 bg-blue-50 px-3 py-2 rounded-lg">
                <span className="flex-1 text-sm font-medium text-gray-700">
                  {key}: ≥ {value}
                </span>
                <button
                  type="button"
                  onClick={() => handleRemoveSpec(key)}
                  className="text-red-600 hover:text-red-800"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))}

            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Spec name (e.g., power_w)"
                value={specKey}
                onChange={(e) => setSpecKey(e.target.value)}
                className="input-field flex-1"
              />
              <input
                type="number"
                placeholder="Min value"
                value={specValue}
                onChange={(e) => setSpecValue(e.target.value)}
                className="input-field w-24"
              />
              <button
                type="button"
                onClick={handleAddSpec}
                className="btn-secondary"
              >
                +
              </button>
            </div>
          </div>
        </div>

        {/* Constraints */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="label">Max Cost ($)</label>
            <input
              type="number"
              name="max_cost"
              value={formData.max_cost}
              onChange={handleChange}
              placeholder="6000"
              className="input-field"
            />
          </div>
          <div>
            <label className="label">Max Delivery (days)</label>
            <input
              type="number"
              name="latest_delivery_days"
              value={formData.latest_delivery_days}
              onChange={handleChange}
              placeholder="30"
              className="input-field"
            />
          </div>
        </div>

        {/* Weights */}
        <div>
          <label className="label">Scoring Weights</label>
          <div className="space-y-3">
            {Object.entries(formData.weights).map(([key, value]) => (
              <div key={key}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-700 capitalize">{key.replace('_', ' ')}</span>
                  <span className="font-medium text-gray-900">{value}</span>
                </div>
                <input
                  type="range"
                  name={key}
                  min="0"
                  max="1"
                  step="0.1"
                  value={value}
                  onChange={handleWeightChange}
                  className="w-full"
                />
              </div>
            ))}
          </div>
        </div>

        {/* Options */}
        <div>
          <label className="label">Options</label>
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <input
                type="number"
                name="top_k"
                min="1"
                max="10"
                value={formData.top_k}
                onChange={handleChange}
                className="input-field w-20"
              />
              <span className="text-sm text-gray-700">Top candidates to show</span>
            </div>

            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                name="investigate"
                checked={formData.investigate}
                onChange={handleChange}
                className="w-4 h-4 text-blue-600 rounded"
              />
              <span className="text-sm text-gray-700">Enable tool investigation</span>
            </label>

            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                name="negotiate"
                checked={formData.negotiate}
                onChange={handleChange}
                className="w-4 h-4 text-blue-600 rounded"
              />
              <span className="text-sm text-gray-700">Run negotiation</span>
            </label>

            <select
              name="llm_provider"
              value={formData.llm_provider}
              onChange={handleChange}
              className="input-field"
            >
              <option value="mock">Mock LLM (Offline)</option>
              <option value="openai">OpenAI</option>
            </select>

            {formData.llm_provider === 'openai' && (
              <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-xs text-blue-700">
                  Using OpenAI API key from server environment configuration.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3 pt-4">
          <button
            type="submit"
            disabled={loading || !formData.component}
            className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Processing...' : 'Run Procurement'}
          </button>
          <button
            type="button"
            onClick={handleReset}
            className="btn-secondary"
            disabled={loading}
          >
            Reset
          </button>
        </div>
      </form>
    </div>
  )
}

export default RequestForm
