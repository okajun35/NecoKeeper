#!/usr/bin/env python3
"""
Sample PDF care log generator

This script creates a sample PDF file that simulates a scanned care log form
for testing the PDF conversion functionality.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def create_pdf_from_image(image_path: str | Path, pdf_path: str | Path) -> None:
    """
    Convert an image to PDF format.

    Args:
        image_path: Path to the source image
        pdf_path: Path to save the PDF
    """
    img = Image.open(image_path)

    # Convert to RGB if necessary
    if img.mode != "RGB":
        img = img.convert("RGB")

    # Save as PDF
    pdf_path = Path(pdf_path)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(pdf_path, "PDF", resolution=100.0)
    print(f"Created PDF: {pdf_path}")


def create_multi_page_care_log_image(
    output_path: str | Path,
    cat_name: str = "あみ",
    year_month: str = "2025年5月",
) -> None:
    """
    Create a care log image suitable for PDF conversion.

    Args:
        output_path: Path to save the image
        cat_name: Name of the cat
        year_month: Year and month for the records
    """
    # Create a larger image suitable for PDF
    width, height = 1200, 1600
    img = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(img)

    # Try to use a Japanese font
    japanese_fonts = [
        "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",  # IPAGothic
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",  # WenQuanYi Zen Hei
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",  # Noto Sans CJK
    ]

    font_title = None
    for font_path in japanese_fonts:
        try:
            font_title = ImageFont.truetype(font_path, 36)
            font_header = ImageFont.truetype(font_path, 24)
            font_body = ImageFont.truetype(font_path, 20)
            font_small = ImageFont.truetype(font_path, 16)
            break
        except OSError:
            continue

    if font_title is None:
        font_title = ImageFont.load_default()
        font_header = ImageFont.load_default()
        font_body = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Draw title and header
    draw.text((100, 50), "猫世話記録表", fill="black", font=font_title)
    draw.text((100, 120), f"猫の名前: {cat_name}", fill="black", font=font_header)
    draw.text((100, 160), f"記録期間: {year_month}", fill="black", font=font_header)

    # Draw table
    y_offset = 250
    headers = ["日付", "時間", "ごはん", "元気", "排尿", "排便", "嘔吐", "投薬", "備考"]
    x_positions = [100, 200, 320, 440, 560, 680, 800, 920, 1040]

    # Draw header row
    for i, header in enumerate(headers):
        draw.text((x_positions[i], y_offset), header, fill="black", font=font_header)

    # Draw horizontal line under header
    draw.line([(80, y_offset + 40), (1150, y_offset + 40)], fill="black", width=3)

    # Sample data for multiple days
    records = [
        {
            "date": "5/1",
            "slots": [
                {
                    "time": "朝",
                    "meal": "○",
                    "energy": "○",
                    "urine": "○",
                    "stool": "○",
                    "vomit": "×",
                    "med": "×",
                },
                {
                    "time": "昼",
                    "meal": "○",
                    "energy": "○",
                    "urine": "×",
                    "stool": "×",
                    "vomit": "×",
                    "med": "×",
                },
                {
                    "time": "夕",
                    "meal": "○",
                    "energy": "○",
                    "urine": "○",
                    "stool": "○",
                    "vomit": "×",
                    "med": "×",
                    "notes": "元気",
                },
            ],
        },
        {
            "date": "5/2",
            "slots": [
                {
                    "time": "朝",
                    "meal": "○",
                    "energy": "○",
                    "urine": "○",
                    "stool": "○",
                    "vomit": "×",
                    "med": "×",
                },
                {
                    "time": "昼",
                    "meal": "△",
                    "energy": "△",
                    "urine": "×",
                    "stool": "×",
                    "vomit": "×",
                    "med": "×",
                },
                {
                    "time": "夕",
                    "meal": "○",
                    "energy": "○",
                    "urine": "○",
                    "stool": "×",
                    "vomit": "×",
                    "med": "×",
                },
            ],
        },
        {
            "date": "5/3",
            "slots": [
                {
                    "time": "朝",
                    "meal": "○",
                    "energy": "○",
                    "urine": "○",
                    "stool": "○",
                    "vomit": "×",
                    "med": "×",
                },
                {
                    "time": "昼",
                    "meal": "○",
                    "energy": "○",
                    "urine": "○",
                    "stool": "×",
                    "vomit": "×",
                    "med": "×",
                },
                {
                    "time": "夕",
                    "meal": "○",
                    "energy": "○",
                    "urine": "○",
                    "stool": "○",
                    "vomit": "×",
                    "med": "×",
                },
            ],
        },
        {
            "date": "5/4",
            "slots": [
                {
                    "time": "朝",
                    "meal": "×",
                    "energy": "×",
                    "urine": "×",
                    "stool": "×",
                    "vomit": "○",
                    "med": "○",
                    "notes": "体調不良",
                },
                {
                    "time": "昼",
                    "meal": "×",
                    "energy": "×",
                    "urine": "×",
                    "stool": "×",
                    "vomit": "×",
                    "med": "○",
                },
                {
                    "time": "夕",
                    "meal": "△",
                    "energy": "△",
                    "urine": "○",
                    "stool": "×",
                    "vomit": "×",
                    "med": "○",
                    "notes": "少し回復",
                },
            ],
        },
        {
            "date": "5/5",
            "slots": [
                {
                    "time": "朝",
                    "meal": "○",
                    "energy": "○",
                    "urine": "○",
                    "stool": "○",
                    "vomit": "×",
                    "med": "×",
                },
                {
                    "time": "昼",
                    "meal": "○",
                    "energy": "○",
                    "urine": "×",
                    "stool": "×",
                    "vomit": "×",
                    "med": "×",
                },
                {
                    "time": "夕",
                    "meal": "○",
                    "energy": "○",
                    "urine": "○",
                    "stool": "○",
                    "vomit": "×",
                    "med": "×",
                    "notes": "完全回復",
                },
            ],
        },
    ]

    # Draw records
    y_offset += 60
    for record in records:
        date = record["date"]

        for slot in record["slots"]:
            # Draw date (only for first slot)
            if slot == record["slots"][0]:
                draw.text(
                    (x_positions[0], y_offset), date, fill="black", font=font_body
                )

            # Draw time
            draw.text(
                (x_positions[1], y_offset), slot["time"], fill="black", font=font_body
            )

            # Draw meal
            draw.text(
                (x_positions[2], y_offset), slot["meal"], fill="black", font=font_body
            )

            # Draw energy
            draw.text(
                (x_positions[3], y_offset), slot["energy"], fill="black", font=font_body
            )

            # Draw urine
            draw.text(
                (x_positions[4], y_offset), slot["urine"], fill="black", font=font_body
            )

            # Draw stool
            draw.text(
                (x_positions[5], y_offset), slot["stool"], fill="black", font=font_body
            )

            # Draw vomit
            draw.text(
                (x_positions[6], y_offset), slot["vomit"], fill="black", font=font_body
            )

            # Draw medication
            draw.text(
                (x_positions[7], y_offset), slot["med"], fill="black", font=font_body
            )

            # Draw notes
            if "notes" in slot:
                draw.text(
                    (x_positions[8], y_offset),
                    slot["notes"],
                    fill="black",
                    font=font_small,
                )

            y_offset += 45

        # Draw horizontal line after each day
        draw.line([(80, y_offset), (1150, y_offset)], fill="lightgray", width=1)
        y_offset += 10

    # Draw vertical grid lines
    for x in x_positions:
        draw.line([(x - 10, 290), (x - 10, y_offset - 10)], fill="lightgray", width=1)

    # Draw border
    draw.rectangle([(80, 250), (1150, y_offset - 10)], outline="black", width=2)

    # Save image
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)
    print(f"Created care log image: {output_path}")


def main() -> None:
    """Generate sample PDF files."""
    fixtures_dir = Path(__file__).parent

    # Create a care log image
    temp_image = fixtures_dir / "temp_pdf_image.png"
    create_multi_page_care_log_image(
        temp_image,
        cat_name="あみ",
        year_month="2025年5月",
    )

    # Convert to PDF
    pdf_path = fixtures_dir / "sample_care_log.pdf"
    create_pdf_from_image(temp_image, pdf_path)

    # Clean up temporary image
    temp_image.unlink()

    print("\nSample PDF created successfully!")


if __name__ == "__main__":
    main()
