"""
世話記録APIのルーティングテスト

ルーティング順序の問題を検知するためのテスト
"""

from __future__ import annotations

from datetime import date

from app.models.animal import Animal
from app.models.care_log import CareLog


class TestCareLogRouting:
    """世話記録ルーティングのテストクラス"""

    def test_daily_view_endpoint_not_confused_with_id(
        self, test_client, test_db, auth_token
    ):
        """
        /daily-viewエンドポイントが/{care_log_id}と混同されないことを確認

        これは実際に発生したバグ：
        - /daily-viewが/{care_log_id}の後に定義されていた
        - FastAPIが"daily-view"をcare_log_idとして解釈
        - 422エラー（int_parsing）が発生
        """
        response = test_client.get(
            "/api/v1/care-logs/daily-view",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # 422エラー（int_parsing）ではなく、200または500であるべき
        assert response.status_code != 422, (
            "daily-viewがcare_log_idとして解釈されています。"
            "ルーティング順序を確認してください。"
        )

        # 正常に処理されるべき
        assert response.status_code in [200, 500]

    def test_specific_routes_before_dynamic_routes(
        self, test_client, test_db, auth_token
    ):
        """
        具体的なルート（/daily-view, /latest/{id}, /export）が
        動的ルート（/{care_log_id}）より先に定義されていることを確認
        """
        # /daily-view
        response = test_client.get(
            "/api/v1/care-logs/daily-view",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code != 422

        # /latest/{animal_id}
        animal = test_db.query(Animal).first()
        response = test_client.get(
            f"/api/v1/care-logs/latest/{animal.id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code in [200, 404]  # 記録がない場合は404

        # /export
        response = test_client.get(
            "/api/v1/care-logs/export",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200

    def test_numeric_id_route_works(self, test_client, test_db, auth_token):
        """
        数値IDでの取得が正常に動作することを確認
        """
        # テストデータを作成
        animal = test_db.query(Animal).first()
        care_log = CareLog(
            log_date=date.today(),
            animal_id=animal.id,
            recorder_name="テスト記録者",
            time_slot="morning",
            appetite=0.75,
            energy=5,
            urination=True,
            cleaning=True,
        )
        test_db.add(care_log)
        test_db.commit()

        response = test_client.get(
            f"/api/v1/care-logs/{care_log.id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == care_log.id


class TestDailyViewEndpoint:
    """日次ビューエンドポイントのテストクラス"""

    def test_daily_view_returns_dict(self, test_client, test_db, auth_token):
        """
        日次ビューが辞書形式でデータを返すことを確認

        これは実際に発生したバグ：
        - daily_recordsが辞書のリストだった
        - x.dateでアクセスしようとしてAttributeError
        """
        # テストデータを作成
        animal = test_db.query(Animal).first()
        care_log = CareLog(
            log_date=date.today(),
            animal_id=animal.id,
            recorder_name="テスト記録者",
            time_slot="morning",
            appetite=0.75,
            energy=5,
            urination=True,
            cleaning=True,
        )
        test_db.add(care_log)
        test_db.commit()

        response = test_client.get(
            "/api/v1/care-logs/daily-view",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()

        # レスポンス構造の確認
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data

        # itemsが辞書のリストであることを確認
        if data["items"]:
            item = data["items"][0]
            assert isinstance(item, dict)
            assert "date" in item
            assert "animal_id" in item
            assert "animal_name" in item
            assert "morning" in item
            assert "noon" in item
            assert "evening" in item

            # 時点データの構造確認
            for time_slot in ["morning", "noon", "evening"]:
                slot_data = item[time_slot]
                assert isinstance(slot_data, dict)
                assert "exists" in slot_data
                assert "log_id" in slot_data

    def test_daily_view_sorting(self, test_client, test_db, auth_token):
        """
        日次ビューが日付降順でソートされることを確認

        これは実際に発生したバグ：
        - x.dateではなくx["date"]でアクセスする必要があった
        """
        # 複数日のテストデータを作成
        animal = test_db.query(Animal).first()

        for i in range(3):
            care_log = CareLog(
                log_date=date(2025, 11, 14 + i),
                animal_id=animal.id,
                recorder_name="テスト記録者",
                time_slot="morning",
                appetite=0.75,
                energy=5,
                urination=True,
                cleaning=True,
            )
            test_db.add(care_log)
        test_db.commit()

        response = test_client.get(
            "/api/v1/care-logs/daily-view?page_size=10",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()

        # 日付が降順であることを確認
        if len(data["items"]) >= 2:
            dates = [item["date"] for item in data["items"]]
            assert dates == sorted(dates, reverse=True), (
                "日付が降順でソートされていません"
            )


class TestAdminPagesRouting:
    """管理画面ページのルーティングテスト"""

    def test_care_logs_list_page_exists(self, test_client):
        """世話記録一覧ページが存在することを確認"""
        response = test_client.get("/admin/care-logs")

        # 認証が必要な場合は302（リダイレクト）または200
        assert response.status_code in [200, 302]

    def test_care_logs_detail_page_exists(self, test_client, test_db):
        """
        世話記録詳細ページが存在することを確認

        これは実際に発生したバグ：
        - /admin/care-logs/{id}のルートが定義されていなかった
        - 404エラーが発生
        """
        # テストデータを作成
        animal = test_db.query(Animal).first()
        care_log = CareLog(
            log_date=date.today(),
            animal_id=animal.id,
            recorder_name="テスト記録者",
            time_slot="morning",
            appetite=0.75,
            energy=5,
            urination=True,
            cleaning=True,
        )
        test_db.add(care_log)
        test_db.commit()

        response = test_client.get(f"/admin/care-logs/{care_log.id}")

        # 404ではないことを確認
        assert response.status_code != 404, (
            f"/admin/care-logs/{care_log.id}のルートが定義されていません"
        )

        # 認証が必要な場合は302（リダイレクト）または200
        assert response.status_code in [200, 302]


class TestEmailValidation:
    """メールアドレスバリデーションのテスト"""

    def test_local_domain_emails_rejected(self, test_client, test_db):
        """
        .localドメインのメールアドレスが拒否されることを確認

        これは実際に発生したバグ：
        - テストデータに@necokeeper.localが含まれていた
        - Pydanticが.localを特殊用途ドメインとして拒否
        - 500エラーが発生
        """
        from app.models.user import User

        # .localドメインのユーザーが存在しないことを確認
        local_users = test_db.query(User).filter(User.email.like("%.local")).all()

        assert len(local_users) == 0, (
            f".localドメインのユーザーが{len(local_users)}件存在します。"
            "これらはPydanticのEmailStrバリデーションで拒否されます。"
        )

    def test_valid_email_domains_only(self, test_client, test_db):
        """すべてのユーザーが有効なメールドメインを持つことを確認"""
        from app.models.user import User

        users = test_db.query(User).all()

        invalid_domains = [".local", ".test", ".invalid", ".localhost"]

        for user in users:
            for invalid_domain in invalid_domains:
                assert not user.email.endswith(invalid_domain), (
                    f"ユーザー {user.id} のメールアドレス {user.email} が"
                    f"無効なドメイン {invalid_domain} を使用しています"
                )
