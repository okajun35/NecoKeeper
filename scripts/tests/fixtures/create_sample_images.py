#!/usr/bin/env python3
"""
Sample handwritten care log image generator

This script creates sample images that simulate handwritten care log forms
for testing the OCR import functionality.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def create_care_log_image(
    output_path: str | Path,
    cat_name: str = "たま",
    year_month: str = "2025年11月",
    records: list[dict] | None = None,
) -> None:
    """
    Create a sample care log image with handwritten-style text.

    Args:
        output_path: Path to save the image
        cat_name: Name of the cat
        year_month: Year and month for the records
        records: List of care log records with date, time_slot, and values
    """
    if records is None:
        records = [
            {
                "date": "11/4",
                "morning": {"meal": "○", "energy": "○", "urine": "○", "stool": "○"},
                "noon": {"meal": "○", "energy": "○", "urine": "×", "stool": "×"},
                "evening": {
                    "meal": "○",
                    "energy": "○",
                    "urine": "○",
                    "stool": "○",
                    "notes": "よく食べた",
                },
            },
            {
                "date": "11/5",
                "morning": {"meal": "△", "energy": "△", "urine": "○", "stool": "○"},
                "noon": {"meal": "△", "energy": "△", "urine": "×", "stool": "×"},
                "evening": {
                    "meal": "○",
                    "energy": "○",
                    "urine": "○",
                    "stool": "○",
                    "notes": "夕方には元気",
                },
            },
        ]

    # Create image
    width, height = 800, 600
    img = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(img)

    # Try to use a Japanese font
    japanese_fonts = [
        "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",  # IPAGothic
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",  # WenQuanYi Zen Hei
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",  # Noto Sans CJK
    ]

    font_large = None
    for font_path in japanese_fonts:
        try:
            font_large = ImageFont.truetype(font_path, 24)
            font_medium = ImageFont.truetype(font_path, 18)
            font_small = ImageFont.truetype(font_path, 14)
            break
        except OSError:
            continue

    if font_large is None:
        # Fallback to default font
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Draw title
    draw.text((50, 20), f"猫世話記録表 - {cat_name}", fill="black", font=font_large)
    draw.text((50, 50), year_month, fill="black", font=font_medium)

    # Draw table header
    y_offset = 100
    headers = ["日付", "時間", "ごはん", "元気", "排尿", "排便", "備考"]
    x_positions = [50, 120, 200, 280, 360, 440, 520]

    for i, header in enumerate(headers):
        draw.text((x_positions[i], y_offset), header, fill="black", font=font_medium)

    # Draw horizontal line
    draw.line([(40, y_offset + 30), (750, y_offset + 30)], fill="black", width=2)

    # Draw records
    y_offset += 50
    time_slots = {"morning": "朝", "noon": "昼", "evening": "夕"}

    for record in records:
        date = record["date"]
        row_y = y_offset

        for time_key, time_label in time_slots.items():
            if time_key in record:
                data = record[time_key]

                # Draw date (only for first time slot)
                if time_key == "morning":
                    draw.text(
                        (x_positions[0], row_y), date, fill="black", font=font_small
                    )

                # Draw time slot
                draw.text(
                    (x_positions[1], row_y), time_label, fill="black", font=font_small
                )

                # Draw meal
                draw.text(
                    (x_positions[2], row_y),
                    data.get("meal", ""),
                    fill="black",
                    font=font_medium,
                )

                # Draw energy
                draw.text(
                    (x_positions[3], row_y),
                    data.get("energy", ""),
                    fill="black",
                    font=font_medium,
                )

                # Draw urine
                draw.text(
                    (x_positions[4], row_y),
                    data.get("urine", ""),
                    fill="black",
                    font=font_medium,
                )

                # Draw stool
                draw.text(
                    (x_positions[5], row_y),
                    data.get("stool", ""),
                    fill="black",
                    font=font_medium,
                )

                # Draw notes
                notes = data.get("notes", "")
                if notes:
                    draw.text(
                        (x_positions[6], row_y), notes, fill="black", font=font_small
                    )

                row_y += 35

        y_offset = row_y

    # Draw grid lines
    for x in x_positions:
        draw.line([(x - 5, 130), (x - 5, y_offset)], fill="lightgray", width=1)

    # Save image
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)
    print(f"Created sample image: {output_path}")


def create_poor_quality_image(output_path: str | Path) -> None:
    """
    Create a poor quality image to test error handling.

    Args:
        output_path: Path to save the image
    """
    # Create a blurry, low-contrast image
    width, height = 400, 300
    img = Image.new("RGB", (width, height), color="lightgray")
    draw = ImageDraw.Draw(img)

    japanese_fonts = [
        "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    ]

    font = None
    for font_path in japanese_fonts:
        try:
            font = ImageFont.truetype(font_path, 12)
            break
        except OSError:
            continue

    if font is None:
        font = ImageFont.load_default()

    # Draw some barely visible text
    draw.text((50, 50), "猫世話記録表", fill="gray", font=font)
    draw.text((50, 80), "読み取り困難", fill="gray", font=font)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, quality=20)  # Low quality JPEG
    print(f"Created poor quality image: {output_path}")


def main() -> None:
    """Generate all sample images."""
    fixtures_dir = Path(__file__).parent

    # Create standard quality image
    create_care_log_image(
        fixtures_dir / "sample_care_log.png",
        cat_name="たま",
        year_month="2025年11月",
    )

    # Create image with edge cases
    edge_case_records = [
        {
            "date": "11/10",
            "morning": {
                "meal": "×",
                "energy": "×",
                "urine": "×",
                "stool": "×",
                "notes": "体調不良",
            },
            "noon": {"meal": "×", "energy": "×", "urine": "×", "stool": "×"},
            "evening": {"meal": "△", "energy": "△", "urine": "○", "stool": "×"},
        }
    ]

    create_care_log_image(
        fixtures_dir / "sample_edge_case.png",
        cat_name="みけ",
        year_month="2025年11月",
        records=edge_case_records,
    )

    # Create poor quality image
    create_poor_quality_image(fixtures_dir / "sample_poor_quality.png")

    print("\nAll sample images created successfully!")


if __name__ == "__main__":
    main()
