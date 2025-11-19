function MetricsPanel({ metrics }) {
  if (!metrics) return null

  return (
    <div className="card">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Performance Metrics</h2>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
          <p className="text-sm text-blue-600 font-medium mb-1">Total Latency</p>
          <p className="text-2xl font-bold text-blue-900">
            {metrics.total_latency?.toFixed(3)}s
          </p>
        </div>

        <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
          <p className="text-sm text-purple-600 font-medium mb-1">Candidates Found</p>
          <p className="text-2xl font-bold text-purple-900">
            {metrics.total_candidates}
          </p>
        </div>

        <div className="bg-green-50 rounded-lg p-4 border border-green-200">
          <p className="text-sm text-green-600 font-medium mb-1">Top K Selected</p>
          <p className="text-2xl font-bold text-green-900">
            {metrics.top_k_selected}
          </p>
        </div>

        <div className="bg-orange-50 rounded-lg p-4 border border-orange-200">
          <p className="text-sm text-orange-600 font-medium mb-1">After Filtering</p>
          <p className="text-2xl font-bold text-orange-900">
            {metrics.candidates_after_filtering}
          </p>
        </div>

        <div className="bg-indigo-50 rounded-lg p-4 border border-indigo-200">
          <p className="text-sm text-indigo-600 font-medium mb-1">Tools Called</p>
          <p className="text-2xl font-bold text-indigo-900">
            {metrics.tools_called}
          </p>
        </div>
      </div>

      {metrics.step_latencies && Object.keys(metrics.step_latencies).length > 0 && (
        <div>
          <h3 className="font-semibold text-gray-900 mb-3">Step Latencies</h3>
          <div className="space-y-2">
            {Object.entries(metrics.step_latencies).map(([step, latency]) => (
              <div key={step} className="flex items-center gap-3">
                <div className="flex-1">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm text-gray-700 capitalize">
                      {step.replace('_', ' ')}
                    </span>
                    <span className="text-sm font-medium text-gray-900">
                      {latency.toFixed(4)}s
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all"
                      style={{
                        width: `${(latency / metrics.total_latency) * 100}%`
                      }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default MetricsPanel
