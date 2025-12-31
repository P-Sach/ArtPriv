-- SQL Schema for Supabase
-- Run this in the Supabase SQL Editor to create all tables

-- Drop existing types if they exist (for idempotency)
DROP TYPE IF EXISTS eligibility_status CASCADE;
DROP TYPE IF EXISTS test_report_source CASCADE;
DROP TYPE IF EXISTS counseling_status CASCADE;
DROP TYPE IF EXISTS counseling_method CASCADE;
DROP TYPE IF EXISTS consent_status CASCADE;
DROP TYPE IF EXISTS bank_state CASCADE;
DROP TYPE IF EXISTS donor_state CASCADE;

-- Create custom types (enums)
CREATE TYPE donor_state AS ENUM (
    'visitor',
    'bank_selected',
    'lead_created',
    'account_created',
    'counseling_requested',
    'consent_pending',
    'consent_verified',
    'tests_pending',
    'eligibility_decision',
    'donor_onboarded'
);

CREATE TYPE bank_state AS ENUM (
    'unregistered',
    'account_created',
    'verification_pending',
    'verified',
    'subscription_pending',
    'subscribed_onboarded',
    'operational'
);

CREATE TYPE consent_status AS ENUM (
    'pending',
    'signed',
    'verified',
    'rejected'
);

CREATE TYPE counseling_method AS ENUM (
    'call',
    'video',
    'in_person',
    'email'
);

CREATE TYPE counseling_status AS ENUM (
    'requested',
    'scheduled',
    'completed',
    'cancelled'
);

CREATE TYPE test_report_source AS ENUM (
    'bank_conducted'
);

CREATE TYPE eligibility_status AS ENUM (
    'pending',
    'approved',
    'rejected'
);

-- Drop existing tables if they exist (for idempotency)
DROP TABLE IF EXISTS bank_state_history CASCADE;
DROP TABLE IF EXISTS donor_state_history CASCADE;
DROP TABLE IF EXISTS test_reports CASCADE;
DROP TABLE IF EXISTS counseling_sessions CASCADE;
DROP TABLE IF EXISTS donor_consents CASCADE;
DROP TABLE IF EXISTS consent_templates CASCADE;
DROP TABLE IF EXISTS donors CASCADE;
DROP TABLE IF EXISTS banks CASCADE;

-- Banks table
CREATE TABLE banks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    state bank_state NOT NULL DEFAULT 'account_created',
    
    address TEXT,
    phone VARCHAR(50),
    website VARCHAR(255),
    description TEXT,
    
    certification_documents JSONB,
    
    is_verified BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMPTZ,
    verified_by VARCHAR(255),
    
    is_subscribed BOOLEAN DEFAULT FALSE,
    subscription_tier VARCHAR(100),
    subscription_started_at TIMESTAMPTZ,
    subscription_expires_at TIMESTAMPTZ,
    billing_details JSONB,
    
    counseling_config JSONB,
    logo_url VARCHAR(500),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_banks_email ON banks(email);
CREATE INDEX idx_banks_state ON banks(state);

-- Donors table
CREATE TABLE donors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE,
    hashed_password VARCHAR(255),
    state donor_state NOT NULL DEFAULT 'visitor',
    
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(50),
    date_of_birth TIMESTAMPTZ,
    address TEXT,
    
    medical_interest_info JSONB,
    
    bank_id UUID REFERENCES banks(id) ON DELETE SET NULL,
    selected_at TIMESTAMPTZ,
    
    legal_documents JSONB,
    
    consent_pending BOOLEAN DEFAULT FALSE,
    counseling_pending BOOLEAN DEFAULT FALSE,
    tests_pending BOOLEAN DEFAULT FALSE,
    
    eligibility_status eligibility_status DEFAULT 'pending',
    eligibility_notes TEXT,
    eligibility_decided_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_donors_email ON donors(email);
CREATE INDEX idx_donors_bank_id ON donors(bank_id);
CREATE INDEX idx_donors_state ON donors(state);

-- Consent templates table
CREATE TABLE consent_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bank_id UUID NOT NULL REFERENCES banks(id) ON DELETE CASCADE,
    
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    version VARCHAR(50) DEFAULT '1.0',
    "order" INTEGER DEFAULT 1,
    
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_consent_templates_bank_id ON consent_templates(bank_id);

-- Donor consents table
CREATE TABLE donor_consents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    donor_id UUID NOT NULL REFERENCES donors(id) ON DELETE CASCADE,
    template_id UUID NOT NULL REFERENCES consent_templates(id) ON DELETE CASCADE,
    
    status consent_status NOT NULL DEFAULT 'pending',
    
    signed_at TIMESTAMPTZ,
    signature_data JSONB,
    
    verified_at TIMESTAMPTZ,
    verified_by VARCHAR(255),
    verification_notes TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_donor_consents_donor_id ON donor_consents(donor_id);
CREATE INDEX idx_donor_consents_template_id ON donor_consents(template_id);

-- Counseling sessions table
CREATE TABLE counseling_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    donor_id UUID NOT NULL REFERENCES donors(id) ON DELETE CASCADE,
    bank_id UUID NOT NULL REFERENCES banks(id) ON DELETE CASCADE,
    
    status counseling_status NOT NULL DEFAULT 'requested',
    method counseling_method,
    
    requested_at TIMESTAMPTZ DEFAULT NOW(),
    scheduled_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    
    meeting_link VARCHAR(500),
    location VARCHAR(500),
    notes TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_counseling_sessions_donor_id ON counseling_sessions(donor_id);
CREATE INDEX idx_counseling_sessions_bank_id ON counseling_sessions(bank_id);

-- Test reports table
CREATE TABLE test_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    donor_id UUID NOT NULL REFERENCES donors(id) ON DELETE CASCADE,
    bank_id UUID NOT NULL REFERENCES banks(id) ON DELETE CASCADE,
    
    source test_report_source NOT NULL,
    
    test_type VARCHAR(100) NOT NULL,
    test_name VARCHAR(255) NOT NULL,
    file_url VARCHAR(500) NOT NULL,
    file_name VARCHAR(255),
    
    uploaded_by VARCHAR(255),
    uploaded_at TIMESTAMPTZ DEFAULT NOW(),
    
    test_date TIMESTAMPTZ,
    lab_name VARCHAR(255),
    notes TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_test_reports_donor_id ON test_reports(donor_id);
CREATE INDEX idx_test_reports_bank_id ON test_reports(bank_id);

-- Donor state history table
CREATE TABLE donor_state_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    donor_id UUID NOT NULL REFERENCES donors(id) ON DELETE CASCADE,
    
    from_state donor_state,
    to_state donor_state NOT NULL,
    
    changed_by VARCHAR(255),
    changed_by_role VARCHAR(50),
    reason TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_donor_state_history_donor_id ON donor_state_history(donor_id);

-- Bank state history table
CREATE TABLE bank_state_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bank_id UUID NOT NULL REFERENCES banks(id) ON DELETE CASCADE,
    
    from_state bank_state,
    to_state bank_state NOT NULL,
    
    changed_by VARCHAR(255),
    reason TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_bank_state_history_bank_id ON bank_state_history(bank_id);

-- Enable Row Level Security
ALTER TABLE banks ENABLE ROW LEVEL SECURITY;
ALTER TABLE donors ENABLE ROW LEVEL SECURITY;
ALTER TABLE consent_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE donor_consents ENABLE ROW LEVEL SECURITY;
ALTER TABLE counseling_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE test_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE donor_state_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE bank_state_history ENABLE ROW LEVEL SECURITY;

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add updated_at triggers
CREATE TRIGGER update_banks_updated_at BEFORE UPDATE ON banks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_donors_updated_at BEFORE UPDATE ON donors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_consent_templates_updated_at BEFORE UPDATE ON consent_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_donor_consents_updated_at BEFORE UPDATE ON donor_consents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_counseling_sessions_updated_at BEFORE UPDATE ON counseling_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_test_reports_updated_at BEFORE UPDATE ON test_reports
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Storage Buckets Setup
-- Run these commands to create storage buckets for file uploads

-- 1. Create buckets (run in Supabase Dashboard > Storage)
-- Note: Create these buckets manually in Supabase Dashboard or use the Supabase Storage API

-- Bucket: certification-documents (for bank certification PDFs)
-- insert into storage.buckets (id, name, public) values ('certification-documents', 'certification-documents', false);

-- Bucket: consent-forms (for consent form PDFs)
-- insert into storage.buckets (id, name, public) values ('consent-forms', 'consent-forms', false);

-- Bucket: test-reports (for donor and bank test report PDFs)
-- insert into storage.buckets (id, name, public) values ('test-reports', 'test-reports', false);

-- Bucket: counseling-reports (for counseling session reports/notes PDFs)
-- insert into storage.buckets (id, name, public) values ('counseling-reports', 'counseling-reports', false);

-- 2. Storage Policies (adjust based on your RLS requirements)
-- Allow authenticated users to upload to their respective buckets

-- Certification documents: Banks can upload
-- CREATE POLICY "Banks can upload certification documents"
-- ON storage.objects FOR INSERT
-- TO authenticated
-- WITH CHECK (bucket_id = 'certification-documents');

-- Banks can read their own certification documents
-- CREATE POLICY "Banks can read their certification documents"
-- ON storage.objects FOR SELECT
-- TO authenticated
-- USING (bucket_id = 'certification-documents');

-- Test reports: Banks and donors can upload
-- CREATE POLICY "Authenticated users can upload test reports"
-- ON storage.objects FOR INSERT
-- TO authenticated
-- WITH CHECK (bucket_id = 'test-reports');

-- Donors can read their own test reports, banks can read their donors' reports
-- CREATE POLICY "Users can read test reports"
-- ON storage.objects FOR SELECT
-- TO authenticated
-- USING (bucket_id = 'test-reports');

-- Consent forms: Donors can upload signatures
-- CREATE POLICY "Donors can upload consent forms"
-- ON storage.objects FOR INSERT
-- TO authenticated
-- WITH CHECK (bucket_id = 'consent-forms');

-- Users can read consent forms
-- CREATE POLICY "Users can read consent forms"
-- ON storage.objects FOR SELECT
-- TO authenticated
-- USING (bucket_id = 'consent-forms');

-- Counseling reports: Banks can upload
-- CREATE POLICY "Banks can upload counseling reports"
-- ON storage.objects FOR INSERT
-- TO authenticated
-- WITH CHECK (bucket_id = 'counseling-reports');

-- Donors and banks can read counseling reports
-- CREATE POLICY "Users can read counseling reports"
-- ON storage.objects FOR SELECT
-- TO authenticated
-- USING (bucket_id = 'counseling-reports');
