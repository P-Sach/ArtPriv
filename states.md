A. Donor State Machine
States & Transitions
Visitor
Browses donor site
Views banks by location
Can read basic info only
Bank Selected
Donor selects a specific bank
Bank context is locked for the onboarding journey
Lead Created
Donor submits personal + medical interest info
Lead exists, not a full user yet
Status flags may include:
Consent pending
Counseling pending
Tests pending
Account Created
Donor creates login (email/password + OTP)
Legal documents uploaded if required
Can access donor dashboard
Counseling Requested
Donor requests counseling
Bank-specific rules apply:
Available time slots
Allowed contact methods (call / video / in-person / email)
Bank schedules or confirms counseling
Consent Pending
Donor views 4 mandatory bank-specific consent forms
Each form has:
Bank logo
Bank legal details
Donor identity
Donor digitally signs / accepts
Awaiting bank verification
Consent Verified (Bank Action)
Bank reviews consent
Bank confirms validity
Donor cannot self-advance here
Tests Pending
Bank decides testing approach:
Bank-conducted tests
OR donor uploads third-party test reports
Both sources are allowed
Donor can view/download all reports
Eligibility Decision (Bank Final Authority)
Bank reviews test reports
Bank explicitly approves or rejects donor
No automatic progression allowed
Donor Onboarded
Eligible donor moves from “lead” to “active donor”
Full donor profile is created
Linked permanently to the bank
B. Bank State Machine
States & Transitions
Unregistered Bank Visitor
Lands on bank onboarding page
Bank Account Created
Email + password login
Basic bank info submitted
Certification documents uploaded
Verification Pending
Bank cannot access platform features
Admin review required
Verified Bank
Bank is approved by platform
Can proceed to subscription
Subscription Pending
Bank enters financial details
Chooses pricing tier
Subscribed & Onboarded
Payment successful
Bank dashboard activated
Operational Bank
Can:
View donor leads
Configure counseling rules
Upload consent templates
Upload or review test reports
Approve or reject donors
2. High-Level Bank Flow (Clean Narrative)
Bank onboarding happens before donor interaction is meaningful.
Bank signs up using email and password
Submits:
Basic bank information
Official certification documents
Bank waits for platform verification
Once verified:
Bank enters account and billing details
Chooses and pays for subscription
Bank gains access to dashboard
Bank configures:
Counseling timings
Allowed contact methods
Consent documents (with logo & details)
Bank can now receive and manage donor leads
Until verification + subscription is complete, banks cannot influence donors.
