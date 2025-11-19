function NegotiationPanel({ negotiation }) {
  if (!negotiation) return null

  const getVerdictColor = (verdict) => {
    switch (verdict) {
      case 'APPROVED':
        return 'bg-green-100 text-green-800 border-green-300'
      case 'APPROVED_WITH_CONDITIONS':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300'
      case 'ESCALATED':
        return 'bg-red-100 text-red-800 border-red-300'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300'
    }
  }

  return (
    <div className="card bg-gradient-to-br from-purple-50 to-pink-50 border-2 border-purple-200">
      <div className="flex items-center gap-3 mb-6">
        <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z" />
        </svg>
        <h2 className="text-2xl font-bold text-gray-900">Multi-Agent Negotiation</h2>
      </div>

      <div className="mb-6">
        <div className="flex items-center justify-between bg-white rounded-lg p-4 border-2 border-purple-200">
          <div>
            <p className="text-sm text-gray-600">Item</p>
            <p className="font-semibold text-gray-900">{negotiation.item_id}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Vendor</p>
            <p className="font-semibold text-gray-900">{negotiation.vendor}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Price</p>
            <p className="font-semibold text-gray-900">${negotiation.price?.toLocaleString()}</p>
          </div>
          <div>
            <span className={`px-4 py-2 rounded-lg border-2 font-bold ${getVerdictColor(negotiation.verdict)}`}>
              {negotiation.verdict}
            </span>
          </div>
        </div>
      </div>

      <div className="space-y-3">
        <h3 className="font-semibold text-gray-900">Transcript</h3>
        {negotiation.transcript?.map((message, index) => {
          const isAgent = message.startsWith('Agent:')
          return (
            <div
              key={index}
              className={`rounded-lg p-4 ${
                isAgent
                  ? 'bg-blue-50 border-l-4 border-blue-500'
                  : 'bg-white border-l-4 border-purple-500'
              }`}
            >
              <p className="text-sm font-medium mb-1 text-gray-700">
                {isAgent ? 'Procurement Agent' : 'Procurement Officer'}
              </p>
              <p className="text-gray-900">
                {message.replace(/^(Agent:|Officer:)\s*/, '')}
              </p>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default NegotiationPanel
