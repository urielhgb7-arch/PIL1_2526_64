from app.database import db
from app.models.user import User
from app.models.profile import Profile, Disponible
from app.models.services import ProfilCompetence, ProfilLacune, Matiere, Demand, Matching

COMPETENCE_LEVELS = {
    'Débutant':      1,
    'Intermédiaire': 2,
    'Avancé':        3,
    'Expert':        4
}

LACUNE_LEVELS = {
    'Basse':    1,
    'Moyenne':  2,
    'Haute':    3,
    'Urgente':  4
}

def _score_niveau_vs_gravite(niveau_competence: str, priorite_lacune: str) -> float:
    comp_val   = COMPETENCE_LEVELS.get(niveau_competence, 1)
    lacune_val = LACUNE_LEVELS.get(priorite_lacune, 1)
    ratio = comp_val / lacune_val if lacune_val > 0 else 0
    ratio = min(ratio, 1.0)
    return round(ratio * 20, 2)


def _score_disponibilites(demand_slots: set, candidate_slots: set) -> float:
    if not demand_slots:
        return 0.0
    shared = demand_slots.intersection(candidate_slots)
    if not shared:
        return 0.0
    denom = max(len(demand_slots), 1)
    return round(min(len(shared) / denom, 1.0) * 25, 2)


def _score_format_bonus(current_format: str, candidate_format: str) -> float:
    if not current_format or not candidate_format:
        return 0.0
    return 10.0 if current_format == candidate_format else 0.0


def _build_explanation(matched_subjects: list, shared_slots_count: int, same_filiere: bool, same_niveau: bool, same_format: bool, score: float) -> dict:
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
    return {"score_pct": f"{score}%", "raisons": raisons}


def _get_excluded_user_ids(current_user_id: int) -> tuple:
    matchings = Matching.query.filter(
        (Matching.user_one_id == current_user_id) | (Matching.user_two_id == current_user_id)
    ).all()
    blocked = set()
    rejected_set = set()
    for m in matchings:
        other_id = m.user_two_id if m.user_one_id == current_user_id else m.user_one_id
        if m.status in ('pending', 'accepted'):
            blocked.add(other_id)
        elif m.status == 'rejected':
            rejected_set.add(other_id)
    return blocked, rejected_set


def _make_candidate_result(candidate, candidate_user, matched_subjects, shared_slots, same_filiere, same_niveau, same_format, score_matiere, score_niveau, score_dispos, score_niveau_acad, score_filiere, score_format, penalty, total_score):
    explication = _build_explanation(
        matched_subjects=matched_subjects,
        shared_slots_count=len(shared_slots),
        same_filiere=same_filiere,
        same_niveau=same_niveau,
        same_format=same_format,
        score=total_score
    )
    return {
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
        "score_detail": {
            "matiere":           score_matiere,
            "niveau_vs_gravite": score_niveau,
            "disponibilites":    score_dispos,
            "meme_niveau":       score_niveau_acad,
            "meme_filiere":      score_filiere,
            "format_preference": score_format,
            "penalite_rejet":    penalty,
        },
        "rejected_before": penalty < 0
    }


def calculate_matches_demand(current_user_id: int, demand_id: int) -> list:
    demandeur_profile = Profile.query.filter_by(user_id=current_user_id).first()
    if not demandeur_profile:
        return []

    demande = db.session.get(Demand, demand_id)
    if not demande or demande.profile.user_id != current_user_id:
        return []

    matiere_id = demande.matiere_id
    demand_slot = (demande.jour, demande.creneau)

    blocked_ids, rejected_ids = _get_excluded_user_ids(current_user_id)

    # Tous les profils avec au moins une competence (sans filtrer par matiere)
    candidates = db.session.query(Profile).join(
        ProfilCompetence, ProfilCompetence.profile_id == Profile.id
    ).filter(
        Profile.user_id != current_user_id,
        ProfilCompetence.is_available_to_help == True
    ).distinct().all()

    matiere_obj = db.session.get(Matiere, matiere_id)
    lacune = ProfilLacune.query.filter_by(
        profile_id=demandeur_profile.id, matiere_id=matiere_id
    ).first()

    # Recuperer tous les creneaux de la demande (disponibilites JSON + jour/creneau)
    demand_slots = set()
    if demande.disponibilites and isinstance(demande.disponibilites, list):
        for slot in demande.disponibilites:
            if isinstance(slot, dict) and "jour" in slot and "creneau" in slot:
                demand_slots.add((slot["jour"], slot["creneau"]))
            elif isinstance(slot, list) and len(slot) == 2:
                demand_slots.add((slot[0], slot[1]))
    if demande.jour and demande.creneau:
        demand_slots.add(demand_slot)
    if not demand_slots:
        demand_slots.add(demand_slot)

    resultats = []
    for candidate in candidates:
        if candidate.user_id in blocked_ids:
            continue

        candidate_user = db.session.get(User, candidate.user_id)
        if not candidate_user:
            continue

        # Verifier si le candidat a la competence dans la matiere de la demande
        comp = ProfilCompetence.query.filter_by(
            profile_id=candidate.id, matiere_id=matiere_id, is_available_to_help=True
        ).first()

        if comp:
            score_matiere = 35.0
            score_niveau = _score_niveau_vs_gravite(
                comp.niveau if comp else 'Intermédiaire',
                lacune.priorite if lacune else 'Moyenne'
            )
            matched_subjects = []
            if matiere_obj:
                matched_subjects.append({
                    "matiere_id": matiere_id,
                    "nom": matiere_obj.nom,
                    "niveau_competence": comp.niveau if comp else 'Intermédiaire',
                    "priorite_lacune": lacune.priorite if lacune else 'Moyenne'
                })
        else:
            # Verifier si le candidat a d'autres competences (pas la matiere demande)
            autres_comp = ProfilCompetence.query.filter(
                ProfilCompetence.profile_id == candidate.id,
                ProfilCompetence.is_available_to_help == True,
                ProfilCompetence.matiere_id != matiere_id
            ).first()
            if not autres_comp:
                continue  # Aucune competence utile
            score_matiere = 10.0
            score_niveau = 0.0
            matched_subjects = []

        # Disponibilites : creneaux du candidat
        candidate_dispos = Disponible.query.filter_by(profile_id=candidate.id, is_reserved=False).all()
        candidate_slots = {(d.jour, d.creneau) for d in candidate_dispos}

        shared_slots = demand_slots.intersection(candidate_slots)
        score_dispos = _score_disponibilites(demand_slots, candidate_slots) if shared_slots else 0

        same_niveau = demandeur_profile.niveau == candidate.niveau
        score_niveau_acad = 10 if same_niveau else 0

        same_filiere = demandeur_profile.filiere == candidate.filiere
        score_filiere = 10 if same_filiere else 0

        same_format = demandeur_profile.format_preference == candidate.format_preference
        score_format = _score_format_bonus(demandeur_profile.format_preference, candidate.format_preference)

        penalty = -5 if candidate.user_id in rejected_ids else 0

        total_score = round(min(100.0, score_matiere + score_niveau + score_dispos + score_niveau_acad + score_filiere + score_format + penalty), 2)

        resultats.append(_make_candidate_result(
            candidate, candidate_user, matched_subjects, shared_slots,
            same_filiere, same_niveau, same_format,
            score_matiere, score_niveau, score_dispos,
            score_niveau_acad, score_filiere, score_format,
            penalty, total_score
        ))

    resultats.sort(key=lambda x: x["score"], reverse=True)
    return resultats


def calculate_matches_general(current_user_id: int, matiere_id: int = None) -> list:
    demandeur_profile = Profile.query.filter_by(user_id=current_user_id).first()
    if not demandeur_profile:
        return []

    lacunes_query = ProfilLacune.query.filter_by(profile_id=demandeur_profile.id)
    if matiere_id:
        lacunes_query = lacunes_query.filter_by(matiere_id=matiere_id)

    mes_lacunes = lacunes_query.all()
    if not mes_lacunes:
        return []

    lacunes_dict = {l.matiere_id: l.priorite for l in mes_lacunes}
    matiere_ids_cherchees = set(lacunes_dict.keys())

    mes_dispos = Disponible.query.filter_by(profile_id=demandeur_profile.id, is_reserved=False).all()
    mes_slots = {(d.jour, d.creneau) for d in mes_dispos}

    blocked_ids, rejected_ids = _get_excluded_user_ids(current_user_id)

    candidates = Profile.query.filter(Profile.user_id != current_user_id).all()

    resultats = []
    for candidate in candidates:
        if candidate.user_id in blocked_ids:
            continue

        competences_candidates = ProfilCompetence.query.filter(
            ProfilCompetence.profile_id == candidate.id,
            ProfilCompetence.matiere_id.in_(matiere_ids_cherchees),
            ProfilCompetence.is_available_to_help == True
        ).all()
        if not competences_candidates:
            continue

        nb_matieres_cherchees = len(matiere_ids_cherchees)
        nb_matieres_matchees = len(competences_candidates)
        score_matiere = round(35 * (nb_matieres_matchees / nb_matieres_cherchees), 2)

        scores_niveau = []
        matched_subjects = []
        for comp in competences_candidates:
            priorite_lacune = lacunes_dict.get(comp.matiere_id, 'Moyenne')
            s = _score_niveau_vs_gravite(comp.niveau, priorite_lacune)
            scores_niveau.append(s)
            matiere_obj = db.session.get(Matiere, comp.matiere_id)
            if matiere_obj:
                matched_subjects.append({
                    "matiere_id": comp.matiere_id,
                    "nom": matiere_obj.nom,
                    "niveau_competence": comp.niveau,
                    "priorite_lacune": priorite_lacune
                })

        score_niveau = round(sum(scores_niveau) / len(scores_niveau), 2) if scores_niveau else 0

        candidate_dispos = Disponible.query.filter_by(profile_id=candidate.id, is_reserved=False).all()
        candidate_slots = {(d.jour, d.creneau) for d in candidate_dispos}

        shared_slots = mes_slots.intersection(candidate_slots)
        score_dispos = _score_disponibilites(mes_slots, candidate_slots) if shared_slots else 0

        same_niveau = demandeur_profile.niveau == candidate.niveau
        score_niveau_acad = 10 if same_niveau else 0

        same_filiere = demandeur_profile.filiere == candidate.filiere
        score_filiere = 10 if same_filiere else 0

        same_format = demandeur_profile.format_preference == candidate.format_preference
        score_format = _score_format_bonus(demandeur_profile.format_preference, candidate.format_preference)

        penalty = -5 if candidate.user_id in rejected_ids else 0

        total_score = round(
            min(100.0, score_matiere + score_niveau + score_dispos + score_niveau_acad + score_filiere + score_format + penalty),
            2
        )

        candidate_user = db.session.get(User, candidate.user_id)
        if not candidate_user:
            continue

        resultats.append(_make_candidate_result(
            candidate, candidate_user, matched_subjects, shared_slots,
            same_filiere, same_niveau, same_format,
            score_matiere, score_niveau, score_dispos,
            score_niveau_acad, score_filiere, score_format,
            penalty, total_score
        ))

    resultats.sort(key=lambda x: x["score"], reverse=True)
    return resultats


def calculate_matches(current_user_id: int, matiere_id: int = None, demand_id: int = None) -> list:
    if demand_id:
        return calculate_matches_demand(current_user_id, demand_id)
    return calculate_matches_general(current_user_id, matiere_id)
