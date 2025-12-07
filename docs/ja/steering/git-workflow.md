---
inclusion: always
---

# Git ワークフロー

このドキュメントは、NecoKeeperプロジェクトのGitワークフローを定義します。

## ブランチ戦略

### メインブランチ
- **main**: 本番環境用の安定版ブランチ
  - 常にデプロイ可能な状態を維持
  - 直接コミット禁止（Pull Requestのみ）

### 作業ブランチ

#### フィーチャーブランチ（機能開発）
- **命名規則**: `feature/<機能名>`
- **例**:
  - `feature/public-form`
  - `feature/pdf-generation`
  - `feature/medical-records`
- **作成元**: `develop`
- **マージ先**: `develop`

#### バグ修正ブランチ
- **命名規則**: `fix/<バグ内容>`
- **例**:
  - `fix/404-errors`
  - `fix/timezone-issue`
  - `fix/form-validation`
- **作成元**: `develop`（緊急の場合は `main`）
- **マージ先**: `develop`（緊急の場合は `main` と `develop` 両方）

#### リファクタリングブランチ
- **命名規則**: `refactor/<対象>`
- **例**:
  - `refactor/type-hints`
  - `refactor/error-handling`
- **作成元**: `develop`
- **マージ先**: `develop`

#### ドキュメントブランチ
- **命名規則**: `docs/<内容>`
- **例**:
  - `docs/setup-guide`
  - `docs/api-documentation`
- **作成元**: `develop`
- **マージ先**: `develop`

#### テストブランチ
- **命名規則**: `test/<対象>`
- **例**:
  - `test/care-log-service`
  - `test/authentication`
- **作成元**: `develop`
- **マージ先**: `develop`

## コミットメッセージ規約

### フォーマット
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type（必須）
- **feat**: 新機能
- **fix**: バグ修正
- **docs**: ドキュメントのみの変更
- **style**: コードの意味に影響しない変更（空白、フォーマット等）
- **refactor**: バグ修正や機能追加を伴わないコード変更
- **perf**: パフォーマンス改善
- **test**: テストの追加・修正
- **chore**: ビルドプロセスやツールの変更

### Scope（任意）
変更の範囲を示す：
- `auth`: 認証関連
- `api`: APIエンドポイント
- `model`: データモデル
- `service`: ビジネスロジック
- `ui`: ユーザーインターフェース
- `test`: テスト
- `docs`: ドキュメント

### Subject（必須）
- 50文字以内
- 命令形で記述（"追加した" ではなく "追加"）
- 文末にピリオド不要
- 日本語または英語

### Body（任意）
- 変更の理由と内容を詳細に説明
- 72文字で改行

### Footer（任意）
- Issue番号の参照
- Breaking Changesの記載

### 例

```bash
# 新機能追加
feat(api): Public APIエンドポイントを追加

認証不要の世話記録入力用APIを実装。
- GET /api/v1/public/animals/{id}
- POST /api/v1/public/care-logs

Closes #123

# バグ修正
fix(ui): 404エラーを修正

PWAアイコンとデフォルト画像のパスを修正。
- Service Worker登録コードを追加
- default.svgを作成

# リファクタリング
refactor(model): 型ヒントをモダンな構文に更新

- Optional[X] → X | None
- List[X] → list[X]
- from __future__ import annotations を追加

# ドキュメント
docs: PWAアイコンのセットアップガイドを追加

# テスト
test(service): care_log_serviceのテストを追加

カバレッジを68%から85%に向上
```

## ワークフロー

### 1. 新機能開発の流れ

```bash
# 1. developブランチを最新化
git checkout develop
git pull origin develop

# 2. フィーチャーブランチを作成
git checkout -b feature/new-feature

# 3. 開発とコミット
git add .
git commit -m "feat(scope): 機能を追加"

# 4. 定期的にdevelopの変更を取り込む
git fetch origin
git rebase origin/develop

# 5. リモートにプッシュ
git push origin feature/new-feature

# 6. Pull Requestを作成（GitHub/GitLab）
# 7. レビュー後、developにマージ
```

### 2. バグ修正の流れ

```bash
# 1. developブランチから修正ブランチを作成
git checkout develop
git pull origin develop
git checkout -b fix/bug-description

# 2. 修正とコミット
git add .
git commit -m "fix(scope): バグを修正"

# 3. プッシュとPull Request
git push origin fix/bug-description
```

### 3. 緊急バグ修正（Hotfix）

```bash
# 1. mainブランチから修正ブランチを作成
git checkout main
git pull origin main
git checkout -b hotfix/critical-bug

# 2. 修正とコミット
git add .
git commit -m "fix(scope): 緊急バグを修正"

# 3. mainとdevelopの両方にマージ
git checkout main
git merge hotfix/critical-bug
git push origin main

git checkout develop
git merge hotfix/critical-bug
git push origin develop

# 4. hotfixブランチを削除
git branch -d hotfix/critical-bug
```

## コミットのタイミング

### 頻繁にコミット
- 論理的な単位で小さくコミット
- 1つのコミットで1つの変更
- 動作する状態でコミット

### コミットすべきタイミング
- ✅ 新しいファイルを追加した
- ✅ 機能の一部が完成した
- ✅ バグを修正した
- ✅ リファクタリングが完了した
- ✅ テストを追加した
- ✅ ドキュメントを更新した

### コミットすべきでないタイミング
- ❌ コードが動作しない状態
- ❌ テストが失敗している状態
- ❌ 複数の無関係な変更を含む
- ❌ デバッグ用のコードが残っている

## コミット前のチェック（必須）

**すべてのコミット前に必ず実行してください**

### Makeコマンドで一括チェック（推奨）

```bash
# pre-commitと同じ順番で全チェック
make all
```

このコマンドは以下を順番に実行します：
1. **Lint**: Ruffでコード品質チェック
2. **Format**: Ruffでコードフォーマット
3. **Mypy**: 型チェック
4. **Pytest**: 全テスト実行（345テスト）
5. **Prettier**: JavaScript/JSON/YAMLフォーマット

### 個別チェック

```bash
# 基本チェックのみ（format + lint + test）
make check

# 個別実行
make lint      # Lintチェック
make format    # コードフォーマット
make mypy      # 型チェック
make test      # テスト実行
make coverage  # カバレッジ付きテスト
```

### 推奨ワークフロー

```bash
# 1. コード変更後、コミット前に全チェック
make all

# 2. 全てパスしたらコミット
git add .
git commit -m "feat(scope): 機能を追加"

# 3. プッシュ
git push origin feature/your-feature
```

### チェックが失敗した場合

- **Lint/Formatエラー**: 自動修正されるので再度`make all`を実行
- **Mypyエラー**: 型ヒントを修正
- **Testエラー**: テストを修正してから再実行

### pre-commitフック

コミット時に自動的にチェックが実行されます：

```bash
# pre-commitフックをインストール（初回のみ）
pre-commit install

# 手動で全ファイルをチェック
pre-commit run --all-files
```

## プッシュのタイミング

### 定期的にプッシュ
- 1日の作業終了時
- 重要な変更を完了した時
- 他の開発者と共有したい時
- バックアップとして保存したい時

### プッシュ前のチェックリスト
- [ ] **`make all`を実行して全てパス**（最重要）
- [ ] すべてのテストがパス
- [ ] Lintエラーがない
- [ ] 型チェックがパス
- [ ] コミットメッセージが適切
- [ ] 機密情報が含まれていない

## ブランチの削除

### マージ後のブランチ削除

```bash
# ローカルブランチを削除
git branch -d feature/completed-feature

# リモートブランチを削除
git push origin --delete feature/completed-feature
```

## .gitignoreの管理

以下のファイルは必ずコミットしない：

```gitignore
# 環境変数
.env
.env.local

# データベース
*.db
*.sqlite
*.sqlite3

# Python
__pycache__/
*.pyc
*.pyo
.venv/
venv/

# IDE
.vscode/
.idea/
*.swp

# ログ
*.log

# テスト
.coverage
htmlcov/
.pytest_cache/

# ビルド成果物
dist/
build/
*.egg-info/
```

## トラブルシューティング

### コミットを取り消す

```bash
# 直前のコミットを取り消し（変更は保持）
git reset --soft HEAD~1

# 直前のコミットを取り消し（変更も破棄）
git reset --hard HEAD~1

# コミットメッセージを修正
git commit --amend -m "新しいメッセージ"
```

### マージコンフリクトの解決

```bash
# 1. コンフリクトを確認
git status

# 2. ファイルを編集してコンフリクトを解決
# （<<<<<<<, =======, >>>>>>> を削除）

# 3. 解決したファイルをステージング
git add <resolved-file>

# 4. マージを完了
git commit
```

### 間違ったブランチにコミットした

```bash
# 1. コミットを別のブランチに移動
git checkout correct-branch
git cherry-pick <commit-hash>

# 2. 元のブランチからコミットを削除
git checkout wrong-branch
git reset --hard HEAD~1
```

## ベストプラクティス

1. **小さく頻繁にコミット**: 大きな変更を避け、論理的な単位で分割
2. **意味のあるコミットメッセージ**: 将来の自分や他の開発者のために
3. **定期的にプッシュ**: バックアップとして、また共同作業のために
4. **developを最新に保つ**: マージコンフリクトを最小化
5. **テストを書く**: コミット前にテストを実行
6. **レビューを受ける**: Pull Requestで品質を保証
7. **ブランチを整理**: マージ後は不要なブランチを削除

## 参考リンク

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)
