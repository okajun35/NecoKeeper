# Requirements Document

## Introduction

NecoKeeperは、日本の保護猫活動における記録・管理業務をデジタル化するWebシステムです。紙台帳やスプレッドシートで行われている保護猫の個体管理、日々の世話記録、獣医診療記録、里親探し・譲渡管理を、スマートフォンでも簡単に扱える形で統合管理します。QRコードを活用した認証不要の記録入力、PDF帳票出力、SQLiteベースのローカル運用を特徴とし、ITリテラシーが低〜中程度の保護猫団体・地域猫ボランティア・獣医師を対象としています。代表＋スタッフ＋ボランティア10名前後の小規模団体での運用を想定し、紙との併用や段階的なデジタル化にも対応します。団体代表は保護猫活動以外に本業を持つため、管理業務の負担を最小限にする設計を重視します。保護頭数は10〜20頭程度を想定しています。Render、Railway、Fly.ioなどの無料ホスティングサービスへの簡単デプロイにより、小規模団体でも運用コストを抑えられます。

## Glossary

- **NecoKeeper**: 本システムの名称。保護猫管理Webシステム
- **Animal Master**: 猫の個体情報を管理するマスターデータベース
- **CareLog**: 日々の世話記録（体重、食事、排泄など）を記録するログシステム
- **Medical Record**: 獣医による診療記録システム
- **Public Form**: 認証不要で誰でもアクセス可能な記録入力フォーム
- **QR Card**: 猫の顔写真・名前・QRコード付きのPDF台帳カード
- **Volunteer**: ボランティア記録者
- **Vet**: 獣医師ユーザー
- **Admin**: システム管理者兼団体の代表
- **Staff**: スタッフユーザー（CSV取込、帳票閲覧、記録閲覧権限あり）


- **WeasyPrint**: HTMLからPDFを生成するライブラリ
- **FastAPI**: バックエンドフレームワーク
- **SQLite**: 本番運用データベース
- **AdminLTE**: 管理画面UIフレームワーク
- **Tailwind CSS**: PublicフォームのCSSフレームワーク
- **Adoption**: 里親への譲渡プロセス
- **Applicant**: 里親希望者
- **Status**: 猫の状態（保護中、譲渡可能、譲渡済み、治療中など）
- **i18n**: 国際化（Internationalization）。多言語対応のための仕組み
- **Translation File**: 対訳ファイル。言語ごとのUI文言を定義したJSONファイル
- **OCR**: 光学文字認識（Optical Character Recognition）。画像やPDFから文字を認識する技術
- **Kiro Hook**: Kiroの自動実行機能。ファイル追加などのイベントをトリガーにエージェント実行を開始
- **MCP**: Model Context Protocol。外部サービスとの連携プロトコル

- **Render**: クラウドホスティングサービス。無料枠あり
- **Railway**: クラウドプラットフォーム。無料枠あり
- **Fly.io**: グローバル分散ホスティングサービス。無料枠あり

## Requirements

### Requirement 1: 猫の個体登録と管理

**User Story:** 保護猫団体の管理者として、保護している猫の個体情報を登録・編集できるようにしたい。これにより、各猫の識別情報を正確に管理できる。

#### Acceptance Criteria

1. WHEN 管理者がAnimal Master画面で新規登録ボタンをクリックしたとき、THE NecoKeeper SHALL 猫の個体情報入力フォームを表示する
2. WHEN 管理者が必須項目（顔写真、柄・色、尻尾の長さ、年齢、性別）を入力して保存ボタンをクリックしたとき、THE NecoKeeper SHALL 猫の個体情報をAnimal Masterに保存する
3. WHEN 管理者がAnimal Master一覧画面で既存の猫レコードを選択したとき、THE NecoKeeper SHALL 当該猫の詳細情報を表示し編集可能にする
4. THE NecoKeeper SHALL 猫の識別項目として顔写真、柄・色、尻尾の長さ、首輪有無・色、年齢（大きさ）、性別、耳カット有無、外傷・特徴・性格を記録する
5. THE NecoKeeper SHALL 猫レコードの物理削除を行わず、Statusによる論理削除で管理する

### Requirement 2: QRカードと紙記録フォームのPDF出力

**User Story:** 保護猫団体のスタッフとして、猫ごとのQRコード付き台帳カードと紙記録フォームをPDF出力したい。これにより、現場で猫を識別し、スマホまたは紙で記録入力できる。

#### Acceptance Criteria

1. WHEN 管理者がAnimal Master画面で猫を選択してQRカード出力ボタンをクリックしたとき、THE NecoKeeper SHALL 当該猫の名前、顔写真、QRコード、IDを含むA6サイズのPDFを生成する
2. WHEN 管理者が複数の猫を選択して面付けカード出力ボタンをクリックしたとき、THE NecoKeeper SHALL A4用紙に2×5枚（10枚）のQRカードを配置したPDFを生成する
3. THE NecoKeeper SHALL QRコードに猫の個体IDと記録入力用URLを埋め込む
4. WHEN ユーザーがQRコードをスマートフォンでスキャンしたとき、THE NecoKeeper SHALL 当該猫のPublic記録入力フォームを表示する
5. WHEN 管理者がAnimal Master画面で猫を選択して紙記録フォーム出力ボタンをクリックしたとき、THE NecoKeeper SHALL 1ヶ月分の日付欄と記録欄（時点、食欲、元気、排尿、清掃、メモ）を含むA4サイズのPDFを生成する
6. THE NecoKeeper SHALL 紙記録フォームに猫の名前、顔写真、ID、対象年月を表示する
7. THE NecoKeeper SHALL 紙記録フォームの各日付欄に記録者名欄を配置する
8. WHEN 管理者が複数の猫を選択して紙記録フォーム一括出力ボタンをクリックしたとき、THE NecoKeeper SHALL 選択された全猫の紙記録フォームを1つのPDFにまとめて生成する

### Requirement 3: 認証不要の日々の世話記録入力

**User Story:** ボランティアとして、QRコードをスキャンして認証なしで猫の世話記録を入力したい。これにより、現場で素早く記録を残せる。

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

### Requirement 4: 記録者管理

**User Story:** 管理者として、不定期・継続的に活動するボランティア記録者を登録・管理したい。これにより、誰が記録したかを追跡できる。

#### Acceptance Criteria

1. WHEN 管理者がVolunteerマスター画面で新規登録ボタンをクリックしたとき、THE NecoKeeper SHALL 記録者情報（名前、連絡先、所属、活動開始日）の入力フォームを表示する
2. WHEN 管理者が記録者情報を入力して保存ボタンをクリックしたとき、THE NecoKeeper SHALL 記録者情報をVolunteerマスターに保存する
3. THE NecoKeeper SHALL Volunteerマスターに活動状態（アクティブ、休止中）を記録する
4. THE NecoKeeper SHALL Public記録フォームの選択リストにアクティブ状態のボランティアのみを表示する
5. WHEN 管理者がVolunteerマスター画面で記録者を選択したとき、THE NecoKeeper SHALL 当該記録者の活動履歴（記録回数、最終記録日）を表示する

### Requirement 5: 獣医診療記録の登録

**User Story:** 獣医師として、診療内容を記録したい。これにより、医療履歴を正確に管理できる。

#### Acceptance Criteria

1. WHEN 獣医師または管理者が認証済みでMedical Record画面にアクセスしたとき、THE NecoKeeper SHALL 診療記録入力フォームを表示する
2. THE NecoKeeper SHALL 診療記録入力フォームに診療年月日、時間帯、薬品名、投薬量、その他（ワクチンのロット番号など）、体重、体温、症状、コメントの入力欄を表示する
3. WHEN 獣医師が必須項目（診療年月日、体重、症状）を入力して保存ボタンをクリックしたとき、THE NecoKeeper SHALL 診療記録をMedical Recordに保存する
4. THE NecoKeeper SHALL 薬品名入力欄でMedicationマスターからの選択または自由入力を可能にする
5. THE NecoKeeper SHALL 診療記録の一覧画面で猫ごとの診療履歴を時系列で表示する

### Requirement 6: 診療行為マスターデータ管理

**User Story:** 管理者として、診療行為（薬剤・ワクチン・検査）のマスターデータを期間別の価格で管理したい。これにより、値上がりや自由診療の原価・請求価格を正確に記録できる。

#### Acceptance Criteria

1. WHEN 管理者が診療行為マスター画面で新規登録ボタンをクリックしたとき、THE NecoKeeper SHALL 診療名称、適用開始日、適用終了日、原価、請求価格、投薬・処置料金、通貨単位（JPY/USD）の入力フォームを表示する
2. WHEN 管理者がマスターデータを入力して保存ボタンをクリックしたとき、THE NecoKeeper SHALL 当該マスターデータをデータベースに保存する
3. THE NecoKeeper SHALL 適用終了日を未設定（NULL）にすることで、現在も有効な価格として扱う
4. THE NecoKeeper SHALL 料金計算を「請求価格×投薬量＋投薬・処置料金」で実施する
5. THE NecoKeeper SHALL 原価、請求価格、投薬・処置料金を小数点2桁までのDECIMAL型で管理する

### Requirement 7: 診療明細出力

**User Story:** 獣医師として、診療記録の明細を複数形式で出力したい。これにより、団体への請求書や記録保管、データ分析に使用できる。

#### Acceptance Criteria

1. WHEN 獣医師または管理者が診療記録を選択して明細出力ボタンをクリックしたとき、THE NecoKeeper SHALL PDF、CSV、Excelの形式選択オプションを表示する
2. WHEN 獣医師がPDF形式を選択したとき、THE NecoKeeper SHALL A4縦サイズの診療明細PDFを生成する
3. THE NecoKeeper SHALL 診療明細PDFに猫の顔写真、診療日、時間帯、体重、体温、症状、薬品名、投薬量、その他、コメントを含める
4. WHEN 獣医師がCSV形式を選択したとき、THE NecoKeeper SHALL 診療記録データをCSV形式でダウンロード可能にする
5. WHEN 獣医師がExcel形式を選択したとき、THE NecoKeeper SHALL 診療記録データをExcel形式（.xlsx）でダウンロード可能にする

### Requirement 8: CSVインポート・エクスポート

**User Story:** 管理者として、猫の個体情報をCSV形式でインポート・エクスポートしたい。これにより、既存データの移行やバックアップが容易になる。

#### Acceptance Criteria

1. WHEN 管理者がAnimal Master画面でCSVエクスポートボタンをクリックしたとき、THE NecoKeeper SHALL 全猫の個体情報をCSV形式でダウンロード可能にする
2. WHEN 管理者がAnimal Master画面でCSVインポートボタンをクリックしてCSVファイルを選択したとき、THE NecoKeeper SHALL CSVファイルの内容を検証する
3. WHEN CSVファイルの形式が正しいとき、THE NecoKeeper SHALL CSVデータをAnimal Masterにインポートする
4. WHEN CSVファイルに形式エラーがあるとき、THE NecoKeeper SHALL エラー内容を表示しインポートを中止する

### Requirement 9: 帳票出力（日報・週報・月次集計）

**User Story:** 管理者として、期間別の世話記録集計や医療費集計を複数形式で出力したい。これにより、活動報告や会計処理、データ分析に使用できる。

#### Acceptance Criteria

1. WHEN 管理者が帳票出力画面で期間を指定して日報出力ボタンをクリックしたとき、THE NecoKeeper SHALL PDF、CSV、Excelの形式選択オプションを表示する
2. WHEN 管理者がPDF形式を選択したとき、THE NecoKeeper SHALL 指定期間のCareLog集計をPDF形式で生成する
3. WHEN 管理者がCSV形式を選択したとき、THE NecoKeeper SHALL 指定期間のCareLog集計をCSV形式でダウンロード可能にする
4. WHEN 管理者がExcel形式を選択したとき、THE NecoKeeper SHALL 指定期間のCareLog集計をExcel形式（.xlsx）でダウンロード可能にする
5. WHEN 管理者が帳票出力画面で期間を指定して週報出力ボタンをクリックしたとき、THE NecoKeeper SHALL PDF、CSV、Excelの形式選択オプションを表示する
6. WHEN 管理者が帳票出力画面で月を指定して月次集計出力ボタンをクリックしたとき、THE NecoKeeper SHALL 指定月の医療費総計、診療件数、対象動物数をPDF、CSV、Excel形式で出力可能にする
7. WHEN 管理者が猫の詳細画面で個別帳票出力ボタンをクリックしたとき、THE NecoKeeper SHALL 当該猫の世話記録と診療記録をまとめた帳票をPDF、CSV、Excel形式で出力可能にする
8. THE NecoKeeper SHALL 猫ごとの個別帳票に期間指定オプション（全期間、過去1ヶ月、過去3ヶ月、過去6ヶ月、カスタム期間）を提供する

### Requirement 10: 権限管理とアクセス制御

**User Story:** システム管理者として、ユーザーごとに適切な権限を設定したい。これにより、セキュリティと業務分担を適切に管理できる。

#### Acceptance Criteria

1. THE NecoKeeper SHALL adminロールに全機能（台帳、記録、診療、マスター、設定）へのアクセス権限を付与する
2. THE NecoKeeper SHALL vetロールに診療記録のCRUD、帳票出力、集計へのアクセス権限を付与する
3. THE NecoKeeper SHALL staffロールにCSV取込、帳票閲覧、世話記録・診療記録の閲覧へのアクセス権限を付与する
4. THE NecoKeeper SHALL read_onlyロールに閲覧専用権限を付与する
5. THE NecoKeeper SHALL volunteerロールにPublicフォーム入力のみを許可し、認証を不要とする
6. WHEN 権限のないユーザーが制限された機能にアクセスしようとしたとき、THE NecoKeeper SHALL アクセスを拒否しエラーメッセージを表示する

### Requirement 11: データバックアップ

**User Story:** システム管理者として、データベースとメディアファイルを自動バックアップしたい。これにより、データ損失のリスクを軽減できる。

#### Acceptance Criteria

1. THE NecoKeeper SHALL 毎晩定時にapp.sqlite3データベースファイルのバックアップを実行する
2. THE NecoKeeper SHALL 毎晩定時に/mediaディレクトリ（画像ファイル等）のバックアップを実行する
3. THE NecoKeeper SHALL バックアップファイルに日付タイムスタンプを付与して保存する
4. WHEN バックアップ処理が失敗したとき、THE NecoKeeper SHALL エラーログを記録する
5. THE NecoKeeper SHALL 毎日1回、/data/app.sqlite3を日時付きでコピーし7世代保持する

### Requirement 12: 管理画面UI

**User Story:** 管理者として、直感的で使いやすい管理画面を使用したい。これにより、効率的にシステムを操作できる。

#### Acceptance Criteria

1. THE NecoKeeper SHALL 管理画面UIにAdminLTEフレームワークを使用する
2. THE NecoKeeper SHALL 管理画面に猫台帳、世話記録、診療記録、マスター管理、帳票出力、設定のメニューを配置する
3. WHEN 管理者が管理画面にログインしたとき、THE NecoKeeper SHALL ダッシュボードに登録猫数、Status別猫数を表示する
4. THE NecoKeeper SHALL 管理画面の各一覧画面に検索・フィルタ・ソート機能を提供する

### Requirement 13: Publicフォームのモバイル最適化

**User Story:** ボランティアとして、スマートフォンで快適に記録入力したい。これにより、現場での記録作業がスムーズになる。

#### Acceptance Criteria

1. THE NecoKeeper SHALL PublicフォームをTailwind CSSでレスポンシブデザインとして実装する
2. THE NecoKeeper SHALL Publicフォームの入力ボタンを指で押しやすい大きさ（最小44×44px）で配置する
3. THE NecoKeeper SHALL Publicフォームを1画面完結型とし、スクロールを最小限にする
4. THE NecoKeeper SHALL Publicフォームの保存ボタンを画面下部に固定配置する
5. WHEN ユーザーがスマートフォンでPublicフォームにアクセスしたとき、THE NecoKeeper SHALL モバイル最適化されたレイアウトを表示する

### Requirement 14: 里親探しと譲渡管理

**User Story:** 保護猫団体の代表として、保護猫の里親希望者を管理し、譲渡プロセスを記録したい。これにより、猫の新しい飼い主を適切にマッチングできる。

#### Acceptance Criteria

1. WHEN 管理者が里親希望者管理画面で新規登録ボタンをクリックしたとき、THE NecoKeeper SHALL 希望者情報（氏名、連絡先、住所、家族構成、飼育環境、希望条件）の入力フォームを表示する
2. WHEN 管理者が里親希望者情報を入力して保存ボタンをクリックしたとき、THE NecoKeeper SHALL 希望者情報をApplicantマスターに保存する
3. WHEN 管理者が猫の詳細画面で譲渡候補者を選択して面談記録を入力したとき、THE NecoKeeper SHALL 面談日、面談内容、判定結果を記録する
4. WHEN 管理者が譲渡決定ボタンをクリックして譲渡日と譲渡先を入力したとき、THE NecoKeeper SHALL 猫のStatusを「譲渡済み」に更新し、譲渡記録を保存する
5. THE NecoKeeper SHALL 譲渡後フォロー記録（譲渡後の連絡日、状況確認内容）を登録可能にする

### Requirement 15: 猫のステータス管理と論理削除

**User Story:** スタッフとして、猫の現在の状態を管理したい。これにより、保護中・治療中・譲渡可能・譲渡済みなどの状況を把握でき、監査のために過去の記録も保持できる。

#### Acceptance Criteria

1. THE NecoKeeper SHALL 猫のStatusとして「保護中」「治療中」「譲渡可能」「譲渡済み」「死亡」「その他」を設定可能にする
2. WHEN 管理者が猫の詳細画面でStatusを変更して保存ボタンをクリックしたとき、THE NecoKeeper SHALL 猫のStatusを更新し、変更履歴（変更日時、変更者、変更前Status、変更後Status）を記録する
3. WHEN 管理者がAnimal Master一覧画面でStatusフィルタを選択したとき、THE NecoKeeper SHALL 指定Statusの猫のみを表示する
4. THE NecoKeeper SHALL ダッシュボードにStatus別の猫数を集計表示する
5. THE NecoKeeper SHALL 猫レコードを物理削除せず、Statusによる論理削除で管理する
6. WHEN 管理者がAnimal Master一覧画面にアクセスしたとき、THE NecoKeeper SHALL デフォルトで「保護中」「治療中」「譲渡可能」のStatusの猫のみを表示する
7. WHEN 管理者が「全て表示」フィルタを選択したとき、THE NecoKeeper SHALL 「譲渡済み」「死亡」を含む全Statusの猫を表示する

### Requirement 16: 活動状況の可視化

**User Story:** 保護猫団体の代表として、現在の活動状況を一目で把握したい。これにより、団体運営の意思決定に役立てられる。

#### Acceptance Criteria

1. WHEN 管理者がダッシュボードにアクセスしたとき、THE NecoKeeper SHALL 保護中の猫数、譲渡可能な猫数、今月の譲渡数を表示する
2. WHEN 管理者がダッシュボードにアクセスしたとき、THE NecoKeeper SHALL 今月の診療件数、今月の医療費総額を表示する
3. WHEN 管理者がダッシュボードにアクセスしたとき、THE NecoKeeper SHALL 直近7日間の世話記録入力数の推移グラフを表示する
4. WHEN 管理者がダッシュボードにアクセスしたとき、THE NecoKeeper SHALL 長期保護猫（保護期間6ヶ月以上）の一覧を表示する

### Requirement 17: 紙記録からのデータ移行支援

**User Story:** スタッフとして、既存の紙記録を効率的にシステムに入力したい。これにより、過去の記録もデジタル化でき、手入力の負担を軽減できる。

#### Acceptance Criteria

1. WHEN スタッフが管理画面で過去日付を指定してCareLogを入力したとき、THE NecoKeeper SHALL 指定日付で記録を保存する
2. WHEN スタッフが管理画面で過去日付を指定してMedical Recordを入力したとき、THE NecoKeeper SHALL 指定日付で診療記録を保存する
3. THE NecoKeeper SHALL 記録入力時に「紙記録からの転記」フラグを設定可能にする
4. THE NecoKeeper SHALL CSVインポート機能で過去の世話記録を一括登録可能にする
5. WHEN スタッフが管理画面で画像ファイル（JPG、PNG）またはPDFファイルをアップロードしたとき、THE NecoKeeper SHALL OCR処理を実行して文字認識を行う
6. WHEN OCR処理が完了したとき、THE NecoKeeper SHALL 認識されたテキストを編集可能なフォームに表示する
7. WHEN スタッフがOCR結果を確認・修正して保存ボタンをクリックしたとき、THE NecoKeeper SHALL 記録をデータベースに保存する
8. THE NecoKeeper SHALL Kiro Hook機能を使用して、指定フォルダに画像・PDFファイルが追加されたときに自動的にOCR処理を実行する
9. THE NecoKeeper SHALL MCP（Model Context Protocol）サーバ連携により、外部OCRサービス（Tesseract、Google Cloud Vision API、AWS Textractなど）を利用可能にする
10. THE NecoKeeper SHALL OCR処理の進捗状況と結果をスタッフに通知する

### Requirement 18: PWA対応とオフライン機能

**User Story:** ボランティアとして、インターネット接続が不安定な現場でも記録入力したい。これにより、オフライン時でも作業を継続できる。

#### Acceptance Criteria

1. THE NecoKeeper SHALL Publicフォームをプログレッシブウェブアプリ（PWA）として実装する
2. WHEN ユーザーがスマートフォンでPublicフォームに初回アクセスしたとき、THE NecoKeeper SHALL ホーム画面への追加を促すプロンプトを表示する
3. WHEN ユーザーがオフライン状態でPublicフォームに記録を入力したとき、THE NecoKeeper SHALL 記録をローカルストレージに一時保存する
4. WHEN ユーザーのデバイスがオンラインに復帰したとき、THE NecoKeeper SHALL ローカルストレージの記録を自動的にサーバーに同期する
5. THE NecoKeeper SHALL 同期状態（同期済み、同期待ち、同期中）をユーザーに表示する
6. THE NecoKeeper SHALL 管理画面もPWA対応とし、スマートフォンでの閲覧・操作を最適化する
7. THE NecoKeeper SHALL 同一レコードの競合は最終保存（updated_at）優先とする

### Requirement 19: 多言語対応（日本語・英語）

**User Story:** ハッカソン参加者や海外ボランティアとして、英語でもシステムを利用したい。これにより、国際的な保護猫活動にも対応できる。

#### Acceptance Criteria

1. THE NecoKeeper SHALL 日本語と英語の2言語に対応する
2. THE NecoKeeper SHALL UI表示文言を対訳ファイル（JSON形式）で管理する
3. WHEN ユーザーが言語設定画面で言語を選択したとき、THE NecoKeeper SHALL 選択された言語でUI全体を表示する
4. THE NecoKeeper SHALL ユーザーの言語設定をブラウザのローカルストレージに保存する
5. WHEN ユーザーが初回アクセス時に言語設定がないとき、THE NecoKeeper SHALL ブラウザの言語設定（navigator.language）から日本語または英語を自動選択する
6. THE NecoKeeper SHALL 対訳ファイルに以下のカテゴリの文言を含める：共通UI、猫台帳、世話記録、診療記録、里親管理、帳票、エラーメッセージ
7. THE NecoKeeper SHALL PDF帳票出力時も選択された言語で出力する

### Requirement 20: 簡単デプロイとホスティング

**User Story:** システム管理者として、無料または低コストのホスティングサービスに簡単にデプロイしたい。これにより、小規模団体でも運用コストを抑えられる。

#### Acceptance Criteria

1. THE NecoKeeper SHALL Render、Railway、Fly.ioなどの永続化ストレージをサポートする無料枠があるホスティングサービスにデプロイ可能な構成とする
2. THE NecoKeeper SHALL デプロイ設定ファイル（render.yaml、railway.json、fly.toml等）をプロジェクトに含める
3. THE NecoKeeper SHALL 環境変数による設定管理（データベースパス、シークレットキー、OCR APIキーなど）をサポートする
4. THE NecoKeeper SHALL SQLiteデータベースの永続化ストレージ設定（ボリュームマウント）をドキュメント化する
5. WHEN 管理者がデプロイコマンドを実行したとき、THE NecoKeeper SHALL 必要な依存関係を自動インストールし、アプリケーションを起動する
6. THE NecoKeeper SHALL デプロイ手順を記載したREADME.mdを提供する
7. THE NecoKeeper SHALL ワンクリックデプロイボタン（Deploy to Render、Deploy to Railwayなど）をREADME.mdに配置する

### Requirement 21: 認証とユーザー管理

**User Story:** システム管理者として、管理画面へのアクセスを制御し、ユーザーを管理したい。これにより、セキュリティを確保できる。

#### Acceptance Criteria

1. WHEN ユーザーが管理画面にアクセスしたとき、THE NecoKeeper SHALL ログイン画面を表示する
2. WHEN ユーザーがメールアドレスとパスワードを入力してログインボタンをクリックしたとき、THE NecoKeeper SHALL 認証情報を検証する
3. WHEN 認証が成功したとき、THE NecoKeeper SHALL セッションIDをCookieに保存し管理画面にリダイレクトする
4. WHEN 認証が失敗したとき、THE NecoKeeper SHALL エラーメッセージを表示する
5. THE NecoKeeper SHALL 管理者がユーザー管理画面で新規ユーザーを登録できる機能を提供する
6. THE NecoKeeper SHALL ユーザー登録時にメールアドレス、パスワード、氏名、ロール（admin/vet/staff/read_only）を入力可能にする
7. THE NecoKeeper SHALL パスワードをbcryptでハッシュ化して保存する
8. THE NecoKeeper SHALL ログアウト機能を提供する
9. WHEN ユーザーがログアウトボタンをクリックしたとき、THE NecoKeeper SHALL セッションを破棄しログイン画面にリダイレクトする

### Requirement 22: セキュリティ対策

**User Story:** システム管理者として、システムを安全に運用したい。これにより、不正アクセスやデータ漏洩を防止できる。

#### Acceptance Criteria

1. THE NecoKeeper SHALL パスワードに最小8文字、英数字混在のポリシーを適用する
2. THE NecoKeeper SHALL ログイン試行回数を制限し、5回失敗後15分間アカウントをロックする（データベースで管理）
3. THE NecoKeeper SHALL セッションタイムアウトを2時間に設定する
4. WHEN セッションがタイムアウトしたとき、THE NecoKeeper SHALL ユーザーをログイン画面にリダイレクトする
5. THE NecoKeeper SHALL HTTPS通信を推奨し、本番環境ではHTTPSを必須とする
6. THE NecoKeeper SHALL SQLAlchemyのORMを使用してSQLインジェクション対策を実施する
7. THE NecoKeeper SHALL 環境変数でシークレットキー（セッション署名用）を管理する
8. THE NecoKeeper SHALL Cookieにhttponly、secure、samesiteフラグを設定する

### Requirement 23: 監査ログ

**User Story:** システム管理者として、重要な操作の履歴を記録したい。これにより、問題発生時の原因究明や監査に対応できる。

#### Acceptance Criteria

1. THE NecoKeeper SHALL 以下の操作を監査ログに記録する：猫のStatus変更、譲渡決定、ユーザー登録・削除、マスターデータ変更
2. THE NecoKeeper SHALL 監査ログに操作日時、操作者、操作内容、変更前後の値を記録する
3. WHEN 管理者が監査ログ画面にアクセスしたとき、THE NecoKeeper SHALL 監査ログ一覧を時系列で表示する
4. THE NecoKeeper SHALL 監査ログ画面に日付範囲、操作者、操作種別でのフィルタ機能を提供する
5. THE NecoKeeper SHALL 監査ログをCSV形式でエクスポート可能にする
6. THE NecoKeeper SHALL 各レコードにlast_updated_at / last_updated_byを保持する（差分本文の記録はしない）

### Requirement 24: 検索機能

**User Story:** スタッフとして、猫を素早く検索したい。これにより、目的の猫の情報に迅速にアクセスできる。

#### Acceptance Criteria

1. THE NecoKeeper SHALL Animal Master一覧画面に検索ボックスを配置する
2. WHEN ユーザーが検索ボックスにキーワードを入力したとき、THE NecoKeeper SHALL 猫の名前、柄・色、特徴、性格を対象に部分一致検索を実行する
3. THE NecoKeeper SHALL 検索結果をリアルタイムで表示する
4. THE NecoKeeper SHALL 詳細検索機能（性別、年齢範囲、Status、保護日範囲）を提供する
5. WHEN ユーザーが詳細検索条件を指定して検索ボタンをクリックしたとき、THE NecoKeeper SHALL 条件に一致する猫のみを表示する

### Requirement 25: 世話記録のCSVエクスポート

**User Story:** 管理者として、世話記録をCSV形式でエクスポートしたい。これにより、外部ツールでのデータ分析が可能になる。

#### Acceptance Criteria

1. WHEN 管理者が世話記録一覧画面でCSVエクスポートボタンをクリックしたとき、THE NecoKeeper SHALL 期間指定ダイアログを表示する
2. WHEN 管理者が期間を指定してエクスポート実行ボタンをクリックしたとき、THE NecoKeeper SHALL 指定期間の全世話記録をCSV形式でダウンロード可能にする
3. THE NecoKeeper SHALL CSVファイルに猫名、記録日時、記録者、時点、食欲、元気、排尿、清掃、メモを含める
4. THE NecoKeeper SHALL 猫ごとの世話記録CSVエクスポート機能を提供する

### Requirement 26: 体重推移の可視化

**User Story:** スタッフとして、猫の体重推移をグラフで確認したい。これにより、健康状態の変化を視覚的に把握できる。

#### Acceptance Criteria

1. WHEN ユーザーが猫の詳細画面にアクセスしたとき、THE NecoKeeper SHALL 過去3ヶ月の体重推移グラフを表示する
2. THE NecoKeeper SHALL 体重推移グラフに世話記録と診療記録の体重データを統合して表示する
3. THE NecoKeeper SHALL 体重推移グラフの期間を変更可能にする（1ヶ月、3ヶ月、6ヶ月、1年、全期間）
4. WHEN 体重が前回比10%以上増減しているとき、THE NecoKeeper SHALL グラフ上に警告マーカーを表示する

### Requirement 27: 画像ギャラリー

**User Story:** スタッフとして、猫の複数の写真を管理したい。これにより、成長記録や傷の経過を視覚的に記録できる。

#### Acceptance Criteria

1. WHEN ユーザーが猫の詳細画面の画像ギャラリータブにアクセスしたとき、THE NecoKeeper SHALL 当該猫の全画像をサムネイル表示する
2. WHEN ユーザーが画像追加ボタンをクリックしたとき、THE NecoKeeper SHALL 画像アップロードダイアログを表示する
3. WHEN ユーザーが画像ファイルを選択してアップロードボタンをクリックしたとき、THE NecoKeeper SHALL 画像を保存し撮影日、説明を入力可能にする
4. WHEN ユーザーがサムネイルをクリックしたとき、THE NecoKeeper SHALL 画像を拡大表示する
5. THE NecoKeeper SHALL 画像ギャラリーを撮影日順または登録日順でソート可能にする
6. THE NecoKeeper SHALL 管理者が設定画面で1猫あたりの最大画像枚数を設定可能にする
7. THE NecoKeeper SHALL 管理者が設定画面で1画像あたりの最大ファイルサイズ（MB）を設定可能にする
8. WHEN 猫の画像枚数が設定された最大枚数に達しているとき、THE NecoKeeper SHALL 画像追加ボタンを無効化しメッセージを表示する
9. WHEN アップロードしようとする画像が設定された最大ファイルサイズを超えているとき、THE NecoKeeper SHALL アップロードを拒否しエラーメッセージを表示する
10. THE NecoKeeper SHALL デフォルト設定として最大画像枚数20枚、最大ファイルサイズ5MBを適用する

### Requirement 28: 非機能要件（パフォーマンス・可用性）

**User Story:** システム管理者として、安定したシステムパフォーマンスを確保したい。これにより、ユーザーが快適に利用できる。

#### Acceptance Criteria

1. THE NecoKeeper SHALL 管理画面の画面遷移を3秒以内に完了する
2. THE NecoKeeper SHALL Publicフォームの記録保存を2秒以内に完了する
3. THE NecoKeeper SHALL PDF生成を10秒以内に完了する
4. THE NecoKeeper SHALL 同時接続ユーザー数20名まで対応する
5. THE NecoKeeper SHALL 猫の登録数100頭まで快適に動作する
6. THE NecoKeeper SHALL システム稼働率95%以上を目標とする
7. THE NecoKeeper SHALL Chrome、Firefox、Safari、Edgeの最新版および1つ前のバージョンをサポートする
8. THE NecoKeeper SHALL iOS 14以降、Android 10以降のモバイルブラウザをサポートする

### Requirement 29: エラーハンドリングと例外処理

**User Story:** ユーザーとして、エラー発生時に適切なメッセージを受け取りたい。これにより、問題を理解し対処できる。

#### Acceptance Criteria

1. WHEN システムエラーが発生したとき、THE NecoKeeper SHALL ユーザーにわかりやすいエラーメッセージを表示する
2. WHEN データベース接続エラーが発生したとき、THE NecoKeeper SHALL エラーログを記録し管理者に通知する
3. WHEN ファイルアップロードが失敗したとき、THE NecoKeeper SHALL 失敗理由をユーザーに表示し再試行を促す
4. WHEN ネットワークエラーが発生したとき、THE NecoKeeper SHALL オフラインモードに切り替え（PWA）、復旧後に自動同期する
5. WHEN データ不整合が検出されたとき、THE NecoKeeper SHALL 管理者に警告を表示し修正を促す
6. THE NecoKeeper SHALL 全エラーをログファイルに記録し、エラーレベル（INFO、WARNING、ERROR、CRITICAL）を付与する

### Requirement 30: データ保持期間とプライバシーポリシー

**User Story:** システム管理者として、データ保持期間とプライバシーを適切に管理したい。これにより、法令遵守とストレージ管理ができる。

#### Acceptance Criteria

1. THE NecoKeeper SHALL バックアップファイルを90日間保持する
2. THE NecoKeeper SHALL 90日を超えたバックアップファイルを自動削除する
3. THE NecoKeeper SHALL 譲渡済み猫のデータを無期限保持する（監査目的）
4. THE NecoKeeper SHALL 里親希望者の個人情報を譲渡完了後3年間保持する
5. THE NecoKeeper SHALL 管理者が個人情報削除リクエストを受けた際、該当データを完全削除する機能を提供する
6. THE NecoKeeper SHALL プライバシーポリシーページを提供し、データ収集・利用目的を明示する

### Requirement 31: 初期セットアップとマスターデータ

**User Story:** システム管理者として、初回セットアップを簡単に実行したい。これにより、迅速にシステムを利用開始できる。

#### Acceptance Criteria

1. WHEN システムを初回起動したとき、THE NecoKeeper SHALL セットアップウィザードを表示する
2. THE NecoKeeper SHALL セットアップウィザードで初期管理者アカウント（メールアドレス、パスワード、氏名）を作成可能にする
3. THE NecoKeeper SHALL セットアップウィザードで団体情報（団体名、住所、連絡先）を登録可能にする
4. THE NecoKeeper SHALL セットアップウィザードで基本設定（言語、タイムゾーン、画像制限）を設定可能にする
5. WHEN セットアップが完了したとき、THE NecoKeeper SHALL 管理画面にリダイレクトする
6. THE NecoKeeper SHALL サンプルデータ（猫1頭、ボランティア1名）を初期データとして提供する

### Requirement 32: ヘルプとサポート機能

**User Story:** ユーザーとして、システムの使い方を学びたい。これにより、自己解決できる。

#### Acceptance Criteria

1. THE NecoKeeper SHALL 管理画面にヘルプボタンを配置する
2. WHEN ユーザーがヘルプボタンをクリックしたとき、THE NecoKeeper SHALL オンラインヘルプページを表示する
3. THE NecoKeeper SHALL オンラインヘルプに各機能の使い方を画像付きで説明する
4. THE NecoKeeper SHALL よくある質問（FAQ）ページを提供する
5. THE NecoKeeper SHALL 問い合わせフォームを提供する
6. WHEN ユーザーが問い合わせフォームを送信したとき、THE NecoKeeper SHALL 管理者にメール通知する

## 制約条件

### 技術的制約

1. THE NecoKeeper SHALL FastAPI、SQLite、WeasyPrint、AdminLTE、Tailwind CSSを使用する
2. THE NecoKeeper SHALL Pythonバージョン3.10以降で動作する（型ヒント `X | None` 構文のため）
3. THE NecoKeeper SHALL オープンソースライセンス（MIT、Apache 2.0等）のライブラリのみを使用する
4. THE NecoKeeper SHALL SQLAlchemy 2.0+のモダンなパターン（`Mapped`, `mapped_column`）を使用する
5. THE NecoKeeper SHALL Mypy strict modeでの型チェックをパスする
6. THE NecoKeeper SHALL PostgreSQL互換の命名規則を使用する（将来の移行を考慮）
7. THE NecoKeeper SHALL すべてのコードに完全な型ヒントとDocstringを含める

### 予算・リソース制約

1. THE NecoKeeper SHALL 無料または低コスト（月額$10以下）のホスティングサービスで運用可能とする
2. THE NecoKeeper SHALL 外部有料APIの使用を最小限にする（OCRは任意機能）

### スケジュール制約

1. THE NecoKeeper SHALL ハッカソン期間内にMVP（Minimum Viable Product）を完成させる

## 前提条件

### インフラ前提

1. ホスティングサービスがPython 3.9以降をサポートする
2. ホスティングサービスがSQLiteデータベースの永続化ストレージを提供する
3. HTTPS通信が利用可能である

### ユーザー前提

1. ユーザーはスマートフォンまたはPCを所有している
2. ユーザーはインターネット接続環境を利用できる（オフライン機能は補助的）
3. ボランティアは基本的なスマートフォン操作（QRコードスキャン、フォーム入力）ができる
