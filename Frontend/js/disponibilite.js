// Rendre chaque cellule cliquable
document.querySelectorAll("table.grille td").forEach(cell => {
  // Ignorer la première colonne (les heures)
  if (cell.cellIndex > 0) {
    cell.addEventListener("click", () => {
      cell.classList.toggle("selected");
    });
  }
});

// Fonction pour sélectionner une plage horaire
function selectRange(start, end) {
  // Parcourir chaque ligne du tableau
  document.querySelectorAll("table.grille tbody tr").forEach(row => {
    const heure = row.querySelector("td:first-child").innerText;

    // Extraire l'heure de début (ex: "08h - 09h" → 8)
    const match = heure.match(/^(\d{2})h/);
    if (match) {
      const hour = parseInt(match[1]);
      if (hour >= start && hour < end) {
        // Sélectionner toutes les cellules de cette ligne (sauf la première)
        row.querySelectorAll("td").forEach((cell, index) => {
          if (index > 0) {
            cell.classList.add("selected");
          }
        });
      }
    }
  });
}

// Bouton pour récupérer les disponibilités
document.getElementById("enregistrer").addEventListener("click", () => {
  const disponibilites = [];

  // Parcourir chaque ligne du tableau
  document.querySelectorAll("table.grille tbody tr").forEach(row => {
    const heure = row.querySelector("td:first-child").innerText;

    row.querySelectorAll("td").forEach((cell, index) => {
      if (index > 0 && cell.classList.contains("selected")) {
        const jour = document.querySelector(`table.grille thead th:nth-child(${index+1})`).innerText;
        disponibilites.push({ jour, heure });
      }
    });
  });

  console.log("Disponibilités sélectionnées :", disponibilites);
  alert("Disponibilités enregistrées (voir console) !");
});
// Bouton précédent
document.getElementById("precedent").addEventListener("click", () => {
  // Exemple : revenir à la page précédente
  window.history.back();
});

// Bouton suivant
document.getElementById("suivant").addEventListener("click", () => {
  // Exemple : aller à la page suivante
  window.location.href = "page_suivante.html";
});
