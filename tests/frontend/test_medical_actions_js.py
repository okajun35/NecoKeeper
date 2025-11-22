"""
医療行為マスターJavaScript機能のテスト
Tests for medical_actions.js functionality
"""

from datetime import date
from decimal import Decimal

from app.models.medical_action import MedicalAction


class TestMedicalActionsJSList:
    """診療行為一覧の表示とフィルタリング"""

    def test_load_medical_actions_success(self, test_client, auth_headers, test_db):
        """
        Given: 複数の診療行為が存在する
        When: GET /api/v1/medical-actions をリクエスト
        Then: 200 OK で診療行為一覧が返される
        """
        # Given: 診療行為を作成
        action1 = MedicalAction(
            name="ワクチンA",
            valid_from=date(2024, 1, 1),
            cost_price=Decimal("500.00"),
            selling_price=Decimal("1000.00"),
            procedure_fee=Decimal("200.00"),
            currency="JPY",
        )
        action2 = MedicalAction(
            name="検査B",
            valid_from=date(2024, 1, 1),
            cost_price=Decimal("300.00"),
            selling_price=Decimal("800.00"),
            procedure_fee=Decimal("100.00"),
            currency="JPY",
        )
        test_db.add_all([action1, action2])
        test_db.commit()

        # When: 診療行為一覧をリクエスト
        response = test_client.get("/api/v1/medical-actions", headers=auth_headers)

        # Then: 成功し、両方の診療行為が返される
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2
        names = [item["name"] for item in data["items"]]
        assert "ワクチンA" in names
        assert "検査B" in names

    def test_load_medical_actions_with_name_filter(
        self, test_client, auth_headers, test_db
    ):
        """
        Given: 異なる名前を持つ診療行為が存在する
        When: name_filterパラメータ付きでリクエスト
        Then: フィルタリングされた診療行為のみが返される
        """
        # Given: 2つの診療行為
        action1 = MedicalAction(
            name="ワクチンA",
            valid_from=date(2024, 1, 1),
            selling_price=Decimal("1000.00"),
            currency="JPY",
        )
        action2 = MedicalAction(
            name="検査B",
            valid_from=date(2024, 1, 1),
            selling_price=Decimal("800.00"),
            currency="JPY",
        )
        test_db.add_all([action1, action2])
        test_db.commit()

        # When: "ワクチン" でフィルタリング
        response = test_client.get(
            "/api/v1/medical-actions?name_filter=ワクチン",
            headers=auth_headers,
        )

        # Then: ワクチンAのみが返される
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["name"] == "ワクチンA"

    def test_load_medical_actions_unauthorized(self, test_client):
        """
        Given: 認証トークンなし
        When: GET /api/v1/medical-actions をリクエスト
        Then: 401 Unauthorized が返される（JS側でlogoutが実行される）
        """
        # Given: 認証なし
        # When: 診療行為一覧をリクエスト
        response = test_client.get("/api/v1/medical-actions")

        # Then: 401エラーが返される
        assert response.status_code == 401


class TestMedicalActionsJSCreate:
    """診療行為の新規作成"""

    def test_create_medical_action_success(
        self, test_client, vet_auth_headers, test_db
    ):
        """
        Given: 有効な診療行為データ
        When: POST /api/v1/medical-actions をリクエスト
        Then: 201 Created で診療行為が作成される
        """
        # Given: 新規診療行為データ
        action_data = {
            "name": "新しいワクチン",
            "valid_from": "2024-01-01",
            "cost_price": 500.00,
            "selling_price": 1000.00,
            "procedure_fee": 200.00,
            "currency": "JPY",
            "unit": "本",
        }

        # When: 診療行為を作成
        response = test_client.post(
            "/api/v1/medical-actions",
            json=action_data,
            headers=vet_auth_headers,
        )

        # Then: 成功し、診療行為が作成される
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "新しいワクチン"
        assert data["currency"] == "JPY"
        assert data["unit"] == "本"

        # DB確認
        action = test_db.query(MedicalAction).filter_by(name="新しいワクチン").first()
        assert action is not None
        assert action.selling_price == Decimal("1000.00")


class TestMedicalActionsJSUpdate:
    """診療行為の更新"""

    def test_update_medical_action_success(
        self, test_client, vet_auth_headers, test_db
    ):
        """
        Given: 既存の診療行為
        When: PUT /api/v1/medical-actions/{id} で更新データを送信
        Then: 200 OK で診療行為が更新される
        """
        # Given: 既存の診療行為
        action = MedicalAction(
            name="旧ワクチン",
            valid_from=date(2024, 1, 1),
            selling_price=Decimal("1000.00"),
            currency="JPY",
        )
        test_db.add(action)
        test_db.commit()
        action_id = action.id

        # When: 診療行為を更新
        update_data = {
            "name": "新ワクチン",
            "valid_from": "2024-01-01",
            "cost_price": 600.00,
            "selling_price": 1200.00,
            "procedure_fee": 300.00,
            "currency": "JPY",
        }
        response = test_client.put(
            f"/api/v1/medical-actions/{action_id}",
            json=update_data,
            headers=vet_auth_headers,
        )

        # Then: 成功し、診療行為が更新される
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "新ワクチン"
        assert float(data["selling_price"]) == 1200.00

        # DB確認
        test_db.refresh(action)
        assert action.name == "新ワクチン"
        assert action.selling_price == Decimal("1200.00")

    def test_update_medical_action_not_found(
        self, test_client, vet_auth_headers, test_db
    ):
        """
        Given: 存在しない診療行為ID
        When: PUT /api/v1/medical-actions/{id} をリクエスト
        Then: 404 Not Found が返される
        """
        # Given: 存在しないID
        non_existent_id = 99999

        # When: 存在しない診療行為を更新しようとする
        update_data = {
            "name": "更新不可",
            "valid_from": "2024-01-01",
            "selling_price": 1000.00,
            "currency": "JPY",
        }
        response = test_client.put(
            f"/api/v1/medical-actions/{non_existent_id}",
            json=update_data,
            headers=vet_auth_headers,
        )

        # Then: 404エラーが返される
        assert response.status_code == 404


class TestMedicalActionsJSPagination:
    """ページネーション"""

    def test_pagination_works_correctly(self, test_client, auth_headers, test_db):
        """
        Given: 25件の診療行為が存在する
        When: page_size=20 でページ1とページ2をリクエスト
        Then: ページ1には20件、ページ2には5件が返される
        """
        # Given: 25件の診療行為を作成
        for i in range(25):
            action = MedicalAction(
                name=f"診療行為{i + 1}",
                valid_from=date(2024, 1, 1),
                selling_price=Decimal("1000.00"),
                currency="JPY",
            )
            test_db.add(action)
        test_db.commit()

        # When: ページ1をリクエスト
        response1 = test_client.get(
            "/api/v1/medical-actions?page=1&page_size=20",
            headers=auth_headers,
        )
        assert response1.status_code == 200
        data1 = response1.json()

        # Then: 20件が返される
        assert len(data1["items"]) == 20
        assert data1["total"] == 25
        assert data1["page"] == 1
        assert data1["total_pages"] == 2

        # When: ページ2をリクエスト
        response2 = test_client.get(
            "/api/v1/medical-actions?page=2&page_size=20",
            headers=auth_headers,
        )
        assert response2.status_code == 200
        data2 = response2.json()

        # Then: 5件が返される
        assert len(data2["items"]) == 5
        assert data2["page"] == 2
