import { useState, useEffect } from 'react'

interface Product {
  id: number
  name: string
  sku: string
  price: number
  currency: string
  category?: string
  brand?: string
  stock_quantity: number
  min_stock_level: number
  is_active: boolean
  is_featured: boolean
  created_at: string
}

interface ProductForm {
  name: string
  sku: string
  price: number
  currency: string
  category: string
  brand: string
  stock_quantity: number
  min_stock_level: number
  is_active: boolean
  is_featured: boolean
}

export function Products() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingProduct, setEditingProduct] = useState<Product | null>(null)
  const [form, setForm] = useState<ProductForm>({
    name: '',
    sku: '',
    price: 0,
    currency: 'BDT',
    category: '',
    brand: '',
    stock_quantity: 0,
    min_stock_level: 0,
    is_active: true,
    is_featured: false
  })

  useEffect(() => {
    loadProducts()
  }, [])

  const loadProducts = async () => {
    try {
      const response = await fetch('/api/products/')
      if (response.ok) {
        const data = await response.json()
        setProducts(data)
      } else {
        console.error('Failed to load products:', response.status, response.statusText)
      }
    } catch (error) {
      console.error('Failed to load products:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const url = editingProduct ? `/api/products/${editingProduct.id}/` : '/api/products/'
      const method = editingProduct ? 'PUT' : 'POST'

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      })

      if (response.ok) {
        await loadProducts()
        setShowForm(false)
        setEditingProduct(null)
        resetForm()
      }
    } catch (error) {
      console.error('Failed to save product:', error)
    }
  }

  const handleEdit = (product: Product) => {
    setEditingProduct(product)
    setForm({
      name: product.name,
      sku: product.sku,
      price: product.price,
      currency: product.currency,
      category: product.category || '',
      brand: product.brand || '',
      stock_quantity: product.stock_quantity,
      min_stock_level: product.min_stock_level,
      is_active: product.is_active,
      is_featured: product.is_featured
    })
    setShowForm(true)
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this product?')) return

    try {
      const response = await fetch(`/api/products/${id}/`, { method: 'DELETE' })
      if (response.ok) {
        await loadProducts()
      }
    } catch (error) {
      console.error('Failed to delete product:', error)
    }
  }

  const resetForm = () => {
    setForm({
      name: '',
      sku: '',
      price: 0,
      currency: 'BDT',
      category: '',
      brand: '',
      stock_quantity: 0,
      min_stock_level: 0,
      is_active: true,
      is_featured: false
    })
  }

  const getStockStatus = (product: Product) => {
    if (product.stock_quantity <= 0) return { text: 'Out of Stock', color: '#dc2626' }
    if (product.stock_quantity <= product.min_stock_level) return { text: 'Low Stock', color: '#d97706' }
    return { text: 'In Stock', color: '#16a34a' }
  }

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '40px' }}>Loading products...</div>
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 'bold' }}>Products</h1>
          <p style={{ margin: '4px 0 0 0', color: '#6b7280' }}>Manage your product catalog</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          style={{
            background: '#3b82f6',
            color: 'white',
            border: 'none',
            padding: '8px 16px',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '14px'
          }}
        >
          Add Product
        </button>
      </div>

      {showForm && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            background: 'white',
            padding: '24px',
            borderRadius: '8px',
            width: '500px',
            maxWidth: '90vw'
          }}>
            <h2 style={{ margin: '0 0 20px 0' }}>
              {editingProduct ? 'Edit Product' : 'Add Product'}
            </h2>

            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>
                  Name *
                </label>
                <input
                  type="text"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  required
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #d1d5db',
                    borderRadius: '4px'
                  }}
                />
              </div>

              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>
                  SKU *
                </label>
                <input
                  type="text"
                  value={form.sku}
                  onChange={(e) => setForm({ ...form, sku: e.target.value })}
                  required
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #d1d5db',
                    borderRadius: '4px'
                  }}
                />
              </div>

              <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>
                    Price *
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={form.price}
                    onChange={(e) => setForm({ ...form, price: parseFloat(e.target.value) || 0 })}
                    required
                    style={{
                      width: '100%',
                      padding: '8px',
                      border: '1px solid #d1d5db',
                      borderRadius: '4px'
                    }}
                  />
                </div>
                <div style={{ width: '80px' }}>
                  <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>
                    Currency
                  </label>
                  <input
                    type="text"
                    value={form.currency}
                    onChange={(e) => setForm({ ...form, currency: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '8px',
                      border: '1px solid #d1d5db',
                      borderRadius: '4px'
                    }}
                  />
                </div>
              </div>

              <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>
                    Category
                  </label>
                  <input
                    type="text"
                    value={form.category}
                    onChange={(e) => setForm({ ...form, category: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '8px',
                      border: '1px solid #d1d5db',
                      borderRadius: '4px'
                    }}
                  />
                </div>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>
                    Brand
                  </label>
                  <input
                    type="text"
                    value={form.brand}
                    onChange={(e) => setForm({ ...form, brand: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '8px',
                      border: '1px solid #d1d5db',
                      borderRadius: '4px'
                    }}
                  />
                </div>
              </div>

              <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>
                    Stock Quantity
                  </label>
                  <input
                    type="number"
                    value={form.stock_quantity}
                    onChange={(e) => setForm({ ...form, stock_quantity: parseInt(e.target.value) || 0 })}
                    style={{
                      width: '100%',
                      padding: '8px',
                      border: '1px solid #d1d5db',
                      borderRadius: '4px'
                    }}
                  />
                </div>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>
                    Min Stock Level
                  </label>
                  <input
                    type="number"
                    value={form.min_stock_level}
                    onChange={(e) => setForm({ ...form, min_stock_level: parseInt(e.target.value) || 0 })}
                    style={{
                      width: '100%',
                      padding: '8px',
                      border: '1px solid #d1d5db',
                      borderRadius: '4px'
                    }}
                  />
                </div>
              </div>

              <div style={{ display: 'flex', gap: '12px', marginBottom: '20px' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <input
                    type="checkbox"
                    checked={form.is_active}
                    onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
                  />
                  Active
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <input
                    type="checkbox"
                    checked={form.is_featured}
                    onChange={(e) => setForm({ ...form, is_featured: e.target.checked })}
                  />
                  Featured
                </label>
              </div>

              <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  onClick={() => {
                    setShowForm(false)
                    setEditingProduct(null)
                    resetForm()
                  }}
                  style={{
                    padding: '8px 16px',
                    border: '1px solid #d1d5db',
                    background: 'white',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  style={{
                    padding: '8px 16px',
                    background: '#3b82f6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  {editingProduct ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div style={{ background: 'white', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <div style={{ padding: '20px', borderBottom: '1px solid #e5e7eb' }}>
          <h3 style={{ margin: 0 }}>Product Catalog ({products.length})</h3>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: '500' }}>Product</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: '500' }}>SKU</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: '500' }}>Price</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: '500' }}>Stock</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: '500' }}>Category</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: '500' }}>Status</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: '500' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {products.map((product) => {
                const stockStatus = getStockStatus(product)
                return (
                  <tr key={product.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                    <td style={{ padding: '12px' }}>
                      <div>
                        <div style={{ fontWeight: '500' }}>{product.name}</div>
                        {product.brand && (
                          <div style={{ fontSize: '12px', color: '#6b7280' }}>{product.brand}</div>
                        )}
                      </div>
                    </td>
                    <td style={{ padding: '12px', fontFamily: 'monospace' }}>{product.sku}</td>
                    <td style={{ padding: '12px' }}>
                      {product.currency} {product.price.toLocaleString()}
                    </td>
                    <td style={{ padding: '12px' }}>
                      <span style={{
                        color: stockStatus.color,
                        fontWeight: '500'
                      }}>
                        {product.stock_quantity}
                      </span>
                      {product.stock_quantity <= product.min_stock_level && (
                        <span style={{ color: '#d97706', fontSize: '12px', marginLeft: '4px' }}>
                          (Low)
                        </span>
                      )}
                    </td>
                    <td style={{ padding: '12px' }}>{product.category || '-'}</td>
                    <td style={{ padding: '12px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{
                          padding: '2px 8px',
                          borderRadius: '12px',
                          fontSize: '12px',
                          fontWeight: '500',
                          background: product.is_active ? '#dcfce7' : '#fee2e2',
                          color: product.is_active ? '#166534' : '#991b1b'
                        }}>
                          {product.is_active ? 'Active' : 'Inactive'}
                        </span>
                        {product.is_featured && (
                          <span style={{
                            padding: '2px 8px',
                            borderRadius: '12px',
                            fontSize: '12px',
                            fontWeight: '500',
                            background: '#fef3c7',
                            color: '#92400e'
                          }}>
                            Featured
                          </span>
                        )}
                      </div>
                    </td>
                    <td style={{ padding: '12px' }}>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <button
                          onClick={() => handleEdit(product)}
                          style={{
                            padding: '4px 8px',
                            background: '#3b82f6',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: 'pointer',
                            fontSize: '12px'
                          }}
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDelete(product.id)}
                          style={{
                            padding: '4px 8px',
                            background: '#dc2626',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: 'pointer',
                            fontSize: '12px'
                          }}
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>

        {products.length === 0 && (
          <div style={{ padding: '40px', textAlign: 'center', color: '#6b7280' }}>
            No products found. Click "Add Product" to create your first product.
          </div>
        )}
      </div>
    </div>
  )
}
