import { useState, useEffect } from 'react'

interface Customer {
  id: number
  customer_id: string
  name?: string
  email?: string
  phone?: string
  channel: string
  channel_user_id: string
  total_orders: number
  total_spent: number
  last_order_at?: string
  created_at: string
}

export function Customers() {
  const [customers, setCustomers] = useState<Customer[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null)
  const [stats, setStats] = useState<any>(null)

  useEffect(() => {
    loadCustomers()
    loadStats()
  }, [])

  const loadCustomers = async () => {
    try {
      const response = await fetch('/api/customers/')
      if (response.ok) {
        const data = await response.json()
        setCustomers(data)
      }
    } catch (error) {
      console.error('Failed to load customers:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadStats = async () => {
    try {
      const response = await fetch('/api/customers/stats/overview/')
      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }
    } catch (error) {
      console.error('Failed to load stats:', error)
    }
  }


  const getChannelIcon = (channel: string) => {
    const icons: Record<string, string> = {
      whatsapp: '📱',
      messenger: '💬',
      instagram: '📸',
      webchat: '🌐',
      voice: '📞'
    }
    return icons[channel.toLowerCase()] || '👤'
  }

  const getChannelColor = (channel: string) => {
    const colors: Record<string, string> = {
      whatsapp: '#25d366',
      messenger: '#0084ff',
      instagram: '#e1306c',
      webchat: '#6b7280',
      voice: '#10b981'
    }
    return colors[channel.toLowerCase()] || '#6b7280'
  }

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '40px' }}>Loading customers...</div>
  }

  return (
    <div>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 'bold' }}>Customers</h1>
        <p style={{ margin: '4px 0 0 0', color: '#6b7280' }}>Manage customer relationships and data</p>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
          <div style={{ background: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#3b82f6' }}>{stats.total_customers}</div>
            <div style={{ color: '#6b7280', fontSize: '14px' }}>Total Customers</div>
          </div>
          <div style={{ background: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#10b981' }}>{stats.customers_with_orders}</div>
            <div style={{ color: '#6b7280', fontSize: '14px' }}>Active Customers</div>
          </div>
          <div style={{ background: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f59e0b' }}>
              {stats.customers_with_orders > 0 ? ((stats.customers_with_orders / stats.total_customers) * 100).toFixed(1) : 0}%
            </div>
            <div style={{ color: '#6b7280', fontSize: '14px' }}>Conversion Rate</div>
          </div>
        </div>
      )}

      <div style={{ display: 'flex', gap: '24px' }}>
        {/* Customers List */}
        <div style={{ flex: 1, background: 'white', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <div style={{ padding: '20px', borderBottom: '1px solid #e5e7eb' }}>
            <h3 style={{ margin: 0 }}>Customer Directory ({customers.length})</h3>
          </div>

          <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
            {customers.map((customer) => (
              <div
                key={customer.id}
                onClick={() => setSelectedCustomer(customer)}
                style={{
                  padding: '16px 20px',
                  borderBottom: '1px solid #f3f4f6',
                  cursor: 'pointer',
                  background: selectedCustomer?.id === customer.id ? '#f9fafb' : 'white',
                  transition: 'background 0.2s'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{
                      width: '40px',
                      height: '40px',
                      borderRadius: '50%',
                      background: getChannelColor(customer.channel),
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '18px'
                    }}>
                      {getChannelIcon(customer.channel)}
                    </div>
                    <div>
                      <div style={{ fontWeight: '500' }}>
                        {customer.name || `Customer ${customer.customer_id.slice(-8)}`}
                      </div>
                      <div style={{ fontSize: '14px', color: '#6b7280' }}>
                        {customer.channel} • {customer.total_orders} orders
                      </div>
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontWeight: '500' }}>
                      BDT {customer.total_spent.toLocaleString()}
                    </div>
                    {customer.last_order_at && (
                      <div style={{ fontSize: '12px', color: '#6b7280' }}>
                        Last order: {new Date(customer.last_order_at).toLocaleDateString()}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {customers.length === 0 && (
            <div style={{ padding: '40px', textAlign: 'center', color: '#6b7280' }}>
              No customers found.
            </div>
          )}
        </div>

        {/* Customer Details */}
        {selectedCustomer && (
          <div style={{ width: '400px', background: 'white', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <div style={{ padding: '20px', borderBottom: '1px solid #e5e7eb' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{
                  width: '50px',
                  height: '50px',
                  borderRadius: '50%',
                  background: getChannelColor(selectedCustomer.channel),
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '22px'
                }}>
                  {getChannelIcon(selectedCustomer.channel)}
                </div>
                <div>
                  <h3 style={{ margin: '0 0 4px 0' }}>
                    {selectedCustomer.name || `Customer ${selectedCustomer.customer_id.slice(-8)}`}
                  </h3>
                  <div style={{ fontSize: '14px', color: '#6b7280' }}>
                    {selectedCustomer.channel} • ID: {selectedCustomer.customer_id.slice(-8)}
                  </div>
                </div>
              </div>
            </div>

            <div style={{ padding: '20px' }}>
              {/* Contact Information */}
              <div style={{ marginBottom: '20px' }}>
                <h4 style={{ margin: '0 0 12px 0' }}>Contact Information</h4>
                <div style={{ display: 'grid', gap: '8px' }}>
                  {selectedCustomer.email && (
                    <div>
                      <span style={{ fontWeight: '500', color: '#6b7280' }}>Email:</span> {selectedCustomer.email}
                    </div>
                  )}
                  {selectedCustomer.phone && (
                    <div>
                      <span style={{ fontWeight: '500', color: '#6b7280' }}>Phone:</span> {selectedCustomer.phone}
                    </div>
                  )}
                  <div>
                    <span style={{ fontWeight: '500', color: '#6b7280' }}>Channel:</span> {selectedCustomer.channel}
                  </div>
                  <div>
                    <span style={{ fontWeight: '500', color: '#6b7280' }}>User ID:</span> {selectedCustomer.channel_user_id}
                  </div>
                </div>
              </div>

              {/* Customer Stats */}
              <div style={{ marginBottom: '20px' }}>
                <h4 style={{ margin: '0 0 12px 0' }}>Statistics</h4>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                  <div style={{ textAlign: 'center', padding: '12px', background: '#f9fafb', borderRadius: '6px' }}>
                    <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#3b82f6' }}>
                      {selectedCustomer.total_orders}
                    </div>
                    <div style={{ fontSize: '12px', color: '#6b7280' }}>Total Orders</div>
                  </div>
                  <div style={{ textAlign: 'center', padding: '12px', background: '#f9fafb', borderRadius: '6px' }}>
                    <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#10b981' }}>
                      BDT {selectedCustomer.total_spent.toLocaleString()}
                    </div>
                    <div style={{ fontSize: '12px', color: '#6b7280' }}>Total Spent</div>
                  </div>
                </div>
              </div>

              {/* Recent Activity */}
              <div>
                <h4 style={{ margin: '0 0 12px 0' }}>Activity</h4>
                <div style={{ display: 'grid', gap: '8px' }}>
                  <div style={{ padding: '8px 12px', background: '#f9fafb', borderRadius: '4px', fontSize: '14px' }}>
                    <span style={{ fontWeight: '500', color: '#6b7280' }}>Joined:</span> {new Date(selectedCustomer.created_at).toLocaleDateString()}
                  </div>
                  {selectedCustomer.last_order_at && (
                    <div style={{ padding: '8px 12px', background: '#f9fafb', borderRadius: '4px', fontSize: '14px' }}>
                      <span style={{ fontWeight: '500', color: '#6b7280' }}>Last Order:</span> {new Date(selectedCustomer.last_order_at).toLocaleDateString()}
                    </div>
                  )}
                  <div style={{ padding: '8px 12px', background: '#f9fafb', borderRadius: '4px', fontSize: '14px' }}>
                    <span style={{ fontWeight: '500', color: '#6b7280' }}>Channel:</span> {selectedCustomer.channel}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
