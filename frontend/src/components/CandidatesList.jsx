function CandidatesList({ candidates }) {
  if (!candidates || candidates.length === 0) return null

  return (
    <div className="card">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">
        All Candidates ({candidates.length})
      </h2>

      <div className="space-y-4">
        {candidates.map((candidate, index) => (
          <div
            key={candidate.id}
            className={`border rounded-lg p-4 transition-all ${
              index === 0
                ? 'border-green-300 bg-green-50'
                : 'border-gray-200 bg-gray-50 hover:bg-gray-100'
            }`}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className={`flex items-center justify-center w-8 h-8 rounded-full font-bold text-sm ${
                  index === 0 ? 'bg-green-500 text-white' : 'bg-gray-300 text-gray-700'
                }`}>
                  {index + 1}
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">{candidate.id}</h3>
                  <p className="text-sm text-gray-600">{candidate.vendor}</p>
                </div>
              </div>
              <div className="text-right">
                <div className={`text-lg font-bold ${
                  index === 0 ? 'text-green-700' : 'text-gray-900'
                }`}>
                  {candidate.score?.toFixed(4)}
                </div>
                <div className="text-xs text-gray-500">Score</div>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <p className="text-gray-600">Price</p>
                <p className="font-semibold text-gray-900">${candidate.price.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-gray-600">Lead Time</p>
                <p className="font-semibold text-gray-900">{candidate.lead_time_days} days</p>
              </div>
              <div>
                <p className="text-gray-600">Reliability</p>
                <p className="font-semibold text-gray-900">{(candidate.reliability * 100).toFixed(1)}%</p>
              </div>
            </div>

            {candidate.specs && (
              <div className="mt-3 pt-3 border-t border-gray-200">
                <p className="text-xs text-gray-600 mb-2">Specifications</p>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(candidate.specs).map(([key, value]) => (
                    <span
                      key={key}
                      className="bg-white px-2 py-1 rounded text-xs font-medium text-gray-700 border border-gray-200"
                    >
                      {key}: {value}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default CandidatesList
