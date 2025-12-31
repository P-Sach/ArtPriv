You are building a backend-only system for a platform that connects donors and banks.
The system has two distinct user types: donors and banks, each with separate dashboards and permissions.
Banks must be verified and subscribed before they can interact with donors.
Donors progress through a staged onboarding process involving personal details, counseling, consent, medical testing, and eligibility review.
Banks control counseling rules, verify consents, review test reports, and make the final eligibility decision.
The system must enforce strict state transitions, ensuring that donors cannot self-advance past steps that require bank approval.
Test reports may originate from either banks or donors but must always be accessible to donors.
All workflows must be auditable, state-driven, and bank-authoritative where medical or legal decisions are involved.