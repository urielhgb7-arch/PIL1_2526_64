import sqlite3

conn = sqlite3.connect('instance/dev.db')
cursor = conn.cursor()

# Lister les tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables:")
for t in tables:
    print(f"  - {t[0]}")

# Compter les matières
try:
    cursor.execute("SELECT COUNT(*) FROM matieres")
    count = cursor.fetchone()[0]
    print(f"\n✅ Matières: {count}")
    
    cursor.execute("SELECT id, nom, filiere FROM matieres LIMIT 3")
    samples = cursor.fetchall()
    print("\nSamples:")
    for row in samples:
        print(f"  - {row[1]} ({row[2]})")
except Exception as e:
    print(f"\n❌ Erreur: {e}")

conn.close()
