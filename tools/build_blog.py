#!/usr/bin/env python3
"""Génère le blog SCALEON (blog/*.html), sitemap.xml et robots.txt.

Ajouter un article : créer content/blog/<slug>.html (en-tête entre ---), puis lancer
    python3 tools/build_blog.py
Après l'achat du nom de domaine, modifier SITE_URL ci-dessous et relancer le script.
"""
import html, json, re, unicodedata
from datetime import date
from pathlib import Path

SITE_URL = "https://scaleon-business.netlify.app"
ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "blog"
OUT = ROOT / "blog"
PAGES = ["index", "a-propos", "offres", "formations", "blog/index", "contact"]
MONTHS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
          "septembre", "octobre", "novembre", "décembre"]
SAME_AS = [
    "https://www.linkedin.com/company/scaleon-business",
    "https://web.facebook.com/scaleonbusiness",
    "https://www.instagram.com/paulshunkiss/",
    "https://www.tiktok.com/@paulshunkiss",
    "https://x.com/shunkisspaul",
]
AUTHOR = {"@type": "Person", "name": "Paul Shunkiss Missambo M.", "jobTitle": "Founder & CEO, SCALEON",
          "url": f"{SITE_URL}/a-propos.html",
          "sameAs": ["https://www.linkedin.com/in/paul-shunkiss-missambo-59b833148"] + SAME_AS[2:]}
PUBLISHER = {"@type": "Organization", "name": "SCALEON", "url": SITE_URL,
             "logo": {"@type": "ImageObject", "url": f"{SITE_URL}/assets/img/logo-full.png"}}
ARROW = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M13 5l7 7-7 7"/></svg>'


def slugify(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def fr_date(d):
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}"


def parse(path):
    raw = path.read_text(encoding="utf-8")
    _, head, body = raw.split("---", 2)
    meta, faq = {}, []
    for line in head.strip().splitlines():
        key, _, value = line.partition(":")
        if key.strip() == "faq":
            q, _, a = value.partition("||")
            faq.append((q.strip(), a.strip()))
        else:
            meta[key.strip()] = value.strip()
    meta.update(slug=path.stem, faq=faq, date=date.fromisoformat(meta["date"]), read=int(meta.get("read", 6)))
    toc = []

    def add_id(m):
        title = re.sub(r"<[^>]+>", "", m.group(1))
        anchor = slugify(title)
        toc.append((anchor, title))
        return f'<h2 id="{anchor}">{m.group(1)}</h2>'

    meta["body"] = re.sub(r"<h2>(.*?)</h2>", add_id, body.strip())
    meta["toc"] = toc
    return meta


def chrome():
    src = (ROOT / "contact.html").read_text(encoding="utf-8")
    header = src[src.index("<header"):src.index("</header>") + 9]
    footer = src[src.index("<footer"):src.index("</body>")]
    header = header.replace(' class="active"', "")
    fix = lambda s: re.sub(r'(href|src)="(?!https?:|mailto:|tel:|#|\.\./)', r'\1="../', s)
    header = fix(header).replace('href="../blog/index.html"', 'href="index.html" class="active"')
    footer = fix(footer).replace('href="../blog/index.html"', 'href="index.html"')
    return header, footer


def head(title, desc, url, image, og_type="website", extra=""):
    t, d = html.escape(title), html.escape(desc)
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{t}</title>
<meta name="description" content="{d}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="fr" href="{url}">
<link rel="alternate" hreflang="x-default" href="{url}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:locale" content="fr_FR">
<meta property="og:site_name" content="SCALEON">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:type" content="{og_type}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@shunkisspaul">
<link rel="icon" type="image/png" href="../assets/img/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700;800&family=Open+Sans:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/css/styles.css">
{extra}</head>
<body>
"""


def ld(obj):
    return f'<script type="application/ld+json">{json.dumps(obj, ensure_ascii=False)}</script>\n'


def card(p, base=""):
    img = "assets/img/" if base else "../assets/img/"
    return (f'<a class="card card--media post-card reveal" href="{base}{p["slug"]}.html" data-cat="{html.escape(p["category"])}">'
            f'<img src="{img}{p["image"]}" alt="{html.escape(p["image_alt"])}" loading="lazy">'
            f'<div class="card__body"><span class="card__kicker">{html.escape(p["category"])}</span>'
            f'<h3>{html.escape(p["title"])}</h3><p>{html.escape(p["description"])}</p>'
            f'<span class="post-meta"><time datetime="{p["date"]}">{fr_date(p["date"])}</time> · {p["read"]} min de lecture</span></div></a>')


CTA = f"""<section class="section"><div class="container"><div class="cta reveal">
  <div><h2>Passez de la lecture à l'action</h2><p>Réservez votre audit gratuit : en 48h, vous savez exactement où vous en êtes et par quoi commencer.</p></div>
  <div class="btn-row"><a href="../contact.html#audit" class="btn btn--white">Réserver mon audit gratuit {ARROW}</a><a href="https://wa.me/237694836346" target="_blank" rel="noopener" class="btn btn--ghost">WhatsApp</a></div>
</div></div></section>
"""


def article_page(p, posts, header, footer):
    url = f"{SITE_URL}/blog/{p['slug']}.html"
    img = f"{SITE_URL}/assets/img/{p['image']}"
    schema = ld({"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"],
                 "description": p["description"], "image": img, "datePublished": str(p["date"]),
                 "dateModified": str(p["date"]), "inLanguage": "fr", "articleSection": p["category"],
                 "keywords": p.get("keywords", ""), "author": AUTHOR, "publisher": PUBLISHER,
                 "mainEntityOfPage": {"@type": "WebPage", "@id": url}})
    schema += ld({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Accueil", "item": f"{SITE_URL}/"},
        {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{SITE_URL}/blog/"},
        {"@type": "ListItem", "position": 3, "name": p["title"], "item": url}]})
    if p["faq"]:
        schema += ld({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]})
    extra = f'<meta property="article:published_time" content="{p["date"]}">\n<meta property="article:section" content="{html.escape(p["category"])}">\n<meta name="keywords" content="{html.escape(p.get("keywords", ""))}">\n' + schema
    toc = "".join(f'<li><a href="#{a}">{html.escape(re.sub(r"^\d+\.\s*", "", t))}</a></li>' for a, t in p["toc"])
    faq = "".join(f"<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>" for q, a in p["faq"])
    related = sorted((o for o in posts if o["slug"] != p["slug"]), key=lambda o: (o["category"] != p["category"], -o["date"].toordinal()))[:3]
    return head(f"{p['title']} | Blog SCALEON", p["description"], url, img, "article", extra) + header + f"""
<main>
<section class="hero hero--page hero--post"><div class="container hero__inner">
  <nav class="breadcrumb" aria-label="Fil d'Ariane"><a href="../index.html">Accueil</a><span>›</span><a href="index.html">Blog</a><span>›</span><span>{html.escape(p['category'])}</span></nav>
  <span class="eyebrow">{html.escape(p['category'])}</span>
  <h1>{html.escape(p['title'])}</h1>
  <p class="post-meta post-meta--hero">Par <a href="../a-propos.html">Paul Shunkiss</a> · <time datetime="{p['date']}">{fr_date(p['date'])}</time> · {p['read']} min de lecture</p>
</div></section>

<section class="section section--post"><div class="container article-layout">
  <article class="prose">
    <img class="article-cover" src="../assets/img/{p['image']}" alt="{html.escape(p['image_alt'])}">
    {p['body']}
    <h2 id="faq">Questions fréquentes</h2>
    <div class="faq faq--post">{faq}</div>
    <div class="author-box"><img src="../assets/img/paul-shunkiss.png" alt="Paul Shunkiss Missambo M." loading="lazy"><div><strong>Paul Shunkiss Missambo M.</strong><span>Founder &amp; CEO de SCALEON · consultant en stratégie business, marketing digital et transformation numérique. Il accompagne les PME et entrepreneurs d'Afrique francophone et de la diaspora.</span><a class="link" href="../a-propos.html">En savoir plus</a></div></div>
  </article>
  <aside class="article-aside">
    <div class="toc"><strong>Sommaire</strong><ol>{toc}<li><a href="#faq">Questions fréquentes</a></li></ol></div>
    <div class="aside-cta"><strong>Audit digital gratuit</strong><p>Un plan d'actions concret pour votre entreprise en 48h.</p><a href="../contact.html#audit" class="btn btn--white">Je réserve</a></div>
  </aside>
</div></section>

<section class="section section--sand"><div class="container">
  <div class="section-head center reveal"><span class="eyebrow">À lire aussi</span><h2>Articles recommandés</h2></div>
  <div class="grid grid--3">{''.join(card(o) for o in related)}</div>
</div></section>
{CTA}</main>
{footer}</body>
</html>
"""


def index_page(posts, header, footer):
    url = f"{SITE_URL}/blog/"
    cats = sorted({p["category"] for p in posts})
    schema = ld({"@context": "https://schema.org", "@type": "Blog", "name": "Blog SCALEON", "url": url, "inLanguage": "fr",
                 "publisher": PUBLISHER, "blogPost": [
                     {"@type": "BlogPosting", "headline": p["title"], "url": f"{SITE_URL}/blog/{p['slug']}.html",
                      "datePublished": str(p["date"]), "author": {"@type": "Person", "name": AUTHOR["name"]}} for p in posts]})
    chips = '<button class="chip active" data-filter="*">Tous les articles</button>' + "".join(
        f'<button class="chip" data-filter="{html.escape(c)}">{html.escape(c)}</button>' for c in cats)
    desc = "Guides evergreen sur le SEO local et international, le marketing digital, la stratégie business et la transformation numérique pour les PME d'Afrique francophone et de la diaspora."
    return head("Blog SCALEON | SEO, marketing digital et croissance des PME en Afrique", desc, url,
                f"{SITE_URL}/assets/img/logo-full.png", extra=schema) + header + f"""
<main>
<section class="hero hero--page"><div class="container hero__inner">
  <span class="eyebrow">Blog &amp; ressources</span>
  <h1>Des conseils concrets pour faire grandir votre entreprise</h1>
  <p class="lead">Guides pratiques sur le SEO local et international, le marketing digital, la stratégie et la transformation numérique, pour les PME d'Afrique et de la diaspora.</p>
</div></section>

<section class="section"><div class="container">
  <div class="filters" role="toolbar" aria-label="Filtrer par thème">{chips}</div>
  <div class="grid grid--3 post-grid">{''.join(card(p) for p in posts)}</div>
</div></section>
{CTA}</main>
{footer}</body>
</html>
"""


def write_sitemap(posts):
    today = max(p["date"] for p in posts)
    urls = [(f"{SITE_URL}/" if pg == "index" else f"{SITE_URL}/blog/" if pg == "blog/index" else f"{SITE_URL}/{pg}.html", today, "1.0" if pg == "index" else "0.8") for pg in PAGES]
    urls += [(f"{SITE_URL}/blog/{p['slug']}.html", p["date"], "0.7") for p in posts]
    body = "".join(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod><priority>{pr}</priority></url>\n" for u, d, pr in urls)
    (ROOT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}</urlset>\n', encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")


def patch_root_pages():
    for pg in ["index", "a-propos", "offres", "formations", "contact"]:
        f = ROOT / f"{pg}.html"
        t = f.read_text(encoding="utf-8")
        url = f"{SITE_URL}/" if pg == "index" else f"{SITE_URL}/{pg}.html"
        t = re.sub(r'\n<link rel="canonical"[^>]*>\n<meta property="og:url"[^>]*>', "", t)
        t = t.replace('<link rel="icon"', f'<link rel="canonical" href="{url}">\n<meta property="og:url" content="{url}">\n<link rel="icon"', 1)
        t = re.sub(r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{SITE_URL}/assets/img/logo-full.png">', t)
        if 'href="blog/index.html"' not in t:
            t = t.replace('<a href="contact.html" class="active">Contact</a>', '<a href="blog/index.html">Blog</a><a href="contact.html" class="active">Contact</a>')
            t = t.replace('<a href="formations.html">Formations</a><a href="contact.html">Contact</a>', '<a href="formations.html">Formations</a><a href="blog/index.html">Blog</a><a href="contact.html">Contact</a>')
            t = t.replace('<a href="formations.html" class="active">Formations</a><a href="contact.html">Contact</a>', '<a href="formations.html" class="active">Formations</a><a href="blog/index.html">Blog</a><a href="contact.html">Contact</a>')
            t = t.replace('<li><a href="formations.html">Formations</a></li>', '<li><a href="formations.html">Formations</a></li><li><a href="blog/index.html">Blog</a></li>')
        if pg == "index":
            t = re.sub(r'<script type="application/ld\+json" id="org-schema">.*?</script>\n', "", t, flags=re.S)
            org = {"@context": "https://schema.org", "@type": "ProfessionalService", "name": "SCALEON Business Consulting",
                   "url": f"{SITE_URL}/", "logo": f"{SITE_URL}/assets/img/logo-full.png", "image": f"{SITE_URL}/assets/img/logo-full.png",
                   "description": "Cabinet de conseil en stratégie business, marketing digital, transformation numérique et formation pour les PME d'Afrique francophone et de la diaspora.",
                   "telephone": "+237694836346", "email": "contact@scaleonbusiness.com",
                   "address": {"@type": "PostalAddress", "addressLocality": "Douala", "addressCountry": "CM"},
                   "areaServed": ["Cameroun", "Afrique francophone", "Royaume-Uni", "France"],
                   "openingHoursSpecification": {"@type": "OpeningHoursSpecification",
                                                 "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
                                                 "opens": "08:00", "closes": "18:00"},
                   "founder": {"@type": "Person", "name": AUTHOR["name"]},
                   "paymentAccepted": "Orange Money, MTN MoMo, Virement bancaire, PayPal, WorldRemit, Remitly",
                   "sameAs": SAME_AS}
            t = t.replace("</head>", f'<script type="application/ld+json" id="org-schema">{json.dumps(org, ensure_ascii=False)}</script>\n</head>', 1)
        f.write_text(t, encoding="utf-8")


def patch_home_latest(posts):
    f = ROOT / "index.html"
    t = re.sub(r"<!--blog:latest-->.*?<!--/blog:latest-->\n", "", f.read_text(encoding="utf-8"), flags=re.S)
    block = f"""<!--blog:latest--><section class="section section--sand"><div class="container">
  <div class="section-head center reveal"><span class="eyebrow">Blog</span><h2>Nos derniers conseils</h2><p class="lead" style="margin-inline:auto">Des guides pratiques pour attirer plus de clients et structurer votre croissance.</p></div>
  <div class="grid grid--3">{''.join(card(p, "blog/") for p in posts[:3])}</div>
  <div class="center" style="margin-top:36px"><a href="blog/index.html" class="btn btn--red">Voir tous les articles {ARROW}</a></div>
</div></section><!--/blog:latest-->
"""
    marker = '<section class="section"><div class="container"><div class="cta reveal">'
    f.write_text(t.replace(marker, block + "\n" + marker, 1), encoding="utf-8")


def main():
    patch_root_pages()
    posts = sorted((parse(p) for p in CONTENT.glob("*.html")), key=lambda p: p["date"], reverse=True)
    header, footer = chrome()
    OUT.mkdir(exist_ok=True)
    for p in posts:
        (OUT / f"{p['slug']}.html").write_text(article_page(p, posts, header, footer), encoding="utf-8")
    (OUT / "index.html").write_text(index_page(posts, header, footer), encoding="utf-8")
    patch_home_latest(posts)
    write_sitemap(posts)
    print(f"{len(posts)} articles générés")


if __name__ == "__main__":
    main()
