# SCALEON - Site web

Site statique (HTML/CSS/JS) de SCALEON Business Consulting.

Aperçu local : `python3 -m http.server 8080` puis ouvrir http://localhost:8080

Pages : index, a-propos, offres, formations, contact. Le formulaire de contact envoie la demande sur WhatsApp (+237 694 836 346).

Déploiement : GitHub Pages (branche main) et Netlify (`netlify.toml`, publication du dossier racine).

## Blog (SEO)

Les articles sont dans `content/blog/` (un fichier HTML par article, avec un en-tête entre `---`).
Pour publier un nouvel article : ajouter le fichier puis lancer `python3 tools/build_blog.py`.
Le script génère `blog/`, la section « Nos derniers conseils » de l'accueil, `sitemap.xml` et `robots.txt`.
Après l'achat du nom de domaine, modifier `SITE_URL` dans `tools/build_blog.py` et relancer le script.
