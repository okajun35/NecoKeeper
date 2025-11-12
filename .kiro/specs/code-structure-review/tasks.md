# Implementation Plan

- [x] 1. 基盤整備とMypy設定





  - mypy.ini設定ファイルを作成し、strict modeを有効化
  - .gitignoreにMypy関連ファイルを追加
  - _Requirements: 8.7_

- [x] 1.1 mypy.ini設定ファイルを作成


  - strict mode設定を追加
  - pydantic.mypyとsqlalchemy.ext.mypy.pluginプラグインを設定
  - 除外パターン（.venv, alembic/versions）を設定
  - _Requirements: 8.7_

- [x] 1.2 .gitignoreにMypy関連を追加


  - .mypy_cache/を追加
  - mypy-report/を追加
  - _Requirements: 8.7_

- [x] 2. データベースモジュールの改善





  - app/database.pyに命名規則を追加し、Base クラスを改善
  - 型ヒントを最新の構文に更新
  - _Requirements: 1.1, 1.2, 1.3, 8.1, 8.2, 8.4_


- [x] 2.1 命名規則の追加

  - NAMING_CONVENTIONディクショナリを定義
  - Base.metadataに命名規則を統合
  - _Requirements: 1.2_


- [x] 2.2 型ヒントの改善

  - `from __future__ import annotations`を追加
  - `collections.abc.Generator`を使用
  - `Session | None`構文を使用
  - _Requirements: 8.1, 8.2, 8.4_

- [x] 3. Alembic env.pyの改善


  - すべてのモデルを明示的にインポート
  - 命名規則を統合し、型ヒントを追加
  - _Requirements: 5.2, 5.4, 8.1, 8.4_

- [x] 3.1 モデルの明示的インポート


  - app.modelsからすべてのモデルをインポート
  - Base.metadataが完全であることを確認
  - _Requirements: 5.2_

- [x] 3.2 型ヒントと設定の改善


  - `from __future__ import annotations`を追加
  - context.configureにcompare_typeとcompare_server_defaultを追加
  - _Requirements: 8.1, 8.4_

- [x] 4. 未使用ディレクトリの整理


  - app/db/とapp/tasks/ディレクトリを削除または整理
  - プロジェクト構造をクリーンに保つ
  - _Requirements: 6.2_

- [x] 4.1 app/db/ディレクトリの削除


  - ディレクトリが空であることを確認
  - ディレクトリを削除
  - _Requirements: 6.2_

- [x] 4.2 app/tasks/ディレクトリの確認


  - 将来の使用計画を確認
  - 不要であれば削除
  - _Requirements: 6.2_

- [x] 5. 基盤モデルの改善（User, Animal, CareLog）


  - 型ヒントを最新構文に更新
  - server_defaultとonupdateを一貫して使用
  - Optional型を明示化
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 8.1, 8.2, 8.6_



- [x] 5.1 app/models/user.pyの改善

  - `from __future__ import annotations`を追加
  - Optional型ヒントを明示化
  - server_defaultとonupdateを使用
  - _Requirements: 2.1, 2.2, 2.3, 8.1, 8.2, 8.6_

- [x] 5.2 app/models/animal.pyの改善


  - `from __future__ import annotations`を追加
  - Optional型ヒントを明示化
  - server_defaultとonupdateを使用
  - _Requirements: 2.1, 2.2, 2.3, 8.1, 8.2, 8.6_

- [x] 5.3 app/models/care_log.pyの改善


  - `from __future__ import annotations`を追加
  - Optional型ヒントを明示化
  - server_defaultとonupdateを使用
  - _Requirements: 2.1, 2.2, 2.3, 8.1, 8.2, 8.6_

- [x] 6. 関連モデルの改善




  - 残りのモデルファイルに同様の改善を適用
  - 一貫性を保つ
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 8.1, 8.2, 8.6_

- [x] 6.1 app/models/medical_record.pyの改善


  - 型ヒントとserver_defaultの改善
  - _Requirements: 2.1, 2.2, 2.3, 8.1, 8.2_

- [x] 6.2 app/models/medical_action.pyの改善


  - 型ヒントとserver_defaultの改善
  - _Requirements: 2.1, 2.2, 2.3, 8.1, 8.2_

- [x] 6.3 その他のモデルファイルの改善


  - status_history.py, animal_image.py, adoption_record.py等
  - _Requirements: 2.1, 2.2, 2.3, 8.1, 8.2_

- [x] 7. サービス層の改善

  - エラーハンドリングを統一
  - 型ヒントを改善
  - ロギングを追加
  - _Requirements: 3.5, 8.1, 8.2, 9.1, 9.2, 9.5_

- [x] 7.1 app/services/animal_service.pyの改善


  - `from __future__ import annotations`を追加
  - エラーハンドリングパターンを実装
  - 型ヒントを`collections.abc`に更新
  - ロギングを追加
  - _Requirements: 8.1, 8.2, 9.1, 9.2, 9.5_

- [x] 7.2 app/services/care_log_service.pyの改善


  - エラーハンドリングとロギングを追加
  - 型ヒントを改善
  - _Requirements: 8.1, 8.2, 9.1, 9.2, 9.5_

- [x] 8. APIエンドポイントの改善








  - 型ヒントを最新構文に更新
  - ドキュメントを充実
  - _Requirements: 3.4, 8.1, 8.2, 8.3_

- [x] 8.1 app/api/v1/animals.pyの改善


  - `from __future__ import annotations`を追加
  - `collections.abc`の型を使用
  - Docstringを充実
  - _Requirements: 3.4, 8.1, 8.2_

- [x] 8.2 app/api/v1/care_logs.pyの改善





  - 型ヒントとドキュメントを改善
  - _Requirements: 3.4, 8.1, 8.2_

- [x] 8.3 app/api/v1/auth.pyの改善





  - 型ヒントとドキュメントを改善
  - _Requirements: 3.4, 8.1, 8.2_

- [x] 9. スキーマの改善



  - 型ヒントを最新構文に更新
  - バリデーションを強化
  - _Requirements: 8.1, 8.2, 9.2_

- [x] 9.1 app/schemas/animal.pyの改善


  - `from __future__ import annotations`を追加
  - `X | None`構文を使用
  - _Requirements: 8.1, 8.2_

- [x] 9.2 app/schemas/care_log.pyの改善


  - 型ヒントを改善
  - _Requirements: 8.1, 8.2_

- [x] 9.3 app/schemas/auth.pyの改善


  - 型ヒントを改善
  - _Requirements: 8.1, 8.2_



- [ ] 10. テストフィクスチャの改善
  - スコープを最適化
  - 型ヒントを追加
  - _Requirements: 4.1, 4.2, 8.1, 8.2_



- [ ] 10.1 tests/conftest.pyの改善
  - `from __future__ import annotations`を追加


  - フィクスチャのスコープを最適化
  - 型ヒントを`collections.abc.Generator`に更新
  - _Requirements: 4.1, 4.2, 8.1, 8.2_



- [ ] 11. 型チェックの実行と修正
  - mypy .を実行してエラーを特定
  - エラーを修正


  - _Requirements: 8.8_



- [ ] 11.1 Mypyエラーの特定
  - `mypy .`を実行
  - エラーリストを作成
  - _Requirements: 8.8_



- [ ] 11.2 Mypyエラーの修正
  - 優先度の高いファイルから修正


  - 必要に応じて`# type: ignore`を使用
  - _Requirements: 8.8_



- [ ] 12. コードフォーマットとLint
  - Ruffでフォーマットとlintを実行
  - エラーを修正


  - _Requirements: 7.1_

- [x] 12.1 Ruffフォーマットの実行

  - `ruff format .`を実行
  - フォーマットを確認
  - _Requirements: 7.1_


- [ ] 12.2 Ruff lintの実行
  - `ruff check . --fix`を実行
  - 残りのエラーを手動修正
  - _Requirements: 7.1_


- [ ] 13. テストの実行と修正
  - すべてのテストを実行
  - 失敗したテストを修正

  - _Requirements: 4.3, 4.4_

- [ ] 13.1 テストの実行
  - `python -m pytest -v`を実行


  - 失敗したテストを特定
  - _Requirements: 4.3_

- [ ] 13.2 テストの修正
  - 失敗したテストを修正
  - すべてのテストがパスすることを確認
  - _Requirements: 4.4_



- [ ] 14. ドキュメントの更新
  - README.mdを更新
  - 開発ガイドを作成
  - _Requirements: 7.2, 7.3_

- [ ] 14.1 README.mdの更新
  - 型チェックの手順を追加
  - 開発環境のセットアップを更新

  - _Requirements: 7.2_

- [ ] 14.2 開発ガイドの作成
  - ベストプラクティスをドキュメント化
  - コーディング規約を明記

  - _Requirements: 7.3_

- [-] 15. 最終検証


  - すべてのチェックを実行


  - 品質指標を確認
  - _Requirements: すべて_

- [ ] 15.1 品質チェックの実行



  - `ruff format .`
  - `ruff check .`
  - `mypy .`
  - `python -m pytest`
  - _Requirements: すべて_

- [ ] 15.2 品質指標の確認
  - 型カバレッジ: 95%以上
  - テストカバレッジ: 80%以上
  - すべてのエラー: 0件
  - _Requirements: すべて_
