import { useState } from 'react'

function ExecutionTrace({ trace }) {
  const [isExpanded, setIsExpanded] = useState(false)

  if (!trace || trace.length === 0) return null

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-gray-900">
          Execution Trace ({trace.length} steps)
        </h2>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
        >
          {isExpanded ? (
            <>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
              </svg>
              Hide Details
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
              Show Details
            </>
          )}
        </button>
      </div>

      {!isExpanded && (
        <p className="text-sm text-gray-600">
          Technical execution details (for developers and advanced users)
        </p>
      )}

      {isExpanded && (
        <div className="relative">
          {/* Timeline line */}
          <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200"></div>

          <div className="space-y-4">
            {trace.map((step, index) => (
              <div key={index} className="relative flex gap-4 items-start">
                {/* Timeline dot */}
                <div className={`relative z-10 flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                  step.step === 'tool_call'
                    ? 'bg-blue-500'
                    : step.status === 'success'
                    ? 'bg-green-500'
                    : 'bg-gray-400'
                }`}>
                  {step.step === 'tool_call' ? (
                    <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                  ) : (
                    <div className="w-2 h-2 bg-white rounded-full"></div>
                  )}
                </div>

                {/* Content */}
                <div className="flex-1 bg-gray-50 rounded-lg p-4 border border-gray-200">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 capitalize">
                        {step.step?.replace('_', ' ') || step.tool}
                      </h3>

                      {step.input && (
                        <p className="text-sm text-gray-600 mt-1">
                          <span className="font-medium">Input:</span>{' '}
                          {typeof step.input === 'string' ? step.input : JSON.stringify(step.input)}
                        </p>
                      )}

                      {step.result && (
                        <p className="text-sm text-gray-700 mt-1">{step.result}</p>
                      )}

                      {step.summary && (
                        <p className="text-sm text-gray-700 mt-1">{step.summary}</p>
                      )}

                      {step.status && (
                        <span className={`inline-block mt-2 px-2 py-1 rounded text-xs font-medium ${
                          step.status === 'success'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {step.status}
                        </span>
                      )}
                    </div>

                    <span className="text-xs text-gray-500 ml-2">
                      Step {index + 1}
                    </span>
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

export default ExecutionTrace
