"""
猫識別ユーティリティ

NecoKeeper APIを使用して、猫をIDまたは名前で識別します。
データベースに直接アクセスせず、APIのみを使用します。
"""

from __future__ import annotations

import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)


class CatNotFoundError(Exception):
    """猫が見つからない場合のエラー"""

    pass


class MultipleCatsFoundError(Exception):
    """複数の猫が見つかった場合のエラー"""

    def __init__(self, message: str, matching_cats: list[dict[str, Any]]) -> None:
        """
        Args:
            message: エラーメッセージ
            matching_cats: マッチした猫のリスト
        """
        super().__init__(message)
        self.matching_cats = matching_cats


class CatIdentifier:
    """
    猫識別クラス

    NecoKeeper APIを使用して猫を識別します。
    IDまたは名前で検索し、一意の猫を特定します。
    """

    def __init__(self, api_base_url: str, auth_token: str) -> None:
        """
        Args:
            api_base_url: NecoKeeper APIのベースURL
            auth_token: 認証トークン
        """
        self.api_base_url = api_base_url.rstrip("/")
        self.auth_token = auth_token
        self.headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
        }
        self._animals_cache: list[dict[str, Any]] | None = None

    def _fetch_all_animals(self) -> list[dict[str, Any]]:
        """
        全ての猫をAPIから取得

        Returns:
            list[dict]: 猫のリスト

        Raises:
            requests.RequestException: API呼び出しに失敗した場合
        """
        if self._animals_cache is not None:
            return self._animals_cache

        try:
            # ページネーション対応で全ての猫を取得
            all_animals: list[dict[str, Any]] = []
            page = 1
            page_size = 100

            while True:
                url = f"{self.api_base_url}/api/v1/animals"
                params = {"page": page, "page_size": page_size}

                logger.debug(f"Fetching animals: page={page}, page_size={page_size}")
                response = requests.get(
                    url, headers=self.headers, params=params, timeout=10
                )
                response.raise_for_status()

                data = response.json()
                items = data.get("items", [])
                all_animals.extend(items)

                # 最後のページに到達したら終了
                total_pages = data.get("total_pages", 1)
                if page >= total_pages:
                    break

                page += 1

            logger.info(f"Fetched {len(all_animals)} animals from API")
            self._animals_cache = all_animals
            return all_animals

        except requests.RequestException as e:
            logger.error(f"Failed to fetch animals from API: {e}")
            raise

    def identify_by_id(self, animal_id: int) -> int:
        """
        IDで猫を識別

        Args:
            animal_id: 猫のID

        Returns:
            int: 猫のID（検証済み）

        Raises:
            CatNotFoundError: 指定されたIDの猫が見つからない場合
        """
        animals = self._fetch_all_animals()

        for animal in animals:
            if animal.get("id") == animal_id:
                logger.info(
                    f"Found cat by ID: {animal_id} (name: {animal.get('name')})"
                )
                return animal_id

        raise CatNotFoundError(f"猫ID {animal_id} が見つかりません")

    def identify_by_name(self, name: str) -> int:
        """
        名前で猫を識別（大文字小文字を区別しない）

        Args:
            name: 猫の名前

        Returns:
            int: 猫のID

        Raises:
            CatNotFoundError: 指定された名前の猫が見つからない場合
            MultipleCatsFoundError: 複数の猫が見つかった場合
        """
        animals = self._fetch_all_animals()

        # 大文字小文字を区別しない検索
        name_lower = name.lower()
        matching_animals = [
            animal
            for animal in animals
            if animal.get("name") and animal["name"].lower() == name_lower
        ]

        if len(matching_animals) == 0:
            raise CatNotFoundError(f"猫の名前 '{name}' が見つかりません")

        if len(matching_animals) > 1:
            # 複数の猫が見つかった場合
            cat_info = [
                (
                    f"ID: {cat['id']}, 名前: {cat.get('name')}, "
                    f"毛色: {cat.get('coat_color')}"
                )
                for cat in matching_animals
            ]
            error_msg = (
                f"名前 '{name}' に一致する猫が複数見つかりました:\n"
                + "\n".join(cat_info)
                + "\n\nIDを指定して再度実行してください。"
            )
            raise MultipleCatsFoundError(error_msg, matching_animals)

        # 一意の猫が見つかった
        animal = matching_animals[0]
        animal_id = animal["id"]
        logger.info(f"Found cat by name: '{name}' -> ID: {animal_id}")
        return animal_id

    def identify(self, identifier: str | int) -> int:
        """
        IDまたは名前で猫を識別

        Args:
            identifier: 猫のID（整数）または名前（文字列）

        Returns:
            int: 猫のID

        Raises:
            CatNotFoundError: 猫が見つからない場合
            MultipleCatsFoundError: 複数の猫が見つかった場合
        """
        if isinstance(identifier, int):
            return self.identify_by_id(identifier)
        else:
            # 文字列の場合、まず整数に変換できるか試す
            try:
                animal_id = int(identifier)
                return self.identify_by_id(animal_id)
            except ValueError:
                # 整数に変換できない場合は名前として扱う
                return self.identify_by_name(identifier)


def identify_cat(
    identifier: str | int,
    api_base_url: str,
    auth_token: str,
) -> int:
    """
    猫をIDまたは名前で識別（便利関数）

    Args:
        identifier: 猫のID（整数）または名前（文字列）
        api_base_url: NecoKeeper APIのベースURL
        auth_token: 認証トークン

    Returns:
        int: 猫のID

    Raises:
        CatNotFoundError: 猫が見つからない場合
        MultipleCatsFoundError: 複数の猫が見つかった場合

    Example:
        >>> token = "your-auth-token"
        >>> cat_id = identify_cat(5, "http://localhost:8000", token)
        >>> cat_id = identify_cat("たま", "http://localhost:8000", token)
    """
    identifier_obj = CatIdentifier(api_base_url, auth_token)
    return identifier_obj.identify(identifier)
