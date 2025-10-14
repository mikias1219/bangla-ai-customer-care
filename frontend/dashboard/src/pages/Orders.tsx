import { useState, useEffect } from 'react'

interface OrderItem {
  id: number
  product_name: string
  product_sku: string
  quantity: number
  unit_price: number
  total_price: number
}

interface Order {
  id: number
  order_number: string
  customer_id: number
  status: string
  payment_status: string
  currency: string
  subtotal: number
  tax_amount: number
  discount_amount: number
  shipping_amount: number
  total_amount: number
  ordered_at: string
  confirmed_at?: string
  shipped_at?: string
  delivered_at?: string
  cancelled_at?: string
  items: OrderItem[]
}

export function Orders() {
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null)
  const [stats, setStats] = useState<any>(null)

  useEffect(() => {
    loadOrders()
    loadStats()
  }, [])

  const loadOrders = async () => {
    try {
      const response = await fetch('/api/orders/')
      if (response.ok) {
        const data = await response.json()
        setOrders(data)
      }
    } catch (error) {
      console.error('Failed to load orders:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadStats = async () => {
    try {
      const response = await fetch('/api/orders/stats/overview/')
      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }
    } catch (error) {
      console.error('Failed to load stats:', error)
    }
  }

  const updateOrderStatus = async (orderId: number, status: string) => {
    try {
      const response = await fetch(`/api/orders/${orderId}/`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status })
      })

      if (response.ok) {
        await loadOrders()
        await loadStats()
      }
    } catch (error) {
      console.error('Failed to update order:', error)
    }
  }

  const updatePaymentStatus = async (orderId: number, paymentStatus: string) => {
    try {
      const response = await fetch(`/api/orders/${orderId}/`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ payment_status: paymentStatus })
      })

      if (response.ok) {
        await loadOrders()
        await loadStats()
      }
    } catch (error) {
      console.error('Failed to update payment status:', error)
    }
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: '#f59e0b',
      confirmed: '#3b82f6',
      processing: '#8b5cf6',
      shipped: '#06b6d4',
      delivered: '#10b981',
      cancelled: '#ef4444',
      refunded: '#6b7280'
    }
    return colors[status] || '#6b7280'
  }

  const getPaymentStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: '#f59e0b',
      paid: '#10b981',
      failed: '#ef4444',
      refunded: '#6b7280'
    }
    return colors[status] || '#6b7280'
  }

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '40px' }}>Loading orders...</div>
  }

  return (
    <div>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 'bold' }}>Orders</h1>
        <p style={{ margin: '4px 0 0 0', color: '#6b7280' }}>Manage customer orders and transactions</p>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
          <div style={{ background: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#3b82f6' }}>{stats.total_orders}</div>
            <div style={{ color: '#6b7280', fontSize: '14px' }}>Total Orders</div>
          </div>
          <div style={{ background: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#10b981' }}>{stats.total_revenue?.toLocaleString()} BDT</div>
            <div style={{ color: '#6b7280', fontSize: '14px' }}>Total Revenue</div>
          </div>
          <div style={{ background: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f59e0b' }}>{stats.pending_orders}</div>
            <div style={{ color: '#6b7280', fontSize: '14px' }}>Pending Orders</div>
          </div>
          <div style={{ background: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#06b6d4' }}>{stats.shipped_orders}</div>
            <div style={{ color: '#6b7280', fontSize: '14px' }}>Shipped Orders</div>
          </div>
        </div>
      )}

      <div style={{ display: 'flex', gap: '24px' }}>
        {/* Orders List */}
        <div style={{ flex: 1, background: 'white', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <div style={{ padding: '20px', borderBottom: '1px solid #e5e7eb' }}>
            <h3 style={{ margin: 0 }}>Recent Orders ({orders.length})</h3>
          </div>

          <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
            {orders.map((order) => (
              <div
                key={order.id}
                onClick={() => setSelectedOrder(order)}
                style={{
                  padding: '16px 20px',
                  borderBottom: '1px solid #f3f4f6',
                  cursor: 'pointer',
                  background: selectedOrder?.id === order.id ? '#f9fafb' : 'white',
                  transition: 'background 0.2s'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontWeight: '500' }}>{order.order_number}</div>
                    <div style={{ fontSize: '14px', color: '#6b7280' }}>
                      {new Date(order.ordered_at).toLocaleDateString()} • {order.items.length} items
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontWeight: '500' }}>{order.currency} {order.total_amount.toLocaleString()}</div>
                    <div style={{ display: 'flex', gap: '8px', marginTop: '4px' }}>
                      <span style={{
                        padding: '2px 8px',
                        borderRadius: '12px',
                        fontSize: '12px',
                        fontWeight: '500',
                        background: `${getStatusColor(order.status)}20`,
                        color: getStatusColor(order.status)
                      }}>
                        {order.status}
                      </span>
                      <span style={{
                        padding: '2px 8px',
                        borderRadius: '12px',
                        fontSize: '12px',
                        fontWeight: '500',
                        background: `${getPaymentStatusColor(order.payment_status)}20`,
                        color: getPaymentStatusColor(order.payment_status)
                      }}>
                        {order.payment_status}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {orders.length === 0 && (
            <div style={{ padding: '40px', textAlign: 'center', color: '#6b7280' }}>
              No orders found.
            </div>
          )}
        </div>

        {/* Order Details */}
        {selectedOrder && (
          <div style={{ width: '400px', background: 'white', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <div style={{ padding: '20px', borderBottom: '1px solid #e5e7eb' }}>
              <h3 style={{ margin: 0 }}>Order Details</h3>
              <div style={{ fontSize: '14px', color: '#6b7280', marginTop: '4px' }}>
                {selectedOrder.order_number}
              </div>
            </div>

            <div style={{ padding: '20px' }}>
              {/* Order Status */}
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', fontWeight: '500', marginBottom: '8px' }}>
                  Order Status
                </label>
                <select
                  value={selectedOrder.status}
                  onChange={(e) => updateOrderStatus(selectedOrder.id, e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #d1d5db',
                    borderRadius: '4px'
                  }}
                >
                  <option value="pending">Pending</option>
                  <option value="confirmed">Confirmed</option>
                  <option value="processing">Processing</option>
                  <option value="shipped">Shipped</option>
                  <option value="delivered">Delivered</option>
                  <option value="cancelled">Cancelled</option>
                </select>
              </div>

              {/* Payment Status */}
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', fontWeight: '500', marginBottom: '8px' }}>
                  Payment Status
                </label>
                <select
                  value={selectedOrder.payment_status}
                  onChange={(e) => updatePaymentStatus(selectedOrder.id, e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #d1d5db',
                    borderRadius: '4px'
                  }}
                >
                  <option value="pending">Pending</option>
                  <option value="paid">Paid</option>
                  <option value="failed">Failed</option>
                  <option value="refunded">Refunded</option>
                </select>
              </div>

              {/* Order Items */}
              <div style={{ marginBottom: '20px' }}>
                <h4 style={{ margin: '0 0 12px 0' }}>Items</h4>
                <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
                  {selectedOrder.items.map((item) => (
                    <div key={item.id} style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      padding: '8px 0',
                      borderBottom: '1px solid #f3f4f6'
                    }}>
                      <div>
                        <div style={{ fontWeight: '500', fontSize: '14px' }}>{item.product_name}</div>
                        <div style={{ fontSize: '12px', color: '#6b7280' }}>
                          SKU: {item.product_sku} • Qty: {item.quantity}
                        </div>
                      </div>
                      <div style={{ fontWeight: '500' }}>
                        {selectedOrder.currency} {item.total_price.toLocaleString()}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Order Summary */}
              <div style={{ borderTop: '1px solid #e5e7eb', paddingTop: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span>Subtotal:</span>
                  <span>{selectedOrder.currency} {selectedOrder.subtotal.toLocaleString()}</span>
                </div>
                {selectedOrder.tax_amount > 0 && (
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <span>Tax:</span>
                    <span>{selectedOrder.currency} {selectedOrder.tax_amount.toLocaleString()}</span>
                  </div>
                )}
                {selectedOrder.shipping_amount > 0 && (
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <span>Shipping:</span>
                    <span>{selectedOrder.currency} {selectedOrder.shipping_amount.toLocaleString()}</span>
                  </div>
                )}
                {selectedOrder.discount_amount > 0 && (
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px', color: '#10b981' }}>
                    <span>Discount:</span>
                    <span>-{selectedOrder.currency} {selectedOrder.discount_amount.toLocaleString()}</span>
                  </div>
                )}
                <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 'bold', fontSize: '16px', marginTop: '8px', paddingTop: '8px', borderTop: '1px solid #e5e7eb' }}>
                  <span>Total:</span>
                  <span>{selectedOrder.currency} {selectedOrder.total_amount.toLocaleString()}</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
