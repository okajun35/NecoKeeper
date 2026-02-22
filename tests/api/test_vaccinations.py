from __future__ import annotations

from datetime import date


def test_create_and_list_vaccination_record(test_client, vet_auth_headers, test_animal):
    payload = {
        "animal_id": test_animal.id,
        "vaccine_category": "3core",
        "administered_on": date(2024, 12, 1).isoformat(),
        "next_due_on": date(2025, 6, 1).isoformat(),
        "memo": "初回接種済み",
    }

    create_response = test_client.post(
        "/api/v1/vaccinations", json=payload, headers=vet_auth_headers
    )
    assert create_response.status_code == 201, create_response.json()
    created = create_response.json()

    assert created["animal_id"] == payload["animal_id"]
    assert created["vaccine_category"] == payload["vaccine_category"]
    assert created["administered_on"] == payload["administered_on"]
    assert created["next_due_on"] == payload["next_due_on"]
    assert created["memo"] == payload["memo"]

    list_response = test_client.get(
        f"/api/v1/vaccinations/animal/{test_animal.id}", headers=vet_auth_headers
    )
    assert list_response.status_code == 200
    records = list_response.json()

    assert len(records) == 1
    assert records[0]["id"] == created["id"]
    assert records[0]["animal_id"] == test_animal.id


def test_create_vaccination_requires_permission(test_client, auth_headers, test_animal):
    payload = {
        "animal_id": test_animal.id,
        "vaccine_category": "3core",
        "administered_on": date(2024, 12, 1).isoformat(),
    }

    response = test_client.post(
        "/api/v1/vaccinations", json=payload, headers=auth_headers
    )

    assert response.status_code == 403


def test_get_and_list_vaccination_require_auth(test_client, test_animal):
    list_response = test_client.get(f"/api/v1/vaccinations/animal/{test_animal.id}")
    assert list_response.status_code == 401

    detail_response = test_client.get("/api/v1/vaccinations/99999")
    assert detail_response.status_code == 401


def test_update_vaccination_requires_permission(
    test_client, vet_auth_headers, auth_headers, test_animal
):
    test_client.cookies.clear()
    payload = {
        "animal_id": test_animal.id,
        "vaccine_category": "3core",
        "administered_on": date(2024, 12, 1).isoformat(),
    }
    create_response = test_client.post(
        "/api/v1/vaccinations", json=payload, headers=vet_auth_headers
    )
    assert create_response.status_code == 201
    record_id = create_response.json()["id"]

    update_response = test_client.put(
        f"/api/v1/vaccinations/{record_id}",
        json={"memo": "更新"},
        headers=auth_headers,
    )
    assert update_response.status_code == 403


def test_delete_vaccination_requires_permission(
    test_client, vet_auth_headers, auth_headers, test_animal
):
    test_client.cookies.clear()
    payload = {
        "animal_id": test_animal.id,
        "vaccine_category": "3core",
        "administered_on": date(2024, 12, 1).isoformat(),
    }
    create_response = test_client.post(
        "/api/v1/vaccinations", json=payload, headers=vet_auth_headers
    )
    assert create_response.status_code == 201
    record_id = create_response.json()["id"]

    delete_response = test_client.delete(
        f"/api/v1/vaccinations/{record_id}", headers=auth_headers
    )
    assert delete_response.status_code == 403


def test_vaccination_endpoints_not_found(test_client, vet_auth_headers, test_animal):
    response = test_client.get("/api/v1/vaccinations/99999", headers=vet_auth_headers)
    assert response.status_code == 404

    update_response = test_client.put(
        "/api/v1/vaccinations/99999",
        json={"memo": "更新"},
        headers=vet_auth_headers,
    )
    assert update_response.status_code == 404

    delete_response = test_client.delete(
        "/api/v1/vaccinations/99999", headers=vet_auth_headers
    )
    assert delete_response.status_code == 404
