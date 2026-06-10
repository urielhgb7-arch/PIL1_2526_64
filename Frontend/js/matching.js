
    const mentors = [
      {
        name: "Aïcha D.", initials: "AD", role: "GL · L3", match: "98%",
        about: "Peut aider avec les algorithmes récursifs complexes, la programmation dynamique et les révisions d'examens.",
        tags: [
          { cls: "algo", label: "Algorithmique" },
          { cls: "gl",   label: "GL" },
          { cls: "time", label: "Mer. Après-midi" }
        ]
      },
      {
        name: "Kofi M.", initials: "KM", role: "IA · M1", match: "91%",
        about: "Spécialisé en machine learning, réseaux de neurones et traitement du langage naturel.",
        tags: [
          { cls: "algo", label: "Machine Learning" },
          { cls: "gl",   label: "Python" },
          { cls: "time", label: "Lun. Matin" }
        ]
      },
      {
        name: "Fatou S.", initials: "FS", role: "SR · L2", match: "85%",
        about: "Experte en bases de données relationnelles, SQL avancé et modélisation UML.",
        tags: [
          { cls: "gl",   label: "SQL" },
          { cls: "info", label: "UML" },
          { cls: "time", label: "Ven. Soir" }
        ]
      },
      {
        name: "Driss A.", initials: "DA", role: "GL · M2", match: "79%",
        about: "Maîtrise des architectures distribuées, Docker, Kubernetes et pipelines CI/CD.",
        tags: [
          { cls: "time", label: "DevOps" },
          { cls: "gl",   label: "Docker" },
          { cls: "algo", label: "Mar. Midi" }
        ]
      }
    ];

    let currentIndex = 0;

    function swipe(direction) {
      const card = document.getElementById('card');

      // animate out
      card.classList.add(direction === 'like' ? 'swipe-right' : 'swipe-left');

      setTimeout(() => {
        // advance to next mentor
        currentIndex = (currentIndex + 1) % mentors.length;
        renderCard(mentors[currentIndex]);

        // reset & animate in
        card.classList.remove('swipe-right', 'swipe-left', 'pop-in');
        void card.offsetWidth; // reflow
        card.classList.add('pop-in');
      }, 280);
    }

    function renderCard(mentor) {
      document.getElementById('avatar').textContent       = mentor.initials;
      document.getElementById('mentor-name').textContent  = mentor.name;
      document.getElementById('mentor-role').textContent  = mentor.role;
      document.getElementById('match-badge').textContent  = mentor.match + ' Match';
      document.getElementById('about').textContent        = mentor.about;

      const tagsEl = document.getElementById('tags');
      tagsEl.innerHTML = mentor.tags
        .map(t => `<span class="tag ${t.cls}">${t.label}</span>`)
        .join('');
    }
  