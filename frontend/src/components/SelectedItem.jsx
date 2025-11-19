function SelectedItem({ selected, justification, onOptimize }) {
  if (!selected) return null

  return (
    <div className="card bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200">
      <div className="flex items-start gap-4">
        <div className="flex-shrink-0 bg-green-500 text-white rounded-full p-3">
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>

        <div className="flex-1">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-gray-900">Selected Item</h2>
            <div className="flex gap-2 items-center">
              <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-semibold">
                Score: {selected.score?.toFixed(4)}
              </span>
              {onOptimize && (
                <button
                  onClick={onOptimize}
                  className="bg-gradient-to-r from-green-600 to-emerald-600 text-white px-4 py-1 rounded-full text-sm font-semibold hover:from-green-700 hover:to-emerald-700 transition-all"
                >
                  💰 Optimize Cost
                </button>
              )}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <p className="text-sm text-gray-600">Item ID</p>
              <p className="text-lg font-semibold text-gray-900">{selected.id}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Vendor</p>
              <p className="text-lg font-semibold text-gray-900">{selected.vendor}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Price</p>
              <p className="text-lg font-semibold text-gray-900">${selected.price.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Lead Time</p>
              <p className="text-lg font-semibold text-gray-900">{selected.lead_time_days} days</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Reliability</p>
              <p className="text-lg font-semibold text-gray-900">{(selected.reliability * 100).toFixed(1)}%</p>
            </div>
            {selected.specs && (
              <div>
                <p className="text-sm text-gray-600">Specifications</p>
                <div className="text-sm font-medium text-gray-900">
                  {Object.entries(selected.specs).map(([key, value]) => (
                    <div key={key}>{key}: {value}</div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {justification && (
            <div className="bg-white rounded-lg p-4 border border-green-200">
              <h3 className="font-semibold text-gray-900 mb-2">AI Justification</h3>
              <p className="text-gray-700 leading-relaxed">{justification}</p>
            </div>
          )}

          {selected.tools && (
            <div className="mt-4 space-y-3">
              <h3 className="font-semibold text-gray-900">Investigation Results</h3>

              {selected.tools.price_history && (
                <div className="bg-white rounded-lg p-4 border border-gray-200">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Price History</h4>
                  <div className="space-y-1">
                    {selected.tools.price_history.history.slice(-3).map((entry, idx) => (
                      <div key={idx} className="flex justify-between text-sm">
                        <span className="text-gray-600">{entry.date}</span>
                        <span className="font-medium text-gray-900">${entry.price}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {selected.tools.availability && (
                <div className="bg-white rounded-lg p-4 border border-gray-200">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Vendor Availability</h4>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-gray-600">Avg Lead Time:</span>
                      <span className="font-medium text-gray-900 ml-1">
                        {selected.tools.availability.avg_lead_time_days} days
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-600">In Stock:</span>
                      <span className={`font-medium ml-1 ${selected.tools.availability.in_stock ? 'text-green-600' : 'text-red-600'}`}>
                        {selected.tools.availability.in_stock ? 'Yes' : 'No'}
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default SelectedItem
