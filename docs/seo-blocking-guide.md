# SEO Blocking Guide - ハッカソンデモサイト用

## 概要

NecoKeeperはハッカソン用のデモサイトであり、Renderの無料プランを使用しているため、検索エンジンのクローラーによるインデックスを防ぐ必要があります。

このドキュメントでは、実装されているSEOブロッキング機能について説明します。

## 実装内容

### 1. Meta Robotsタグ（HTML）

**ファイル**: `app/templates/public/landing.html`

```html
<!-- Prevent search engine indexing (hackathon demo site) -->
<meta name="robots" content="noindex, nofollow">
```

**効果**:
- `noindex`: 検索エンジンにこのページをインデックスしないよう指示
- `nofollow`: このページからのリンクをたどらないよう指示

**対象**:
- Google
- Bing
- Yahoo
- その他のメジャーな検索エンジン

### 2. robots.txt（ルートパス）

**ファイル**: `app/main.py` (動的生成)

**エンドポイント**: `GET /robots.txt`

```txt
# NecoKeeper - Hackathon Demo Site
# Prevent all search engine crawlers from indexing this site

User-agent: *
Disallow: /
```

**効果**:
- すべてのクローラー（`User-agent: *`）に対して
- サイト全体（`Disallow: /`）のクロールを禁止

**対象**:
- Google Bot
- Bing Bot
- Yahoo Slurp
- その他すべてのクローラー

### 3. 静的ファイル版（バックアップ）

**ファイル**: `app/static/robots.txt`

静的ファイルとしても配置されており、`/static/robots.txt` でアクセス可能です。
ただし、SEOの観点から `/robots.txt` が優先されます。

## 動作確認

### 1. robots.txtの確認

```bash
curl http://localhost:8000/robots.txt
```

**期待される出力**:
```txt
# NecoKeeper - Hackathon Demo Site
# Prevent all search engine crawlers from indexing this site

User-agent: *
Disallow: /
```

### 2. Meta Robotsタグの確認

```bash
curl http://localhost:8000/ | grep "robots"
```

**期待される出力**:
```html
<meta name="robots" content="noindex, nofollow">
```

### 3. ブラウザでの確認

1. ブラウザで `http://localhost:8000/` にアクセス
2. 開発者ツール（F12）を開く
3. Elements タブで `<head>` セクションを確認
4. `<meta name="robots" content="noindex, nofollow">` が存在することを確認

## 検索エンジンの動作

### Google

1. **robots.txt**: Googlebotは最初に `/robots.txt` をチェック
2. **Meta Robots**: HTMLの `<meta name="robots">` タグを確認
3. **結果**: サイト全体がインデックスされない

### Bing

1. **robots.txt**: Bingbotも同様に `/robots.txt` をチェック
2. **Meta Robots**: HTMLのメタタグを確認
3. **結果**: サイト全体がインデックスされない

### その他の検索エンジン

ほとんどの検索エンジンは `robots.txt` と `<meta name="robots">` の両方をサポートしています。

## 注意事項

### 1. 既にインデックスされている場合

もしサイトが既に検索エンジンにインデックスされている場合：

1. **Google Search Console** で削除リクエストを送信
2. **Bing Webmaster Tools** で削除リクエストを送信
3. クローラーが再訪問するまで待つ（通常数日〜数週間）

### 2. 本番環境への移行時

本番環境に移行する際は、以下を変更してください：

#### app/templates/public/landing.html
```html
<!-- 削除または変更 -->
<meta name="robots" content="noindex, nofollow">
↓
<meta name="robots" content="index, follow">
```

#### app/main.py
```python
# robots.txt エンドポイントを変更
content = """User-agent: *
Allow: /

# 管理画面は非公開
Disallow: /admin/
Disallow: /api/

# Sitemap
Sitemap: https://your-domain.com/sitemap.xml
"""
```

### 3. Renderの無料プラン制限

Renderの無料プランには以下の制限があります：

- **スリープ**: 15分間アクセスがないとスリープ
- **帯域幅**: 月100GB
- **ビルド時間**: 月500分

検索エンジンのクローラーがアクセスすると、これらのリソースを消費する可能性があります。

## テスト

### 単体テスト

```python
# tests/test_seo_blocking.py
def test_robots_txt(test_client):
    """robots.txtが正しく返される"""
    response = test_client.get("/robots.txt")
    assert response.status_code == 200
    assert "User-agent: *" in response.text
    assert "Disallow: /" in response.text

def test_landing_page_meta_robots(test_client):
    """ランディングページにmeta robotsタグが含まれる"""
    response = test_client.get("/")
    assert response.status_code == 200
    assert 'name="robots" content="noindex, nofollow"' in response.text
```

### 統合テスト

```bash
# robots.txtのテスト
curl -I http://localhost:8000/robots.txt
# 期待: 200 OK, Content-Type: text/plain

# ランディングページのテスト
curl http://localhost:8000/ | grep "robots"
# 期待: <meta name="robots" content="noindex, nofollow">
```

## 参考資料

### 公式ドキュメント

- [Google: robots.txt の概要](https://developers.google.com/search/docs/crawling-indexing/robots/intro)
- [Google: robots メタタグ](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag)
- [Bing: robots.txt](https://www.bing.com/webmasters/help/how-to-create-a-robots-txt-file-cb7c31ec)

### ツール

- [Google Search Console](https://search.google.com/search-console)
- [Bing Webmaster Tools](https://www.bing.com/webmasters)
- [robots.txt Tester](https://www.google.com/webmasters/tools/robots-testing-tool)

## まとめ

NecoKeeperでは、以下の2つの方法で検索エンジンのクローラーをブロックしています：

1. **Meta Robotsタグ**: HTMLの `<head>` に `<meta name="robots" content="noindex, nofollow">` を追加
2. **robots.txt**: `/robots.txt` エンドポイントで `User-agent: * / Disallow: /` を返す

これにより、ハッカソンデモサイトとして適切にSEOをブロックし、Renderの無料プランのリソースを節約できます。

---

**最終更新**: 2024-12-07
**バージョン**: 1.0.0
