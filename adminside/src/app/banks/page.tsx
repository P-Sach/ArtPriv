'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';

interface Bank {
    id: string;
    email: string;
    name: string;
    state: string;
    is_verified: boolean;
    is_subscribed: boolean;
    subscription_tier: string | null;
    subscription_expires_at: string | null;
    donor_count: number;
    created_at: string;
}

interface BankListResponse {
    items: Bank[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
}

export default function BanksPage() {
    const [data, setData] = useState<BankListResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [filter, setFilter] = useState<'all' | 'verified' | 'unverified' | 'subscribed'>('all');
    const router = useRouter();

    useEffect(() => {
        fetchBanks();
    }, [filter]);

    const fetchBanks = async () => {
        try {
            setLoading(true);
            const params: any = {};
            if (filter === 'verified') params.is_verified = true;
            if (filter === 'unverified') params.is_verified = false;
            if (filter === 'subscribed') params.is_subscribed = true;
            if (search) params.search = search;

            const response = await api.getBanks(params);
            setData(response);
        } catch (err) {
            if (err instanceof Error && err.message.includes('401')) {
                router.push('/login');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        fetchBanks();
    };

    const getStateBadge = (state: string) => {
        const badges: Record<string, string> = {
            operational: 'badge-success',
            verified: 'badge-info',
            subscribed_onboarded: 'badge-info',
            verification_pending: 'badge-warning',
            account_created: 'badge-warning',
        };
        return badges[state] || 'badge-info';
    };

    const getSubscriptionStatus = (bank: Bank) => {
        if (!bank.is_subscribed) return <span className="badge badge-warning">Not Subscribed</span>;
        if (bank.subscription_expires_at) {
            const expiry = new Date(bank.subscription_expires_at);
            const now = new Date();
            const daysUntilExpiry = Math.ceil((expiry.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));

            if (daysUntilExpiry < 0) return <span className="badge badge-danger">Expired</span>;
            if (daysUntilExpiry <= 30) return <span className="badge badge-warning">Expiring in {daysUntilExpiry}d</span>;
        }
        return <span className="badge badge-success">{bank.subscription_tier}</span>;
    };

    return (
        <div className="min-h-screen p-8">
            <div className="max-w-7xl mx-auto">
                <header className="mb-8 flex justify-between items-center">
                    <div>
                        <h1 className="text-3xl font-bold">Banks</h1>
                        <p className="text-gray-400 mt-1">Manage all registered fertility banks</p>
                    </div>
                    <button onClick={() => router.push('/dashboard')} className="text-gray-400 hover:text-white">
                        ← Back to Dashboard
                    </button>
                </header>

                {/* Filters */}
                <div className="glass-card p-4 mb-6 flex flex-wrap gap-4 items-center">
                    <form onSubmit={handleSearch} className="flex gap-2 flex-1">
                        <input
                            type="text"
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            placeholder="Search banks..."
                            className="glass-input max-w-xs"
                        />
                        <button type="submit" className="btn-primary">Search</button>
                    </form>

                    <div className="flex gap-2">
                        {(['all', 'verified', 'unverified', 'subscribed'] as const).map((f) => (
                            <button
                                key={f}
                                onClick={() => setFilter(f)}
                                className={`px-4 py-2 rounded-lg transition-all ${filter === f
                                        ? 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30'
                                        : 'text-gray-400 hover:text-white'
                                    }`}
                            >
                                {f.charAt(0).toUpperCase() + f.slice(1)}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Table */}
                <div className="glass-card overflow-hidden">
                    {loading ? (
                        <div className="p-8 text-center text-gray-400">Loading banks...</div>
                    ) : (
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Bank Name</th>
                                    <th>Email</th>
                                    <th>State</th>
                                    <th>Subscription</th>
                                    <th>Donors</th>
                                    <th>Created</th>
                                </tr>
                            </thead>
                            <tbody>
                                {data?.items.map((bank) => (
                                    <tr key={bank.id} className="cursor-pointer" onClick={() => router.push(`/banks/${bank.id}`)}>
                                        <td className="font-medium">{bank.name}</td>
                                        <td className="text-gray-400">{bank.email}</td>
                                        <td>
                                            <span className={`badge ${getStateBadge(bank.state)}`}>
                                                {bank.state.replace('_', ' ')}
                                            </span>
                                        </td>
                                        <td>{getSubscriptionStatus(bank)}</td>
                                        <td>{bank.donor_count}</td>
                                        <td className="text-gray-400">{new Date(bank.created_at).toLocaleDateString()}</td>
                                    </tr>
                                ))}
                                {(!data?.items || data.items.length === 0) && (
                                    <tr>
                                        <td colSpan={6} className="text-center text-gray-400 py-8">
                                            No banks found
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    )}
                </div>

                {/* Pagination */}
                {data && data.total_pages > 1 && (
                    <div className="mt-4 flex justify-center gap-2">
                        {Array.from({ length: data.total_pages }, (_, i) => (
                            <button
                                key={i}
                                onClick={() => api.getBanks({ page: i + 1 }).then(setData)}
                                className={`px-3 py-1 rounded ${data.page === i + 1 ? 'bg-indigo-500' : 'bg-gray-800'
                                    }`}
                            >
                                {i + 1}
                            </button>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
