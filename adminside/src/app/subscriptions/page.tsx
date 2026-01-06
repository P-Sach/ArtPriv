'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';

interface SubscriptionSummary {
    tier: string;
    count: number;
    revenue_estimate: number;
}

interface MonthlyTrend {
    month: string;
    new_subscriptions: number;
}

interface AnalyticsData {
    active_subscriptions: number;
    expiring_soon: number;
    expired: number;
    never_subscribed: number;
    total_revenue_estimate: number;
    tier_breakdown: SubscriptionSummary[];
    monthly_trend: MonthlyTrend[];
}

export default function SubscriptionsPage() {
    const [data, setData] = useState<AnalyticsData | null>(null);
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await api.getSubscriptionAnalytics();
                setData(response);
            } catch (err) {
                if (err instanceof Error && err.message.includes('401')) {
                    router.push('/login');
                }
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [router]);

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-xl text-gray-400">Loading analytics...</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen p-8">
            <div className="max-w-7xl mx-auto">
                <header className="mb-8 flex justify-between items-center">
                    <div>
                        <h1 className="text-3xl font-bold">Subscriptions</h1>
                        <p className="text-gray-400 mt-1">Subscription analytics and revenue tracking</p>
                    </div>
                    <button onClick={() => router.push('/dashboard')} className="text-gray-400 hover:text-white">
                        ← Back to Dashboard
                    </button>
                </header>

                {/* Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <div className="stat-card">
                        <p className="text-gray-400 text-sm">Active Subscriptions</p>
                        <p className="text-4xl font-bold text-green-400 mt-2">{data?.active_subscriptions || 0}</p>
                    </div>
                    <div className="stat-card">
                        <p className="text-gray-400 text-sm">Expiring Soon</p>
                        <p className="text-4xl font-bold text-yellow-400 mt-2">{data?.expiring_soon || 0}</p>
                        <p className="text-gray-500 text-sm mt-1">Next 30 days</p>
                    </div>
                    <div className="stat-card">
                        <p className="text-gray-400 text-sm">Expired</p>
                        <p className="text-4xl font-bold text-red-400 mt-2">{data?.expired || 0}</p>
                    </div>
                    <div className="stat-card">
                        <p className="text-gray-400 text-sm">Monthly Revenue</p>
                        <p className="text-4xl font-bold text-indigo-400 mt-2">
                            ₹{(data?.total_revenue_estimate || 0).toLocaleString()}
                        </p>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Tier Breakdown */}
                    <div className="glass-card p-6">
                        <h2 className="text-xl font-semibold mb-4">Tier Distribution</h2>
                        <div className="space-y-4">
                            {data?.tier_breakdown.map((tier) => (
                                <div key={tier.tier} className="flex items-center justify-between p-4 rounded-lg bg-white/5">
                                    <div>
                                        <span className="font-semibold text-lg">{tier.tier}</span>
                                        <p className="text-gray-400 text-sm">{tier.count} banks</p>
                                    </div>
                                    <div className="text-right">
                                        <span className="text-green-400 font-semibold">₹{tier.revenue_estimate.toLocaleString()}</span>
                                        <p className="text-gray-500 text-sm">per month</p>
                                    </div>
                                </div>
                            ))}
                            {(!data?.tier_breakdown || data.tier_breakdown.length === 0) && (
                                <p className="text-gray-400 text-center py-4">No subscription data</p>
                            )}
                        </div>
                    </div>

                    {/* Monthly Trend */}
                    <div className="glass-card p-6">
                        <h2 className="text-xl font-semibold mb-4">Monthly Trend</h2>
                        <div className="space-y-3">
                            {data?.monthly_trend.map((month) => (
                                <div key={month.month} className="flex items-center gap-4">
                                    <span className="text-gray-400 w-20">{month.month}</span>
                                    <div className="flex-1 bg-white/5 rounded-full h-4 overflow-hidden">
                                        <div
                                            className="bg-gradient-to-r from-indigo-500 to-purple-500 h-full rounded-full"
                                            style={{ width: `${Math.min(month.new_subscriptions * 20, 100)}%` }}
                                        />
                                    </div>
                                    <span className="w-8 text-right">{month.new_subscriptions}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Never Subscribed */}
                <div className="mt-6 glass-card p-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <h2 className="text-xl font-semibold">Never Subscribed</h2>
                            <p className="text-gray-400">Banks that registered but never started a subscription</p>
                        </div>
                        <span className="text-4xl font-bold text-gray-400">{data?.never_subscribed || 0}</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
