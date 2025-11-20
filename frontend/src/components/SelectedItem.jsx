function SelectedItem({ selected, justification, onOptimize, onNegotiate }) {
  if (!selected) return null

  return (
    <div className="space-y-4">
      {/* Header Card */}
      <div className="card bg-gradient-to-br from-green-50 to-emerald-50 border-l-4 border-green-500">
        <div className="flex items-start justify-between mb-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className="inline-flex items-center justify-center bg-green-500 text-white rounded-full w-10 h-10 font-bold text-lg">✓</span>
              <h2 className="text-3xl font-bold text-gray-900">Selected Item</h2>
            </div>
            <p className="text-sm text-gray-600">Highest scoring component based on your requirements</p>
          </div>
          <span className="bg-green-100 text-green-800 px-4 py-2 rounded-lg text-sm font-bold">
            Score: {selected.score?.toFixed(3)}
          </span>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-white rounded-lg p-3 border border-green-100">
            <p className="text-xs text-gray-600 font-semibold uppercase">Item</p>
            <p className="text-lg font-bold text-gray-900 mt-1">{selected.id}</p>
          </div>
          <div className="bg-white rounded-lg p-3 border border-green-100">
            <p className="text-xs text-gray-600 font-semibold uppercase">Vendor</p>
            <p className="text-lg font-bold text-gray-900 mt-1">{selected.vendor}</p>
          </div>
          <div className="bg-white rounded-lg p-3 border border-green-100">
            <p className="text-xs text-gray-600 font-semibold uppercase">Price</p>
            <p className="text-lg font-bold text-green-700 mt-1">${selected.price.toLocaleString()}</p>
          </div>
          <div className="bg-white rounded-lg p-3 border border-green-100">
            <p className="text-xs text-gray-600 font-semibold uppercase">Lead Time</p>
            <p className="text-lg font-bold text-gray-900 mt-1">{selected.lead_time_days}d</p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3 mt-4 pt-4 border-t border-green-200">
          {onOptimize && (
            <button
              onClick={onOptimize}
              className="flex-1 bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              <span>💰</span> Optimize Cost
            </button>
          )}
          {onNegotiate && (
            <button
              onClick={onNegotiate}
              className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              <span>🤝</span> Negotiate
            </button>
          )}
        </div>
      </div>

      {/* Details Grid */}
      <div className="card">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Details</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs text-gray-600 font-semibold uppercase mb-1">Reliability</p>
            <div className="flex items-center gap-2">
              <div className="flex-1 bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full"
                  style={{ width: `${selected.reliability * 100}%` }}
                ></div>
              </div>
              <span className="text-sm font-bold text-gray-900">{(selected.reliability * 100).toFixed(0)}%</span>
            </div>
          </div>
          <div>
            <p className="text-xs text-gray-600 font-semibold uppercase mb-1">Availability</p>
            <span className="inline-block bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-semibold">
              In Stock
            </span>
          </div>
        </div>

        {/* Specifications */}
        {selected.specs && (
          <div className="mt-6 pt-6 border-t border-gray-200">
            <p className="text-xs text-gray-600 font-semibold uppercase mb-3">Specifications</p>
            <div className="flex flex-wrap gap-2">
              {Object.entries(selected.specs).map(([key, value]) => (
                <span
                  key={key}
                  className="bg-blue-50 text-blue-700 px-3 py-1 rounded-full text-xs font-medium border border-blue-200"
                >
                  {key}: <strong>{value}</strong>
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Justification */}
      {justification && (
        <div className="card bg-blue-50 border-l-4 border-blue-500">
          <h3 className="text-lg font-bold text-gray-900 mb-3">Why This Component?</h3>
          <p className="text-gray-700 leading-relaxed">{justification}</p>
        </div>
      )}

      {/* Investigation Results */}
      {selected.tools && (
        <div className="card">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Market Analysis</h3>
          <div className="grid grid-cols-2 gap-4">
            {selected.tools.price_history && (
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="text-sm font-bold text-gray-900 mb-3">Recent Prices</h4>
                <div className="space-y-2">
                  {selected.tools.price_history.history.slice(-3).map((entry, idx) => (
                    <div key={idx} className="flex justify-between text-sm">
                      <span className="text-gray-600">{entry.date}</span>
                      <span className="font-semibold text-gray-900">${entry.price.toLocaleString()}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {selected.tools.availability && (
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="text-sm font-bold text-gray-900 mb-3">Vendor Info</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Avg Lead Time:</span>
                    <span className="font-semibold text-gray-900">{selected.tools.availability.avg_lead_time_days}d</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Stock Status:</span>
                    <span className={`font-semibold ${selected.tools.availability.in_stock ? 'text-green-600' : 'text-red-600'}`}>
                      {selected.tools.availability.in_stock ? '✓ In Stock' : '✗ Out of Stock'}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default SelectedItem
