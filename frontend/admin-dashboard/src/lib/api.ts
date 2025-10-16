import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Admin token interceptor
api.interceptors.request.use((config) => {
  const adminToken = localStorage.getItem('admin_token');
  if (adminToken) {
    config.headers.Authorization = `Bearer ${adminToken}`;
  }
  return config;
});

export interface Client {
  id: number;
  tenant_id: string;
  business_name: string;
  business_email: string;
  business_phone?: string;
  business_address?: string;
  contact_person?: string;
  contact_email?: string;
  contact_phone?: string;
  business_type?: string;
  website_url?: string;
  facebook_page_url?: string;
  instagram_username?: string;
  status: string;
  subscription_plan: string;
  monthly_customers_limit?: number;
  current_month_customers?: number;
  ai_reply_balance?: number;
  language_preference: string;
  trial_started_at?: string;
  subscription_started_at?: string;
  subscription_renewal_at?: string;
  created_at: string;
  updated_at?: string;
}

export interface ClientUser {
  id: number;
  client_id: number;
  username: string;
  email: string;
  full_name?: string;
  role: string;
  is_active: boolean;
  last_login_at?: string;
  created_at: string;
  updated_at?: string;
}

export const adminApi = {
  // Authentication
  login: (token: string) => {
    localStorage.setItem('admin_token', token);
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  },

  logout: () => {
    localStorage.removeItem('admin_token');
    delete api.defaults.headers.common['Authorization'];
  },

  isAuthenticated: () => {
    return !!localStorage.getItem('admin_token');
  },

  // Clients
  getClients: (params?: { skip?: number; limit?: number; status?: string }) => {
    return api.get('/admin/clients', { params });
  },

  getClient: (clientId: number) => {
    return api.get(`/admin/clients/${clientId}`);
  },

  createClient: (clientData: Partial<Client>) => {
    return api.post('/admin/clients', clientData);
  },

  updateClient: (clientId: number, clientData: Partial<Client>) => {
    return api.put(`/admin/clients/${clientId}`, clientData);
  },

  deleteClient: (clientId: number) => {
    return api.delete(`/admin/clients/${clientId}`);
  },

  // Client Users
  getClientUsers: (clientId: number) => {
    return api.get(`/admin/clients/${clientId}/users`);
  },

  createClientUser: (clientId: number, userData: {
    username: string;
    email: string;
    password: string;
    full_name?: string;
    role?: string;
  }) => {
    return api.post(`/admin/clients/${clientId}/users`, userData);
  },

  // Subscriptions
  createSubscription: (clientId: number, subscriptionData: {
    plan: string;
    amount: number;
    currency?: string;
    auto_renew?: boolean;
  }) => {
    return api.post(`/admin/clients/${clientId}/subscriptions`, subscriptionData);
  },

  // Payments
  processPayment: (clientId: number, paymentData: {
    amount: number;
    payment_type: string;
    gateway?: string;
    description?: string;
  }) => {
    return api.post('/payments/admin/process-payment', {
      client_id: clientId,
      ...paymentData
    });
  }
};

export default api;
