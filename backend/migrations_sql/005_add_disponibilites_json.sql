-- Ajout de la colonne disponibilites (JSON) aux tables offers et demands
ALTER TABLE offers ADD COLUMN disponibilites TEXT DEFAULT '[]';
ALTER TABLE demands ADD COLUMN disponibilites TEXT DEFAULT '[]';
-- Remplir avec les données existantes (jour/creneau)
UPDATE offers SET disponibilites = CASE
  WHEN jour IS NOT NULL AND creneau IS NOT NULL THEN '[]' ELSE '[]' END;
UPDATE demands SET disponibilites = CASE
  WHEN jour IS NOT NULL AND creneau IS NOT NULL THEN '[]' ELSE '[]' END;
