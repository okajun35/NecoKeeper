import re
from pathlib import Path


class TestAdoptionRecordsJSApplicantSelection:
    """面談記録モーダルの里親希望者選択ロジック回帰テスト"""

    def test_ensure_applicant_option_exists_accepts_fallback_candidate(self) -> None:
        """
        Given: 初期ロード外の候補を hidden select に追加する必要がある
        When: adoption_records.js の option 追加ロジックを確認する
        Then: 候補オブジェクト / fallback から option を構成できる
        """
        script = Path("app/static/js/admin/adoption_records.js").read_text(
            encoding="utf-8"
        )

        assert (
            "function ensureApplicantOptionExists(selectElement, applicantRef, fallbackApplicant = null)"
            in script
        )
        assert (
            "const directApplicant = typeof applicantRef === 'object' ? applicantRef : null;"
            in script
        )
        assert re.search(
            r"const applicant\s*=\s*directApplicant \|\| fallbackApplicant \|\| applicants\.find\(a => a\.id === applicantId\);",
            script,
        )
        assert (
            "option.textContent = applicant?.name || `申込者 #${optionValue}`;"
            in script
        )

    def test_select_candidate_passes_object_to_option_builder(self) -> None:
        """
        Given: 検索APIで取得した候補オブジェクト
        When: 候補選択時のロジックを確認する
        Then: idのみではなく候補オブジェクトを option 生成へ渡している
        """
        script = Path("app/static/js/admin/adoption_records.js").read_text(
            encoding="utf-8"
        )

        assert "ensureApplicantOptionExists(applicantSelect, selected);" in script

    def test_open_modal_fetches_applicant_name_when_not_cached(self) -> None:
        """
        Given: 編集対象 applicant_id が初期キャッシュに存在しない
        When: 面談記録モーダルを開く
        Then: applicant詳細APIを再取得して実名表示に使う
        """
        script = Path("app/static/js/admin/adoption_records.js").read_text(
            encoding="utf-8"
        )

        assert "async function fetchApplicantById(applicantId)" in script
        assert "`/api/v1/adoptions/applicants-extended/${applicantId}`" in script
        assert "async function resolveApplicantForRecord(applicantId)" in script
        assert (
            "const selectedApplicant = await resolveApplicantForRecord(record.applicant_id);"
            in script
        )
        assert (
            "searchInput.value = selectedApplicant?.name || `申込者 #${record.applicant_id}`;"
            in script
        )
