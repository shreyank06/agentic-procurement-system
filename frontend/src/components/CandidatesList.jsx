function CandidatesList({ candidates }) {
  if (!candidates || candidates.length === 0) return null

  return (
    <div className="card">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Alternative Options</h2>
        <p className="text-sm text-gray-600 mt-1">{candidates.length} other candidates available</p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b-2 border-gray-300">
              <th className="text-left py-3 px-4 font-semibold text-gray-700">Rank</th>
              <th className="text-left py-3 px-4 font-semibold text-gray-700">Component</th>
              <th className="text-left py-3 px-4 font-semibold text-gray-700">Vendor</th>
              <th className="text-right py-3 px-4 font-semibold text-gray-700">Price</th>
              <th className="text-center py-3 px-4 font-semibold text-gray-700">Lead Time</th>
              <th className="text-center py-3 px-4 font-semibold text-gray-700">Reliability</th>
              <th className="text-right py-3 px-4 font-semibold text-gray-700">Score</th>
            </tr>
          </thead>
          <tbody>
            {candidates.map((candidate, index) => (
              <tr
                key={candidate.id}
                className={`border-b transition-colors ${
                  index === 0
                    ? 'bg-green-50 hover:bg-green-100'
                    : 'hover:bg-gray-50'
                }`}
              >
                <td className="py-3 px-4">
                  <span className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold ${
                    index === 0 ? 'bg-green-500 text-white' : 'bg-gray-300 text-gray-700'
                  }`}>
                    {index + 1}
                  </span>
                </td>
                <td className="py-3 px-4 font-medium text-gray-900">{candidate.id}</td>
                <td className="py-3 px-4 text-gray-600">{candidate.vendor}</td>
                <td className="py-3 px-4 text-right font-semibold text-gray-900">${candidate.price.toLocaleString()}</td>
                <td className="py-3 px-4 text-center text-gray-900">{candidate.lead_time_days}d</td>
                <td className="py-3 px-4 text-center text-gray-900">{(candidate.reliability * 100).toFixed(0)}%</td>
                <td className={`py-3 px-4 text-right font-bold ${
                  index === 0 ? 'text-green-700' : 'text-gray-900'
                }`}>
                  {candidate.score?.toFixed(3)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Show specs summary if available */}
      {candidates[0]?.specs && (
        <div className="mt-6 pt-4 border-t border-gray-200">
          <p className="text-xs font-semibold text-gray-600 mb-2">TOP CANDIDATE SPECS</p>
          <div className="flex flex-wrap gap-2">
            {Object.entries(candidates[0].specs).map(([key, value]) => (
              <span
                key={key}
                className="bg-blue-50 px-3 py-1 rounded-full text-xs font-medium text-blue-700 border border-blue-200"
              >
                {key}: {value}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default CandidatesList
