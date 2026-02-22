"""
ステータス・ロケーション Enum 定義

Issue #85: ステータス・ロケーション管理システム
"""

from enum import Enum


class AnimalStatus(str, Enum):
    """猫のステータス"""

    QUARANTINE = "QUARANTINE"  # 隔離中
    IN_CARE = "IN_CARE"  # 在籍中
    TRIAL = "TRIAL"  # トライアル中
    ADOPTED = "ADOPTED"  # 譲渡済み（終端）
    DECEASED = "DECEASED"  # 死亡（終端）

    def is_terminal(self) -> bool:
        """終端ステータスか判定"""
        return self in (AnimalStatus.ADOPTED, AnimalStatus.DECEASED)

    def display_name_ja(self) -> str:
        """日本語表示名"""
        names = {
            AnimalStatus.QUARANTINE: "保護中",
            AnimalStatus.IN_CARE: "在籍中（施設/カフェ/預かり含む）",
            AnimalStatus.TRIAL: "トライアル中",
            AnimalStatus.ADOPTED: "譲渡済み",
            AnimalStatus.DECEASED: "死亡",
        }
        return names.get(self, self.value)

    def display_name_en(self) -> str:
        """英語表示名"""
        names = {
            AnimalStatus.QUARANTINE: "Quarantine",
            AnimalStatus.IN_CARE: "In Care",
            AnimalStatus.TRIAL: "On Trial",
            AnimalStatus.ADOPTED: "Adopted",
            AnimalStatus.DECEASED: "Deceased",
        }
        return names.get(self, self.value)


class LocationType(str, Enum):
    """猫のロケーションタイプ"""

    FACILITY = "FACILITY"  # 施設（保護施設・猫カフェ・シェルター）
    FOSTER_HOME = "FOSTER_HOME"  # 預かりボランティア宅
    ADOPTER_HOME = "ADOPTER_HOME"  # 里親候補宅（トライアル先）

    def display_name_ja(self) -> str:
        """日本語表示名"""
        names = {
            LocationType.FACILITY: "施設（保護施設・猫カフェ・シェルター）",
            LocationType.FOSTER_HOME: "預かりボランティア宅",
            LocationType.ADOPTER_HOME: "里親候補宅（トライアル先）",
        }
        return names.get(self, self.value)

    def display_name_en(self) -> str:
        """英語表示名"""
        names = {
            LocationType.FACILITY: "Facility",
            LocationType.FOSTER_HOME: "Foster Home",
            LocationType.ADOPTER_HOME: "Adopter Home",
        }
        return names.get(self, self.value)


class VaccineCategoryEnum(str, Enum):
    """ワクチン種別

    Issue #83: プロフィールに医療情報を追加
    「どの病気のワクチンを打ったか」ではなく「どのワクチンを打ったか」を記録する設計。
    """

    VACCINE_3CORE = "3core"  # FVR+FCV+FPV（3種混合）
    VACCINE_4CORE = "4core"  # 3種＋FeLV（4種混合）
    VACCINE_5CORE = "5core"  # 4種＋クラミジア（5種混合）

    def display_name_ja(self) -> str:
        """日本語表示名"""
        names = {
            VaccineCategoryEnum.VACCINE_3CORE: "3種",
            VaccineCategoryEnum.VACCINE_4CORE: "4種",
            VaccineCategoryEnum.VACCINE_5CORE: "5種",
        }
        return names.get(self, self.value)

    def display_name_en(self) -> str:
        """英語表示名"""
        names = {
            VaccineCategoryEnum.VACCINE_3CORE: "3-in-1",
            VaccineCategoryEnum.VACCINE_4CORE: "4-in-1",
            VaccineCategoryEnum.VACCINE_5CORE: "5-in-1",
        }
        return names.get(self, self.value)
