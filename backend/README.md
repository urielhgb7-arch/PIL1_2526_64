# Projet IFRI MentorLink - Branche Principale (Production)

## Tests locaux

1. Activez l'environnement virtuel du projet :
```bash
cd D:\IFRI-MentorLink\backend
..\ .venv\Scripts\activate
```
2. Installez les dépendances si nécessaire :
```bash
pip install -r requirements.txt
```
3. Exécutez la suite de tests backend :
```bash
python -m pytest -q
```

### Tests ciblés
- `python -m pytest tests/test_backend.py -q`
- `python -m pytest tests/test_offers.py -q`
- `python -m pytest tests/test_sockets.py -q`
