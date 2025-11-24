"""
OCR Import用ロギング設定モジュール

OCR処理のログを専用ファイルに記録するための設定を提供します。
"""

from __future__ import annotations

import logging
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

    # ファイルハンドラー
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
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
