"""Seed 10 utilisateurs de test avec profils, compétences et lacunes."""
import os, sys, random
from pathlib import Path

# Force dev mode + fournit les clés pour éviter les erreurs de config
os.environ.setdefault('FLASK_ENV', 'development')
os.environ.setdefault('SECRET_KEY', 'dev-secret-key-for-testing-12345')
os.environ.setdefault('JWT_SECRET_KEY', 'super-secret-key-for-testing-12345')

base_dir = Path(__file__).resolve().parent
env_file = base_dir / '.env.local'
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(env_file)

from app import create_app
from app.database import db
from sqlalchemy import text
from app.models import User, Profile, Matiere, ProfilCompetence, ProfilLacune, Disponible

app = create_app()

with app.app_context():
    # S'assurer que la colonne email_verified existe (déploiement local)
    try:
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        cols = [c['name'] for c in inspector.get_columns('users')]
        if 'email_verified' not in cols:
            db.session.execute(text("ALTER TABLE users ADD COLUMN email_verified BOOLEAN NOT NULL DEFAULT FALSE"))
            db.session.commit()
            print("Colonne email_verified ajoutée à users")
    except Exception as e:
        db.session.rollback()
        print(f"Note: {e}")

    # Nettoyer les anciens utilisateurs test (optionnel)
    test_emails = [f'user{i}@test.ifri.edu' for i in range(1, 11)]
    existing = User.query.filter(User.email.in_(test_emails)).all()
    for u in existing:
        db.session.delete(u)
    db.session.commit()
    print("Anciens utilisateurs test supprimés")

    # Récupérer les matières disponibles
    matieres = {m.nom: m for m in Matiere.query.all()}
    if not matieres:
        print("ERREUR: Aucune matière trouvée. Lancez d'abord seed_matieres.py")
        sys.exit(1)

    print(f"{len(matieres)} matières disponibles")

    # Données des 10 utilisateurs
    users_data = [
        # (email, password, nom, prenom, filiere, niveau, bio, role,
        #  competences_noms, lacunes_noms, dispos)
        ("user1@test.ifri.edu", "pass1234", "Koffi", "Jean", "GL", "L3",
         "Étudiant en L3 GL, passionné de développement web et mobile. Disponible pour du tutorat.",
         "student",
         ["Web Development", "Programmation Orientée Objet", "Base de données SQL"],
         ["Génie logiciel", "Intelligence artificielle"],
         [("Lundi", "14-15"), ("Mercredi", "10-11"), ("Vendredi", "15-16")]),

         ("user2@test.ifri.edu", "pass1234", "Sossa", "Marie", "GL", "M1",
          "Étudiante en Master GL, spécialisée en Machine Learning et IA. Mentor expérimentée.",
          "student",
          ["Machine Learning", "Intelligence artificielle", "Algorithmique", "Python"],
          ["Big Data", "Cloud Computing"],
          [("Mardi", "09-10"), ("Jeudi", "14-15"), ("Samedi", "10-11")]),

         ("user3@test.ifri.edu", "pass1234", "Assogba", "David", "RSI", "L2",
          "Étudiant RSI, passionné par les réseaux et la cybersécurité.",
          "student",
          ["Réseaux informatiques", "Administration système"],
          ["Sécurité des réseaux", "Télécommunications", "Cloud Computing"],
          [("Lundi", "10-11"), ("Mercredi", "14-15"), ("Vendredi", "09-10")]),

         ("user4@test.ifri.edu", "pass1234", "Hounkpe", "Sarah", "Sécurité", "L3",
          "Étudiante en sécurité, passionnée par la cybersécurité et le pentesting.",
          "student",
          ["Sécurité web", "Cryptographie", "Sécurité des applications"],
          ["Cyberdéfense", "Ethical Hacking"],
          [("Mardi", "11-12"), ("Jeudi", "15-16"), ("Samedi", "14-15")]),

         ("user5@test.ifri.edu", "pass1234", "Tossa", "Paul", "GL", "M2",
          "Étudiant en Master 2 GL, expert en gestion de projet et développement full-stack.",
          "student",
          ["Gestion de projet informatique", "Cloud Computing", "Web Development", "Base de données SQL"],
          ["Intelligence artificielle", "Big Data"],
          [("Lundi", "09-10"), ("Jeudi", "10-11"), ("Vendredi", "14-15")]),

         ("user6@test.ifri.edu", "pass1234", "Dossa", "Alice", "RSI", "M1",
          "Étudiante en Master RSI, spécialisée en Big Data et Cloud. Mentor expérimentée.",
          "student",
          ["Big Data", "Cloud Computing", "Base de données SQL", "Administration système"],
          ["Machine Learning", "Sécurité des réseaux"],
          [("Mardi", "14-15"), ("Mercredi", "09-10"), ("Samedi", "09-10")]),

         ("user7@test.ifri.edu", "pass1234", "Gbaguidi", "Ernest", "GL", "L1",
          "Nouvel étudiant en L1 GL, motivé à apprendre et à progresser.",
          "student",
          ["Algorithmique"],
          ["Programmation Orientée Objet", "Base de données SQL", "Structures de données", "Web Development"],
          [("Lundi", "15-16"), ("Mercredi", "14-15"), ("Vendredi", "10-11")]),

         ("user8@test.ifri.edu", "pass1234", "Adanle", "Bénédicte", "Sécurité", "M2",
          "Étudiante en Master Sécurité, spécialisée en audit et cybersécurité. Mentor expérimentée.",
          "student",
          ["Cyberdéfense", "Ethical Hacking", "Audit de sécurité", "Sécurité web", "Cryptographie"],
          ["Machine Learning"],
          [("Mardi", "10-11"), ("Jeudi", "09-10"), ("Samedi", "11-12")]),

         ("user9@test.ifri.edu", "pass1234", "Hountondji", "Franck", "GL", "L2",
          "Étudiant en L2 GL, bonne base en programmation. Cherche à progresser.",
          "student",
          ["Programmation Orientée Objet", "Algorithmique", "Structures de données"],
          ["Génie logiciel", "Base de données SQL", "Web Development"],
          [("Lundi", "11-12"), ("Mercredi", "15-16"), ("Vendredi", "10-11")]),

         ("user10@test.ifri.edu", "pass1234", "Zinsou", "Grace", "GL", "L3",
          "Étudiante en L3 GL, passionnée par le développement mobile et l'IA.",
          "student",
          ["Développement mobile", "Intelligence artificielle", "Web Development"],
          ["Génie logiciel", "Machine Learning", "Cloud Computing"],
          [("Mardi", "15-16"), ("Jeudi", "11-12"), ("Samedi", "09-10")]),
    ]

    created = []
    for email, pwd, nom, prenom, filiere, niveau, bio, role, comps, lacs, dispos in users_data:
        user = User(email=email, role=role, email_verified=True)
        user.set_password(pwd)
        db.session.add(user)
        db.session.flush()

        tel = f"+229{random.randint(60000000, 99999999)}"
        profile = Profile(
            user_id=user.id, nom=nom, prenom=prenom,
            filiere=filiere, niveau=niveau, bio=bio,
            telephone=tel, format_preference=random.choice(["Présentiel", "Distanciel", "Hybride"]),
        )
        db.session.add(profile)
        db.session.flush()

        # Compétences
        for cnom in comps:
            m = matieres.get(cnom)
            if m:
                db.session.add(ProfilCompetence(
                    profile_id=profile.id, matiere_id=m.id,
                    niveau=random.choice(["Débutant", "Intermédiaire", "Avancé", "Expert"]),
                    is_available_to_help=True
                ))
            else:
                print(f"  Matière introuvable pour compétence: {cnom}")

        # Lacunes
        for lnom in lacs:
            m = matieres.get(lnom)
            if m:
                db.session.add(ProfilLacune(
                    profile_id=profile.id, matiere_id=m.id,
                    priorite=random.choice(["Basse", "Moyenne", "Haute"])
                ))
            else:
                print(f"  Matière introuvable pour lacune: {lnom}")

        # Disponibilités
        for jour, creneau in dispos:
            db.session.add(Disponible(profile_id=profile.id, jour=jour, creneau=creneau))

        created.append((email, nom, prenom, filiere, niveau))

    db.session.commit()
    print(f"\n✅ {len(created)} utilisateurs créés :\n")
    print(f"{'Email':30} {'Nom':15} {'Prénom':15} {'Filière':10} {'Niveau':6}")
    print("-" * 80)
    for e, n, p, f, lvl in created:
        print(f"{e:30} {n:15} {p:15} {f:10} {lvl:6}")
    print("\n🔑 Mot de passe pour tous : pass1234")
