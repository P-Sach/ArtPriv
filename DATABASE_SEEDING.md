# Database Seeding - Quick Reference

## Overview
The database has been populated with realistic dummy data for testing the complete ART Connect platform.

## What Was Created

### 🏦 Banks (8 Total)
Realistic fertility banks across major Indian cities with complete information:

1. **LifeSpring Fertility Bank** - Mumbai
   - Email: contact@lifespring.in
   - Status: Operational, Verified, Subscribed (Professional)
   - Donors: 2

2. **Nova Reproductive Health Center** - Delhi
   - Email: info@nova-fertility.com
   - Status: Operational, Verified, Subscribed (Enterprise)
   - Donors: 2

3. **Genesis Fertility Solutions** - Bangalore
   - Email: hello@genesis-fertility.in
   - Status: Operational, Verified, Subscribed (Professional)
   - Donors: 2

4. **Bloom Fertility Bank** - Hyderabad
   - Email: support@bloomfertility.com
   - Status: Operational, Verified, Subscribed (Starter)
   - Donors: 2

5. **Radiance Reproductive Bank** - Chennai
   - Email: info@radiancebank.in
   - Status: Operational, Verified, Subscribed (Professional)
   - Donors: 2

6. **Hope Fertility Center** - Pune
   - Email: contact@hopefertility.in
   - Status: Verified (not subscribed yet)
   - Donors: 2

7. **Serenity Reproductive Solutions** - Ahmedabad
   - Email: info@serenity-fertility.com
   - Status: Operational, Verified, Subscribed (Starter)
   - Donors: 2

8. **Zenith Fertility Bank** - Kolkata
   - Email: hello@zenithfertility.in
   - Status: Verification Pending
   - Donors: 0

### 👥 Donors (15 Total)
15 donors with varying states in the onboarding process:

- **Fully Onboarded (7):** Priya Sharma, Kavya Patel, Divya Nair, Riya Agarwal, Lakshmi Iyer, Isha Mehta
- **In Process (7):** Anjali Reddy (consent verified), Sneha Kumar (tests pending), Meera Singh (counseling requested), Aditi Verma (consent pending), Pooja Desai (eligibility decision), Neha Joshi (account created), Simran Kapoor (lead created)
- **Visitors (1):** Aisha Khan (bank selected), Tanvi Shah (no bank yet)

### 📄 Consent Templates
4 consent templates created for each operational bank:
- General Consent Form
- Medical Information Release
- Privacy Policy Agreement
- Legal Rights Acknowledgment

## 🔑 Login Credentials

**Default Password for ALL accounts:** `password123`

### Bank Login Examples:
- contact@lifespring.in
- info@nova-fertility.com
- hello@genesis-fertility.in
- support@bloomfertility.com
- info@radiancebank.in

### Donor Login Examples:
- priya.sharma@example.com
- anjali.reddy@example.com
- kavya.patel@example.com
- sneha.kumar@example.com
- divya.nair@example.com

## 📂 Scripts Available

### `seed_data.py`
Adds dummy data to the database (can be run multiple times)

### `view_data.py`
Displays all existing banks and donors in the database

### `clear_data.py`
Clears all data from the database (requires confirmation)

### `reset_database.py`
Complete reset: clears all data and reseeds with dummy data

## 🚀 Usage

To view current data:
```bash
cd backend
python view_data.py
```

To reset and reseed:
```bash
cd backend
python reset_database.py
```

To add more data (without clearing):
```bash
cd backend
python seed_data.py
```

## 📊 Data Distribution

- **By City:**
  - Mumbai: 1 bank, 2 donors
  - Delhi: 1 bank, 2 donors
  - Bangalore: 1 bank, 2 donors
  - Hyderabad: 1 bank, 2 donors
  - Chennai: 1 bank, 2 donors
  - Pune: 1 bank, 2 donors
  - Ahmedabad: 1 bank, 2 donors
  - Kolkata: 1 bank, 0 donors
  - No bank: 1 donor

- **By Donor State:**
  - donor_onboarded: 7
  - consent_verified: 1
  - tests_pending: 1
  - counseling_requested: 1
  - consent_pending: 1
  - eligibility_decision: 1
  - account_created: 1
  - lead_created: 1
  - bank_selected: 1

- **By Bank State:**
  - operational: 7 banks
  - verified: 1 bank
  - verification_pending: 1 bank

## ✅ Testing Workflows

You can now test:
1. **Bank login** - Use any bank email with password123
2. **Donor login** - Use any donor email with password123
3. **Bank dashboard** - View registered donors for each bank
4. **Donor workflows** - Test different states (onboarded, pending tests, etc.)
5. **Search functionality** - Search for donors across different cities
6. **Subscription tiers** - Different banks have different subscription levels
7. **Verification states** - Test with verified and unverified banks

## 🎯 Next Steps

1. Login to any bank or donor account
2. Explore the dashboards
3. Test the onboarding workflows
4. Verify data persistence through the backend
5. Test API endpoints with real data

---

**Note:** All data is for testing purposes only. All emails are dummy addresses and passwords are intentionally weak for development.
