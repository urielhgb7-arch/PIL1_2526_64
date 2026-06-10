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

SCORE_MINIMUM = 55
MAX_RESULTS = 50


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
            if m.initiator_id == current_user_id:
                blocked.add(other_id)
            else:
                rejected_set.add(other_id)
    return blocked, rejected_set


def _make_candidate_result(candidate, candidate_user, matched_subjects, shared_slots, same_filiere, same_niveau, same_format, score_matiere, score_niveau, score_dispos, score_niveau_acad, score_filiere, score_format, penalty, total_score, competences_list=None):
    explication = _build_explanation(
        matched_subjects=matched_subjects,
        shared_slots_count=len(shared_slots),
        same_filiere=same_filiere,
        same_niveau=same_niveau,
        same_format=same_format,
        score=total_score
    )

    matiere_id = matched_subjects[0]["matiere_id"] if matched_subjects else None

    return {
        "student_id":      candidate_user.id,
        "profile_id":      candidate.id,
        "matiere_id":      matiere_id,
        "nom":             candidate.nom,
        "prenom":          candidate.prenom,
        "filiere":         candidate.filiere,
        "niveau":          candidate.niveau,
        "avatar_url":      candidate.avatar_url,
        "bio":             candidate.bio,
        "format_preference": candidate.format_preference,
        "score":           total_score,
        "matched_subjects": matched_subjects,
        "competences":     competences_list or [],
        "shared_slots":    [{"jour": s[0], "creneau": s[1]} for s in shared_slots],
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


def _limit_results(resultats: list) -> list:
    resultats.sort(key=lambda x: x["score"], reverse=True)
    resultats = [r for r in resultats if r["score"] >= SCORE_MINIMUM]
    return resultats[:MAX_RESULTS]


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

    candidates = db.session.query(Profile).join(
        ProfilCompetence, ProfilCompetence.profile_id == Profile.id
    ).filter(
        Profile.user_id != current_user_id,
        ProfilCompetence.is_available_to_help == True
    ).distinct().all()

    matiere_obj = db.session.get(Matiere, matiere_id)
    matieres_map = {m.id: m.nom for m in Matiere.query.all()}
    lacune = ProfilLacune.query.filter_by(
        profile_id=demandeur_profile.id, matiere_id=matiere_id
    ).first()

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

    if not candidates:
        return []

    # ── Pre-load en masse (3 requêtes au lieu de 3N) ──
    candidate_ids = [c.id for c in candidates]
    candidate_user_ids = [c.user_id for c in candidates]

    users_map = {u.id: u for u in User.query.filter(User.id.in_(candidate_user_ids)).all()}

    comps_map = {}
    for c in ProfilCompetence.query.filter(
        ProfilCompetence.profile_id.in_(candidate_ids),
        ProfilCompetence.matiere_id == matiere_id,
        ProfilCompetence.is_available_to_help == True
    ).all():
        comps_map[c.profile_id] = c

    autres_comps_map = set()
    for c in ProfilCompetence.query.filter(
        ProfilCompetence.profile_id.in_(candidate_ids),
        ProfilCompetence.is_available_to_help == True,
        ProfilCompetence.matiere_id != matiere_id
    ).all():
        autres_comps_map.add(c.profile_id)

    # Pré-chargement de toutes les compétences pour chaque candidat
    all_candidate_comps = {}
    for c in ProfilCompetence.query.filter(
        ProfilCompetence.profile_id.in_(candidate_ids),
        ProfilCompetence.is_available_to_help == True
    ).all():
        all_candidate_comps.setdefault(c.profile_id, []).append(c)

    dispos_map = {}
    for d in Disponible.query.filter(
        Disponible.profile_id.in_(candidate_ids),
        Disponible.is_reserved == False
    ).all():
        dispos_map.setdefault(d.profile_id, []).append(d)

    # ── Boucle principale (0 requête DB) ──
    resultats = []
    for candidate in candidates:
        if candidate.user_id in blocked_ids:
            continue

        candidate_user = users_map.get(candidate.user_id)
        if not candidate_user:
            continue

        comp = comps_map.get(candidate.id)

        if comp:
            score_matiere = 35.0
            score_niveau = _score_niveau_vs_gravite(
                comp.niveau, lacune.priorite if lacune else 'Moyenne'
            )
            matched_subjects = []
            if matiere_obj:
                matched_subjects.append({
                    "matiere_id": matiere_id,
                    "nom": matiere_obj.nom,
                    "niveau_competence": comp.niveau,
                    "priorite_lacune": lacune.priorite if lacune else 'Moyenne'
                })
        else:
            if candidate.id not in autres_comps_map:
                continue
            score_matiere = 10.0
            score_niveau = 0.0
            matched_subjects = []

        candidate_dispos = dispos_map.get(candidate.id) or []
        candidate_slots = {(d.jour, d.creneau) for d in candidate_dispos}

        shared_slots = demand_slots.intersection(candidate_slots)
        if not shared_slots:
            continue
        score_dispos = _score_disponibilites(demand_slots, candidate_slots)

        same_niveau = demandeur_profile.niveau == candidate.niveau
        score_niveau_acad = 10 if same_niveau else 0

        same_filiere = demandeur_profile.filiere == candidate.filiere
        score_filiere = 10 if same_filiere else 0

        same_format = demandeur_profile.format_preference == candidate.format_preference
        score_format = _score_format_bonus(demandeur_profile.format_preference, candidate.format_preference)

        penalty = -5 if candidate.user_id in rejected_ids else 0

        total_score = round(min(100.0, score_matiere + score_niveau + score_dispos + score_niveau_acad + score_filiere + score_format + penalty), 2)

        candidate_comps = all_candidate_comps.get(candidate.id, [])
        competences_list = [{"matiere_id": c.matiere_id, "nom": matieres_map.get(c.matiere_id, ""), "niveau": c.niveau} for c in candidate_comps]

        resultats.append(_make_candidate_result(
            candidate, candidate_user, matched_subjects, shared_slots,
            same_filiere, same_niveau, same_format,
            score_matiere, score_niveau, score_dispos,
            score_niveau_acad, score_filiere, score_format,
            penalty, total_score, competences_list
        ))

    return _limit_results(resultats)


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

    if not candidates:
        return []

    # ── Pre-load en masse ──
    candidate_ids = [c.id for c in candidates]
    candidate_user_ids = [c.user_id for c in candidates]

    users_map = {u.id: u for u in User.query.filter(User.id.in_(candidate_user_ids)).all()}

    competences_map = {}
    for comp in ProfilCompetence.query.filter(
        ProfilCompetence.profile_id.in_(candidate_ids),
        ProfilCompetence.matiere_id.in_(matiere_ids_cherchees),
        ProfilCompetence.is_available_to_help == True
    ).all():
        competences_map.setdefault(comp.profile_id, []).append(comp)

    dispos_map = {}
    for d in Disponible.query.filter(
        Disponible.profile_id.in_(candidate_ids),
        Disponible.is_reserved == False
    ).all():
        dispos_map.setdefault(d.profile_id, []).append(d)

    matieres_map = {m.id: m for m in Matiere.query.all()}

    # Pré-chargement de toutes les compétences pour chaque candidat
    all_candidate_comps = {}
    for c in ProfilCompetence.query.filter(
        ProfilCompetence.profile_id.in_(candidate_ids),
        ProfilCompetence.is_available_to_help == True
    ).all():
        all_candidate_comps.setdefault(c.profile_id, []).append(c)

    # ── Boucle principale (0 requête DB) ──
    resultats = []
    for candidate in candidates:
        if candidate.user_id in blocked_ids:
            continue

        competences_candidates = competences_map.get(candidate.id) or []
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
            matiere_obj = matieres_map.get(comp.matiere_id)
            if matiere_obj:
                matched_subjects.append({
                    "matiere_id": comp.matiere_id,
                    "nom": matiere_obj.nom,
                    "niveau_competence": comp.niveau,
                    "priorite_lacune": priorite_lacune
                })

        score_niveau = round(sum(scores_niveau) / len(scores_niveau), 2) if scores_niveau else 0

        candidate_dispos = dispos_map.get(candidate.id) or []
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

        candidate_user = users_map.get(candidate.user_id)
        if not candidate_user:
            continue

        candidate_comps = all_candidate_comps.get(candidate.id, [])
        competences_list = [{"matiere_id": c.matiere_id, "nom": matieres_map.get(c.matiere_id).nom if matieres_map.get(c.matiere_id) else "", "niveau": c.niveau} for c in candidate_comps]

        resultats.append(_make_candidate_result(
            candidate, candidate_user, matched_subjects, shared_slots,
            same_filiere, same_niveau, same_format,
            score_matiere, score_niveau, score_dispos,
            score_niveau_acad, score_filiere, score_format,
            penalty, total_score, competences_list
        ))

    return _limit_results(resultats)


def calculate_matches(current_user_id: int, matiere_id: int = None, demand_id: int = None) -> list:
    if demand_id:
        return calculate_matches_demand(current_user_id, demand_id)
    return calculate_matches_general(current_user_id, matiere_id)