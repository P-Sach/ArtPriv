'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';

interface Donor {
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
}

interface DonorListResponse {
    items: Donor[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
}

const DONOR_STATES = [
    'visitor', 'bank_selected', 'lead_created', 'account_created',
    'counseling_requested', 'consent_pending', 'consent_verified',
    'tests_pending', 'eligibility_decision', 'donor_onboarded'
];

export default function DonorsPage() {
    const [data, setData] = useState<DonorListResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [stateFilter, setStateFilter] = useState('');
    const router = useRouter();

    useEffect(() => {
        fetchDonors();
    }, [stateFilter]);

    const fetchDonors = async () => {
        try {
            setLoading(true);
            const params: any = {};
            if (stateFilter) params.state = stateFilter;
            if (search) params.search = search;

            const response = await api.getDonors(params);
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
        fetchDonors();
    };

    const getStateBadge = (state: string) => {
        if (state === 'donor_onboarded') return 'badge-success';
        if (['consent_verified', 'tests_pending', 'eligibility_decision'].includes(state)) return 'badge-info';
        if (['visitor', 'bank_selected', 'lead_created'].includes(state)) return 'badge-warning';
        return 'badge-info';
    };

    const getEligibilityBadge = (status: string) => {
        if (status === 'approved') return 'badge-success';
        if (status === 'rejected') return 'badge-danger';
        return 'badge-warning';
    };

    return (
        <div className="min-h-screen p-8">
            <div className="max-w-7xl mx-auto">
                <header className="mb-8 flex justify-between items-center">
                    <div>
                        <h1 className="text-3xl font-bold">Donors</h1>
                        <p className="text-gray-400 mt-1">View all donors across all banks</p>
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
                            placeholder="Search by name or email..."
                            className="glass-input max-w-xs"
                        />
                        <button type="submit" className="btn-primary">Search</button>
                    </form>

                    <select
                        value={stateFilter}
                        onChange={(e) => setStateFilter(e.target.value)}
                        className="glass-input max-w-xs"
                    >
                        <option value="">All States</option>
                        {DONOR_STATES.map((state) => (
                            <option key={state} value={state}>
                                {state.replace('_', ' ')}
                            </option>
                        ))}
                    </select>
                </div>

                {/* Table */}
                <div className="glass-card overflow-hidden">
                    {loading ? (
                        <div className="p-8 text-center text-gray-400">Loading donors...</div>
                    ) : (
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Email</th>
                                    <th>Bank</th>
                                    <th>State</th>
                                    <th>Eligibility</th>
                                    <th>Created</th>
                                </tr>
                            </thead>
                            <tbody>
                                {data?.items.map((donor) => (
                                    <tr key={donor.id} className="cursor-pointer" onClick={() => router.push(`/donors/${donor.id}`)}>
                                        <td className="font-medium">
                                            {donor.first_name && donor.last_name
                                                ? `${donor.first_name} ${donor.last_name}`
                                                : 'Unknown'}
                                        </td>
                                        <td className="text-gray-400">{donor.email || '-'}</td>
                                        <td>{donor.bank_name || <span className="text-gray-500">No bank</span>}</td>
                                        <td>
                                            <span className={`badge ${getStateBadge(donor.state)}`}>
                                                {donor.state.replace('_', ' ')}
                                            </span>
                                        </td>
                                        <td>
                                            <span className={`badge ${getEligibilityBadge(donor.eligibility_status)}`}>
                                                {donor.eligibility_status}
                                            </span>
                                        </td>
                                        <td className="text-gray-400">{new Date(donor.created_at).toLocaleDateString()}</td>
                                    </tr>
                                ))}
                                {(!data?.items || data.items.length === 0) && (
                                    <tr>
                                        <td colSpan={6} className="text-center text-gray-400 py-8">
                                            No donors found
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    )}
                </div>

                {/* Summary */}
                <div className="mt-4 text-gray-400 text-sm">
                    Showing {data?.items.length || 0} of {data?.total || 0} donors
                </div>
            </div>
        </div>
    );
}
