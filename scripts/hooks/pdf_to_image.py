#!/usr/bin/env python3
"""
PDF to Image Conversion Hook Script

PDFファイルの最初のページを画像に変換するHookスクリプト。
Kiroから呼び出され、OCR処理のための画像を生成します。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# パスを追加してモジュールをインポート可能にする
if __name__ == "__main__":
    # スクリプトとして実行される場合、プロジェクトルートをパスに追加
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))

from scripts.utils.logging_config import setup_ocr_logger

# ロガーを設定
logger = setup_ocr_logger()


class PDFConversionError(Exception):
    """PDF変換エラー"""

    pass


def validate_pdf_file(pdf_path: Path) -> None:
    """
    PDFファイルのバリデーション

    Args:
        pdf_path: PDFファイルのパス

    Raises:
        FileNotFoundError: ファイルが存在しない
        ValueError: ファイル拡張子が不正、またはファイルサイズが制限を超える
    """
    # ファイルの存在確認
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDFファイルが見つかりません: {pdf_path}")

    # ファイル拡張子の確認
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"PDFファイルではありません: {pdf_path.suffix}")

    # ファイルサイズの確認（50MB制限）
    max_size = 50 * 1024 * 1024  # 50MB
    file_size = pdf_path.stat().st_size
    if file_size > max_size:
        raise ValueError(
            f"ファイルサイズが制限を超えています: "
            f"{file_size / 1024 / 1024:.2f}MB > {max_size / 1024 / 1024}MB"
        )

    logger.info(f"PDFファイルのバリデーション成功: {pdf_path}")


def convert_pdf_to_image_pdf2image(pdf_path: Path, output_dir: Path) -> Path:
    """
    pdf2imageを使用してPDFを画像に変換

    Args:
        pdf_path: PDFファイルのパス
        output_dir: 出力ディレクトリ

    Returns:
        Path: 生成された画像ファイルのパス

    Raises:
        PDFConversionError: 変換に失敗した場合
    """
    try:
        from pdf2image import convert_from_path

        logger.info(f"pdf2imageを使用してPDF変換を開始: {pdf_path}")

        # 最初のページのみを変換（DPI=300で高品質）
        images = convert_from_path(
            pdf_path,
            dpi=300,
            first_page=1,
            last_page=1,
            fmt="png",
        )

        if not images:
            raise PDFConversionError("PDFから画像を抽出できませんでした")

        # 出力ファイル名を生成
        output_filename = f"{pdf_path.stem}_page1.png"
        output_path = output_dir / output_filename

        # 画像を保存
        images[0].save(output_path, "PNG")

        logger.info(f"PDF変換成功: {output_path}")
        return output_path

    except ImportError as e:
        raise PDFConversionError(
            "pdf2imageライブラリがインストールされていません"
        ) from e
    except Exception as e:
        raise PDFConversionError(f"PDF変換に失敗しました: {e}") from e


def convert_pdf_to_image_pymupdf(pdf_path: Path, output_dir: Path) -> Path:
    """
    PyMuPDF (fitz)を使用してPDFを画像に変換

    Args:
        pdf_path: PDFファイルのパス
        output_dir: 出力ディレクトリ

    Returns:
        Path: 生成された画像ファイルのパス

    Raises:
        PDFConversionError: 変換に失敗した場合
    """
    try:
        import fitz  # PyMuPDF

        logger.info(f"PyMuPDFを使用してPDF変換を開始: {pdf_path}")

        # PDFを開く
        doc = fitz.open(pdf_path)

        if len(doc) == 0:
            raise PDFConversionError("PDFにページが含まれていません")

        # 最初のページを取得
        page = doc[0]

        # 高解像度でレンダリング（300 DPI相当）
        zoom = 300 / 72  # 72 DPI がデフォルト
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)

        # 出力ファイル名を生成
        output_filename = f"{pdf_path.stem}_page1.png"
        output_path = output_dir / output_filename

        # 画像を保存
        pix.save(output_path)

        # ドキュメントを閉じる
        doc.close()

        logger.info(f"PDF変換成功: {output_path}")
        return output_path

    except ImportError as e:
        raise PDFConversionError("PyMuPDFライブラリがインストールされていません") from e
    except Exception as e:
        raise PDFConversionError(f"PDF変換に失敗しました: {e}") from e


def convert_pdf_to_image(
    pdf_path: str | Path,
    output_dir: str | Path = "tmp/images",
    use_pymupdf: bool = False,
) -> str:
    """
    PDFファイルの最初のページを画像に変換

    Args:
        pdf_path: PDFファイルのパス
        output_dir: 出力ディレクトリ（デフォルト: tmp/images）
        use_pymupdf: PyMuPDFを使用するか（デフォルト: False、pdf2imageを使用）

    Returns:
        str: 生成された画像ファイルのパス

    Raises:
        FileNotFoundError: PDFファイルが存在しない
        ValueError: ファイル拡張子が不正、またはファイルサイズが制限を超える
        PDFConversionError: PDF変換に失敗した

    Example:
        >>> image_path = convert_pdf_to_image("document.pdf")
        >>> print(f"画像を生成しました: {image_path}")
    """
    # パスをPathオブジェクトに変換
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)

    # 出力ディレクトリを作成
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # PDFファイルのバリデーション
        validate_pdf_file(pdf_path)

        # PDF変換を実行
        if use_pymupdf:
            output_path = convert_pdf_to_image_pymupdf(pdf_path, output_dir)
        else:
            output_path = convert_pdf_to_image_pdf2image(pdf_path, output_dir)

        return str(output_path)

    except (FileNotFoundError, ValueError, PDFConversionError) as e:
        logger.error(f"PDF変換エラー: {e}")
        raise
    except Exception as e:
        logger.error(f"予期しないエラー: {e}")
        raise PDFConversionError(f"予期しないエラーが発生しました: {e}") from e


def cleanup_temp_files(image_path: str | Path) -> None:
    """
    一時ファイルをクリーンアップ

    Args:
        image_path: 削除する画像ファイルのパス
    """
    try:
        image_path = Path(image_path)
        if image_path.exists():
            image_path.unlink()
            logger.info(f"一時ファイルを削除しました: {image_path}")
    except Exception as e:
        logger.warning(f"一時ファイルの削除に失敗しました: {e}")


def main() -> int:
    """
    メイン関数（CLIエントリーポイント）

    Returns:
        int: 終了コード（0: 成功、1: 失敗）
    """
    parser = argparse.ArgumentParser(
        description="PDFファイルの最初のページを画像に変換"
    )
    parser.add_argument(
        "pdf_path",
        type=str,
        help="PDFファイルのパス",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=str,
        default="tmp/images",
        help="出力ディレクトリ（デフォルト: tmp/images）",
    )
    parser.add_argument(
        "--use-pymupdf",
        action="store_true",
        help="PyMuPDFを使用する（デフォルト: pdf2imageを使用）",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="処理後に一時ファイルを削除する",
    )

    args = parser.parse_args()

    try:
        # PDF変換を実行
        image_path = convert_pdf_to_image(
            args.pdf_path,
            args.output_dir,
            args.use_pymupdf,
        )

        # 成功メッセージを出力
        print(image_path)
        logger.info(f"PDF変換が完了しました: {image_path}")

        # クリーンアップ（オプション）
        if args.cleanup:
            cleanup_temp_files(image_path)

        return 0

    except (FileNotFoundError, ValueError, PDFConversionError) as e:
        print(f"エラー: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"予期しないエラー: {e}", file=sys.stderr)
        logger.exception("予期しないエラーが発生しました")
        return 1


if __name__ == "__main__":
    sys.exit(main())
