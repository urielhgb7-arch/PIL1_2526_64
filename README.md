
      overflow-x: hidden;
    }

    /* ─── BACKGROUND GRID ─── */
    body::before {
      content: '';
      position: fixed; inset: 0;
      background-image:
        linear-gradient(rgba(0,194,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,194,255,0.03) 1px, transparent 1px);
      background-size: 40px 40px;
      pointer-events: none;
      z-index: 0;
    }

    /* ─── NAV ─── */
    nav {
      position: fixed; top: 0; left: 0; right: 0; z-index: 100;
      display: flex; align-items: center; justify-content: space-between;
      padding: 1rem 2.5rem;
      background: rgba(5,8,15,0.9);
      backdrop-filter: blur(16px);
      border-bottom: 1px solid rgba(0,194,255,0.12);
    }
    .nav-logo {
      font-family: var(--heading);
      font-weight: 800; font-size: 1.15rem;
      background: linear-gradient(135deg, var(--blue), var(--gold));
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
      background-clip: text;
    }
    .nav-links { display: flex; gap: 2rem; list-style: none; }
    .nav-links a {
      color: var(--muted); text-decoration: none;
      font-size: 0.78rem; font-weight: 600;
      letter-spacing: 0.1em; text-transform: uppercase;
      transition: color 0.2s;
    }
    .nav-links a:hover { color: var(--blue); }

    /* ─── HERO ─── */
    .hero {
      min-height: 100vh;
      display: flex; flex-direction: column; justify-content: center;
      padding: 8rem 2.5rem 4rem;
      position: relative; overflow: hidden;
    }
    .hero-orb1 {
      position: absolute; top: -150px; right: -100px;
      width: 600px; height: 600px;
      background: radial-gradient(circle, rgba(0,194,255,0.13) 0%, transparent 65%);
      pointer-events: none;
    }
    .hero-orb2 {
      position: absolute; bottom: -100px; left: -100px;
      width: 500px; height: 500px;
      background: radial-gradient(circle, rgba(240,180,41,0.1) 0%, transparent 65%);
      pointer-events: none;
    }
    .hero-orb3 {
      position: absolute; top: 40%; left: 40%;
      width: 300px; height: 300px;
      background: radial-gradient(circle, rgba(0,229,160,0.07) 0%, transparent 65%);
      pointer-events: none;
    }
    .hero-tag {
      display: inline-flex; align-items: center; gap: 0.6rem;
      background: rgba(0,194,255,0.08);
      border: 1px solid rgba(0,194,255,0.25);
      border-radius: 100px;
      padding: 0.4rem 1.1rem;
      font-size: 0.72rem; font-weight: 700;
      color: var(--blue);
      letter-spacing: 0.1em; text-transform: uppercase;
      margin-bottom: 2rem; width: fit-content;
      animation: fadeUp 0.6s ease both;
    }
    .hero-tag::before {
      content: '';
      width: 7px; height: 7px;
      background: var(--green); border-radius: 50%;
      animation: pulse 2s infinite;
      box-shadow: 0 0 6px var(--green);
    }
    @keyframes pulse {
      0%,100% { opacity:1; transform:scale(1); }
      50%      { opacity:.4; transform:scale(.7); }
    }
    h1 {
      font-family: var(--heading);
      font-size: clamp(4rem, 9vw, 7.5rem);
      font-weight: 800; line-height: 0.95;
      margin-bottom: 2rem;
      letter-spacing: -0.02em;
      animation: fadeUp 0.6s 0.1s ease both;
      filter: drop-shadow(0 0 40px rgba(0,194,255,0.18));
    }
    .h1-line1 {
      color: var(--text);
      text-shadow: 0 0 60px rgba(220,238,255,0.15);
    }
    .h1-line2 {
      background: linear-gradient(100deg, #00c2ff 0%, #00e5a0 60%, #00c2ff 100%);
      background-size: 200% auto;
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
      background-clip: text;
      animation: shimmer 4s linear infinite;
    }
    .h1-line3 {
      background: linear-gradient(100deg, #f0b429 0%, #ff9f43 50%, #ffe066 100%);
      background-size: 200% auto;
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
      background-clip: text;
      animation: shimmer 4s linear infinite reverse;
    }
    @keyframes shimmer {
      0%   { background-position: 0% center; }
      100% { background-position: 200% center; }
    }
    .hero-desc {
      max-width: 580px; color: var(--muted);
      font-size: 1.05rem; font-weight: 400;
      line-height: 1.8; margin-bottom: 3rem;
      animation: fadeUp 0.6s 0.2s ease both;
    }
    .hero-meta {
      display: flex; flex-wrap: wrap; gap: 0;
      border: 1px solid var(--border);
      border-radius: 16px; overflow: hidden;
      width: fit-content;
      animation: fadeUp 0.6s 0.3s ease both;
    }
    .meta-item {
      padding: 1rem 1.5rem;
      border-right: 1px solid var(--border);
      display: flex; flex-direction: column; gap: 0.25rem;
    }
    .meta-item:last-child { border-right: none; }
    .meta-label { font-size: 0.68rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.1em; }
    .meta-value { font-family: var(--heading); font-size: 0.9rem; font-weight: 700; color: var(--text); }

    @keyframes fadeUp {
      from { opacity:0; transform:translateY(28px); }
      to   { opacity:1; transform:translateY(0); }
    }

    /* ─── SECTIONS ─── */
    .section-wrap { position: relative; z-index: 1; }
    section { padding: 5rem 2.5rem; max-width: 1120px; margin: 0 auto; }

    .section-label {
      display: inline-flex; align-items: center; gap: 0.5rem;
      font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.14em;
      color: var(--gold); font-weight: 700; margin-bottom: 0.9rem;
    }
    .section-label::before {
      content: '';
      width: 18px; height: 2px;
      background: var(--gold);
      border-radius: 2px;
    }
    h2 {
      font-family: var(--heading);
      font-size: clamp(1.9rem, 3.8vw, 3rem);
      font-weight: 800; line-height: 1.1;
      margin-bottom: 1rem;
    }
    .section-intro {
      color: var(--muted); max-width: 640px;
      margin-bottom: 3rem; font-weight: 400;
      font-size: 0.97rem;
    }

    /* ─── DIVIDER ─── */
    .divider {
      width: 100%; max-width: 1120px; margin: 0 auto;
      height: 1px;
      background: linear-gradient(90deg, transparent, rgba(0,194,255,0.2), rgba(240,180,41,0.2), transparent);
    }

    /* ─── GROUPE ─── */
    .groupe-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 1rem;
    }
    .membre-card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 1.3rem 1.5rem;
      display: flex; align-items: center; gap: 1.1rem;
      position: relative; overflow: hidden;
      transition: transform 0.25s, border-color 0.25s, box-shadow 0.25s;
    }
    .membre-card::after {
      content: '';
      position: absolute; inset: 0;
      background: linear-gradient(135deg, var(--blue-glow), transparent 60%);
      opacity: 0; transition: opacity 0.25s;
    }
    .membre-card:hover {
      transform: translateY(-3px);
      border-color: rgba(0,194,255,0.35);
      box-shadow: 0 8px 32px rgba(0,194,255,0.1);
    }
    .membre-card:hover::after { opacity: 1; }
    .avatar {
      width: 46px; height: 46px; border-radius: 12px;
      display: flex; align-items: center; justify-content: center;
      font-family: var(--heading); font-weight: 800; font-size: 0.95rem;
      flex-shrink: 0; position: relative; z-index: 1;
    }
    .membre-info { flex: 1; min-width: 0; position: relative; z-index: 1; }
    .membre-nom {
      font-weight: 700; font-size: 0.88rem;
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
      color: var(--text);
    }
    .membre-role { font-size: 0.76rem; color: var(--muted); margin-top: 0.15rem; }
    .filiere-badge {
      font-size: 0.66rem; font-weight: 800;
      padding: 0.22rem 0.6rem; border-radius: 6px;
      letter-spacing: 0.05em;
      flex-shrink: 0; position: relative; z-index: 1;
    }
    .badge-blue  { background:rgba(0,194,255,0.12); color:var(--blue);  border:1px solid rgba(0,194,255,0.25); }
    .badge-gold  { background:rgba(240,180,41,0.12); color:var(--gold);  border:1px solid rgba(240,180,41,0.25); }
    .badge-green { background:rgba(0,229,160,0.12); color:var(--green); border:1px solid rgba(0,229,160,0.25); }

    /* ─── FONCTIONNEMENT ─── */
    .fonct-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
    @media (max-width: 640px) { .fonct-grid { grid-template-columns: 1fr; } }
    .fonct-card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 16px; padding: 1.6rem;
      transition: border-color 0.2s;
    }
    .fonct-card:hover { border-color: rgba(240,180,41,0.3); }
    .fonct-card h3 {
      font-family: var(--heading); font-size: 1rem; font-weight: 700;
      margin-bottom: 1rem;
      display: flex; align-items: center; gap: 0.6rem;
      color: var(--gold);
    }
    .fonct-card ul { list-style: none; }
    .fonct-card ul li {
      font-size: 0.86rem; color: var(--muted);
      padding: 0.38rem 0;
      border-bottom: 1px solid rgba(17,34,64,0.8);
      display: flex; align-items: flex-start; gap: 0.6rem;
    }
    .fonct-card ul li:last-child { border-bottom: none; }
    .fonct-card ul li::before { content:'▸'; color:var(--green); flex-shrink:0; }

    /* ─── TABS ─── */
    .conception-tabs { display:flex; gap:0.5rem; margin-bottom:2rem; flex-wrap:wrap; }
    .tab-btn {
      padding: 0.55rem 1.3rem;
      border-radius: 8px;
      border: 1px solid var(--border);
      background: transparent;
      color: var(--muted);
      font-family: var(--body);
      font-size: 0.82rem; font-weight: 600;
      cursor: pointer; transition: all 0.2s;
    }
    .tab-btn.active {
      background: linear-gradient(135deg, var(--blue), var(--green));
      color: #05080f; border-color: transparent;
      box-shadow: 0 0 20px rgba(0,194,255,0.25);
    }
    .tab-btn:hover:not(.active) { border-color: var(--blue); color: var(--text); }
    .tab-content { display:none; }
    .tab-content.active { display:block; }

    /* ─── DB TABLES ─── */
    .db-tables { display:grid; grid-template-columns:repeat(auto-fill,minmax(230px,1fr)); gap:1rem; }
    .db-table {
      background: var(--surface); border:1px solid var(--border);
      border-radius: 12px; overflow: hidden;
      transition: border-color 0.2s, box-shadow 0.2s;
    }
    .db-table:hover { border-color:rgba(0,194,255,0.3); box-shadow:0 4px 20px rgba(0,194,255,0.08); }
    .db-table-header {
      background: linear-gradient(90deg, rgba(0,194,255,0.1), rgba(0,229,160,0.06));
      border-bottom: 1px solid rgba(0,194,255,0.15);
      padding: 0.75rem 1rem;
      font-family: var(--heading); font-size: 0.85rem; font-weight: 700;
      color: var(--blue);
    }
    .db-table-body { padding: 0.4rem 0; }
    .db-field {
      padding: 0.3rem 1rem;
      font-size: 0.76rem; font-family:'Courier New',monospace;
      display:flex; justify-content:space-between; align-items:center; gap:0.8rem;
    }
    .db-field:hover { background:rgba(0,194,255,0.04); }
    .field-name { color:var(--text); }
    .field-type { color:rgba(240,180,41,0.8); font-size:0.7rem; }
    .field-pk   { color:var(--green); font-size:0.66rem; font-weight:800;
                  background:rgba(0,229,160,0.1); padding:0.1rem 0.4rem; border-radius:4px; }

    /* ─── ARCHITECTURE ─── */
    .arch-layers { display:flex; flex-direction:column; gap:0.8rem; }
    .arch-layer {
      background: var(--surface); border:1px solid var(--border);
      border-radius: 14px; padding:1.3rem 1.6rem;
      display:flex; align-items:center; gap:1.4rem;
      transition: border-color 0.2s;
    }
    .arch-layer:nth-child(1):hover { border-color:rgba(0,194,255,0.35); }
    .arch-layer:nth-child(3):hover { border-color:rgba(240,180,41,0.35); }
    .arch-layer:nth-child(5):hover { border-color:rgba(0,229,160,0.35); }
    .arch-icon {
      width:42px; height:42px; border-radius:10px;
      display:flex; align-items:center; justify-content:center;
      font-size:1.2rem; flex-shrink:0;
    }
    .arch-layer h4 { font-family:var(--heading); font-size:0.95rem; font-weight:700; margin-bottom:0.25rem; }
    .arch-layer p  { font-size:0.82rem; color:var(--muted); }
    .arch-arrow { text-align:center; color:var(--muted); padding:0.1rem 0; font-size:0.85rem; letter-spacing:0.05em; }

    /* ─── TREE ─── */
    .tree {
      background: var(--surface); border:1px solid var(--border);
      border-radius: 14px; padding:1.6rem;
      font-family:'Courier New',monospace; font-size:0.82rem; line-height:2;
    }
    .tree .folder { color:var(--gold); font-weight:bold; }
    .tree .file   { color:var(--muted); }
    .tree .comment{ color:var(--green); font-style:italic; opacity:0.8; }

    /* ─── STEPS ─── */
    .steps { display:flex; flex-direction:column; }
    .step { display:flex; gap:1.5rem; position:relative; }
    .step:not(:last-child)::after {
      content:'';
      position:absolute; left:20px; top:46px;
      width:2px; height:calc(100% - 26px);
      background: linear-gradient(180deg, var(--blue), transparent);
    }
    .step-num {
      width:42px; height:42px; border-radius:50%;
      background: linear-gradient(135deg, rgba(0,194,255,0.15), rgba(0,229,160,0.1));
      border:2px solid var(--blue);
      display:flex; align-items:center; justify-content:center;
      font-family:var(--heading); font-weight:800; font-size:0.9rem;
      color:var(--blue); flex-shrink:0; position:relative; z-index:1;
      box-shadow: 0 0 12px rgba(0,194,255,0.2);
    }
    .step-body { padding-bottom:2.2rem; flex:1; }
    .step-body h4 {
      font-family:var(--heading); font-size:1rem; font-weight:700;
      margin-bottom:0.5rem; padding-top:0.65rem; color:var(--text);
    }
    .step-body p { font-size:0.86rem; color:var(--muted); }
    .code-block {
      background:#020509;
      border:1px solid rgba(0,194,255,0.15);
      border-left:3px solid var(--blue);
      border-radius:10px; padding:1rem 1.2rem; margin-top:0.8rem;
      font-family:'Courier New',monospace; font-size:0.79rem;
      line-height:1.8; overflow-x:auto;
    }
    .code-block .cmd     { color:var(--green); }
    .code-block .comment { color:var(--muted); font-style:italic; }

    /* ─── MANUEL ─── */
    .manuel-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(270px,1fr)); gap:1rem; }
    .manuel-card {
      background:var(--surface); border:1px solid var(--border);
      border-radius:16px; padding:1.6rem;
      transition:transform 0.25s, border-color 0.25s, box-shadow 0.25s;
    }
    .manuel-card:hover {
      transform:translateY(-3px);
      border-color:rgba(0,229,160,0.3);
      box-shadow:0 8px 28px rgba(0,229,160,0.08);
    }
    .manuel-icon {
      width:46px; height:46px; border-radius:12px;
      display:flex; align-items:center; justify-content:center;
      font-size:1.4rem; margin-bottom:1rem;
    }
    .manuel-card h3 { font-family:var(--heading); font-size:0.98rem; font-weight:700; margin-bottom:0.7rem; color:var(--text); }
    .manuel-card ol { padding-left:1.2rem; }
    .manuel-card ol li { font-size:0.84rem; color:var(--muted); padding:0.22rem 0; }

    /* ─── FOOTER ─── */
    footer {
      border-top:1px solid rgba(0,194,255,0.1);
      padding:2.5rem 2.5rem;
      max-width:1120px; margin:0 auto;
      display:flex; justify-content:space-between; align-items:center;
      flex-wrap:wrap; gap:1rem;
      position:relative; z-index:1;
    }
    .footer-left {
      font-family:var(--heading); font-weight:800; font-size:1rem;
      background:linear-gradient(135deg,var(--blue),var(--gold));
      -webkit-background-clip:text; -webkit-text-fill-color:transparent;
      background-clip:text;
    }
    .footer-right { font-size:0.78rem; color:var(--muted); }

    /* ─── RESPONSIVE ─── */
    @media (max-width:768px) {
      nav { padding:1rem 1.2rem; }
      .nav-links { display:none; }
      section { padding:3.5rem 1.2rem; }
      .hero { padding:7rem 1.2rem 3rem; }
      .hero-meta { flex-direction:column; width:100%; }
      .meta-item { border-right:none; border-bottom:1px solid var(--border); }
      .meta-item:last-child { border-bottom:none; }
      footer { padding:2rem 1.2rem; flex-direction:column; align-items:flex-start; }
    }
  </style>
</head>
<body>

<!-- NAV -->
<nav>
  <div class="nav-logo">IFRI_MentorLink</div>
  <ul class="nav-links">
    <li><a href="#groupe">Groupe</a></li>
    <li><a href="#fonctionnement">Méthode</a></li>
    <li><a href="#conception">Conception</a></li>
    <li><a href="#deploiement">Déploiement</a></li>
    <li><a href="#manuel">Manuel</a></li>
  </ul>
</nav>

<!-- HERO -->
<header class="hero">
  <div class="hero-orb1"></div>
  <div class="hero-orb2"></div>
  <div class="hero-orb3"></div>
  <div class="hero-tag">PIL1_2526_64 · Rapport de projet</div>
  <h1>
    <span class="h1-line1">IFRI</span><br>
    <span class="h1-line2">_Mentor</span><span class="h1-line3">Link</span>
  </h1>
  <p class="hero-desc">
    Application web de mise en relation mentor–mentoré au sein de l'IFRI.
    Réalisée dans le cadre du Projet Intégrateur de Licence 1ère année — Année universitaire 2025–2026.
  </p>
  <div class="hero-meta">
    <div class="meta-item">
      <span class="meta-label">Établissement</span>
      <span class="meta-value">IFRI — UAC</span>
    </div>
    <div class="meta-item">
      <span class="meta-label">Groupe</span>
      <span class="meta-value">PIL1_2526_64</span>
    </div>
    <div class="meta-item">
      <span class="meta-label">Encadrants</span>
      <span class="meta-value">M. ACCROMBESSI · Mme GAHOU</span>
    </div>
    <div class="meta-item">
      <span class="meta-label">Superviseur</span>
      <span class="meta-value">M. HOUNDJI</span>
    </div>
    <div class="meta-item">
      <span class="meta-label">Dépôt final</span>
      <span class="meta-value">10 juin 2026</span>
    </div>
  </div>
</header>

<div class="divider"></div>

<!-- GROUPE -->
<div class="section-wrap">
<section id="groupe">
  <div class="section-label">01 — Membres</div>
  <h2>Composition du groupe</h2>
  <p class="section-intro">Groupe constitué de façon mixte, réunissant des étudiants issus de différentes filières de l'IFRI — Groupe n°64.</p>

  <div class="groupe-grid">

    <div class="membre-card">
      <div class="avatar" style="background:rgba(0,194,255,0.12);color:var(--blue);">GB</div>
      <div class="membre-info">
        <div class="membre-nom">GOUTONDE Bidossessi Conceptia Sharone</div>
        <div class="membre-role">Développeur Frontend</div>
      </div>
      <div class="filiere-badge badge-blue">SI</div>
    </div>

    <div class="membre-card">
      <div class="avatar" style="background:rgba(240,180,41,0.12);color:var(--gold);">HU</div>
      <div class="membre-info">
        <div class="membre-nom">HOUEGBELO Uriel Verghis Olsen</div>
        <div class="membre-role">Tech Lead / Backend</div>
      </div>
      <div class="filiere-badge badge-gold">GL</div>
    </div>

    <div class="membre-card">
      <div class="avatar" style="background:rgba(0,229,160,0.12);color:var(--green);">LE</div>
      <div class="membre-info">
        <div class="membre-nom">LOTSU Emmanuel Richard Kwasi</div>
        <div class="membre-role">Développeur Backend / Render</div>
      </div>
      <div class="filiere-badge badge-blue">SI</div>
    </div>

    <div class="membre-card">
      <div class="avatar" style="background:rgba(0,194,255,0.12);color:var(--blue);">HA</div>
      <div class="membre-info">
        <div class="membre-nom">HOUNNOUKON Agossou Prince</div>
        <div class="membre-role">Développeur Frontend</div>
      </div>
      <div class="filiere-badge badge-blue">SI</div>
    </div>

    <div class="membre-card">
      <div class="avatar" style="background:rgba(240,180,41,0.12);color:var(--gold);">YS</div>
      <div class="membre-info">
        <div class="membre-nom">YESSOUFOU Scham's-Deen</div>
        <div class="membre-role">Développeur Fullstack</div>
      </div>
      <div class="filiere-badge badge-gold">GL</div>
    </div>

    <div class="membre-card">
      <div class="avatar" style="background:rgba(240,180,41,0.12);color:var(--gold);">TP</div>
      <div class="membre-info">
        <div class="membre-nom">TOCHENALI Paola Eloane</div>
        <div class="membre-role">Développeur Backend</div>
      </div>
      <div class="filiere-badge badge-gold">GL</div>
   
    <div class="step">
      <div class="step-num">1</div>
      <div class="step-body">
        <h4>Cloner le dépôt GitHub</h4>
        <p>Récupérer le code source depuis le dépôt officiel du groupe.</p>
        <div class="code-block">
          <span class="cmd">git clone https://github.com/[votre-org]/PIL1_2526_64.git</span><br>
          <span class="cmd">cd PIL1_2526_64</span>
        </div>
      </div>
    </div>
    <div class="step">
      <div class="step-num">2</div>
      <div class="step-body">
        <h4>Créer l'environnement virtuel Python</h4>
        <p>Isoler les dépendances du projet dans un environnement virtuel.</p>
        <div class="code-block">
          <span class="cmd">python -m venv venv</span><br>
          <span class="cmd">source venv/bin/activate</span>  <span class="comment"># Linux/Mac</span><br>
          <span class="cmd">venv\Scripts\activate</span>     <span class="comment"># Windows</span><br>
          <span class="cmd">pip install -r backend/requirements.txt</span>
        </div>
      </div>
    </div>
    <div class="step">
      <div class="step-num">3</div>
      <div class="step-body">
        <h4>Configurer la base de données</h4>
        <p>Créer la base de données et importer la structure SQL.</p>
        <div class="code-block">
          <span class="comment"># Créer la base dans MySQL</span><br>
          <span class="cmd">mysql -u root -p</span><br>
          <span class="cmd">CREATE DATABASE mentorlink CHARACTER SET utf8mb4;</span><br>
          <span class="cmd">EXIT;</span><br><br>
          <span class="comment"># Importer la structure</span><br>
          <span class="cmd">mysql -u root -p mentorlink &lt; database.sql</span>
        </div>
      </div>
    </div>
    <div class="step">
      <div class="step-num">4</div>
      <div class="step-body">
        <h4>Configurer les variables d'environnement</h4>
        <p>Renseigner les paramètres dans <code>backend/config.py</code>.</p>
        <div class="code-block">
          <span class="comment"># backend/config.py</span><br>
          <span class="cmd">DB_HOST = "localhost"</span><br>
          <span class="cmd">DB_NAME = "mentorlink"</span><br>
          <span class="cmd">DB_USER = "root"</span><br>
          <span class="cmd">DB_PASSWORD = "votre_mdp"</span><br>
          <span class="cmd">SECRET_KEY = "une_cle_secrete_longue"</span>
        </div>
      </div>
    </div>
    <div class="step">
      <div class="step-num">5</div>
      <div class="step-body">
        <h4>Lancer le serveur Flask</h4>
        <p>L'application sera accessible sur <strong>http://localhost:5000</strong>.</p>
        <div class="code-block">
          <span class="cmd">cd backend</span><br>
          <span class="cmd">python app.py</span><br><br>
          <span class="comment"># Ouvrir dans le navigateur :</span><br>
          <span class="cmd">http://localhost:5000</span>
        </div>
      </div>
    </div>
  </div>
</section>
</div>

<div class="divider"></div>

<!-- MANUEL -->
<div class="section-wrap">
<section id="manuel">
  <div class="section-label">05 — Manuel</div>
  <h2>Manuel d'utilisation</h2>
  <p class="section-intro">Guide des principales fonctionnalités de l'application IFRI_MentorLink.</p>

  <div class="manuel-grid">
    <div class="manuel-card">
      <div class="manuel-icon" style="background:rgba(0,194,255,0.1);">👤</div>
      <h3>Créer un compte</h3>
      <ol>
        <li>Cliquer sur "S'inscrire" depuis l'accueil</li>
        <li>Remplir nom, prénom, email, téléphone, mot de passe</li>
        <li>Choisir sa filière et niveau d'études</li>
        <li>Sélectionner ses points forts et faibles</li>
        <li>Valider l'inscription</li>
      </ol>
    </div>
    <div class="manuel-card">
      <div class="manuel-icon" style="background:rgba(240,180,41,0.1);">🔑</div>
      <h3>Se connecter</h3>
      <ol>
        <li>Cliquer sur "Connexion" depuis l'accueil</li>
        <li>Saisir email ou numéro de téléphone</li>
        <li>Entrer son mot de passe</li>
        <li>Cliquer sur "Se connecter"</li>
        <li>En cas d'oubli : "Mot de passe oublié"</li>
      </ol>
    </div>
    <div class="manuel-card">
      <div class="manuel-icon" style="background:rgba(0,229,160,0.1);">🎯</div>
      <h3>Trouver un mentor</h3>
      <ol>
        <li>Accéder à "Matching" depuis le tableau de bord</li>
        <li>L'algorithme propose les profils compatibles</li>
        <li>Consulter le score et les matières communes</li>
        <li>Cliquer sur un profil pour ses disponibilités</li>
        <li>Envoyer une demande de mentorat</li>
      </ol>
    </div>
    <div class="manuel-card">
      <div class="manuel-icon" style="background:rgba(240,180,41,0.1);">📢</div>
      <h3>Publier une offre</h3>
      <ol>
        <li>Aller dans "Mes offres" depuis le tableau de bord</li>
        <li>Cliquer sur "Nouvelle offre" ou "Nouvelle demande"</li>
        <li>Sélectionner la matière concernée</li>
        <li>Indiquer le format (présentiel/en ligne)</li>
        <li>Préciser vos disponibilités et publier</li>
      </ol>
    </div>
    <div class="manuel-card">
      <div class="manuel-icon" style="background:rgba(0,194,255,0.1);">💬</div>
      <h3>Utiliser la messagerie</h3>
      <ol>
        <li>Accéder à "Messages" depuis la navigation</li>
        <li>Sélectionner ou démarrer une conversation</li>
        <li>Taper votre message dans le champ de saisie</li>
        <li>Appuyer sur Entrée ou cliquer sur Envoyer</li>
        <li>Notifications en temps réel à la réception</li>
      </ol>
    </div>
    <div class="manuel-card">
      <div class="manuel-icon" style="background:rgba(0,229,160,0.1);">✏️</div>
      <h3>Modifier son profil</h3>
      <ol>
        <li>Cliquer sur son avatar en haut à droite</li>
        <li>Sélectionner "Mon profil"</li>
        <li>Modifier les informations souhaitées</li>
        <li>Mettre à jour compétences / lacunes</li>
        <li>Enregistrer les modifications</li>
      </ol>
    </div>
  </div>
</section>
</div>

<div class="divider"></div>

<footer>
  <div class="footer-left">IFRI_MentorLink · PIL1_2526_64</div>
  <div class="footer-right">Université d'Abomey-Calavi · IFRI · Année 2025–2026</div>
</footer>

<script>
  function switchTab(name, btn) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.getElementById('tab-' + name).classList.add('active');
    btn.classList.add('active');
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.style.opacity = '1';
        e.target.style.transform = 'translateY(0)';
      }
    });
  }, { threshold: 0.08 });

  document.querySelectorAll('.membre-card, .fonct-card, .manuel-card, .db-table, .arch-layer, .step').forEach((el, i) => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(22px)';
    el.style.transition = `opacity 0.5s ${i * 0.05}s ease, transform 0.5s ${i * 0.05}s ease`;
    observer.observe(el);
  });
</script>

</body>
</html>
