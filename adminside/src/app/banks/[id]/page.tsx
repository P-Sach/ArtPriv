'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import api from '@/lib/api';

interface BankDetail {
    id: string;
    email: string;
    name: string;
    state: string;
    phone: string | null;
    address: string | null;
    website: string | null;
    is_verified: boolean;
    verified_at: string | null;
    is_subscribed: boolean;
    subscription_tier: string | null;
    subscription_started_at: string | null;
    subscription_expires_at: string | null;
    donor_count: number;
    created_at: string;
}

export default function BankDetailPage() {
    const [bank, setBank] = useState<BankDetail | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const router = useRouter();
    const params = useParams();
    const bankId = params.id as string;

    useEffect(() => {
        const fetchBank = async () => {
            try {
                const data = await api.getBank(bankId);
                setBank(data);
            } catch (err) {
                if (err instanceof Error && err.message.includes('401')) {
                    router.push('/login');
                } else {
                    setError(err instanceof Error ? err.message : 'Failed to load bank');
                }
            } finally {
                setLoading(false);
            }
        };

        if (bankId) {
            fetchBank();
        }
    }, [bankId, router]);

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-xl text-gray-400">Loading bank details...</div>
            </div>
        );
    }

    if (error || !bank) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-red-400">{error || 'Bank not found'}</div>
            </div>
        );
    }

    const getSubscriptionStatus = () => {
        if (!bank.is_subscribed) return { text: 'Not Subscribed', class: 'badge-warning' };
        if (bank.subscription_expires_at) {
            const expiry = new Date(bank.subscription_expires_at);
            const now = new Date();
            const daysUntilExpiry = Math.ceil((expiry.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));

            if (daysUntilExpiry < 0) return { text: 'Expired', class: 'badge-danger' };
            if (daysUntilExpiry <= 30) return { text: `Expiring in ${daysUntilExpiry}d`, class: 'badge-warning' };
        }
        return { text: bank.subscription_tier || 'Active', class: 'badge-success' };
    };

    const subscriptionStatus = getSubscriptionStatus();

    return (
        <div className="min-h-screen p-8">
            <div className="max-w-4xl mx-auto">
                <header className="mb-8 flex justify-between items-center">
                    <div>
                        <button onClick={() => router.push('/banks')} className="text-gray-400 hover:text-white mb-2">
                            ← Back to Banks
                        </button>
                        <h1 className="text-3xl font-bold">{bank.name}</h1>
                        <p className="text-gray-400 mt-1">{bank.email}</p>
                    </div>
                    <div className="flex gap-2">
                        <span className={`badge ${bank.is_verified ? 'badge-success' : 'badge-warning'}`}>
                            {bank.is_verified ? 'Verified' : 'Unverified'}
                        </span>
                        <span className={`badge ${subscriptionStatus.class}`}>
                            {subscriptionStatus.text}
                        </span>
                    </div>
                </header>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Basic Info */}
                    <div className="glass-card p-6">
                        <h2 className="text-xl font-semibold mb-4">Basic Information</h2>
                        <div className="space-y-4">
                            <InfoRow label="State" value={bank.state.replace('_', ' ')} />
                            <InfoRow label="Phone" value={bank.phone || 'Not provided'} />
                            <InfoRow label="Website" value={bank.website || 'Not provided'} isLink={!!bank.website} />
                            <InfoRow label="Address" value={bank.address || 'Not provided'} />
                            <InfoRow label="Donor Count" value={bank.donor_count.toString()} />
                            <InfoRow label="Created" value={new Date(bank.created_at).toLocaleDateString()} />
                        </div>
                    </div>

                    {/* Verification Status */}
                    <div className="glass-card p-6">
                        <h2 className="text-xl font-semibold mb-4">Verification Status</h2>
                        <div className="space-y-4">
                            <div className="flex items-center gap-3">
                                <div className={`w-4 h-4 rounded-full ${bank.is_verified ? 'bg-green-500' : 'bg-yellow-500'}`} />
                                <span className="text-lg">{bank.is_verified ? 'Verified' : 'Pending Verification'}</span>
                            </div>
                            {bank.verified_at && (
                                <InfoRow label="Verified On" value={new Date(bank.verified_at).toLocaleDateString()} />
                            )}
                            {!bank.is_verified && (
                                <button className="btn-primary w-full mt-4">
                                    Verify Bank
                                </button>
                            )}
                        </div>
                    </div>

                    {/* Subscription Details */}
                    <div className="glass-card p-6 md:col-span-2">
                        <h2 className="text-xl font-semibold mb-4">Subscription Details</h2>
                        {bank.is_subscribed ? (
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div className="p-4 rounded-lg bg-white/5">
                                    <p className="text-gray-400 text-sm">Tier</p>
                                    <p className="text-2xl font-bold text-indigo-400">{bank.subscription_tier}</p>
                                </div>
                                <div className="p-4 rounded-lg bg-white/5">
                                    <p className="text-gray-400 text-sm">Started</p>
                                    <p className="text-lg">
                                        {bank.subscription_started_at
                                            ? new Date(bank.subscription_started_at).toLocaleDateString()
                                            : 'N/A'}
                                    </p>
                                </div>
                                <div className="p-4 rounded-lg bg-white/5">
                                    <p className="text-gray-400 text-sm">Expires</p>
                                    <p className="text-lg">
                                        {bank.subscription_expires_at
                                            ? new Date(bank.subscription_expires_at).toLocaleDateString()
                                            : 'N/A'}
                                    </p>
                                </div>
                            </div>
                        ) : (
                            <div className="text-center py-8">
                                <p className="text-gray-400 mb-4">This bank does not have an active subscription</p>
                                <button className="btn-primary">
                                    Add Subscription
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

function InfoRow({ label, value, isLink = false }: { label: string; value: string; isLink?: boolean }) {
    return (
        <div className="flex justify-between">
            <span className="text-gray-400">{label}</span>
            {isLink ? (
                <a href={value} target="_blank" rel="noopener noreferrer" className="text-indigo-400 hover:underline">
                    {value}
                </a>
            ) : (
                <span>{value}</span>
            )}
        </div>
    );
}
