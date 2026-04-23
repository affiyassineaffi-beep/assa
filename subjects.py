"""
Tunisian Academic Engine
Subjects, coefficients, optional subjects, and the bonus-points rule.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Subject:
    name_fr: str
    name_ar: str
    coefficient: float
    optional: bool = False
    section: Optional[str] = None  # None = applies to all sections


# ─── Primary (Primaire) ────────────────────────────────────────────────────────
PRIMARY_SUBJECTS: list[Subject] = [
    Subject("Arabe", "عربية", 4),
    Subject("Mathématiques", "رياضيات", 4),
    Subject("Français", "فرنسية", 3),
    Subject("Éveil scientifique", "تربية علمية", 2),
    Subject("Éducation islamique", "تربية إسلامية", 2),
    Subject("Histoire-Géographie", "تاريخ وجغرافيا", 1),
    Subject("Éducation civique", "تربية مدنية", 1),
    Subject("Éducation artistique", "تربية فنية", 1),
    Subject("Éducation physique", "تربية بدنية", 1),
]

# ─── Preparatory / Collège (Préparatoire) ─────────────────────────────────────
PREP_SUBJECTS: list[Subject] = [
    Subject("Arabe", "عربية", 4),
    Subject("Mathématiques", "رياضيات", 4),
    Subject("Français", "فرنسية", 3),
    Subject("Sciences de la Vie et de la Terre", "علوم حياة", 2),
    Subject("Sciences Physiques", "فيزياء", 2),
    Subject("Éducation islamique", "تربية إسلامية", 2),
    Subject("Histoire-Géographie", "تاريخ وجغرافيا", 2),
    Subject("Anglais", "إنجليزية", 2),
    Subject("Informatique", "إعلامية", 1),
    Subject("Technologie", "تكنولوجيا", 1),
    Subject("Éducation artistique", "تربية فنية", 1),
    Subject("Éducation physique", "تربية بدنية", 1),
    Subject("Allemand", "ألمانية", 2, optional=True),
    Subject("Italien", "إيطالية", 2, optional=True),
    Subject("Espagnol", "إسبانية", 2, optional=True),
]

# ─── Secondary (Lycée) — by section ──────────────────────────────────────────
SECONDARY_SUBJECTS: dict[str, list[Subject]] = {
    "Sciences": [
        Subject("Mathématiques", "رياضيات", 5),
        Subject("Sciences Physiques", "فيزياء", 4),
        Subject("Sciences de la Vie et de la Terre", "علوم حياة", 4),
        Subject("Arabe", "عربية", 3),
        Subject("Français", "فرنسية", 3),
        Subject("Anglais", "إنجليزية", 2),
        Subject("Éducation islamique", "تربية إسلامية", 1),
        Subject("Histoire-Géographie", "تاريخ وجغرافيا", 1),
        Subject("Philosophie", "فلسفة", 1),
        Subject("Informatique", "إعلامية", 2, optional=True),
        Subject("Éducation physique", "تربية بدنية", 1),
    ],
    "Informatique": [
        Subject("Mathématiques", "رياضيات", 5),
        Subject("Sciences Physiques", "فيزياء", 3),
        Subject("Informatique", "إعلامية", 5),
        Subject("Arabe", "عربية", 3),
        Subject("Français", "فرنسية", 3),
        Subject("Anglais", "إنجليزية", 2),
        Subject("Éducation islamique", "تربية إسلامية", 1),
        Subject("Histoire-Géographie", "تاريخ وجغرافيا", 1),
        Subject("Philosophie", "فلسفة", 1),
        Subject("Éducation physique", "تربية بدنية", 1),
    ],
    "Lettres": [
        Subject("Arabe", "عربية", 5),
        Subject("Philosophie", "فلسفة", 4),
        Subject("Histoire-Géographie", "تاريخ وجغرافيا", 4),
        Subject("Français", "فرنسية", 3),
        Subject("Anglais", "إنجليزية", 3),
        Subject("Éducation islamique", "تربية إسلامية", 2),
        Subject("Mathématiques", "رياضيات", 2),
        Subject("Italien", "إيطالية", 2, optional=True),
        Subject("Allemand", "ألمانية", 2, optional=True),
        Subject("Espagnol", "إسبانية", 2, optional=True),
        Subject("Éducation physique", "تربية بدنية", 1),
    ],
    "Économie-Gestion": [
        Subject("Gestion", "تصرف", 5),
        Subject("Économie", "اقتصاد", 5),
        Subject("Mathématiques", "رياضيات", 3),
        Subject("Arabe", "عربية", 3),
        Subject("Français", "فرنسية", 3),
        Subject("Anglais", "إنجليزية", 2),
        Subject("Informatique", "إعلامية", 2),
        Subject("Droit", "قانون", 2),
        Subject("Éducation islamique", "تربية إسلامية", 1),
        Subject("Philosophie", "فلسفة", 1),
        Subject("Éducation physique", "تربية بدنية", 1),
    ],
    "Technique": [
        Subject("Sciences Physiques", "فيزياء", 4),
        Subject("Mathématiques", "رياضيات", 4),
        Subject("Sciences Techniques", "تكنولوجيا", 5),
        Subject("Arabe", "عربية", 3),
        Subject("Français", "فرنسية", 3),
        Subject("Anglais", "إنجليزية", 2),
        Subject("Informatique", "إعلامية", 2),
        Subject("Éducation islamique", "تربية إسلامية", 1),
        Subject("Éducation physique", "تربية بدنية", 1),
    ],
}

SECTIONS = list(SECONDARY_SUBJECTS.keys())


def get_subjects(level: str, section: str | None = None) -> list[Subject]:
    if level == "Primary":
        return PRIMARY_SUBJECTS
    if level in ("Preparatory", "Basic"):
        return PREP_SUBJECTS
    if level == "Secondary":
        return SECONDARY_SUBJECTS.get(section or "Sciences", [])
    return []


def subject_names_fr(level: str, section: str | None = None) -> list[str]:
    return [s.name_fr for s in get_subjects(level, section)]


def subject_names_ar(level: str, section: str | None = None) -> list[str]:
    return [s.name_ar for s in get_subjects(level, section)]


def coefficient(subject_fr: str, level: str, section: str | None = None) -> float:
    for s in get_subjects(level, section):
        if s.name_fr == subject_fr:
            return s.coefficient
    return 1.0


def is_optional(subject_fr: str, level: str, section: str | None = None) -> bool:
    for s in get_subjects(level, section):
        if s.name_fr == subject_fr:
            return s.optional
    return False


@dataclass
class GradeEntry:
    subject_fr: str
    score: float
    level: str
    section: str | None = None

    @property
    def coef(self) -> float:
        return coefficient(self.subject_fr, self.level, self.section)

    @property
    def optional(self) -> bool:
        return is_optional(self.subject_fr, self.level, self.section)

    @property
    def bonus(self) -> float:
        """Bonus points for optional subjects: only points above 10 count."""
        if not self.optional:
            return 0.0
        if self.score > 10:
            return (self.score - 10) * self.coef
        return 0.0

    @property
    def weighted(self) -> float:
        """Weighted score for mandatory subjects (used in average calculation)."""
        if self.optional:
            return 0.0
        return self.score * self.coef


def compute_average(entries: list[GradeEntry]) -> dict:
    """
    Returns:
      weighted_average – Tunisian coefficient-weighted average
      total_bonus      – sum of bonus points from optional subjects
      final_average    – weighted_average + total_bonus / total_coef * 20 (capped at 20)
      total_coef       – sum of mandatory coefficients
    """
    mandatory = [e for e in entries if not e.optional]
    total_coef = sum(e.coef for e in mandatory)
    total_bonus = sum(e.bonus for e in entries)

    if total_coef == 0:
        return {"weighted_average": 0, "total_bonus": 0, "final_average": 0, "total_coef": 0}

    weighted_avg = sum(e.weighted for e in mandatory) / total_coef
    # Bonus adds (bonus_points / total_coef) to the average
    bonus_contribution = total_bonus / total_coef
    final = min(weighted_avg + bonus_contribution, 20.0)

    return {
        "weighted_average": round(weighted_avg, 2),
        "total_bonus": round(total_bonus, 2),
        "final_average": round(final, 2),
        "total_coef": total_coef,
    }


def generate_mentor_advice(entries: list[GradeEntry], lang: str = "fr") -> list[str]:
    """AI-style study tips based on grade performance."""
    if not entries:
        return []

    tips = []
    avg = compute_average(entries)["final_average"]

    weak = sorted(
        [e for e in entries if not e.optional and e.score < 10],
        key=lambda e: e.score,
    )
    strong = sorted(
        [e for e in entries if e.score >= 15],
        key=lambda e: e.score,
        reverse=True,
    )

    if lang == "ar":
        if avg >= 15:
            tips.append("🏆 أداء ممتاز! استمر في هذا المستوى الرائع.")
        elif avg >= 12:
            tips.append("👍 مستوى جيد. بعض التحسينات ستجعلك في القمة.")
        elif avg >= 10:
            tips.append("⚠️ معدلك فوق الحد الأدنى، لكن هناك مجال للتحسن.")
        else:
            tips.append("🔴 معدلك دون 10. يجب العمل بجدية أكبر.")
        for e in weak[:3]:
            tips.append(f"📚 ركز على مادة «{e.subject_fr}» (معدل: {e.score}/20، معامل: {e.coef})")
        for e in strong[:2]:
            tips.append(f"⭐ أداء رائع في مادة «{e.subject_fr}» — حافظ على هذا المستوى")
    else:
        if avg >= 15:
            tips.append("🏆 Excellent ! Continue sur cette lancée remarquable.")
        elif avg >= 12:
            tips.append("👍 Bon niveau. Quelques efforts ciblés te feront atteindre l'excellence.")
        elif avg >= 10:
            tips.append("⚠️ Moyenne au-dessus de 10, mais des améliorations sont nécessaires.")
        else:
            tips.append("🔴 Moyenne en dessous de 10. Un plan de travail sérieux s'impose.")
        for e in weak[:3]:
            tips.append(f"📚 Focus sur «{e.subject_fr}» (note: {e.score}/20, coeff: {e.coef})")
        for e in strong[:2]:
            tips.append(f"⭐ Excellent en «{e.subject_fr}» — maintiens ce niveau !")

    return tips
