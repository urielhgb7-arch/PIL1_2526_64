# backend/app/services/matching.py
# ============================================================
# MOTEUR DE MATCHING — IFRI MENTORLINK
# Conforme à : IFRI_Mentorlink_Vision_du_Système_de_Matching.pdf
# Score sur 100 = Matière(35) + Niveau↔Gravité(20) + Dispos(25) + Niveau académique(10) + Filière(10)
# ============================================================

from app.database import db
from app.models import (
    User, Profile, Disponible,
    ProfilCompetence, ProfilLacune, Matiere
)

# ── Mapping des niveaux en valeurs numériques ────────────────────────────────
COMPETENCE_LEVELS = {
    'Débutant':      1,
    'Intermédiaire': 2,
    'Avancé':        3,
    'Expert':        4
}

LACUNE_LEVELS = {
    'Basse':    1,   # correspond à "Faible" dans le PDF
    'Moyenne':  2,
    'Haute':    3,   # correspond à "Importante"
    'Urgente':  4    # correspond à "Critique"
}


def _score_niveau_vs_gravite(niveau_competence: str, priorite_lacune: str) -> float:
    """
    Critère 2 — Niveau de compétence du candidat vs gravité de la lacune du demandeur.
    Score max : 20 points.

    Logique : plus le niveau du candidat est élevé par rapport à la gravité de la lacune,
    meilleur est le score. Un Expert face à une lacune Urgente = score maximal.

    Exemple :
      Expert(4) ↔ Urgente(4)  → 20/20
      Avancé(3) ↔ Urgente(4)  → 15/20
      Débutant(1) ↔ Urgente(4) → 5/20
    """
    comp_val   = COMPETENCE_LEVELS.get(niveau_competence, 1)
    lacune_val = LACUNE_LEVELS.get(priorite_lacune, 1)

    # Ratio : quel % du besoin le candidat couvre-t-il ?
    ratio = comp_val / lacune_val if lacune_val > 0 else 0
    # On plafonne à 1 (un Expert face à une lacune Faible ne dépasse pas 20)
    ratio = min(ratio, 1.0)

    return round(ratio * 20, 2)


def _score_disponibilites(profile_slots: set, candidate_slots: set) -> float:
    """
    Critère 3 — Créneaux communs.
    Score max : 25 points.

    Plus les créneaux communs sont nombreux par rapport aux créneaux du demandeur,
    plus le score est élevé.
    """
    if not profile_slots:
        return 0.0

    shared = profile_slots.intersection(candidate_slots)
    ratio  = len(shared) / len(profile_slots)
    return round(ratio * 25, 2)


def _build_explanation(
    matched_subjects: list,
    shared_slots_count: int,
    same_filiere: bool,
    same_niveau: bool,
    same_format: bool,
    score: float
) -> dict:
    """
    Génère l'explication lisible du score (Section 9 du PDF).
    Affiché dans l'interface swipe sur la carte candidat.
    """
    raisons = []

    for subj in matched_subjects:
        raisons.append(f"Compétent en {subj['nom']} (niveau {subj['niveau_competence']})")

    if shared_slots_count > 0:
        raisons.append(f"{shared_slots_count} créneau(x) disponible(s) en commun")

    if same_filiere:
        raisons.append("Même filière")

    if same_niveau:
        raisons.append("Même année académique")

    if same_format:
        raisons.append("Même format d'apprentissage")

    return {
        "score_pct": f"{score}%",
        "raisons": raisons
    }


def _score_format_bonus(current_format: str, candidate_format: str) -> float:
    if not current_format or not candidate_format:
        return 0.0
    return 10.0 if current_format == candidate_format else 0.0


def calculate_matches(current_user_id: int, matiere_id: int = None) -> list:
    """
    Fonction principale du moteur de matching.

    Paramètres :
        current_user_id : l'utilisateur connecté (le demandeur)
        matiere_id      : filtre optionnel sur une matière précise

    Retourne :
        Liste de candidats triés par score décroissant, avec explication.

    Étapes (conformes au PDF) :
        1. Récupérer le profil du demandeur
        2. Récupérer ses lacunes (avec priorité)
        3. Filtrer : exclure le demandeur, les profils sans compétence sur les matières cherchées
        4. Pour chaque candidat, calculer le score sur 100
        5. Trier par score décroissant
    """

    # ── 1. Profil du demandeur ───────────────────────────────────────────────
    demandeur_profile = Profile.query.filter_by(user_id=current_user_id).first()
    if not demandeur_profile:
        return []

    # ── 2. Lacunes du demandeur ──────────────────────────────────────────────
    lacunes_query = ProfilLacune.query.filter_by(profile_id=demandeur_profile.id)

    # Filtre optionnel sur une matière précise (vient de ?matiere_id=X dans la route)
    if matiere_id:
        lacunes_query = lacunes_query.filter_by(matiere_id=matiere_id)

    mes_lacunes = lacunes_query.all()

    if not mes_lacunes:
        return []

    # Dict : matiere_id → priorité de la lacune
    lacunes_dict = {l.matiere_id: l.priorite for l in mes_lacunes}
    matiere_ids_cherchees = set(lacunes_dict.keys())

    # ── 3. Créneaux du demandeur ─────────────────────────────────────────────
    mes_dispos = Disponible.query.filter_by(profile_id=demandeur_profile.id).all()
    mes_slots  = {(d.jour, d.creneau) for d in mes_dispos}

    # ── 4. Candidats potentiels ──────────────────────────────────────────────
    # Filtrage initial : tous les profils sauf le demandeur
    candidates = Profile.query.filter(
        Profile.user_id != current_user_id
    ).all()

    resultats = []

    for candidate in candidates:

        # ── Compétences du candidat sur les matières cherchées ───────────────
        competences_candidates = ProfilCompetence.query.filter(
            ProfilCompetence.profile_id == candidate.id,
            ProfilCompetence.matiere_id.in_(matiere_ids_cherchees),
            ProfilCompetence.is_available_to_help == True
        ).all()

        # Filtre : éliminer les candidats sans compétence sur aucune matière cherchée
        if not competences_candidates:
            continue

        # ── CRITÈRE 1 — Correspondance matière (35 pts) ──────────────────────
        nb_matieres_cherchees = len(matiere_ids_cherchees)
        nb_matieres_matchees  = len(competences_candidates)
        score_matiere = round(35 * (nb_matieres_matchees / nb_matieres_cherchees), 2)

        # ── CRITÈRE 2 — Niveau compétence ↔ gravité lacune (20 pts) ──────────
        # Pour chaque matière matchée, on compare le niveau du candidat
        # à la priorité de la lacune du demandeur, puis on fait la moyenne
        scores_niveau = []
        matched_subjects = []

        for comp in competences_candidates:
            priorite_lacune = lacunes_dict.get(comp.matiere_id, 'Moyenne')
            s = _score_niveau_vs_gravite(comp.niveau, priorite_lacune)
            scores_niveau.append(s)

            # Récupérer le nom de la matière pour l'explication
            matiere_obj = db.session.get(Matiere, comp.matiere_id)
            if matiere_obj:
                matched_subjects.append({
                    "matiere_id":        comp.matiere_id,
                    "nom":               matiere_obj.nom,
                    "niveau_competence": comp.niveau,
                    "priorite_lacune":   priorite_lacune
                })

        score_niveau = round(sum(scores_niveau) / len(scores_niveau), 2) if scores_niveau else 0

        # ── CRITÈRE 3 — Disponibilités communes (25 pts) ────────────────────
        candidate_dispos = Disponible.query.filter_by(profile_id=candidate.id).all()
        candidate_slots  = {(d.jour, d.creneau) for d in candidate_dispos}
        shared_slots     = mes_slots.intersection(candidate_slots)
        score_dispos     = _score_disponibilites(mes_slots, candidate_slots)

        # ── CRITÈRE 4 — Même année académique (10 pts) ───────────────────────
        same_niveau  = demandeur_profile.niveau == candidate.niveau
        score_niveau_acad = 10 if same_niveau else 0

        # ── CRITÈRE 5 — Même filière (10 pts) ───────────────────────────────
        same_filiere  = demandeur_profile.filiere == candidate.filiere
        score_filiere = 10 if same_filiere else 0

        # ── BONUS — Même format d'apprentissage (10 pts) ────────────────
        same_format = demandeur_profile.format_preference == candidate.format_preference
        score_format = _score_format_bonus(demandeur_profile.format_preference, candidate.format_preference)

        # ── SCORE TOTAL ──────────────────────────────────────────────────────
        total_score = round(
            min(100.0, score_matiere + score_niveau + score_dispos + score_niveau_acad + score_filiere + score_format),
            2
        )

        # ── EXPLICATION (Section 9 du PDF) ──────────────────────────────────
        explication = _build_explanation(
            matched_subjects=matched_subjects,
            shared_slots_count=len(shared_slots),
            same_filiere=same_filiere,
            same_niveau=same_niveau,
            same_format=same_format,
            score=total_score
        )

        # ── Récupérer le user_id du candidat ────────────────────────────────
        candidate_user = db.session.get(User, candidate.user_id)
        if not candidate_user:
            continue

        resultats.append({
            "student_id":      candidate_user.id,
            "profile_id":      candidate.id,
            "nom":             candidate.nom,
            "prenom":          candidate.prenom,
            "filiere":         candidate.filiere,
            "niveau":          candidate.niveau,
            "avatar_url":      candidate.avatar_url,
            "score":           total_score,
            "matched_subjects": matched_subjects,
            "explication":     explication,
            # Détail des sous-scores pour debug / transparence
            "score_detail": {
                "matiere":           score_matiere,
                "niveau_vs_gravite": score_niveau,
                "disponibilites":    score_dispos,
                "meme_niveau":       score_niveau_acad,
                "meme_filiere":      score_filiere,
                "format_preference": score_format
            }
        })

    # ── 5. Tri par score décroissant ─────────────────────────────────────────
    resultats.sort(key=lambda x: x["score"], reverse=True)
    return resultats