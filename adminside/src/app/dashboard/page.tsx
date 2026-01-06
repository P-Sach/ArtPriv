'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';

interface DashboardStats {
    total_banks: number;
    verified_banks: number;
    subscribed_banks: number;
    operational_banks: number;
    total_donors: number;
    onboarded_donors: number;
    pending_verifications: number;
    expiring_subscriptions: number;
    expired_subscriptions: number;
    recent_signups: number;
}

interface SubscriptionSummary {
    tier: string;
    count: number;
    revenue_estimate: number;
}

interface ActivityLog {
    id: string;
    admin_name: string;
    action: string;
    entity_type: string;
    created_at: string;
}

interface DashboardData {
    stats: DashboardStats;
    subscription_breakdown: SubscriptionSummary[];
    recent_activity: ActivityLog[];
}

export default function DashboardPage() {
    const [data, setData] = useState<DashboardData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const router = useRouter();

    useEffect(() => {
        const fetchDashboard = async () => {
            try {
                const dashboardData = await api.getDashboard();
                setData(dashboardData);
            } catch (err) {
                if (err instanceof Error && err.message.includes('401')) {
                    router.push('/login');
                } else {
                    setError(err instanceof Error ? err.message : 'Failed to load dashboard');
                }
            } finally {
                setLoading(false);
            }
        };

        fetchDashboard();
    }, [router]);

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-xl text-gray-400">Loading dashboard...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-red-400">{error}</div>
            </div>
        );
    }

    const stats = data?.stats;

    return (
        <div className="min-h-screen p-8">
            <div className="max-w-7xl mx-auto">
                <header className="mb-8">
                    <h1 className="text-3xl font-bold">Dashboard</h1>
                    <p className="text-gray-400 mt-1">Overview of your ArtPriv platform</p>
                </header>

                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    <StatCard
                        title="Total Banks"
                        value={stats?.total_banks || 0}
                        subtitle={`${stats?.verified_banks || 0} verified`}
                        color="indigo"
                    />
                    <StatCard
                        title="Subscribed Banks"
                        value={stats?.subscribed_banks || 0}
                        subtitle={`${stats?.expiring_subscriptions || 0} expiring soon`}
                        color="green"
                    />
                    <StatCard
                        title="Total Donors"
                        value={stats?.total_donors || 0}
                        subtitle={`${stats?.onboarded_donors || 0} onboarded`}
                        color="purple"
                    />
                    <StatCard
                        title="Pending Actions"
                        value={stats?.pending_verifications || 0}
                        subtitle="verifications pending"
                        color="orange"
                    />
                </div>

                {/* Quick Links */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <QuickAction
                        title="Manage Banks"
                        description="View and manage all registered banks"
                        href="/banks"
                        icon="🏦"
                    />
                    <QuickAction
                        title="View Donors"
                        description="Browse all donors across banks"
                        href="/donors"
                        icon="👥"
                    />
                    <QuickAction
                        title="Subscriptions"
                        description="Monitor subscription analytics"
                        href="/subscriptions"
                        icon="💳"
                    />
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Subscription Breakdown */}
                    <div className="glass-card p-6">
                        <h2 className="text-xl font-semibold mb-4">Subscription Tiers</h2>
                        <div className="space-y-4">
                            {data?.subscription_breakdown.map((tier) => (
                                <div key={tier.tier} className="flex items-center justify-between">
                                    <div>
                                        <span className="font-medium">{tier.tier}</span>
                                        <span className="text-gray-400 ml-2">({tier.count} banks)</span>
                                    </div>
                                    <span className="text-green-400">₹{tier.revenue_estimate.toLocaleString()}/mo</span>
                                </div>
                            ))}
                            {(!data?.subscription_breakdown || data.subscription_breakdown.length === 0) && (
                                <p className="text-gray-400">No active subscriptions</p>
                            )}
                        </div>
                    </div>

                    {/* Recent Activity */}
                    <div className="glass-card p-6">
                        <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
                        <div className="space-y-4">
                            {data?.recent_activity.slice(0, 5).map((log) => (
                                <div key={log.id} className="flex items-start gap-3">
                                    <div className="w-2 h-2 mt-2 rounded-full bg-indigo-400" />
                                    <div>
                                        <p className="text-sm">
                                            <span className="font-medium">{log.admin_name || 'System'}</span>
                                            <span className="text-gray-400"> {log.action.replace('_', ' ')}</span>
                                        </p>
                                        <p className="text-xs text-gray-500">
                                            {new Date(log.created_at).toLocaleString()}
                                        </p>
                                    </div>
                                </div>
                            ))}
                            {(!data?.recent_activity || data.recent_activity.length === 0) && (
                                <p className="text-gray-400">No recent activity</p>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

function StatCard({ title, value, subtitle, color }: {
    title: string;
    value: number;
    subtitle: string;
    color: string
}) {
    const colorClasses: Record<string, string> = {
        indigo: 'from-indigo-500/20 to-indigo-600/10 border-indigo-500/30',
        green: 'from-green-500/20 to-green-600/10 border-green-500/30',
        purple: 'from-purple-500/20 to-purple-600/10 border-purple-500/30',
        orange: 'from-orange-500/20 to-orange-600/10 border-orange-500/30',
    };

    return (
        <div className={`stat-card bg-gradient-to-br ${colorClasses[color]}`}>
            <p className="text-gray-400 text-sm">{title}</p>
            <p className="text-4xl font-bold mt-2">{value}</p>
            <p className="text-gray-500 text-sm mt-1">{subtitle}</p>
        </div>
    );
}

function QuickAction({ title, description, href, icon }: {
    title: string;
    description: string;
    href: string;
    icon: string;
}) {
    const router = useRouter();

    return (
        <button
            onClick={() => router.push(href)}
            className="glass-card p-6 text-left hover:border-indigo-500/30 transition-all"
        >
            <span className="text-3xl">{icon}</span>
            <h3 className="font-semibold mt-3">{title}</h3>
            <p className="text-gray-400 text-sm mt-1">{description}</p>
        </button>
    );
}
