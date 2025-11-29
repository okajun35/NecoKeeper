from pathlib import Path

from paddleocr import PaddleOCR


# --- 関数: 座標を使って行と列を整列させるロジック ---
def sort_and_format_lines(ocr_results, y_threshold=15):
    """
    OCR結果を座標に基づいて行ごとに整理し、左から右へ並べ替える
    y_threshold: 同じ行とみなすY座標のズレ許容値（ピクセル）
    """
    if not ocr_results:
        return []

    # 1. 全てのボックス情報をフラットなリストにする
    # データ構造: {'text': 文字, 'conf': 確信度, 'box': [[x1,y1], [x2,y1], [x2,y2], [x1,y2]]}
    items = []

    # PaddleOCRのバージョンによる構造の違いを吸収
    for res in ocr_results:
        if isinstance(res, dict) and "rec_texts" in res:  # 新バージョン(v2.9+)
            boxes = res["dt_polys"]
            texts = res["rec_texts"]
            scores = res["rec_scores"]
            for box, text, score in zip(boxes, texts, scores, strict=True):
                items.append({"box": box, "text": text, "conf": score})
        elif isinstance(res, list):  # 旧バージョン or シンプルリスト
            for line in res:
                items.append({"box": line[0], "text": line[1][0], "conf": line[1][1]})

    if not items:
        return []

    # 2. Y座標（各ボックスの中心の高さ）を計算して追加
    for item in items:
        # box[0][1]は左上のY, box[2][1]は右下のY。平均を取って中心Yとする
        center_y = (item["box"][0][1] + item["box"][2][1]) / 2
        center_x = (item["box"][0][0] + item["box"][2][0]) / 2
        item["cy"] = center_y
        item["cx"] = center_x

    # 3. Y座標（上から下）で全体をソート
    items.sort(key=lambda x: x["cy"])

    # 4. Y座標が近いものを同じ「行」としてグループ化
    lines = []
    current_line = []
    if items:
        current_line.append(items[0])

    for i in range(1, len(items)):
        prev = current_line[-1]
        curr = items[i]

        # 前の文字との高さの差が閾値以内なら同じ行
        if abs(curr["cy"] - prev["cy"]) < y_threshold:
            current_line.append(curr)
        else:
            # 行が変わったので、今の行を保存して新しい行を開始
            lines.append(current_line)
            current_line = [curr]
    lines.append(current_line)  # 最後の行を追加

    # 5. 各行の中でX座標（左から右）でソート
    formatted_output = []
    for line in lines:
        line.sort(key=lambda x: x["cx"])
        # 行内のテキストをタブ区切りなどで結合
        row_text = " | ".join([item["text"] for item in line])
        formatted_output.append(row_text)

    return formatted_output


# --- メイン処理 ---
base_dir = Path(__file__).resolve().parent
img_path = base_dir / "file_page1.png"

if not img_path.exists():
    print("画像がありません")
    exit()

ocr = PaddleOCR(
    use_angle_cls=True,
    lang="japan",
    # --- 追記設定 ---
    det_db_thresh=0.1,  # 検出の閾値（デフォルト0.3）。下げると薄い線も拾う
    det_db_box_thresh=0.1,  # ボックスを作る閾値（デフォルト0.6）。下げると小さなゴミも拾うが記号も拾う
    # rec_char_dict_path=None # デフォルト辞書を使う
)
results = ocr.ocr(img_path)

# 整形して表示
formatted_lines = sort_and_format_lines(results)

print("\n--- テーブル復元結果 ---")
for line in formatted_lines:
    print(line)
