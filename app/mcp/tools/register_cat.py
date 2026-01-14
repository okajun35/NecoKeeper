"""
register_cat MCP Tool

This module provides the register_cat tool for the MCP server, allowing
Claude to register cat profiles through natural language conversation.

Context7 Reference: /jlowin/fastmcp (Benchmark Score: 82.4)
Requirements: 1.1, 1.2, 1.3, 1.4, 6.3, 7.1, 7.2, 7.3, 7.4
"""

from __future__ import annotations

import logging
from typing import Annotated, Any

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import Field

from app.mcp.api_client import NecoKeeperAPIClient
from app.mcp.error_handler import handle_api_error, validate_non_empty_string

logger = logging.getLogger(__name__)


def register_tool(mcp: FastMCP, api_client: NecoKeeperAPIClient) -> None:
    """
    Register the register_cat tool with the MCP server.

    This function registers the tool using the FastMCP decorator pattern,
    binding it to the provided API client for making authenticated requests.

    Args:
        mcp: FastMCP server instance
        api_client: NecoKeeper API client for making authenticated requests

    Context7: FastMCP tool registration using @mcp.tool decorator
    """

    @mcp.tool  # type: ignore[misc]
    async def register_cat(
        name: Annotated[
            str, Field(description="猫の名前", min_length=1, max_length=100)
        ],
        pattern: Annotated[
            str, Field(description="柄・色（例: キジトラ、三毛、黒猫）")
        ],
        tail_length: Annotated[
            str, Field(description="尻尾の長さ（例: 長い、短い、なし）")
        ],
        gender: Annotated[
            str, Field(description="性別: male (オス), female (メス), unknown (不明)")
        ],
        age_months: Annotated[
            int | None, Field(description="月齢（null=不明）", ge=0)
        ] = None,
        age_is_estimated: Annotated[bool, Field(description="推定月齢フラグ")] = False,
        status: Annotated[
            str,
            Field(
                description="ステータス（例: 保護中、譲渡可能、譲渡済み）",
                default="保護中",
            ),
        ] = "保護中",
        photo: Annotated[
            str | None, Field(description="プロフィール画像のファイルパス（任意）")
        ] = None,
        collar: Annotated[str | None, Field(description="首輪の有無と色")] = None,
        ear_cut: Annotated[
            bool, Field(description="耳カットの有無（TNR済みの印）")
        ] = False,
        features: Annotated[
            str | None, Field(description="外傷・特徴・性格（自由記述）")
        ] = None,
        protected_at: Annotated[
            str | None, Field(description="保護日 (YYYY-MM-DD形式)")
        ] = None,
    ) -> dict[str, Any]:
        """
        猫プロフィールを登録

        新しい猫をNecoKeeperシステムに登録します。登録後、猫のIDと
        公開URLが返されます。

        Args:
            name: 猫の名前（必須）
            pattern: 柄・色（必須、例: キジトラ、三毛、黒猫）
            tail_length: 尻尾の長さ（必須、例: 長い、短い、なし）
            age_months: 月齢（任意、null=不明）
            age_is_estimated: 推定月齢フラグ（デフォルト: False）
            gender: 性別（必須、male/female/unknown）
            status: ステータス（デフォルト: 保護中）
            photo: プロフィール画像のファイルパス（任意）
            collar: 首輪の有無と色（任意）
            ear_cut: 耳カットの有無（デフォルト: False）
            features: 外傷・特徴・性格（任意）
            protected_at: 保護日（任意、YYYY-MM-DD形式）

        Returns:
            dict: 登録結果
                - id (int): 猫のID
                - name (str): 猫の名前
                - public_url (str): 公開ケア記録ページのURL

        Raises:
            ToolError: 登録に失敗した場合

        Example:
            >>> result = await register_cat(
            ...     name="たま",
            ...     pattern="キジトラ",
            ...     tail_length="長い",
            ...     age_months=12,
            ...     age_is_estimated=False,
            ...     gender="male",
            ...     status="保護中",
            ... )
            >>> print(result["id"])
            42
        """
        try:
            # Validate required fields using centralized validation
            # Requirements 7.2: Specific validation error details
            validate_non_empty_string(name, "name")
            validate_non_empty_string(pattern, "pattern")
            validate_non_empty_string(tail_length, "tail_length")
            validate_non_empty_string(gender, "gender")

            # Validate gender
            valid_genders = ["male", "female", "unknown"]
            if gender not in valid_genders:
                raise ToolError(
                    f"Validation error: gender must be one of {', '.join(valid_genders)}. "
                    f"Got: {gender}"
                )

            # Build animal data payload
            animal_data: dict[str, Any] = {
                "name": name,
                "pattern": pattern,
                "tail_length": tail_length,
                "age_months": age_months,
                "age_is_estimated": age_is_estimated,
                "gender": gender,
                "status": status,
                "ear_cut": ear_cut,
            }

            # Add optional fields if provided
            if photo is not None:
                animal_data["photo"] = photo
            if collar is not None:
                animal_data["collar"] = collar
            if features is not None:
                animal_data["features"] = features
            if protected_at is not None:
                animal_data["protected_at"] = protected_at

            logger.info(
                f"Registering cat via MCP: name={name}, pattern={pattern}, gender={gender}"
            )

            # Call NecoKeeper API
            # Context7: httpx.AsyncClient handles connection pooling and async I/O
            response = await api_client.create_animal(animal_data)

            # Extract required fields from response
            animal_id = response.get("id")
            animal_name = response.get("name")

            if animal_id is None or animal_name is None:
                raise ToolError(
                    "API error: Response missing required fields (id or name)"
                )

            # Build public URL
            # Requirements 1.3: Return animal_id, name, and public_url
            public_url = (
                f"{api_client.config.api_url}/public/care?animal_id={animal_id}"
            )

            result = {
                "id": animal_id,
                "name": animal_name,
                "public_url": public_url,
            }

            logger.info(
                f"Successfully registered cat: id={animal_id}, name={animal_name}"
            )

            return result

        except ToolError:
            # Re-raise ToolError as-is
            raise

        except Exception as e:
            # Use centralized error handling
            # Requirements 6.3, 7.1, 7.2, 7.3, 7.4: Centralized error handling
            raise handle_api_error(e, "registering cat") from e
