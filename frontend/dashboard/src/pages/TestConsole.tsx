import { useState } from 'react'
import { apiBase } from '../lib/api'
import {
  PlayIcon,
  ChatBubbleLeftRightIcon,
  CpuChipIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline'

export function TestConsole() {
  const [text, setText] = useState('Amar order 123 kothay?')
  const [nlu, setNlu] = useState<any>(null)
  const [dm, setDm] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const sampleQueries = [
    'Amar order 123 kothay?',
    'iPhone 15 price?',
    'আপনার স্টোর কোথায়?',
    'আমি একটা laptop চাই',
    'ডেলিভারি কতদিন লাগে?',
    'রিফান্ড পাব কি?'
  ]

  async function run() {
    if (!text.trim()) return

    setLoading(true)
    setNlu(null)
    setDm(null)
    try {
      const nluRes = await fetch(`${apiBase()}/nlu/resolve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      }).then((r) => r.json())
      setNlu(nluRes)

      const dmRes = await fetch(`${apiBase()}/dm/decide`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          intent: nluRes.intent,
          entities: nluRes.entities,
          context: { channel: 'web', test: true }
        })
      }).then((r) => r.json())
      setDm(dmRes)
    } catch (error) {
      console.error('Test failed:', error)
      setNlu({ error: 'Failed to process NLU' })
      setDm({ error: 'Failed to process dialogue' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
            <CpuChipIcon className="w-6 h-6 text-primary-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Test Console</h1>
            <p className="text-gray-600">Test the AI pipeline with sample customer queries</p>
          </div>
        </div>

        {/* Quick Test Queries */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="text-sm font-medium text-gray-900 mb-3">Quick Test Queries:</h3>
          <div className="flex flex-wrap gap-2">
            {sampleQueries.map((query, index) => (
              <button
                key={index}
                onClick={() => setText(query)}
                className="px-3 py-1.5 bg-white border border-gray-300 rounded-lg text-sm hover:border-primary-300 hover:bg-primary-50 transition-colors"
              >
                {query}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Input Section */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Customer Message
            </label>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Enter a customer message to test..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
              rows={3}
            />
          </div>

          <button
            onClick={run}
            disabled={loading || !text.trim()}
            className="flex items-center gap-2 px-6 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Processing...
              </>
            ) : (
              <>
                <PlayIcon className="w-4 h-4" />
                Test AI Pipeline
              </>
            )}
          </button>
        </div>
      </div>

      {/* Results */}
      {(nlu || dm) && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* NLU Results */}
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div className="border-b border-gray-200 px-6 py-4 bg-gray-50">
              <div className="flex items-center gap-3">
                <ChatBubbleLeftRightIcon className="w-5 h-5 text-blue-600" />
                <h3 className="font-semibold text-gray-900">NLU Analysis</h3>
                {nlu && !nlu.error && (
                  <CheckCircleIcon className="w-5 h-5 text-green-500" />
                )}
                {nlu?.error && (
                  <XCircleIcon className="w-5 h-5 text-red-500" />
                )}
              </div>
            </div>
            <div className="p-6">
              {nlu ? (
                <pre className="text-sm bg-gray-50 p-4 rounded-lg overflow-auto max-h-96">
{JSON.stringify(nlu, null, 2)}
                </pre>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <ChatBubbleLeftRightIcon className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p>NLU results will appear here</p>
                </div>
              )}
            </div>
          </div>

          {/* Dialogue Manager Results */}
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div className="border-b border-gray-200 px-6 py-4 bg-gray-50">
              <div className="flex items-center gap-3">
                <CpuChipIcon className="w-5 h-5 text-purple-600" />
                <h3 className="font-semibold text-gray-900">AI Response</h3>
                {dm && !dm.error && (
                  <CheckCircleIcon className="w-5 h-5 text-green-500" />
                )}
                {dm?.error && (
                  <XCircleIcon className="w-5 h-5 text-red-500" />
                )}
              </div>
            </div>
            <div className="p-6">
              {dm ? (
                <div className="space-y-4">
                  {dm.response_text_bn && (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <h4 className="text-sm font-medium text-blue-900 mb-2">Bot Response:</h4>
                      <p className="text-blue-800 whitespace-pre-wrap">{dm.response_text_bn}</p>
                    </div>
                  )}
                  <pre className="text-sm bg-gray-50 p-4 rounded-lg overflow-auto max-h-80">
{JSON.stringify(dm, null, 2)}
                  </pre>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <CpuChipIcon className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p>AI response will appear here</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Instructions */}
      {!nlu && !dm && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-start gap-3">
            <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
              <span className="text-blue-600 text-sm">ℹ️</span>
            </div>
            <div>
              <h3 className="text-sm font-medium text-blue-900 mb-2">How to Test</h3>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• Enter a customer message in Bangla or English</li>
                <li>• Click "Test AI Pipeline" to see how the system processes it</li>
                <li>• Check NLU Analysis for intent and entity extraction</li>
                <li>• Check AI Response for the generated customer reply</li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
