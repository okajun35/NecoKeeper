"""
OCR Import用ロギング設定モジュール

OCR処理のログを専用ファイルに記録するための設定を提供します。
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path


def setup_ocr_logger(
    log_file: str = "logs/ocr-import.log",
    log_level: str = "INFO",
    console_output: bool = True,
) -> logging.Logger:
    """
    OCR Import用のロガーを設定

    Args:
        log_file: ログファイルのパス
        log_level: ログレベル（DEBUG, INFO, WARNING, ERROR, CRITICAL）
        console_output: コンソールへの出力を有効にするか

    Returns:
        logging.Logger: 設定済みのロガーインスタンス

    Example:
        >>> logger = setup_ocr_logger()
        >>> logger.info("OCR処理を開始します")
    """
    # ロガーを取得
    logger = logging.getLogger("ocr_import")
    logger.setLevel(getattr(logging, log_level.upper()))

    # 既存のハンドラーをクリア（重複を防ぐ）
    logger.handlers.clear()

    # ログフォーマット
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ファイルハンドラー（書き込み可能なパスを確保）
    log_path = _resolve_writable_log_path(Path(log_file))

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(getattr(logging, log_level.upper()))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # コンソールハンドラー（オプション）
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


def get_ocr_logger() -> logging.Logger:
    """
    既存のOCRロガーを取得

    Returns:
        logging.Logger: OCRロガーインスタンス

    Note:
        setup_ocr_logger()を先に呼び出す必要があります
    """
    return logging.getLogger("ocr_import")


def _resolve_writable_log_path(preferred_path: Path) -> Path:
    """Ensure the log path is writable, falling back to tmp/logs if needed."""

    candidates: list[Path] = [preferred_path]

    # フォールバック先: プロジェクト配下の tmp/logs
    fallback_dir = Path.cwd() / "tmp" / "logs"
    fallback_path = fallback_dir / preferred_path.name
    if preferred_path.resolve() != fallback_path.resolve():
        candidates.append(fallback_path)

    for path in candidates:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            # 書き込み可能か試す
            with open(path, "a", encoding="utf-8"):
                os.utime(path, None)
            return path
        except PermissionError:
            continue

    raise PermissionError(
        "ログファイルに書き込めません。logs/ ディレクトリの権限を確認してください。"
    )
