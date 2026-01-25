-- NecoKeeper Demo Data (English)
-- Generated: 2025-12-01

-- Disable foreign key checks during data manipulation
PRAGMA foreign_keys = OFF;

-- Clear existing data (in reverse dependency order)
DELETE FROM adoption_records;
DELETE FROM medical_records;
DELETE FROM care_logs;
DELETE FROM medical_actions;
DELETE FROM applicants;
DELETE FROM volunteers;
DELETE FROM status_history;
DELETE FROM animal_images;
DELETE FROM animals;
DELETE FROM audit_logs;
-- Keep users but update them
DELETE FROM users;

-- Reset auto-increment counters
DELETE FROM sqlite_sequence WHERE name IN ('animals', 'care_logs', 'medical_actions', 'medical_records', 'adoption_records', 'users', 'volunteers', 'applicants', 'animal_images', 'status_history', 'audit_logs');

-- =============================================================================
-- 1. USERS (Admin, Vet, Staff)
-- =============================================================================
-- Password hash for 'password123' using argon2id
INSERT INTO users (id, email, password_hash, name, role, is_active, failed_login_count, created_at, updated_at) VALUES
(1, 'admin@necokeeper.example', '$argon2id$v=19$m=65536,t=3,p=4$6PNLyXzekFCUKrQg5djI/A$g8ODU8lj28Cn6nTUTrSo5USCPd/ikTyifFHKwZgXJBg', 'Admin User', 'admin', 1, 0, '2025-01-01 09:00:00', '2025-01-01 09:00:00'),
(2, 'vet@necokeeper.example', '$argon2id$v=19$m=65536,t=3,p=4$hxVYC0Vz/043pDcyzM/4Hg$YlpwpcV8+X3yoSg84WL1GayiZ7YqOo/s3/DM1HC8gwY', 'Dr. Emily Smith', 'vet', 1, 0, '2025-01-01 09:00:00', '2025-01-01 09:00:00'),
(3, 'staff@necokeeper.example', '$argon2id$v=19$m=65536,t=3,p=4$6PNLyXzekFCUKrQg5djI/A$g8ODU8lj28Cn6nTUTrSo5USCPd/ikTyifFHKwZgXJBg', 'Jane Doe', 'staff', 1, 0, '2025-01-01 09:00:00', '2025-01-01 09:00:00');

-- =============================================================================
-- 2. VOLUNTEERS
-- =============================================================================
INSERT INTO volunteers (id, name, contact, affiliation, status, started_at, created_at, updated_at) VALUES
(1, 'Sarah Johnson', 'sarah@example.com', 'Happy Paws Shelter', 'active', '2025-05-01', '2025-05-01 10:00:00', '2025-05-01 10:00:00'),
(2, 'Mike Brown', 'mike@example.com', 'Happy Paws Shelter', 'active', '2025-06-15', '2025-06-15 10:00:00', '2025-06-15 10:00:00'),
(3, 'Lisa Chen', 'lisa@example.com', NULL, 'active', '2025-07-20', '2025-07-20 10:00:00', '2025-07-20 10:00:00'),
(4, 'David Wilson', 'david@example.com', NULL, 'active', '2025-08-01', '2025-08-01 10:00:00', '2025-08-01 10:00:00');

-- =============================================================================
-- 3. ANIMALS (5 cats)
-- =============================================================================
INSERT INTO animals (id, name, photo, pattern, tail_length, collar, age, gender, ear_cut, features, status, protected_at, created_at, updated_at) VALUES
(1, 'Luna', NULL, 'Black', 'Long', NULL, 'Adult (2 years)', 'female', 0, 'Friendly and calm. Loves being petted. Very gentle with people.', 'Adoptable', '2025-06-15', '2025-06-15 14:00:00', '2025-11-20 10:00:00'),
(2, 'Oliver', NULL, 'Ginger (Orange tabby)', 'Long', 'Blue collar with bell', 'Adult (1 year)', 'male', 0, 'Playful and curious. Gets along well with other cats. Loves toys.', 'In Care', '2025-08-20', '2025-08-20 11:00:00', '2025-11-25 09:00:00'),
(3, 'Misty', NULL, 'White', 'Long', NULL, 'Adult (3 years)', 'female', 0, 'Quiet and independent. Prefers to be the only pet. Enjoys sunny spots.', 'In Care', '2025-04-10', '2025-04-10 15:00:00', '2025-11-28 14:00:00'),
(4, 'Shadow', NULL, 'Grey', 'Long', NULL, 'Adult (4 years)', 'male', 1, 'Shy at first but very affectionate once comfortable. Ear-tipped (TNR). Currently receiving treatment for eye condition.', 'Treatment', '2025-09-05', '2025-09-05 09:00:00', '2025-11-30 11:00:00'),
(5, 'Bella', NULL, 'Calico', 'Short', 'Pink collar', 'Kitten (6 months)', 'female', 0, 'Very energetic and playful. Good with children. Loves climbing and exploring.', 'Adoptable', '2025-09-20', '2025-09-20 16:00:00', '2025-11-29 15:00:00');

-- =============================================================================
-- 4. MEDICAL ACTIONS (Treatment/Medicine Master - USD)
-- =============================================================================
INSERT INTO medical_actions (id, name, valid_from, valid_to, cost_price, selling_price, procedure_fee, currency, unit, created_at, updated_at, last_updated_at, last_updated_by) VALUES
(1, 'FVRCP Vaccine', '2025-01-01', NULL, 12.00, 25.00, 15.00, 'USD', 'dose', '2025-01-01 09:00:00', '2025-01-01 09:00:00', '2025-01-01 09:00:00', 1),
(2, 'Rabies Vaccine', '2025-01-01', NULL, 8.00, 20.00, 15.00, 'USD', 'dose', '2025-01-01 09:00:00', '2025-01-01 09:00:00', '2025-01-01 09:00:00', 1),
(3, 'Dewormer (Oral)', '2025-01-01', NULL, 5.00, 15.00, 10.00, 'USD', 'tablet', '2025-01-01 09:00:00', '2025-01-01 09:00:00', '2025-01-01 09:00:00', 1),
(4, 'Flea Treatment', '2025-01-01', NULL, 10.00, 25.00, 10.00, 'USD', 'application', '2025-01-01 09:00:00', '2025-01-01 09:00:00', '2025-01-01 09:00:00', 1),
(5, 'Antibiotic (Amoxicillin)', '2025-01-01', NULL, 3.00, 10.00, 5.00, 'USD', 'ml', '2025-01-01 09:00:00', '2025-01-01 09:00:00', '2025-01-01 09:00:00', 1),
(6, 'Anti-inflammatory', '2025-01-01', NULL, 4.00, 12.00, 5.00, 'USD', 'tablet', '2025-01-01 09:00:00', '2025-01-01 09:00:00', '2025-01-01 09:00:00', 1),
(7, 'Blood Test (Basic Panel)', '2025-01-01', NULL, 20.00, 50.00, 20.00, 'USD', 'test', '2025-01-01 09:00:00', '2025-01-01 09:00:00', '2025-01-01 09:00:00', 1),
(8, 'Spay/Neuter Surgery', '2025-01-01', NULL, 50.00, 120.00, 80.00, 'USD', 'procedure', '2025-01-01 09:00:00', '2025-01-01 09:00:00', '2025-01-01 09:00:00', 1);

-- =============================================================================
-- 5. APPLICANTS (Potential Adopters)
-- =============================================================================
INSERT INTO applicants (id, name, contact, address, family, environment, conditions, created_at, updated_at) VALUES
(1, 'John Miller', 'john.miller@email.com', '123 Oak Street, Springfield', 'Married couple, no children', 'House with backyard, no other pets', 'Prefer adult cat, calm personality', '2025-10-15 14:00:00', '2025-10-15 14:00:00'),
(2, 'Emma Thompson', 'emma.t@email.com', '456 Maple Avenue, Riverside', 'Single, experienced cat owner', 'Apartment with cat-proofed balcony', 'Any age welcome, loves playful cats', '2025-11-01 11:00:00', '2025-11-01 11:00:00'),
(3, 'Robert & Mary Davis', 'davis.family@email.com', '789 Pine Road, Lakewood', 'Family with 2 children (ages 10 and 12)', 'Large house with fenced yard', 'Kitten or young cat, must be good with kids', '2025-11-15 16:00:00', '2025-11-15 16:00:00');

-- =============================================================================
-- 6. MEDICAL RECORDS (10 records)
-- =============================================================================
INSERT INTO medical_records (id, animal_id, vet_id, date, time_slot, weight, temperature, symptoms, medical_action_id, dosage, other, comment, created_at, updated_at, last_updated_at, last_updated_by) VALUES
-- Luna's records
(1, 1, 2, '2025-06-20', 'morning', 3.80, 38.5, 'Initial health check after rescue. Good overall condition.', 1, 1, 'Lot: FVRCP-2025-A1', 'First vaccination administered. Schedule second dose in 3-4 weeks.', '2025-06-20 10:30:00', '2025-06-20 10:30:00', '2025-06-20 10:30:00', 2),
(2, 1, 2, '2025-07-15', 'morning', 4.00, 38.3, 'Follow-up checkup. Healthy and gaining weight well.', 3, 1, NULL, 'Routine deworming completed. Ready for adoption.', '2025-07-15 11:00:00', '2025-07-15 11:00:00', '2025-07-15 11:00:00', 2),
-- Oliver's records
(3, 2, 2, '2025-08-25', 'afternoon', 4.20, 38.4, 'Brought in with minor scratches on left ear. Possibly from a fight.', 5, 5, NULL, 'Antibiotic treatment for 5 days. Monitor healing.', '2025-08-25 14:00:00', '2025-08-25 14:00:00', '2025-08-25 14:00:00', 2),
(4, 2, 2, '2025-09-10', 'morning', 4.50, 38.2, 'Routine vaccination visit. Scratches healed completely.', 1, 1, 'Lot: FVRCP-2025-B2', 'Vaccination completed. Cat is healthy and social.', '2025-09-10 09:30:00', '2025-09-10 09:30:00', '2025-09-10 09:30:00', 2),
-- Misty's records
(5, 3, 2, '2025-04-15', 'morning', 3.50, 38.6, 'Slight fever, loss of appetite for 2 days.', 6, 2, NULL, 'Anti-inflammatory prescribed. Recheck in 2 weeks.', '2025-04-15 10:00:00', '2025-04-15 10:00:00', '2025-04-15 10:00:00', 2),
(6, 3, 2, '2025-05-01', 'morning', 3.60, 38.3, 'Recovery check. Full recovery observed.', NULL, NULL, NULL, 'Appetite back to normal. No further treatment needed.', '2025-05-01 10:30:00', '2025-05-01 10:30:00', '2025-05-01 10:30:00', 2),
-- Shadow's records (under treatment)
(7, 4, 2, '2025-09-10', 'morning', 5.00, 39.0, 'Eye infection detected. Discharge from left eye.', 5, 7, NULL, 'Started antibiotic treatment. Daily eye drops required.', '2025-09-10 09:00:00', '2025-09-10 09:00:00', '2025-09-10 09:00:00', 2),
(8, 4, 2, '2025-10-01', 'morning', 5.10, 38.5, 'Eye infection follow-up. Condition improving slowly.', 5, 3, NULL, 'Continue treatment for another week. Monitor closely.', '2025-10-01 09:30:00', '2025-10-01 09:30:00', '2025-10-01 09:30:00', 2),
(9, 4, 2, '2025-11-15', 'morning', 5.20, 38.3, 'Blood test for ongoing treatment monitoring.', 7, 1, 'Lab ref: BT-2025-1115', 'Blood panel results normal. Continue current care plan.', '2025-11-15 10:00:00', '2025-11-15 10:00:00', '2025-11-15 10:00:00', 2),
-- Bella's record
(10, 5, 2, '2025-09-25', 'afternoon', 1.80, 38.8, 'First checkup as kitten. Healthy and very active.', 1, 1, 'Lot: FVRCP-2025-C3', 'First vaccination. Schedule booster in 4 weeks. Excellent health.', '2025-09-25 15:00:00', '2025-09-25 15:00:00', '2025-09-25 15:00:00', 2);

-- =============================================================================
-- 7. CARE LOGS (Past 7 days - Nov 25 to Dec 1, 2025)
-- =============================================================================
-- Luna (ID: 1) - Care logs
INSERT INTO care_logs (animal_id, recorder_id, recorder_name, log_date, time_slot, appetite, energy, urination, cleaning, memo, ip_address, user_agent, device_tag, from_paper, created_at, last_updated_at, last_updated_by) VALUES
-- Dec 1
(1, 1, 'Sarah Johnson', '2025-12-01', 'morning', 0.75, 4, 1, 1, 'Ate well this morning. Very happy.', '192.168.1.10', 'Mozilla/5.0', 'device-001', 0, '2025-12-01 08:30:00', '2025-12-01 08:30:00', NULL),
(1, 2, 'Mike Brown', '2025-12-01', 'noon', 0.75, 4, 1, 1, NULL, '192.168.1.11', 'Mozilla/5.0', 'device-002', 0, '2025-12-01 12:30:00', '2025-12-01 12:30:00', NULL),
(1, 3, 'Lisa Chen', '2025-12-01', 'evening', 0.75, 5, 1, 1, 'Extra playful today!', '192.168.1.12', 'Mozilla/5.0', 'device-003', 0, '2025-12-01 18:00:00', '2025-12-01 18:00:00', NULL),
-- Nov 30
(1, 4, 'David Wilson', '2025-11-30', 'morning', 0.75, 4, 1, 1, NULL, '192.168.1.13', 'Mozilla/5.0', 'device-004', 0, '2025-11-30 08:15:00', '2025-11-30 08:15:00', NULL),
(1, 1, 'Sarah Johnson', '2025-11-30', 'noon', 0.75, 4, 1, 1, NULL, '192.168.1.10', 'Mozilla/5.0', 'device-001', 0, '2025-11-30 12:00:00', '2025-11-30 12:00:00', NULL),
(1, 2, 'Mike Brown', '2025-11-30', 'evening', 0.75, 4, 1, 1, NULL, '192.168.1.11', 'Mozilla/5.0', 'device-002', 0, '2025-11-30 18:30:00', '2025-11-30 18:30:00', NULL),
-- Nov 29
(1, 3, 'Lisa Chen', '2025-11-29', 'morning', 0.75, 4, 1, 1, NULL, '192.168.1.12', 'Mozilla/5.0', 'device-003', 0, '2025-11-29 08:00:00', '2025-11-29 08:00:00', NULL),
(1, 4, 'David Wilson', '2025-11-29', 'noon', 0.75, 4, 1, 1, NULL, '192.168.1.13', 'Mozilla/5.0', 'device-004', 0, '2025-11-29 12:30:00', '2025-11-29 12:30:00', NULL),
(1, 1, 'Sarah Johnson', '2025-11-29', 'evening', 1.0, 5, 1, 1, 'Great condition!', '192.168.1.10', 'Mozilla/5.0', 'device-001', 0, '2025-11-29 18:00:00', '2025-11-29 18:00:00', NULL),
-- Nov 28
(1, 2, 'Mike Brown', '2025-11-28', 'morning', 0.75, 4, 1, 1, NULL, '192.168.1.11', 'Mozilla/5.0', 'device-002', 0, '2025-11-28 08:30:00', '2025-11-28 08:30:00', NULL),
(1, 3, 'Lisa Chen', '2025-11-28', 'noon', 0.75, 4, 1, 1, NULL, '192.168.1.12', 'Mozilla/5.0', 'device-003', 0, '2025-11-28 12:00:00', '2025-11-28 12:00:00', NULL),
(1, 4, 'David Wilson', '2025-11-28', 'evening', 0.75, 4, 1, 1, NULL, '192.168.1.13', 'Mozilla/5.0', 'device-004', 0, '2025-11-28 18:30:00', '2025-11-28 18:30:00', NULL),
-- Nov 27
(1, 1, 'Sarah Johnson', '2025-11-27', 'morning', 0.75, 4, 1, 1, NULL, '192.168.1.10', 'Mozilla/5.0', 'device-001', 0, '2025-11-27 08:00:00', '2025-11-27 08:00:00', NULL),
(1, 2, 'Mike Brown', '2025-11-27', 'noon', 0.75, 4, 1, 1, NULL, '192.168.1.11', 'Mozilla/5.0', 'device-002', 0, '2025-11-27 12:30:00', '2025-11-27 12:30:00', NULL),
(1, 3, 'Lisa Chen', '2025-11-27', 'evening', 0.75, 4, 1, 1, NULL, '192.168.1.12', 'Mozilla/5.0', 'device-003', 0, '2025-11-27 18:00:00', '2025-11-27 18:00:00', NULL),
-- Nov 26
(1, 4, 'David Wilson', '2025-11-26', 'morning', 0.75, 4, 1, 1, NULL, '192.168.1.13', 'Mozilla/5.0', 'device-004', 0, '2025-11-26 08:30:00', '2025-11-26 08:30:00', NULL),
(1, 1, 'Sarah Johnson', '2025-11-26', 'noon', 0.75, 4, 1, 1, NULL, '192.168.1.10', 'Mozilla/5.0', 'device-001', 0, '2025-11-26 12:00:00', '2025-11-26 12:00:00', NULL),
(1, 2, 'Mike Brown', '2025-11-26', 'evening', 0.75, 4, 1, 1, NULL, '192.168.1.11', 'Mozilla/5.0', 'device-002', 0, '2025-11-26 18:30:00', '2025-11-26 18:30:00', NULL),
-- Nov 25
(1, 3, 'Lisa Chen', '2025-11-25', 'morning', 0.75, 4, 1, 1, NULL, '192.168.1.12', 'Mozilla/5.0', 'device-003', 0, '2025-11-25 08:00:00', '2025-11-25 08:00:00', NULL),
(1, 4, 'David Wilson', '2025-11-25', 'noon', 0.75, 4, 1, 1, NULL, '192.168.1.13', 'Mozilla/5.0', 'device-004', 0, '2025-11-25 12:30:00', '2025-11-25 12:30:00', NULL),
(1, 1, 'Sarah Johnson', '2025-11-25', 'evening', 0.75, 4, 1, 1, NULL, '192.168.1.10', 'Mozilla/5.0', 'device-001', 0, '2025-11-25 18:00:00', '2025-11-25 18:00:00', NULL);

-- Oliver (ID: 2) - Care logs
INSERT INTO care_logs (animal_id, recorder_id, recorder_name, log_date, time_slot, appetite, energy, urination, cleaning, memo, ip_address, user_agent, device_tag, from_paper, created_at, last_updated_at, last_updated_by) VALUES
-- Dec 1
(2, 4, 'David Wilson', '2025-12-01', 'morning', 1.0, 5, 1, 1, 'Very energetic today!', '192.168.1.13', 'Mozilla/5.0', 'device-004', 0, '2025-12-01 08:00:00', '2025-12-01 08:00:00', NULL),
(2, 1, 'Sarah Johnson', '2025-12-01', 'noon', 1.0, 5, 1, 1, NULL, '192.168.1.10', 'Mozilla/5.0', 'device-001', 0, '2025-12-01 12:00:00', '2025-12-01 12:00:00', NULL),
(2, 2, 'Mike Brown', '2025-12-01', 'evening', 0.75, 5, 1, 1, 'Played with toys for an hour', '192.168.1.11', 'Mozilla/5.0', 'device-002', 0, '2025-12-01 18:30:00', '2025-12-01 18:30:00', NULL),
-- Nov 30
(2, 3, 'Lisa Chen', '2025-11-30', 'morning', 1.0, 5, 1, 1, NULL, '192.168.1.12', 'Mozilla/5.0', 'device-003', 0, '2025-11-30 08:30:00', '2025-11-30 08:30:00', NULL),
(2, 4, 'David Wilson', '2025-11-30', 'noon', 1.0, 5, 1, 1, NULL, '192.168.1.13', 'Mozilla/5.0', 'device-004', 0, '2025-11-30 12:30:00', '2025-11-30 12:30:00', NULL),
(2, 1, 'Sarah Johnson', '2025-11-30', 'evening', 1.0, 4, 1, 1, NULL, '192.168.1.10', 'Mozilla/5.0', 'device-001', 0, '2025-11-30 18:00:00', '2025-11-30 18:00:00', NULL),
-- Nov 29
(2, 2, 'Mike Brown', '2025-11-29', 'morning', 1.0, 5, 1, 1, NULL, '192.168.1.11', 'Mozilla/5.0', 'device-002', 0, '2025-11-29 08:00:00', '2025-11-29 08:00:00', NULL),
(2, 3, 'Lisa Chen', '2025-11-29', 'noon', 1.0, 5, 1, 1, NULL, '192.168.1.12', 'Mozilla/5.0', 'device-003', 0, '2025-11-29 12:00:00', '2025-11-29 12:00:00', NULL),
(2, 4, 'David Wilson', '2025-11-29', 'evening', 1.0, 5, 1, 1, NULL, '192.168.1.13', 'Mozilla/5.0', 'device-004', 0, '2025-11-29 18:30:00', '2025-11-29 18:30:00', NULL),
-- Nov 28
(2, 1, 'Sarah Johnson', '2025-11-28', 'morning', 0.75, 5, 1, 1, NULL, '192.168.1.10', 'Mozilla/5.0', 'device-001', 0, '2025-11-28 08:30:00', '2025-11-28 08:30:00', NULL),
(2, 2, 'Mike Brown', '2025-11-28', 'noon', 1.0, 5, 1, 1, NULL, '192.168.1.11', 'Mozilla/5.0', 'device-002', 0, '2025-11-28 12:30:00', '2025-11-28 12:30:00', NULL),
(2, 3, 'Lisa Chen', '2025-11-28', 'evening', 1.0, 5, 1, 1, NULL, '192.168.1.12', 'Mozilla/5.0', 'device-003', 0, '2025-11-28 18:00:00', '2025-11-28 18:00:00', NULL),
-- Nov 27
(2, 4, 'David Wilson', '2025-11-27', 'morning', 1.0, 5, 1, 1, NULL, '192.168.1.13', 'Mozilla/5.0', 'device-004', 0, '2025-11-27 08:00:00', '2025-11-27 08:00:00', NULL),
(2, 1, 'Sarah Johnson', '2025-11-27', 'noon', 1.0, 4, 1, 1, NULL, '192.168.1.10', 'Mozilla/5.0', 'device-001', 0, '2025-11-27 12:00:00', '2025-11-27 12:00:00', NULL),
(2, 2, 'Mike Brown', '2025-11-27', 'evening', 1.0, 5, 1, 1, NULL, '192.168.1.11', 'Mozilla/5.0', 'device-002', 0, '2025-11-27 18:30:00', '2025-11-27 18:30:00', NULL),
-- Nov 26
(2, 3, 'Lisa Chen', '2025-11-26', 'morning', 1.0, 5, 1, 1, NULL, '192.168.1.12', 'Mozilla/5.0', 'device-003', 0, '2025-11-26 08:30:00', '2025-11-26 08:30:00', NULL),
(2, 4, 'David Wilson', '2025-11-26', 'noon', 1.0, 5, 1, 1, NULL, '192.168.1.13', 'Mozilla/5.0', 'device-004', 0, '2025-11-26 12:30:00', '2025-11-26 12:30:00', NULL),
(2, 1, 'Sarah Johnson', '2025-11-26', 'evening', 1.0, 5, 1, 1, NULL, '192.168.1.10', 'Mozilla/5.0', 'device-001', 0, '2025-11-26 18:00:00', '2025-11-26 18:00:00', NULL),
-- Nov 25
(2, 2, 'Mike Brown', '2025-11-25', 'morning', 1.0, 5, 1, 1, NULL, '192.168.1.11', 'Mozilla/5.0', 'device-002', 0, '2025-11-25 08:00:00', '2025-11-25 08:00:00', NULL),
(2, 3, 'Lisa Chen', '2025-11-25', 'noon', 0.75, 5, 1, 1, NULL, '192.168.1.12', 'Mozilla/5.0', 'device-003', 0, '2025-11-25 12:00:00', '2025-11-25 12:00:00', NULL),
(2, 4, 'David Wilson', '2025-11-25', 'evening', 1.0, 5, 1, 1, NULL, '192.168.1.13', 'Mozilla/5.0', 'device-004', 0, '2025-11-25 18:30:00', '2025-11-25 18:30:00', NULL);

-- Misty (ID: 3) - Care logs (some gaps - quiet cat)
INSERT INTO care_logs (animal_id, recorder_id, recorder_name, log_date, time_slot, appetite, energy, urination, cleaning, memo, ip_address, user_agent, device_tag, from_paper, created_at, last_updated_at, last_updated_by) VALUES
-- Dec 1
(3, 3, 'Lisa Chen', '2025-12-01', 'morning', 0.5, 3, 1, 1, 'Ate slowly as usual', '192.168.1.12', 'Mozilla/5.0', 'device-003', 0, '2025-12-01 08:30:00', '2025-12-01 08:30:00', NULL),
(3, 4, 'David Wilson', '2025-12-01', 'evening', 0.5, 3, 1, 1, NULL, '192.168.1.13', 'Mozilla/5.0', 'device-004', 0, '2025-12-01 18:00:00', '2025-12-01 18:00:00', NULL),
-- Nov 30
(3, 1, 'Sarah Johnson', '2025-11-30', 'morning', 0.5, 3, 1, 1, NULL, '192.168.1.10', 'Mozilla/5.0', 'device-001', 0, '2025-11-30 08:00:00', '2025-11-30 08:00:00', NULL),
(3, 2, 'Mike Brown', '2025-11-30', 'noon', 0.5, 3, 1, 1, NULL, '192.168.1.11', 'Mozilla/5.0', 'device-002', 0, '2025-11-30 12:30:00', '2025-11-30 12:30:00', NULL),
(3, 3, 'Lisa Chen', '2025-11-30', 'evening', 0.5, 3, 1, 1, 'Sleeping in sunny spot', '192.168.1.12', 'Mozilla/5.0', 'device-003', 0, '2025-11-30 18:30:00', '2025-11-30 18:30:00', NULL),
-- Nov 29
(3, 4, 'David Wilson', '2025-11-29', 'morning', 0.5, 3, 1, 1, NULL, '192.168.1.13', 'Mozilla/5.0', 'device-004', 0, '2025-11-29 08:30:00', '2025-11-29 08:30:00', NULL),
(3, 1, 'Sarah Johnson', '2025-11-29', 'evening', 0.5, 3, 1, 1, NULL, '192.168.1.10', 'Mozilla/5.0', 'device-001', 0, '2025-11-29 18:00:00', '2025-11-29 18:00:00', NULL),
-- Nov 28
(3, 2, 'Mike Brown', '2025-11-28', 'morning', 0.5, 3, 1, 1, NULL, '192.168.1.11', 'Mozilla/5.0', 'device-002', 0, '2025-11-28 08:00:00', '2025-11-28 08:00:00', NULL),
(3, 3, 'Lisa Chen', '2025-11-28', 'noon', 0.5, 4, 1, 1, 'More active today', '192.168.1.12', 'Mozilla/5.0', 'device-003', 0, '2025-11-28 12:00:00', '2025-11-28 12:00:00', NULL),
(3, 4, 'David Wilson', '2025-11-28', 'evening', 0.5, 3, 1, 1, NULL, '192.168.1.13', 'Mozilla/5.0', 'device-004', 0, '2025-11-28 18:30:00', '2025-11-28 18:30:00', NULL),
-- Nov 27
(3, 1, 'Sarah Johnson', '2025-11-27', 'morning', 0.5, 3, 1, 1, NULL, '192.168.1.10', 'Mozilla/5.0', 'device-001', 0, '2025-11-27 08:30:00', '2025-11-27 08:30:00', NULL),
(3, 2, 'Mike Brown', '2025-11-27', 'evening', 0.5, 3, 1, 1, NULL, '192.168.1.11', 'Mozilla/5.0', 'device-002', 0, '2025-11-27 18:00:00', '2025-11-27 18:00:00', NULL),
-- Nov 26
(3, 3, 'Lisa Chen', '2025-11-26', 'morning', 0.5, 3, 1, 1, NULL, '192.168.1.12', 'Mozilla/5.0', 'device-003', 0, '2025-11-26 08:00:00', '2025-11-26 08:00:00', NULL),
(3, 4, 'David Wilson', '2025-11-26', 'noon', 0.5, 3, 1, 1, NULL, '192.168.1.13', 'Mozilla/5.0', 'device-004', 0, '2025-11-26 12:30:00', '2025-11-26 12:30:00', NULL),
(3, 1, 'Sarah Johnson', '2025-11-26', 'evening', 0.5, 3, 1, 1, NULL, '192.168.1.10', 'Mozilla/5.0', 'device-001', 0, '2025-11-26 18:30:00', '2025-11-26 18:30:00', NULL),
-- Nov 25
(3, 2, 'Mike Brown', '2025-11-25', 'morning', 0.5, 3, 1, 1, NULL, '192.168.1.11', 'Mozilla/5.0', 'device-002', 0, '2025-11-25 08:30:00', '2025-11-25 08:30:00', NULL),
(3, 3, 'Lisa Chen', '2025-11-25', 'noon', 0.5, 3, 1, 1, NULL, '192.168.1.12', 'Mozilla/5.0', 'device-003', 0, '2025-11-25 12:00:00', '2025-11-25 12:00:00', NULL),
(3, 4, 'David Wilson', '2025-11-25', 'evening', 0.5, 3, 1, 1, NULL, '192.168.1.13', 'Mozilla/5.0', 'device-004', 0, '2025-11-25 18:00:00', '2025-11-25 18:00:00', NULL);

-- Shadow (ID: 4) - Care logs (under treatment - more careful monitoring)
INSERT INTO care_logs (animal_id, recorder_id, recorder_name, log_date, time_slot, appetite, energy, urination, cleaning, memo, ip_address, user_agent, device_tag, from_paper, created_at, last_updated_at, last_updated_by) VALUES
-- Dec 1
(4, 1, 'Sarah Johnson', '2025-12-01', 'morning', 0.5, 3, 1, 1, 'Eye drops administered. Slight improvement.', '192.168.1.10', 'Mozilla/5.0', 'device-001', 0, '2025-12-01 08:00:00', '2025-12-01 08:00:00', NULL),
(4, 3, 'Lisa Chen', '2025-12-01', 'noon', 0.5, 3, 1, 1, NULL, '192.168.1.12', 'Mozilla/5.0', 'device-003', 0, '2025-12-01 12:00:00', '2025-12-01 12:00:00', NULL),
(4, 2, 'Mike Brown', '2025-12-01', 'evening', 0.5, 3, 1, 1, 'Resting comfortably', '192.168.1.11', 'Mozilla/5.0', 'device-002', 0, '2025-12-01 18:30:00', '2025-12-01 18:30:00', NULL),
-- Nov 30
(4, 4, 'David Wilson', '2025-11-30', 'morning', 0.25, 2, 1, 1, 'Appetite slightly lower today', '192.168.1.13', 'Mozilla/5.0', 'device-004', 0, '2025-11-30 08:30:00', '2025-11-30 08:30:00', NULL),
(4, 1, 'Sarah Johnson', '2025-11-30', 'noon', 0.25, 3, 1, 1, 'Eye drops given', '192.168.1.10', 'Mozilla/5.0', 'device-001', 0, '2025-11-30 12:30:00', '2025-11-30 12:30:00', NULL),
(4, 2, 'Mike Brown', '2025-11-30', 'evening', 0.5, 3, 1, 1, NULL, '192.168.1.11', 'Mozilla/5.0', 'device-002', 0, '2025-11-30 18:00:00', '2025-11-30 18:00:00', NULL),
-- Nov 29
(4, 3, 'Lisa Chen', '2025-11-29', 'morning', 0.5, 3, 1, 1, NULL, '192.168.1.12', 'Mozilla/5.0', 'device-003', 0, '2025-11-29 08:00:00', '2025-11-29 08:00:00', NULL),
(4, 4, 'David Wilson', '2025-11-29', 'noon', 0.5, 3, 1, 1, NULL, '192.168.1.13', 'Mozilla/5.0', 'device-004', 0, '2025-11-29 12:00:00', '2025-11-29 12:00:00', NULL),
(4, 1, 'Sarah Johnson', '2025-11-29', 'evening', 0.5, 3, 1, 1, 'Eye drops administered', '192.168.1.10', 'Mozilla/5.0', 'device-001', 0, '2025-11-29 18:30:00', '2025-11-29 18:30:00', NULL),
-- Nov 28
(4, 2, 'Mike Brown', '2025-11-28', 'morning', 0.25, 2, 1, 1, 'Seems a bit tired', '192.168.1.11', 'Mozilla/5.0', 'device-002', 0, '2025-11-28 08:30:00', '2025-11-28 08:30:00', NULL),
(4, 3, 'Lisa Chen', '2025-11-28', 'noon', 0.25, 3, 1, 1, NULL, '192.168.1.12', 'Mozilla/5.0', 'device-003', 0, '2025-11-28 12:30:00', '2025-11-28 12:30:00', NULL),
(4, 4, 'David Wilson', '2025-11-28', 'evening', 0.5, 3, 1, 1, NULL, '192.168.1.13', 'Mozilla/5.0', 'device-004', 0, '2025-11-28 18:00:00', '2025-11-28 18:00:00', NULL),
-- Nov 27
(4, 1, 'Sarah Johnson', '2025-11-27', 'morning', 0.5, 3, 1, 1, NULL, '192.168.1.10', 'Mozilla/5.0', 'device-001', 0, '2025-11-27 08:00:00', '2025-11-27 08:00:00', NULL),
(4, 2, 'Mike Brown', '2025-11-27', 'noon', 0.5, 3, 1, 1, NULL, '192.168.1.11', 'Mozilla/5.0', 'device-002', 0, '2025-11-27 12:00:00', '2025-11-27 12:00:00', NULL),
(4, 3, 'Lisa Chen', '2025-11-27', 'evening', 0.5, 3, 1, 1, 'Medication administered', '192.168.1.12', 'Mozilla/5.0', 'device-003', 0, '2025-11-27 18:30:00', '2025-11-27 18:30:00', NULL),
-- Nov 26
(4, 4, 'David Wilson', '2025-11-26', 'morning', 0.25, 2, 1, 1, NULL, '192.168.1.13', 'Mozilla/5.0', 'device-004', 0, '2025-11-26 08:30:00', '2025-11-26 08:30:00', NULL),
(4, 1, 'Sarah Johnson', '2025-11-26', 'noon', 0.25, 2, 1, 1, 'Eye still showing discharge', '192.168.1.10', 'Mozilla/5.0', 'device-001', 0, '2025-11-26 12:30:00', '2025-11-26 12:30:00', NULL),
(4, 2, 'Mike Brown', '2025-11-26', 'evening', 0.5, 3, 1, 1, NULL, '192.168.1.11', 'Mozilla/5.0', 'device-002', 0, '2025-11-26 18:00:00', '2025-11-26 18:00:00', NULL),
-- Nov 25
(4, 3, 'Lisa Chen', '2025-11-25', 'morning', 0.5, 3, 1, 1, NULL, '192.168.1.12', 'Mozilla/5.0', 'device-003', 0, '2025-11-25 08:00:00', '2025-11-25 08:00:00', NULL),
(4, 4, 'David Wilson', '2025-11-25', 'noon', 0.5, 3, 1, 1, NULL, '192.168.1.13', 'Mozilla/5.0', 'device-004', 0, '2025-11-25 12:00:00', '2025-11-25 12:00:00', NULL),
(4, 1, 'Sarah Johnson', '2025-11-25', 'evening', 0.5, 3, 1, 1, NULL, '192.168.1.10', 'Mozilla/5.0', 'device-001', 0, '2025-11-25 18:30:00', '2025-11-25 18:30:00', NULL);

-- Bella (ID: 5) - Care logs (kitten - very active)
INSERT INTO care_logs (animal_id, recorder_id, recorder_name, log_date, time_slot, appetite, energy, urination, cleaning, memo, ip_address, user_agent, device_tag, from_paper, created_at, last_updated_at, last_updated_by) VALUES
-- Dec 1
(5, 2, 'Mike Brown', '2025-12-01', 'morning', 1.0, 5, 1, 1, 'Super playful this morning!', '192.168.1.11', 'Mozilla/5.0', 'device-002', 0, '2025-12-01 08:00:00', '2025-12-01 08:00:00', NULL),
(5, 4, 'David Wilson', '2025-12-01', 'noon', 1.0, 5, 1, 1, NULL, '192.168.1.13', 'Mozilla/5.0', 'device-004', 0, '2025-12-01 12:30:00', '2025-12-01 12:30:00', NULL),
(5, 1, 'Sarah Johnson', '2025-12-01', 'evening', 1.0, 5, 1, 1, 'Climbing everything!', '192.168.1.10', 'Mozilla/5.0', 'device-001', 0, '2025-12-01 18:00:00', '2025-12-01 18:00:00', NULL),
-- Nov 30
(5, 3, 'Lisa Chen', '2025-11-30', 'morning', 1.0, 5, 1, 1, NULL, '192.168.1.12', 'Mozilla/5.0', 'device-003', 0, '2025-11-30 08:30:00', '2025-11-30 08:30:00', NULL),
(5, 2, 'Mike Brown', '2025-11-30', 'noon', 1.0, 5, 1, 1, 'Playing with feather toy', '192.168.1.11', 'Mozilla/5.0', 'device-002', 0, '2025-11-30 12:00:00', '2025-11-30 12:00:00', NULL),
(5, 4, 'David Wilson', '2025-11-30', 'evening', 1.0, 5, 1, 1, NULL, '192.168.1.13', 'Mozilla/5.0', 'device-004', 0, '2025-11-30 18:30:00', '2025-11-30 18:30:00', NULL),
-- Nov 29
(5, 1, 'Sarah Johnson', '2025-11-29', 'morning', 1.0, 5, 1, 1, NULL, '192.168.1.10', 'Mozilla/5.0', 'device-001', 0, '2025-11-29 08:00:00', '2025-11-29 08:00:00', NULL),
(5, 3, 'Lisa Chen', '2025-11-29', 'noon', 1.0, 5, 1, 1, NULL, '192.168.1.12', 'Mozilla/5.0', 'device-003', 0, '2025-11-29 12:30:00', '2025-11-29 12:30:00', NULL),
(5, 2, 'Mike Brown', '2025-11-29', 'evening', 1.0, 5, 1, 1, 'Very active after dinner', '192.168.1.11', 'Mozilla/5.0', 'device-002', 0, '2025-11-29 18:00:00', '2025-11-29 18:00:00', NULL),
-- Nov 28
(5, 4, 'David Wilson', '2025-11-28', 'morning', 1.0, 5, 1, 1, NULL, '192.168.1.13', 'Mozilla/5.0', 'device-004', 0, '2025-11-28 08:30:00', '2025-11-28 08:30:00', NULL),
(5, 1, 'Sarah Johnson', '2025-11-28', 'noon', 1.0, 5, 1, 1, NULL, '192.168.1.10', 'Mozilla/5.0', 'device-001', 0, '2025-11-28 12:00:00', '2025-11-28 12:00:00', NULL),
(5, 3, 'Lisa Chen', '2025-11-28', 'evening', 1.0, 5, 1, 1, NULL, '192.168.1.12', 'Mozilla/5.0', 'device-003', 0, '2025-11-28 18:30:00', '2025-11-28 18:30:00', NULL),
-- Nov 27
(5, 2, 'Mike Brown', '2025-11-27', 'morning', 1.0, 5, 1, 1, 'Ate all food quickly', '192.168.1.11', 'Mozilla/5.0', 'device-002', 0, '2025-11-27 08:00:00', '2025-11-27 08:00:00', NULL),
(5, 4, 'David Wilson', '2025-11-27', 'noon', 1.0, 5, 1, 1, NULL, '192.168.1.13', 'Mozilla/5.0', 'device-004', 0, '2025-11-27 12:30:00', '2025-11-27 12:30:00', NULL),
(5, 1, 'Sarah Johnson', '2025-11-27', 'evening', 1.0, 5, 1, 1, NULL, '192.168.1.10', 'Mozilla/5.0', 'device-001', 0, '2025-11-27 18:00:00', '2025-11-27 18:00:00', NULL),
-- Nov 26
(5, 3, 'Lisa Chen', '2025-11-26', 'morning', 1.0, 5, 1, 1, NULL, '192.168.1.12', 'Mozilla/5.0', 'device-003', 0, '2025-11-26 08:30:00', '2025-11-26 08:30:00', NULL),
(5, 2, 'Mike Brown', '2025-11-26', 'noon', 1.0, 5, 1, 1, NULL, '192.168.1.11', 'Mozilla/5.0', 'device-002', 0, '2025-11-26 12:00:00', '2025-11-26 12:00:00', NULL),
(5, 4, 'David Wilson', '2025-11-26', 'evening', 1.0, 5, 1, 1, 'So much energy!', '192.168.1.13', 'Mozilla/5.0', 'device-004', 0, '2025-11-26 18:30:00', '2025-11-26 18:30:00', NULL),
-- Nov 25
(5, 1, 'Sarah Johnson', '2025-11-25', 'morning', 1.0, 5, 1, 1, NULL, '192.168.1.10', 'Mozilla/5.0', 'device-001', 0, '2025-11-25 08:00:00', '2025-11-25 08:00:00', NULL),
(5, 3, 'Lisa Chen', '2025-11-25', 'noon', 1.0, 5, 1, 1, NULL, '192.168.1.12', 'Mozilla/5.0', 'device-003', 0, '2025-11-25 12:30:00', '2025-11-25 12:30:00', NULL),
(5, 2, 'Mike Brown', '2025-11-25', 'evening', 1.0, 5, 1, 1, NULL, '192.168.1.11', 'Mozilla/5.0', 'device-002', 0, '2025-11-25 18:00:00', '2025-11-25 18:00:00', NULL);

-- =============================================================================
-- 8. ADOPTION RECORDS
-- =============================================================================
INSERT INTO adoption_records (id, animal_id, applicant_id, interview_date, interview_note, decision, adoption_date, follow_up, created_at, updated_at) VALUES
(1, 1, 1, '2025-11-10', 'Very interested in Luna. Has experience with cats. Home check completed - suitable environment with quiet space.', 'approved', '2025-11-20', '2025-11-25: Phone follow-up. Luna is settling in well. Comfortable in new home. Eating and playing normally. Family very happy.', '2025-11-10 14:00:00', '2025-11-25 16:00:00'),
(2, 5, 3, '2025-11-25', 'Family meeting went well. Children (10 and 12 years old) are gentle and respectful with animals. Large house with plenty of space for an active kitten. Scheduled home visit for Dec 5.', 'pending', NULL, NULL, '2025-11-25 15:00:00', '2025-11-25 15:00:00');

-- Re-enable foreign key checks
PRAGMA foreign_keys = ON;

-- Update sqlite_sequence to match inserted IDs
UPDATE sqlite_sequence SET seq = 3 WHERE name = 'users';
UPDATE sqlite_sequence SET seq = 4 WHERE name = 'volunteers';
UPDATE sqlite_sequence SET seq = 5 WHERE name = 'animals';
UPDATE sqlite_sequence SET seq = 8 WHERE name = 'medical_actions';
UPDATE sqlite_sequence SET seq = 10 WHERE name = 'medical_records';
UPDATE sqlite_sequence SET seq = 3 WHERE name = 'applicants';
UPDATE sqlite_sequence SET seq = 2 WHERE name = 'adoption_records';

-- Verify counts
SELECT 'Animals: ' || COUNT(*) FROM animals;
SELECT 'Users: ' || COUNT(*) FROM users;
SELECT 'Volunteers: ' || COUNT(*) FROM volunteers;
SELECT 'Medical Actions: ' || COUNT(*) FROM medical_actions;
SELECT 'Medical Records: ' || COUNT(*) FROM medical_records;
SELECT 'Care Logs: ' || COUNT(*) FROM care_logs;
SELECT 'Applicants: ' || COUNT(*) FROM applicants;
SELECT 'Adoption Records: ' || COUNT(*) FROM adoption_records;
