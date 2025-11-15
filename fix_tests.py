#!/usr/bin/env python3
"""テストファイルに log_date を追加するスクリプト"""

import re
from pathlib import Path

# 修正対象のファイル
test_files = [
    "tests/api/test_care_logs.py",
    "tests/api/test_public.py",
    "tests/services/test_care_log_service.py",
    "tests/services/test_volunteer_service.py",
]

# 追加するインポート
import_line = "from datetime import date\n"

for file_path in test_files:
    path = Path(file_path)
    if not path.exists():
        print(f"⚠️  {file_path} が見つかりません")
        continue

    content = path.read_text(encoding="utf-8")

    # datetime のインポートがあるか確認
    if "from datetime import" not in content:
        # インポートセクションの最後に追加
        content = re.sub(
            r"(from app\.models\.care_log import CareLog)",
            r"\1\nfrom datetime import date",
            content,
        )
    elif "from datetime import date" not in content:
        # datetime インポートに date を追加
        content = re.sub(
            r"from datetime import (.*)",
            lambda m: f"from datetime import {m.group(1)}, date"
            if "date" not in m.group(1)
            else m.group(0),
            content,
        )

    # CareLog( の後に log_date を追加
    # すでに log_date がある場合はスキップ
    def add_log_date(match):
        indent = match.group(1)
        if "log_date=" in match.group(0):
            return match.group(0)
        return f"{indent}care_log = CareLog(\n{indent}    log_date=date.today(),\n{indent}    animal_id="

    content = re.sub(r"(\s+)care_log = CareLog\(\n\s+animal_id=", add_log_date, content)

    # log1, log2, old_log, new_log, today_log なども対応
    for var_name in [
        "log1",
        "log2",
        "old_log",
        "new_log",
        "today_log",
        "target_log",
        "other_log",
    ]:

        def add_log_date_var(match, var=var_name):
            indent = match.group(1)
            if "log_date=" in match.group(0):
                return match.group(0)
            return f"{indent}{var} = CareLog(\n{indent}    log_date=date.today(),\n{indent}    animal_id="

        content = re.sub(
            rf"(\s+){var_name} = CareLog\(\n\s+animal_id=", add_log_date_var, content
        )

    path.write_text(content, encoding="utf-8")
    print(f"✅ {file_path} を修正しました")

print("\n完了！")
