# Requirements Document

## Introduction

NecoKeeper is a web system that digitizes record-keeping and management tasks for cat rescue activities in Japan. It unifies and manages individual cat records, daily care logs, veterinary medical records, and adoption management (including finding adopters and handling transfers), which are often maintained on paper ledgers or spreadsheets, into a format that can be easily used even on smartphones. It features QR-code–based, authentication-free input forms, PDF report generation, and SQLite-based local operation, targeting cat rescue organizations, community cat volunteers, and veterinarians with low-to-medium IT literacy. The system is designed for small organizations of around 10 people (representative + staff + volunteers), supports mixed paper/digital workflows and gradual digitization, and prioritizes minimizing the administrative burden on representatives who often have a primary job in addition to rescue activities. The expected number of cats managed is roughly 10–20. By enabling simple deployment to free hosting services such as Render, Railway, and Fly.io, NecoKeeper keeps operational costs low even for small organizations.

## Glossary

- **NecoKeeper**: Name of this system; a web system for managing rescued cats
- **Animal Master**: Master database for managing individual cat information
- **CareLog**: Logging system for daily care records (weight, meals, excretion, etc.)
- **Medical Record**: System for veterinary medical records
- **Public Form**: Record input form accessible by anyone without authentication
- **QR Card**: PDF ledger card with cat photo, name, and QR code
- **Volunteer**: Volunteer who records care logs
- **Vet**: Veterinarian user
- **Admin**: System administrator and organization representative
- **Staff**: Staff user (with permissions for CSV import, report viewing, and record viewing)

- **WeasyPrint**: Library for generating PDFs from HTML
- **FastAPI**: Backend web framework
- **SQLite**: Production database
- **AdminLTE**: Admin UI framework
- **Tailwind CSS**: CSS framework for public forms
- **Adoption**: Process of transferring cats to adopters
- **Applicant**: Person applying to adopt a cat
- **Status**: Cat status (e.g., in rescue, adoptable, adopted, under treatment)
- **i18n**: Internationalization; mechanisms for multi-language support
- **Translation File**: Translation file; JSON files defining UI text per language
- **OCR**: Optical Character Recognition; technology for recognizing text from images and PDFs
- **Kiro Hook**: Kiro’s automation feature; starts agent execution triggered by events such as file creation
- **MCP**: Model Context Protocol; protocol for integration with external services

- **Render**: Cloud hosting service with free tier
- **Railway**: Cloud platform with free tier
- **Fly.io**: Globally distributed hosting service with free tier

## Requirements

### Requirement 1: Cat Registration and Management

**User Story:** As an administrator of a cat rescue organization, I want to register and edit information about rescued cats so that I can accurately manage identification information for each cat.

#### Acceptance Criteria

1. WHEN 管理者がAnimal Master画面で新規登録ボタンをクリックしたとき、THE NecoKeeper SHALL 猫の個体情報入力フォームを表示する
2. WHEN 管理者が必須項目（顔写真、柄・色、尻尾の長さ、年齢、性別）を入力して保存ボタンをクリックしたとき、THE NecoKeeper SHALL 猫の個体情報をAnimal Masterに保存する
3. WHEN 管理者がAnimal Master一覧画面で既存の猫レコードを選択したとき、THE NecoKeeper SHALL 当該猫の詳細情報を表示し編集可能にする
4. THE NecoKeeper SHALL 猫の識別項目として顔写真、柄・色、尻尾の長さ、首輪有無・色、年齢（大きさ）、性別、耳カット有無、外傷・特徴・性格を記録する
5. THE NecoKeeper SHALL 猫レコードの物理削除を行わず、Statusによる論理削除で管理する

### Requirement 2: QR Cards and Paper Record Form PDFs

**User Story:** As a staff member of a cat rescue organization, I want to output per-cat ledger cards with QR codes and paper record forms as PDFs so that I can identify cats on site and record information using either smartphones or paper.

#### Acceptance Criteria

1. WHEN 管理者がAnimal Master画面で猫を選択してQRカード出力ボタンをクリックしたとき、THE NecoKeeper SHALL 当該猫の名前、顔写真、QRコード、IDを含むA6サイズのPDFを生成する
2. WHEN 管理者が複数の猫を選択して面付けカード出力ボタンをクリックしたとき、THE NecoKeeper SHALL A4用紙に2×5枚（10枚）のQRカードを配置したPDFを生成する
3. THE NecoKeeper SHALL QRコードに猫の個体IDと記録入力用URLを埋め込む
4. WHEN ユーザーがQRコードをスマートフォンでスキャンしたとき、THE NecoKeeper SHALL 当該猫のPublic記録入力フォームを表示する
5. WHEN 管理者がAnimal Master画面で猫を選択して紙記録フォーム出力ボタンをクリックしたとき、THE NecoKeeper SHALL 1ヶ月分の日付欄と記録欄（時点、食欲、元気、排尿、清掃、メモ）を含むA4サイズのPDFを生成する
6. THE NecoKeeper SHALL 紙記録フォームに猫の名前、顔写真、ID、対象年月を表示する
7. THE NecoKeeper SHALL 紙記録フォームの各日付欄に記録者名欄を配置する
8. WHEN 管理者が複数の猫を選択して紙記録フォーム一括出力ボタンをクリックしたとき、THE NecoKeeper SHALL 選択された全猫の紙記録フォームを1つのPDFにまとめて生成する

### Requirement 3: Authentication-Free Daily Care Logging

**User Story:** As a volunteer, I want to scan a QR code and enter care logs for cats without authentication so that I can quickly record information on site.

#### Acceptance Criteria

1. WHEN ボランティアが猫のQRコードをスキャンしてPublic記録フォームにアクセスしたとき、THE NecoKeeper SHALL 当該猫の名前と顔写真サムネイルを表示する
2. THE NecoKeeper SHALL Public記録フォームに時点、食欲、元気、排尿、清掃、メモの入力欄を1画面で表示する
3. THE NecoKeeper SHALL Public記録フォームに登録済みボランティアの選択リストを表示する
4. WHEN ボランティアが選択リストから自分の名前を選択したとき、THE NecoKeeper SHALL 記録者情報を入力フォームに設定する
5. WHEN ボランティアが保存ボタンをクリックしたとき、THE NecoKeeper SHALL 入力内容をCareLogに保存する
6. THE NecoKeeper SHALL 記録保存時にrecorder_id、recorder_name、IPアドレス、user_agent、created_at、device_tagを自動記録する
7. THE NecoKeeper SHALL Public記録フォームで前回入力値をコピーする機能を提供する
8. THE NecoKeeper SHALL Public記録フォームをPWA対応とし、オフライン入力後のオンライン同期を可能にする
9. THE NecoKeeper SHALL QR URLに乱数UUIDを用いて推測困難化する
10. WHEN ボランティアがPublic記録フォームにアクセスしたとき、THE NecoKeeper SHALL 当該猫の直近7日間の世話記録一覧へのリンクを表示する
11. WHEN ボランティアが記録一覧ページにアクセスしたとき、THE NecoKeeper SHALL 当該猫の直近7日間の世話記録を日付・時点（朝/昼/夕）・記録者名・記録状況（〇/×）で表示する
12. THE NecoKeeper SHALL 当日の朝・昼・夕の記録状況を視覚的に表示する（〇=記録済み、×=未記録）
13. WHEN ボランティアが記録一覧から特定の記録を選択したとき、THE NecoKeeper SHALL 当該記録の詳細（食欲、元気、排尿、清掃、メモ）を表示する
14. THE NecoKeeper SHALL 認証不要で全猫の記録状況一覧ページを提供する
15. WHEN ボランティアが全猫記録状況一覧ページにアクセスしたとき、THE NecoKeeper SHALL 全猫の当日の朝・昼・夕の記録状況を一覧表示する
16. THE NecoKeeper SHALL 全猫記録状況一覧で各猫の名前、顔写真サムネイル、当日の記録状況（朝〇/×、昼〇/×、夕〇/×）を表示する
17. WHEN ボランティアが全猫記録状況一覧で猫を選択したとき、THE NecoKeeper SHALL 当該猫のPublic記録フォームに遷移する
17. WHEN ボランティアが全猫記録状況一覧で猫を選択したとき、THE NecoKeeper SHALL 当該猫のPublic記録フォームに遷移する

### Requirement 4: Recorder Management

**User Story:** As an administrator, I want to register and manage volunteer recorders who participate intermittently or continuously so that I can track who created which records.

#### Acceptance Criteria

1. WHEN 管理者がVolunteerマスター画面で新規登録ボタンをクリックしたとき、THE NecoKeeper SHALL 記録者情報（名前、連絡先、所属、活動開始日）の入力フォームを表示する
2. WHEN 管理者が記録者情報を入力して保存ボタンをクリックしたとき、THE NecoKeeper SHALL 記録者情報をVolunteerマスターに保存する
3. THE NecoKeeper SHALL Volunteerマスターに活動状態（アクティブ、休止中）を記録する
4. THE NecoKeeper SHALL Public記録フォームの選択リストにアクティブ状態のボランティアのみを表示する
5. WHEN 管理者がVolunteerマスター画面で記録者を選択したとき、THE NecoKeeper SHALL 当該記録者の活動履歴（記録回数、最終記録日）を表示する

### Requirement 5: Veterinary Medical Record Registration

**User Story:** As a veterinarian, I want to record details of medical treatments so that I can accurately manage medical histories.

#### Acceptance Criteria

1. WHEN 獣医師または管理者が認証済みでMedical Record画面にアクセスしたとき、THE NecoKeeper SHALL 診療記録入力フォームを表示する
2. THE NecoKeeper SHALL 診療記録入力フォームに診療年月日、時間帯、薬品名、投薬量、その他（ワクチンのロット番号など）、体重、体温、症状、コメントの入力欄を表示する
3. WHEN 獣医師が必須項目（診療年月日、体重、症状）を入力して保存ボタンをクリックしたとき、THE NecoKeeper SHALL 診療記録をMedical Recordに保存する
4. THE NecoKeeper SHALL 薬品名入力欄でMedicationマスターからの選択または自由入力を可能にする
5. THE NecoKeeper SHALL 診療記録の一覧画面で猫ごとの診療履歴を時系列で表示する

### Requirement 6: Medical Procedure Master Data Management

**User Story:** As an administrator, I want to manage master data for medical procedures (medications, vaccines, tests) with prices per period so that I can accurately record cost and billing price changes, including price increases and out-of-pocket treatments.

#### Acceptance Criteria

1. WHEN the administrator clicks the "New" button on the medical procedure master screen, THE NecoKeeper SHALL display an input form for procedure name, effective start date, effective end date, cost, billing price, procedure/administration fee, currency unit (JPY/USD), and dosage unit.
2. THE NecoKeeper SHALL provide the following options for dosage units: "tablet", "vial", "time", and "mL".
3. WHEN the administrator enters master data and clicks the save button, THE NecoKeeper SHALL save the master data to the database.
4. THE NecoKeeper SHALL treat a NULL effective end date as indicating that the price is still currently valid.
5. THE NecoKeeper SHALL calculate charges using the formula: `billing price × dosage amount + procedure/administration fee`.
6. THE NecoKeeper SHALL store cost, billing price, and procedure/administration fee as DECIMAL values with two decimal places.
7. WHEN a medical procedure is selected on the medical record entry screen, THE NecoKeeper SHALL display the corresponding dosage unit in the dosage label.

### Requirement 7: Medical Statement Output

**User Story:** As a veterinarian, I want to output detailed medical records in multiple formats so that they can be used for invoices to the organization, record archiving, and data analysis.

#### Acceptance Criteria

1. WHEN a veterinarian or administrator selects a medical record and clicks the "Output Details" button, THE NecoKeeper SHALL display format options for PDF, CSV, and Excel.
2. WHEN the veterinarian selects PDF format, THE NecoKeeper SHALL generate a vertical A4-sized medical statement PDF.
3. THE NecoKeeper SHALL include the cat's photo, treatment date, time of day, weight, body temperature, symptoms, medication name, dosage amount, other notes, and comments in the medical statement PDF.
4. WHEN the veterinarian selects CSV format, THE NecoKeeper SHALL allow the medical record data to be downloaded in CSV format.
5. WHEN the veterinarian selects Excel format, THE NecoKeeper SHALL allow the medical record data to be downloaded in Excel (.xlsx) format.

### Requirement 8: CSV Import and Export

**User Story:** As an administrator, I want to import and export cat information in CSV format so that it is easy to migrate existing data and create backups.

#### Acceptance Criteria

1. WHEN the administrator clicks the CSV export button on the Animal Master screen, THE NecoKeeper SHALL allow all cat information to be downloaded in CSV format.
2. WHEN the administrator clicks the CSV import button on the Animal Master screen and selects a CSV file, THE NecoKeeper SHALL validate the contents of the CSV file.
3. WHEN the CSV file format is valid, THE NecoKeeper SHALL import the CSV data into the Animal Master.
4. WHEN the CSV file contains format errors, THE NecoKeeper SHALL display the error details and abort the import.

### Requirement 9: Report Output (Daily, Weekly, Monthly Aggregation)

**User Story:** As an administrator, I want to output aggregated care logs and medical expenses by period in multiple formats so that they can be used for activity reports, accounting, and data analysis.

#### Acceptance Criteria

1. WHEN the administrator specifies a period on the report output screen and clicks the "Daily Report" button, THE NecoKeeper SHALL display format options for PDF, CSV, and Excel.
2. WHEN the administrator selects PDF format, THE NecoKeeper SHALL generate an aggregated CareLog report for the specified period in PDF format.
3. WHEN the administrator selects CSV format, THE NecoKeeper SHALL allow the aggregated CareLog report for the specified period to be downloaded in CSV format.
4. WHEN the administrator selects Excel format, THE NecoKeeper SHALL allow the aggregated CareLog report for the specified period to be downloaded in Excel (.xlsx) format.
5. WHEN the administrator specifies a period on the report output screen and clicks the "Weekly Report" button, THE NecoKeeper SHALL display format options for PDF, CSV, and Excel.
6. WHEN the administrator specifies a month on the report output screen and clicks the "Monthly Aggregation" button, THE NecoKeeper SHALL allow the total medical expenses, number of treatments, and number of animals treated for the specified month to be output in PDF, CSV, and Excel formats.
7. WHEN the administrator clicks the "Individual Report" button on a cat's detail screen, THE NecoKeeper SHALL allow a combined report of that cat's care logs and medical records to be output in PDF, CSV, and Excel formats.
8. THE NecoKeeper SHALL provide period selection options for per-cat individual reports (all time, last 1 month, last 3 months, last 6 months, custom period).

### Requirement 10: Permission Management and Access Control

**User Story:** As a system administrator, I want to configure appropriate permissions for each user so that security and role-based responsibilities can be managed properly.

#### Acceptance Criteria

1. THE NecoKeeper SHALL grant the `admin` role access to all features (ledger, records, medical, master data, settings).
2. THE NecoKeeper SHALL grant the `vet` role access to CRUD operations on medical records, report output, and aggregations.
3. THE NecoKeeper SHALL grant the `staff` role access to CSV import, report viewing, and viewing of care and medical records.
4. THE NecoKeeper SHALL grant the `read_only` role view-only permissions.
5. THE NecoKeeper SHALL allow the `volunteer` role to use only the Public form input, without requiring authentication.
6. WHEN a user without sufficient permissions attempts to access a restricted feature, THE NecoKeeper SHALL deny access and display an error message.

### Requirement 11: Data Backup

**User Story:** As a system administrator, I want to automatically back up the database and media files so that the risk of data loss is reduced.

#### Acceptance Criteria

1. THE NecoKeeper SHALL back up the `app.sqlite3` database file at a fixed time every night.
2. THE NecoKeeper SHALL back up the `/media` directory (image files, etc.) at a fixed time every night.
3. THE NecoKeeper SHALL save backup files with a date timestamp.
4. WHEN a backup process fails, THE NecoKeeper SHALL record an error log.
5. THE NecoKeeper SHALL copy `/data/app.sqlite3` once per day with a date-time suffix and retain seven generations.

### Requirement 12: Admin UI

**User Story:** As an administrator, I want to use an intuitive and easy-to-use admin interface so that I can operate the system efficiently.

#### Acceptance Criteria

1. THE NecoKeeper SHALL use the AdminLTE framework for the admin UI.
2. THE NecoKeeper SHALL place menus for cat ledger, care logs, medical records, master data management, report output, and settings in the admin interface.
3. WHEN an administrator logs into the admin interface, THE NecoKeeper SHALL display the number of registered cats and the number of cats per Status on the dashboard.
4. THE NecoKeeper SHALL provide search, filter, and sort functions on each list screen in the admin interface.

### Requirement 13: Mobile Optimization of the Public Form

**User Story:** As a volunteer, I want to enter records comfortably on a smartphone so that record-keeping work on site proceeds smoothly.

#### Acceptance Criteria

1. THE NecoKeeper SHALL implement the Public form as a responsive design using Tailwind CSS.
2. THE NecoKeeper SHALL place input buttons on the Public form with a size that is easy to tap with a finger (minimum 44×44 px).
3. THE NecoKeeper SHALL design the Public form to be a single-screen form, minimizing the need for scrolling.
4. THE NecoKeeper SHALL fix the save button for the Public form at the bottom of the screen.
5. WHEN a user accesses the Public form from a smartphone, THE NecoKeeper SHALL display a mobile-optimized layout.

### Requirement 14: Adoption Matching and Transfer Management

**User Story:** As a representative of a cat rescue organization, I want to manage adoption applicants for rescued cats and record the transfer process so that I can properly match cats with their new owners.

#### Acceptance Criteria

1. WHEN the administrator clicks the "New" button on the adoption applicant management screen, THE NecoKeeper SHALL display an input form for applicant information (name, contact information, address, family structure, living environment, and desired conditions).
2. WHEN the administrator enters adoption applicant information and clicks the save button, THE NecoKeeper SHALL save the applicant information to the Applicant master.
3. WHEN the administrator selects a cat on the interview record entry screen, THE NecoKeeper SHALL display only cats whose Status is "adoptable" as options.
4. WHEN the administrator selects an adoption candidate on a cat's detail screen and enters an interview record, THE NecoKeeper SHALL record the interview date, interview details, and decision result.
5. WHEN the administrator clicks the "Finalize Adoption" button and enters the adoption date and destination, THE NecoKeeper SHALL update the cat's Status to "adopted" and save the adoption record.
6. THE NecoKeeper SHALL allow post-adoption follow-up records (post-adoption contact date and status check details) to be registered.

### Requirement 15: Cat Status Management and Logical Deletion

**User Story:** As a staff member, I want to manage the current status of cats so that I can understand whether they are in rescue, under treatment, adoptable, adopted, etc., while still retaining past records for audit purposes.

#### Acceptance Criteria

1. THE NecoKeeper SHALL allow the following values to be set as cat Status: "in rescue", "under treatment", "adoptable", "adopted", "deceased", and "other".
2. WHEN the administrator changes the Status on a cat's detail screen and clicks the save button, THE NecoKeeper SHALL update the cat's Status and record the change history (change date/time, user who changed it, previous Status, new Status).
3. WHEN the administrator selects a Status filter on the Animal Master list screen, THE NecoKeeper SHALL display only cats with the specified Status.
4. THE NecoKeeper SHALL display aggregated counts of cats per Status on the dashboard.
5. THE NecoKeeper SHALL manage cat records using logical deletion via Status and SHALL NOT physically delete cat records.
6. WHEN the administrator accesses the Animal Master list screen, THE NecoKeeper SHALL, by default, display only cats whose Status is "in rescue", "under treatment", or "adoptable".
7. WHEN the administrator selects the "Show All" filter, THE NecoKeeper SHALL display cats of all Statuses, including "adopted" and "deceased".

### Requirement 16: Visualization of Activity Status

**User Story:** As a representative of a cat rescue organization, I want to grasp the current activity status at a glance so that it can support decision-making for running the organization.

#### Acceptance Criteria

1. WHEN the administrator accesses the dashboard, THE NecoKeeper SHALL display the number of cats in rescue, the number of adoptable cats, and the number of adoptions this month.
2. WHEN the administrator accesses the dashboard, THE NecoKeeper SHALL display the number of medical treatments this month and the total medical expenses for this month.
3. WHEN the administrator accesses the dashboard, THE NecoKeeper SHALL display a trend graph of the number of care log entries for the last 7 days.
4. WHEN the administrator accesses the dashboard, THE NecoKeeper SHALL display a list of long-term rescue cats (rescue period of 6 months or longer).

### Requirement 17: Support for Migrating from Paper Records

**User Story:** As a staff member, I want to efficiently enter existing paper records into the system so that past records can also be digitized and the burden of manual entry is reduced.

#### Acceptance Criteria

1. WHEN a staff member specifies a past date in the admin interface and enters a CareLog, THE NecoKeeper SHALL save the record with the specified date.
2. WHEN a staff member specifies a past date in the admin interface and enters a Medical Record, THE NecoKeeper SHALL save the medical record with the specified date.
3. THE NecoKeeper SHALL allow a "transcribed from paper records" flag to be set when entering records.
4. THE NecoKeeper SHALL allow past care logs to be registered in bulk via the CSV import function.
5. WHEN a staff member uploads an image file (JPG, PNG) or PDF file in the admin interface, THE NecoKeeper SHALL perform OCR processing to recognize text.
6. WHEN OCR processing is completed, THE NecoKeeper SHALL display the recognized text in an editable form.
7. WHEN a staff member reviews and corrects the OCR results and clicks the save button, THE NecoKeeper SHALL save the record to the database.
8. THE NecoKeeper SHALL use the Kiro Hook feature to automatically execute OCR processing when image or PDF files are added to a specified folder.
9. THE NecoKeeper SHALL support using external OCR services (such as Tesseract, Google Cloud Vision API, and AWS Textract) via MCP (Model Context Protocol) server integration.
10. THE NecoKeeper SHALL notify staff of the progress and results of OCR processing.

### Requirement 18: PWA Support and Offline Functionality

**User Story:** As a volunteer, I want to enter records even in environments with unstable internet connections so that I can continue working while offline.

#### Acceptance Criteria

1. THE NecoKeeper SHALL implement the Public form as a Progressive Web App (PWA).
2. WHEN a user first accesses the Public form on a smartphone, THE NecoKeeper SHALL display a prompt suggesting the app be added to the home screen.
3. WHEN a user enters records in the Public form while offline, THE NecoKeeper SHALL temporarily store the records in local storage.
4. WHEN the user's device comes back online, THE NecoKeeper SHALL automatically synchronize the records from local storage to the server.
5. THE NecoKeeper SHALL display synchronization status (synced, pending, syncing) to the user.
6. THE NecoKeeper SHALL also make the admin interface PWA-compatible and optimize it for viewing and operation on smartphones.
7. THE NecoKeeper SHALL resolve conflicts for the same record by prioritizing the last save (based on `updated_at`).

### Requirement 19: Multi-language Support (Japanese and English)

**User Story:** As a hackathon participant or overseas volunteer, I want to use the system in English as well so that it can support international cat rescue activities.

#### Acceptance Criteria

1. THE NecoKeeper SHALL support two languages: Japanese and English.
2. THE NecoKeeper SHALL manage UI text using translation files (in JSON format).
3. WHEN a user selects a language on the language settings screen, THE NecoKeeper SHALL display the entire UI in the selected language.
4. THE NecoKeeper SHALL store the user's language setting in the browser's local storage.
5. WHEN a user accesses the system for the first time and no language setting exists, THE NecoKeeper SHALL automatically select Japanese or English based on the browser language (`navigator.language`).
6. THE NecoKeeper SHALL include the following text categories in the translation files: common UI, cat ledger, care logs, medical records, adoption management, reports, and error messages.
7. THE NecoKeeper SHALL output PDF reports in the selected language as well.

### Requirement 20: Easy Deployment and Hosting

**User Story:** As a system administrator, I want to easily deploy the system to free or low-cost hosting services so that even small organizations can keep operational costs low.

#### Acceptance Criteria

1. THE NecoKeeper SHALL be configured so that it can be deployed to hosting services with free tiers that support persistent storage, such as Render, Railway, and Fly.io.
2. THE NecoKeeper SHALL include deployment configuration files (such as `render.yaml`, `railway.json`, `fly.toml`) in the project.
3. THE NecoKeeper SHALL support configuration via environment variables (database path, secret keys, OCR API keys, etc.).
4. THE NecoKeeper SHALL document persistent storage settings (volume mounts) for the SQLite database.
5. WHEN an administrator runs the deployment command, THE NecoKeeper SHALL automatically install required dependencies and start the application.
6. THE NecoKeeper SHALL provide a `README.md` file describing the deployment steps.
7. THE NecoKeeper SHALL place one-click deployment buttons (Deploy to Render, Deploy to Railway, etc.) in `README.md`.

### Requirement 21: Authentication and User Management

**User Story:** As a system administrator, I want to control access to the admin interface and manage users so that security can be ensured.

#### Acceptance Criteria

1. WHEN a user accesses the admin interface, THE NecoKeeper SHALL display a login screen.
2. WHEN a user enters an email address and password and clicks the login button, THE NecoKeeper SHALL validate the credentials.
3. WHEN authentication succeeds, THE NecoKeeper SHALL store a session ID in a cookie and redirect the user to the admin interface.
4. WHEN authentication fails, THE NecoKeeper SHALL display an error message.
5. THE NecoKeeper SHALL allow administrators to register new users on the user management screen.
6. THE NecoKeeper SHALL allow email address, password, name, and role (`admin`/`vet`/`staff`/`read_only`) to be entered when registering a user.
7. THE NecoKeeper SHALL hash passwords using bcrypt before storing them.
8. THE NecoKeeper SHALL provide a logout function.
9. WHEN a user clicks the logout button, THE NecoKeeper SHALL destroy the session and redirect the user to the login screen.

### Requirement 22: Security Measures

**User Story:** As a system administrator, I want to operate the system securely so that unauthorized access and data breaches can be prevented.

#### Acceptance Criteria

1. THE NecoKeeper SHALL enforce a password policy requiring at least 8 characters and a mix of letters and numbers.
2. THE NecoKeeper SHALL limit login attempts and lock the account for 15 minutes after 5 failed attempts (managed in the database).
3. THE NecoKeeper SHALL set the session timeout to 2 hours.
4. WHEN a session times out, THE NecoKeeper SHALL redirect the user to the login screen.
5. THE NecoKeeper SHALL recommend HTTPS communication and require HTTPS in production environments.
6. THE NecoKeeper SHALL use SQLAlchemy ORM to protect against SQL injection.
7. THE NecoKeeper SHALL manage the secret key (for session signing) via environment variables.
8. THE NecoKeeper SHALL set `httponly`, `secure`, and `samesite` flags on cookies.

### Requirement 23: Audit Logs

**User Story:** As a system administrator, I want to record the history of important operations so that I can investigate causes when problems occur and respond to audits.

#### Acceptance Criteria

1. THE NecoKeeper SHALL record the following operations in audit logs: changes to cat Status, adoption decisions, user registration and deletion, and master data changes.
2. THE NecoKeeper SHALL record the operation date/time, operator, operation details, and values before and after the change in the audit logs.
3. WHEN an administrator accesses the audit log screen, THE NecoKeeper SHALL display the audit logs in chronological order.
4. THE NecoKeeper SHALL provide filters on the audit log screen for date range, operator, and operation type.
5. THE NecoKeeper SHALL allow audit logs to be exported in CSV format.
6. THE NecoKeeper SHALL store `last_updated_at` and `last_updated_by` for each record (without storing diff bodies).

### Requirement 24: Search Functionality

**User Story:** As a staff member, I want to quickly search for cats so that I can rapidly access information about the target cat.

#### Acceptance Criteria

1. THE NecoKeeper SHALL place a search box on the Animal Master list screen.
2. WHEN a user enters a keyword in the search box, THE NecoKeeper SHALL perform a partial match search on cat name, pattern/color, distinguishing features, and temperament.
3. THE NecoKeeper SHALL display search results in real time.
4. THE NecoKeeper SHALL provide advanced search functionality (sex, age range, Status, rescue date range).
5. WHEN a user specifies advanced search conditions and clicks the search button, THE NecoKeeper SHALL display only the cats that match the conditions.

### Requirement 25: CSV Export of Care Logs

**User Story:** As an administrator, I want to export care logs in CSV format so that the data can be analyzed with external tools.

#### Acceptance Criteria

1. WHEN the administrator clicks the CSV export button on the care log list screen, THE NecoKeeper SHALL display a dialog for specifying a period.
2. WHEN the administrator specifies a period and clicks the execute export button, THE NecoKeeper SHALL allow all care logs for the specified period to be downloaded in CSV format.
3. THE NecoKeeper SHALL include cat name, record date/time, recorder, time of day, appetite, energy level, urination, cleaning, and notes in the CSV file.
4. THE NecoKeeper SHALL provide a per-cat care log CSV export function.

### Requirement 26: Visualization of Weight Trends

**User Story:** As a staff member, I want to check a cat's weight trend in graph form so that I can visually understand changes in its health condition.

#### Acceptance Criteria

1. WHEN a user accesses a cat's detail screen, THE NecoKeeper SHALL display a weight trend graph for the past 3 months.
2. THE NecoKeeper SHALL merge and display weight data from both care logs and medical records in the weight trend graph.
3. THE NecoKeeper SHALL allow the period for the weight trend graph to be changed (1 month, 3 months, 6 months, 1 year, all time).
4. WHEN the weight has increased or decreased by 10% or more compared to the previous measurement, THE NecoKeeper SHALL display a warning marker on the graph.

### Requirement 27: Image Gallery

**User Story:** As a staff member, I want to manage multiple photos of cats so that I can visually record growth and the progress of injuries.

#### Acceptance Criteria

1. WHEN a user accesses the image gallery tab on a cat's detail screen, THE NecoKeeper SHALL display all images of that cat as thumbnails.
2. WHEN a user clicks the "Add Image" button, THE NecoKeeper SHALL display an image upload dialog.
3. WHEN a user selects an image file and clicks the upload button, THE NecoKeeper SHALL save the image and allow the shooting date and description to be entered.
4. WHEN a user clicks a thumbnail, THE NecoKeeper SHALL display the image in an enlarged view.
5. THE NecoKeeper SHALL allow the image gallery to be sorted by shooting date or registration date.
6. THE NecoKeeper SHALL allow administrators to configure the maximum number of images per cat in the settings screen.
7. THE NecoKeeper SHALL allow administrators to configure the maximum file size (in MB) per image in the settings screen.
8. WHEN the number of images for a cat has reached the configured maximum, THE NecoKeeper SHALL disable the "Add Image" button and display a message.
9. WHEN an image being uploaded exceeds the configured maximum file size, THE NecoKeeper SHALL reject the upload and display an error message.
10. THE NecoKeeper SHALL apply default settings of a maximum of 20 images per cat and a maximum file size of 5 MB per image.

### Requirement 28: Non-functional Requirements (Performance and Availability)

**User Story:** As a system administrator, I want to ensure stable system performance so that users can use the system comfortably.

#### Acceptance Criteria

1. THE NecoKeeper SHALL complete screen transitions in the admin interface within 3 seconds.
2. THE NecoKeeper SHALL complete saving records on the Public form within 2 seconds.
3. THE NecoKeeper SHALL complete PDF generation within 10 seconds.
4. THE NecoKeeper SHALL support up to 20 concurrent users.
5. THE NecoKeeper SHALL operate comfortably with up to 100 registered cats.
6. THE NecoKeeper SHALL target a system uptime of 95% or higher.
7. THE NecoKeeper SHALL support the latest and one previous version of Chrome, Firefox, Safari, and Edge.
8. THE NecoKeeper SHALL support mobile browsers on iOS 14 and later and Android 10 and later.

### Requirement 29: Error Handling and Exception Processing

**User Story:** As a user, I want to receive appropriate messages when errors occur so that I can understand and deal with the problem.

#### Acceptance Criteria

1. WHEN a system error occurs, THE NecoKeeper SHALL display a clear error message to the user.
2. WHEN a database connection error occurs, THE NecoKeeper SHALL record an error log and notify the administrator.
3. WHEN a file upload fails, THE NecoKeeper SHALL display the reason for failure to the user and prompt them to retry.
4. WHEN a network error occurs, THE NecoKeeper SHALL switch to offline mode (PWA) and automatically synchronize after recovery.
5. WHEN data inconsistencies are detected, THE NecoKeeper SHALL display a warning to the administrator and prompt for correction.
6. THE NecoKeeper SHALL record all errors in a log file and assign an error level (INFO, WARNING, ERROR, CRITICAL).

### Requirement 30: Data Retention Period and Privacy Policy

**User Story:** As a system administrator, I want to properly manage data retention periods and privacy so that legal compliance and storage management can be achieved.

#### Acceptance Criteria

1. THE NecoKeeper SHALL retain backup files for 90 days.
2. THE NecoKeeper SHALL automatically delete backup files older than 90 days.
3. THE NecoKeeper SHALL retain data for adopted cats indefinitely (for audit purposes).
4. THE NecoKeeper SHALL retain adoption applicants' personal information for 3 years after adoption is completed.
5. THE NecoKeeper SHALL provide a function to completely delete relevant data when an administrator receives a personal data deletion request.
6. THE NecoKeeper SHALL provide a privacy policy page that clearly states the purposes of data collection and use.

### Requirement 31: Initial Setup and Master Data

**User Story:** As a system administrator, I want to easily perform the initial setup so that the system can be put into use quickly.

#### Acceptance Criteria

1. WHEN the system is started for the first time, THE NecoKeeper SHALL display a setup wizard.
2. THE NecoKeeper SHALL allow the creation of an initial administrator account (email address, password, name) in the setup wizard.
3. THE NecoKeeper SHALL allow organization information (organization name, address, contact information) to be registered in the setup wizard.
4. THE NecoKeeper SHALL allow basic settings (language, time zone, image limits) to be configured in the setup wizard.
5. WHEN setup is completed, THE NecoKeeper SHALL redirect the user to the admin interface.
6. THE NecoKeeper SHALL provide sample data (one cat and one volunteer) as initial data.

### Requirement 32: Help and Support Functions

**User Story:** As a user, I want to learn how to use the system so that I can resolve issues on my own.

#### Acceptance Criteria

1. THE NecoKeeper SHALL place a help button in the admin interface.
2. WHEN a user clicks the help button, THE NecoKeeper SHALL display an online help page.
3. THE NecoKeeper SHALL explain how to use each feature in the online help, with screenshots or images.
4. THE NecoKeeper SHALL provide a Frequently Asked Questions (FAQ) page.
5. THE NecoKeeper SHALL provide an inquiry form.
6. WHEN a user submits the inquiry form, THE NecoKeeper SHALL send an email notification to the administrator.

## Constraints

### Technical Constraints

1. THE NecoKeeper SHALL use FastAPI, SQLite, WeasyPrint, AdminLTE, and Tailwind CSS.
2. THE NecoKeeper SHALL run on Python version 3.10 or later (for type hint syntax such as `X | None`).
3. THE NecoKeeper SHALL use only libraries under open-source licenses (MIT, Apache 2.0, etc.).
4. THE NecoKeeper SHALL use modern SQLAlchemy 2.0+ patterns (`Mapped`, `mapped_column`).
5. THE NecoKeeper SHALL pass type checking in Mypy strict mode.
6. THE NecoKeeper SHALL use PostgreSQL-compatible naming conventions (to allow for future migration).
7. THE NecoKeeper SHALL include full type hints and docstrings in all code.

### Budget and Resource Constraints

1. THE NecoKeeper SHALL be operable on free or low-cost (≤ USD $10/month) hosting services.
2. THE NecoKeeper SHALL minimize the use of paid external APIs (OCR is an optional feature).

### Schedule Constraints

1. THE NecoKeeper SHALL complete the MVP (Minimum Viable Product) within the hackathon period.

## Assumptions

### Infrastructure Assumptions

1. The hosting service supports Python 3.9 or later.
2. The hosting service provides persistent storage for SQLite databases.
3. HTTPS communication is available.

### User Assumptions

1. Users own a smartphone or PC.
2. Users have access to an internet connection (offline functionality is supplemental).
3. Volunteers can perform basic smartphone operations (QR code scanning, form input).
