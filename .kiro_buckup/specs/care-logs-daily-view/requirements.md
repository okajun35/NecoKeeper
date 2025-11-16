# Requirements Document

## Introduction

世話記録一覧画面を日次ビュー形式に改修します。現在の縦長リスト形式から、1日を横に並べて朝・昼・夕の記録を一目で確認できる形式に変更します。

## Glossary

- **System**: 世話記録一覧画面（Care Logs List Page）
- **Daily View**: 1日の記録を1行で表示する形式
- **Time Slot**: 時点（朝・昼・夕）
- **Record Status**: 記録の有無（○=記録あり、×=記録なし）
- **Admin User**: 管理画面にアクセスする管理者・スタッフ・獣医師

## Requirements

### Requirement 1: 日次ビュー表示

**User Story:** As an Admin User, I want to view care logs in a daily format with morning, noon, and evening records displayed horizontally, so that I can quickly understand the daily care status for each cat.

#### Acceptance Criteria

1. WHEN THE System displays the care logs list, THE System SHALL show each date as a single row with columns for date, cat name, morning record, noon record, and evening record
2. WHEN a care log record exists for a specific time slot, THE System SHALL display "○" (circle) in the corresponding column
3. WHEN a care log record does not exist for a specific time slot, THE System SHALL display "×" (cross) in the corresponding column
4. WHEN THE System displays the daily view, THE System SHALL sort records by date in descending order (newest first)
5. WHEN THE System displays the daily view, THE System SHALL group records by date and cat

### Requirement 2: 記録へのナビゲーション

**User Story:** As an Admin User, I want to click on a record status indicator to navigate to the corresponding care log entry, so that I can view or edit the details.

#### Acceptance Criteria

1. WHEN an Admin User clicks on "○" (existing record), THE System SHALL navigate to the care log detail/edit page for that specific record
2. WHEN an Admin User clicks on "×" (no record), THE System SHALL navigate to the care log creation page with pre-filled date, cat, and time slot information
3. WHEN THE System navigates to a care log page, THE System SHALL pass the necessary parameters (animal_id, date, time_slot, log_id if exists) via URL or form data

### Requirement 3: フィルタリング機能

**User Story:** As an Admin User, I want to filter care logs by cat and date range, so that I can focus on specific animals or time periods.

#### Acceptance Criteria

1. WHEN THE System displays the care logs list, THE System SHALL provide a filter dropdown for selecting a specific cat or "all cats"
2. WHEN THE System displays the care logs list, THE System SHALL provide date range inputs for start date and end date
3. WHEN an Admin User applies filters, THE System SHALL update the daily view to show only records matching the filter criteria
4. WHEN an Admin User clears filters, THE System SHALL reset to show all records with default date range (last 7 days)

### Requirement 4: ページネーション

**User Story:** As an Admin User, I want to navigate through multiple pages of care logs, so that I can view historical records without performance issues.

#### Acceptance Criteria

1. WHEN THE System displays more than 20 daily records, THE System SHALL paginate the results with 20 records per page
2. WHEN THE System displays pagination controls, THE System SHALL show current page number, total pages, and total record count
3. WHEN an Admin User clicks "Next" or "Previous", THE System SHALL load the corresponding page while maintaining filter settings
4. WHEN THE System loads a new page, THE System SHALL scroll to the top of the table

### Requirement 5: レスポンシブデザイン

**User Story:** As an Admin User, I want the daily view to be readable on different screen sizes, so that I can access care logs from various devices.

#### Acceptance Criteria

1. WHEN THE System displays on desktop screens (>1024px), THE System SHALL show all columns in a horizontal table layout
2. WHEN THE System displays on tablet screens (768px-1024px), THE System SHALL maintain the table layout with adjusted column widths
3. WHEN THE System displays on mobile screens (<768px), THE System SHALL use a card-based layout with stacked information for each day
4. WHEN THE System displays on any screen size, THE System SHALL ensure all interactive elements (○, ×) are easily tappable/clickable

### Requirement 6: データ取得とパフォーマンス

**User Story:** As an Admin User, I want the care logs list to load quickly, so that I can efficiently manage daily records.

#### Acceptance Criteria

1. WHEN THE System loads the care logs list, THE System SHALL fetch data from the API endpoint `/api/v1/care-logs/daily-view`
2. WHEN THE System fetches data, THE System SHALL include authentication token in the request header
3. WHEN THE System receives data from the API, THE System SHALL transform the data into daily view format (grouping by date and cat)
4. WHEN THE System encounters an API error, THE System SHALL display a user-friendly error message and provide a retry option
5. WHEN THE System loads data, THE System SHALL show a loading indicator until data is ready

### Requirement 7: CSVエクスポート

**User Story:** As an Admin User, I want to export the filtered care logs to CSV format, so that I can analyze data in external tools.

#### Acceptance Criteria

1. WHEN an Admin User clicks the "CSVエクスポート" button, THE System SHALL generate a CSV file containing all filtered records (not just current page)
2. WHEN THE System generates CSV, THE System SHALL include columns: date, cat name, morning status, noon status, evening status, and record IDs
3. WHEN THE System generates CSV, THE System SHALL use UTF-8 encoding with BOM for Japanese character support
4. WHEN THE System completes CSV generation, THE System SHALL trigger a file download with filename format "care_logs_YYYYMMDD.csv"
