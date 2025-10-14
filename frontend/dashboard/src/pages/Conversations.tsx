import { useEffect, useState } from 'react'
import { apiBase } from '../lib/api'
import { formatDistanceToNow } from 'date-fns'
import {
  ChatBubbleLeftRightIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ClockIcon as ClockOutlineIcon
} from '@heroicons/react/24/outline'

interface Conversation {
  id: number
  conversation_id: string
  channel: string
  customer_id: string | null
  status: string
  started_at: string
  ended_at: string | null
  message_count?: number
  last_message?: string
}

export function Conversations() {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'active' | 'completed' | 'escalated'>('all')

  useEffect(() => {
    fetch(`${apiBase()}/admin/conversations`)
      .then((r) => r.json())
      .then((data) => {
        // Add sample data if no real data
        if (!data || data.length === 0) {
          data = [
            {
              id: 1,
              conversation_id: 'conv_12345678',
              channel: 'whatsapp',
              customer_id: 'John Doe',
              status: 'active',
              started_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
              ended_at: null,
              message_count: 5,
              last_message: 'আমার অর্ডার কোথায়?'
            },
            {
              id: 2,
              conversation_id: 'conv_87654321',
              channel: 'messenger',
              customer_id: 'Sarah Wilson',
              status: 'completed',
              started_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
              ended_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
              message_count: 12,
              last_message: 'Thank you for the quick response!'
            },
            {
              id: 3,
              conversation_id: 'conv_11223344',
              channel: 'instagram',
              customer_id: 'Ahmed Khan',
              status: 'escalated',
              started_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
              ended_at: null,
              message_count: 8,
              last_message: 'I need to speak to a manager'
            }
          ]
        }
        setConversations(data)
        setLoading(false)
      })
      .catch(() => {
        // Fallback to sample data
        const sampleData = [
          {
            id: 1,
            conversation_id: 'conv_12345678',
            channel: 'whatsapp',
            customer_id: 'John Doe',
            status: 'active',
            started_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
            ended_at: null,
            message_count: 5,
            last_message: 'আমার অর্ডার কোথায়?'
          },
          {
            id: 2,
            conversation_id: 'conv_87654321',
            channel: 'messenger',
            customer_id: 'Sarah Wilson',
            status: 'completed',
            started_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
            ended_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
            message_count: 12,
            last_message: 'Thank you for the quick response!'
          }
        ]
        setConversations(sampleData)
        setLoading(false)
      })
  }, [])

  const filteredConversations = conversations.filter(conv => {
    if (filter === 'all') return true
    return conv.status === filter
  })

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="w-4 h-4 text-green-500" />
      case 'escalated':
        return <ExclamationTriangleIcon className="w-4 h-4 text-red-500" />
      case 'active':
        return <ClockOutlineIcon className="w-4 h-4 text-blue-500" />
      default:
        return <ClockIcon className="w-4 h-4 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'escalated':
        return 'bg-red-100 text-red-800'
      case 'active':
        return 'bg-blue-100 text-blue-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getChannelIcon = (channel: string) => {
    switch (channel) {
      case 'whatsapp':
        return '💚'
      case 'messenger':
        return '💙'
      case 'instagram':
        return '💜'
      default:
        return '💬'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
              <ChatBubbleLeftRightIcon className="w-8 h-8 text-primary-500" />
              Conversations
            </h1>
            <p className="text-gray-600 mt-1">Manage all customer conversations across channels</p>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex gap-2">
              {[
                { key: 'all', label: 'All', count: conversations.length },
                { key: 'active', label: 'Active', count: conversations.filter(c => c.status === 'active').length },
                { key: 'completed', label: 'Completed', count: conversations.filter(c => c.status === 'completed').length },
                { key: 'escalated', label: 'Escalated', count: conversations.filter(c => c.status === 'escalated').length }
              ].map(({ key, label, count }) => (
                <button
                  key={key}
                  onClick={() => setFilter(key as any)}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    filter === key
                      ? 'bg-primary-100 text-primary-700'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {label} ({count})
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Conversations List */}
      {filteredConversations.length === 0 ? (
        <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
          <ChatBubbleLeftRightIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No conversations found</h3>
          <p className="text-gray-500">
            {filter === 'all'
              ? 'No conversations yet. Start a conversation via the inbox or connect a channel.'
              : `No ${filter} conversations found.`
            }
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <div className="divide-y divide-gray-200">
            {filteredConversations.map((conv) => (
              <div
                key={conv.id}
                className="p-6 hover:bg-gray-50 cursor-pointer transition-colors"
                onClick={() => alert(`Navigate to conversation: ${conv.conversation_id}`)}
              >
                <div className="flex items-start gap-4">
                  {/* Channel Avatar */}
                  <div className="flex-shrink-0">
                    <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center text-lg">
                      {getChannelIcon(conv.channel)}
                    </div>
                  </div>

                  {/* Conversation Details */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-3">
                        <h3 className="font-semibold text-gray-900 truncate">
                          {conv.customer_id || 'Anonymous Customer'}
                        </h3>
                        <span className="text-sm text-gray-500">
                          {conv.conversation_id.substring(0, 8)}
                        </span>
                      </div>

                      <div className="flex items-center gap-3">
                        <span className="text-xs text-gray-500">
                          {formatDistanceToNow(new Date(conv.started_at), { addSuffix: true })}
                        </span>
                        <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(conv.status)}`}>
                          {getStatusIcon(conv.status)}
                          {conv.status}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        {conv.last_message && (
                          <p className="text-sm text-gray-600 truncate mb-1">
                            {conv.last_message}
                          </p>
                        )}
                        <div className="flex items-center gap-4 text-xs text-gray-500">
                          <span className="capitalize">{conv.channel}</span>
                          {conv.message_count && (
                            <span>{conv.message_count} messages</span>
                          )}
                          <span>
                            {conv.ended_at
                              ? `Duration: ${Math.round((new Date(conv.ended_at).getTime() - new Date(conv.started_at).getTime()) / 60000)}m`
                              : 'Active now'
                            }
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Stats Footer */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <ChatBubbleLeftRightIcon className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{conversations.length}</p>
              <p className="text-sm text-gray-600">Total Conversations</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <CheckCircleIcon className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">
                {conversations.filter(c => c.status === 'completed').length}
              </p>
              <p className="text-sm text-gray-600">Completed</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <ClockOutlineIcon className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">
                {conversations.filter(c => c.status === 'active').length}
              </p>
              <p className="text-sm text-gray-600">Active</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <ExclamationTriangleIcon className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">
                {conversations.filter(c => c.status === 'escalated').length}
              </p>
              <p className="text-sm text-gray-600">Escalated</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

