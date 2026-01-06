const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

interface LoginCredentials {
    email: string;
    password: string;
}

interface LoginResponse {
    access_token: string;
    admin_id: string;
    role: string;
    name: string;
}

class AdminAPI {
    private token: string | null = null;

    constructor() {
        if (typeof window !== 'undefined') {
            this.token = localStorage.getItem('admin_token');
        }
    }

    setToken(token: string) {
        this.token = token;
        if (typeof window !== 'undefined') {
            localStorage.setItem('admin_token', token);
        }
    }

    clearToken() {
        this.token = null;
        if (typeof window !== 'undefined') {
            localStorage.removeItem('admin_token');
        }
    }

    private async request(endpoint: string, options: RequestInit = {}) {
        const headers: HeadersInit = {
            'Content-Type': 'application/json',
            ...(options.headers || {}),
        };

        if (this.token) {
            (headers as Record<string, string>)['Authorization'] = `Bearer ${this.token}`;
        }

        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers,
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Request failed' }));
            throw new Error(error.detail || 'Request failed');
        }

        return response.json();
    }

    // Authentication
    async login(credentials: LoginCredentials): Promise<LoginResponse> {
        const data = await this.request('/api/admin/login', {
            method: 'POST',
            body: JSON.stringify(credentials),
        });
        this.setToken(data.access_token);
        return data;
    }

    logout() {
        this.clearToken();
    }

    // Dashboard
    async getDashboard() {
        return this.request('/api/admin/dashboard');
    }

    // Banks
    async getBanks(params?: { page?: number; state?: string; is_verified?: boolean; is_subscribed?: boolean; search?: string }) {
        const queryParams = new URLSearchParams();
        if (params?.page) queryParams.set('page', params.page.toString());
        if (params?.state) queryParams.set('state', params.state);
        if (params?.is_verified !== undefined) queryParams.set('is_verified', params.is_verified.toString());
        if (params?.is_subscribed !== undefined) queryParams.set('is_subscribed', params.is_subscribed.toString());
        if (params?.search) queryParams.set('search', params.search);

        return this.request(`/api/admin/banks?${queryParams.toString()}`);
    }

    async getBank(bankId: string) {
        return this.request(`/api/admin/banks/${bankId}`);
    }

    async verifyBank(bankId: string, verifiedBy: string, notes?: string) {
        return this.request(`/api/admin/banks/${bankId}/verify`, {
            method: 'PUT',
            body: JSON.stringify({ verified_by: verifiedBy, notes }),
        });
    }

    async updateSubscription(bankId: string, data: {
        subscription_tier: string;
        subscription_started_at: string;
        subscription_expires_at: string;
        notes?: string;
    }) {
        return this.request(`/api/admin/banks/${bankId}/subscription`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    // Donors
    async getDonors(params?: { page?: number; state?: string; bank_id?: string; search?: string }) {
        const queryParams = new URLSearchParams();
        if (params?.page) queryParams.set('page', params.page.toString());
        if (params?.state) queryParams.set('state', params.state);
        if (params?.bank_id) queryParams.set('bank_id', params.bank_id);
        if (params?.search) queryParams.set('search', params.search);

        return this.request(`/api/admin/donors?${queryParams.toString()}`);
    }

    async getDonor(donorId: string) {
        return this.request(`/api/admin/donors/${donorId}`);
    }

    // Activity Logs
    async getActivityLogs(params?: { page?: number; entity_type?: string }) {
        const queryParams = new URLSearchParams();
        if (params?.page) queryParams.set('page', params.page.toString());
        if (params?.entity_type) queryParams.set('entity_type', params.entity_type);

        return this.request(`/api/admin/activity-logs?${queryParams.toString()}`);
    }

    // Subscription Analytics
    async getSubscriptionAnalytics() {
        return this.request('/api/admin/subscriptions/analytics');
    }
}

export const api = new AdminAPI();
export default api;
