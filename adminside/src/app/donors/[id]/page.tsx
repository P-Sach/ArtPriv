'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import api from '@/lib/api';

interface StateHistoryItem {
    id: string;
    from_state: string | null;
    to_state: string;
    changed_by: string | null;
    changed_by_role: string | null;
    reason: string | null;
    created_at: string;
}

interface DonorDetail {
    id: string;
    email: string | null;
    first_name: string | null;
    last_name: string | null;
    phone: string | null;
    state: string;
    bank_id: string | null;
    bank_name: string | null;
    eligibility_status: string;
    created_at: string;
    address: string | null;
    date_of_birth: string | null;
    medical_interest_info: Record<string, any> | null;
    eligibility_notes: string | null;
    selected_at: string | null;
    consent_pending: boolean;
    counseling_pending: boolean;
    tests_pending: boolean;
    state_history: StateHistoryItem[];
}

export default function DonorDetailPage() {
    const [donor, setDonor] = useState<DonorDetail | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const router = useRouter();
    const params = useParams();
    const donorId = params.id as string;

    useEffect(() => {
        const fetchDonor = async () => {
            try {
                const data = await api.getDonor(donorId);
                setDonor(data);
            } catch (err) {
                if (err instanceof Error && err.message.includes('401')) {
                    router.push('/login');
                } else {
                    setError(err instanceof Error ? err.message : 'Failed to load donor');
                }
            } finally {
                setLoading(false);
            }
        };

        if (donorId) {
            fetchDonor();
        }
    }, [donorId, router]);

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-xl text-gray-400">Loading donor details...</div>
            </div>
        );
    }

    if (error || !donor) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-red-400">{error || 'Donor not found'}</div>
            </div>
        );
    }

    const getStateBadgeClass = (state: string) => {
        if (state === 'donor_onboarded') return 'badge-success';
        if (['consent_verified', 'tests_pending', 'eligibility_decision'].includes(state)) return 'badge-info';
        return 'badge-warning';
    };

    const getEligibilityBadgeClass = (status: string) => {
        if (status === 'approved') return 'badge-success';
        if (status === 'rejected') return 'badge-danger';
        return 'badge-warning';
    };

    const fullName = donor.first_name && donor.last_name
        ? `${donor.first_name} ${donor.last_name}`
        : 'Unknown Donor';

    return (
        <div className="min-h-screen p-8">
            <div className="max-w-4xl mx-auto">
                <header className="mb-8 flex justify-between items-center">
                    <div>
                        <button onClick={() => router.push('/donors')} className="text-gray-400 hover:text-white mb-2">
                            ← Back to Donors
                        </button>
                        <h1 className="text-3xl font-bold">{fullName}</h1>
                        <p className="text-gray-400 mt-1">{donor.email || 'No email'}</p>
                    </div>
                    <div className="flex gap-2">
                        <span className={`badge ${getStateBadgeClass(donor.state)}`}>
                            {donor.state.replace('_', ' ')}
                        </span>
                        <span className={`badge ${getEligibilityBadgeClass(donor.eligibility_status)}`}>
                            {donor.eligibility_status}
                        </span>
                    </div>
                </header>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Personal Info */}
                    <div className="glass-card p-6">
                        <h2 className="text-xl font-semibold mb-4">Personal Information</h2>
                        <div className="space-y-4">
                            <InfoRow label="First Name" value={donor.first_name || 'Not provided'} />
                            <InfoRow label="Last Name" value={donor.last_name || 'Not provided'} />
                            <InfoRow label="Phone" value={donor.phone || 'Not provided'} />
                            <InfoRow label="Date of Birth" value={donor.date_of_birth ? new Date(donor.date_of_birth).toLocaleDateString() : 'Not provided'} />
                            <InfoRow label="Address" value={donor.address || 'Not provided'} />
                        </div>
                    </div>

                    {/* Bank & Status */}
                    <div className="glass-card p-6">
                        <h2 className="text-xl font-semibold mb-4">Bank & Status</h2>
                        <div className="space-y-4">
                            <InfoRow label="Bank" value={donor.bank_name || 'No bank assigned'} />
                            <InfoRow label="Selected At" value={donor.selected_at ? new Date(donor.selected_at).toLocaleDateString() : 'N/A'} />
                            <InfoRow label="Created" value={new Date(donor.created_at).toLocaleDateString()} />
                            <div className="pt-4 border-t border-white/10">
                                <p className="text-gray-400 text-sm mb-2">Pending Actions</p>
                                <div className="flex gap-2 flex-wrap">
                                    {donor.consent_pending && <span className="badge badge-warning">Consent Pending</span>}
                                    {donor.counseling_pending && <span className="badge badge-warning">Counseling Pending</span>}
                                    {donor.tests_pending && <span className="badge badge-warning">Tests Pending</span>}
                                    {!donor.consent_pending && !donor.counseling_pending && !donor.tests_pending && (
                                        <span className="text-gray-500">No pending actions</span>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Eligibility */}
                    <div className="glass-card p-6">
                        <h2 className="text-xl font-semibold mb-4">Eligibility</h2>
                        <div className="flex items-center gap-3 mb-4">
                            <div className={`w-4 h-4 rounded-full ${donor.eligibility_status === 'approved' ? 'bg-green-500' :
                                    donor.eligibility_status === 'rejected' ? 'bg-red-500' : 'bg-yellow-500'
                                }`} />
                            <span className="text-lg capitalize">{donor.eligibility_status}</span>
                        </div>
                        {donor.eligibility_notes && (
                            <div className="p-4 rounded-lg bg-white/5">
                                <p className="text-gray-400 text-sm mb-1">Notes</p>
                                <p>{donor.eligibility_notes}</p>
                            </div>
                        )}
                    </div>

                    {/* Medical Interest */}
                    <div className="glass-card p-6">
                        <h2 className="text-xl font-semibold mb-4">Medical Interest Info</h2>
                        {donor.medical_interest_info && Object.keys(donor.medical_interest_info).length > 0 ? (
                            <div className="space-y-2">
                                {Object.entries(donor.medical_interest_info).map(([key, value]) => (
                                    <InfoRow key={key} label={key.replace('_', ' ')} value={String(value)} />
                                ))}
                            </div>
                        ) : (
                            <p className="text-gray-500">No medical interest information available</p>
                        )}
                    </div>

                    {/* State History */}
                    <div className="glass-card p-6 md:col-span-2">
                        <h2 className="text-xl font-semibold mb-4">State History</h2>
                        {donor.state_history && donor.state_history.length > 0 ? (
                            <div className="space-y-4">
                                {donor.state_history.map((item, index) => (
                                    <div key={item.id} className="flex items-start gap-4 p-4 rounded-lg bg-white/5">
                                        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-indigo-500/20 flex items-center justify-center text-indigo-400 text-sm">
                                            {donor.state_history.length - index}
                                        </div>
                                        <div className="flex-1">
                                            <div className="flex items-center gap-2 mb-1">
                                                {item.from_state && (
                                                    <>
                                                        <span className="text-gray-400">{item.from_state.replace('_', ' ')}</span>
                                                        <span className="text-gray-600">→</span>
                                                    </>
                                                )}
                                                <span className="font-medium">{item.to_state.replace('_', ' ')}</span>
                                            </div>
                                            <div className="text-sm text-gray-500">
                                                {new Date(item.created_at).toLocaleString()}
                                                {item.changed_by && ` • by ${item.changed_by}`}
                                                {item.changed_by_role && ` (${item.changed_by_role})`}
                                            </div>
                                            {item.reason && <p className="text-sm text-gray-400 mt-1">{item.reason}</p>}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-gray-500">No state history available</p>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

function InfoRow({ label, value }: { label: string; value: string }) {
    return (
        <div className="flex justify-between">
            <span className="text-gray-400">{label}</span>
            <span>{value}</span>
        </div>
    );
}
