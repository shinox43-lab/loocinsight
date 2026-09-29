#!/usr/bin/env python3
# GEO retrofit for loocinsight.com static mirror.
# Idempotent: creates robots.txt / llms.txt / sitemap.xml at site root,
# and injects LocalBusiness JSON-LD + Open Graph tags into index.html.
# Zero-duplication: mirror already bakes in Yoast Organization+WebSite,
# so we add ONLY a LocalBusiness node (template version B).
import os, re, json, sys, datetime

SITE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site")
DOMAIN = "https://loocinsight.com"
LOGO = f"{DOMAIN}/wp-content/uploads/2023/06/LOOC-Insight-Logo-3Feb2026-e1770437741765.png"
TODAY = datetime.date.today().isoformat()

# Pages to expose in sitemap (clean URLs). Excludes thank-you (form confirmation),
# category (taxonomy), search.
PAGES = [
    ("", "1.0"),
    ("who-we-are/", "0.9"),
    ("family-wealth-management/", "0.9"),
    ("professional-services/", "0.8"),
    ("concierge-service/", "0.8"),
    ("insights/", "0.7"),
    ("where-we-are/", "0.7"),
    ("get-a-consultation/", "0.8"),
    ("contact/", "0.7"),
    ("privacy-policy/", "0.3"),
    ("terms-of-use/", "0.3"),
]

# ---- 1. robots.txt (static site: no wp-admin/cart) ----
ROBOTS = """# LOOC Insight — robots.txt
User-agent: *
Allow: /

# --- AI answer engines: explicitly allowed ---
User-agent: GPTBot
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Claude-Web
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Perplexity-User
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: Applebot-Extended
Allow: /

User-agent: Bingbot
Allow: /

Sitemap: https://loocinsight.com/sitemap.xml
"""

# ---- 2. sitemap.xml ----
def build_sitemap():
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path, prio in PAGES:
        out.append(f"  <url><loc>{DOMAIN}/{path}</loc><lastmod>{TODAY}</lastmod>"
                   f"<priority>{prio}</priority></url>")
    out.append("</urlset>\n")
    return "\n".join(out)

def normalize_site_metadata():
    canonical_tag = re.compile(
        r'<link\b(?=[^>]*\brel=["\']canonical["\'])[^>]*>', re.I
    )
    href_attr = re.compile(r'\bhref\s*=\s*(["\']).*?\1', re.I)
    robots_tag = re.compile(
        r'<meta\b(?=[^>]*\bname=["\']robots["\'])[^>]*>', re.I
    )

    for path in sorted(os.path.join(root, "index.html")
                       for root, _, files in os.walk(SITE)
                       if "index.html" in files):
        relative = os.path.relpath(path, SITE).replace(os.sep, "/")
        route = "/" if relative == "index.html" else "/" + relative[:-len("index.html")]
        canonical = DOMAIN + route
        with open(path, encoding="utf-8") as source_file:
            html = source_file.read()

        def replace_canonical(match):
            tag = match.group(0)
            if href_attr.search(tag):
                return href_attr.sub(f'href="{canonical}"', tag, count=1)
            return tag[:-1] + f' href="{canonical}">'

        if canonical_tag.search(html):
            html = canonical_tag.sub(replace_canonical, html, count=1)
        else:
            html = html.replace(
                "</head>", f'<link rel="canonical" href="{canonical}">\n</head>', 1
            )

        if relative == "who-we-are/index.html":
            html = html.replace(
                'name="robots" content="max-image-preview:large, index, nofollow, noarchive"',
                'name="robots" content="max-image-preview:large, index, follow"',
            )
        elif relative == "category/uncategorized/index.html":
            if robots_tag.search(html):
                html = robots_tag.sub(
                    '<meta name="robots" content="noindex, follow">', html, count=1
                )
            else:
                html = html.replace(
                    "</head>", '<meta name="robots" content="noindex, follow">\n</head>', 1
                )

        html = html.replace('"name":"loocinsight.com"', '"name":"LOOC Insight"')
        if relative == "index.html":
            html = html.replace(
                "<title>Home | LOOC Insight</title>",
                "<title>LOOC Insight | Family Wealth &amp; Legacy Planning in Hong Kong</title>",
            )
            html = re.sub(
                r'(<meta\b(?=[^>]*\bname=["\']description["\'])[^>]*\bcontent=["\'])'
                r'[^"\']*(["\'][^>]*>)',
                r'\1Hong Kong-based family wealth and legacy planning intermediary '
                r'providing succession planning, family office coordination, '
                r'professional services and concierge support.\2',
                html,
                count=1,
                flags=re.I,
            )

        with open(path, "w", encoding="utf-8") as output_file:
            output_file.write(html)

# ---- 3. llms.txt ----
LLMS = """# LOOC Insight

> LOOC Insight is a Hong Kong–based family wealth and legacy planning intermediary
> that helps families "get their house in order." Working from Central & Sheung Wan
> with a global network of talent, it coordinates succession planning, family-office
> support, professional services and concierge service. Engagements are by appointment.

## About LOOC Insight
- Name: LOOC Insight (Hong Kong registered company)
- Focus: Family Wealth & Legacy Planning — intermediary / advisory service provider
- Location: Central & Sheung Wan, Hong Kong Island, Hong Kong
- Phone: +852 5388 4500
- Language: English, 繁體中文
- Currency: HKD
- Engagement: By appointment — request a consultation via the website

## Key pages
- [Home](https://loocinsight.com/): Family wealth & legacy planning overview
- [Who We Are](https://loocinsight.com/who-we-are/): The team and philosophy
- [Family Wealth Management](https://loocinsight.com/family-wealth-management/): Wealth & succession coordination
- [Professional Services](https://loocinsight.com/professional-services/): Advisory and professional support
- [Concierge Service](https://loocinsight.com/concierge-service/): Bespoke lifestyle & concierge support
- [Where We Are](https://loocinsight.com/where-we-are/): Location & global network
- [Insights](https://loocinsight.com/insights/): Articles and updates
- [Get a Consultation](https://loocinsight.com/get-a-consultation/): Request an appointment
- [Contact](https://loocinsight.com/contact/): Get in touch

## Services
- Family wealth management
- Legacy & succession planning
- Family office coordination
- Professional services (advisory / intermediary)
- Concierge service

## Who it serves
High-net-worth individuals and families in Hong Kong and across a global network,
seeking to organise, protect and pass on family wealth and legacy.

## How to engage
Services are by appointment. Request a consultation through the website
(Get a Consultation / Contact) or call +852 5388 4500.
"""

# ---- 4. LocalBusiness JSON-LD (version B — single node, no Org/WebSite dup) ----
LOCALBUSINESS = {
    "@context": "https://schema.org",
    "@type": "ProfessionalService",
    "@id": f"{DOMAIN}/#localbusiness",
    "name": "LOOC Insight",
    "description": ("LOOC Insight is a Hong Kong-based family wealth and legacy planning "
                    "intermediary that helps families get their house in order through "
                    "succession planning, family office coordination, professional services "
                    "and concierge support. Based in Central & Sheung Wan, Hong Kong, with a "
                    "global network of talent. Services are provided by appointment — please "
                    "contact us to arrange a consultation."),
    "url": f"{DOMAIN}/",
    "image": LOGO,
    "logo": LOGO,
    "telephone": "+852-5388-4500",
    "currenciesAccepted": "HKD",
    "address": {
        "@type": "PostalAddress",
        "addressLocality": "Central & Sheung Wan",
        "addressRegion": "Hong Kong Island",
        "addressCountry": "HK"
    },
    "areaServed": {"@type": "Country", "name": "Hong Kong"},
    "knowsAbout": [
        "Family wealth management", "Legacy planning", "Succession planning",
        "Family office services", "Wealth structuring", "Estate planning",
        "Professional services", "Concierge service", "Intermediary services",
        "High-net-worth advisory"
    ]
}

MARKER = "<!-- GEO-RETROFIT:localbusiness -->"

def inject_index():
    p = os.path.join(SITE, "index.html")
    html = open(p, encoding="utf-8").read()
    if MARKER in html:
        # replace existing injected block (idempotent update)
        html = re.sub(re.escape(MARKER) + r".*?<!-- /GEO-RETROFIT -->", "", html, flags=re.S)
    ld = json.dumps(LOCALBUSINESS, ensure_ascii=False, separators=(",", ":"))
    og = (
        f'{MARKER}\n'
        f'<meta property="og:type" content="website">\n'
        f'<meta property="og:site_name" content="LOOC Insight">\n'
        f'<meta property="og:title" content="LOOC Insight — Family Wealth &amp; Legacy Planning">\n'
        f'<meta property="og:description" content="Hong Kong-based family wealth &amp; legacy planning intermediary. We get your house in order — succession planning, family office, professional &amp; concierge services. By appointment.">\n'
        f'<meta property="og:url" content="{DOMAIN}/">\n'
        f'<meta property="og:image" content="{LOGO}">\n'
        f'<meta property="og:locale" content="en_HK">\n'
        f'<meta name="twitter:card" content="summary">\n'
        f'<meta name="twitter:title" content="LOOC Insight — Family Wealth &amp; Legacy Planning">\n'
        f'<meta name="twitter:description" content="Hong Kong-based family wealth &amp; legacy planning intermediary. By appointment.">\n'
        f'<meta name="twitter:image" content="{LOGO}">\n'
        f'<script type="application/ld+json">{ld}</script>\n'
        f'<!-- /GEO-RETROFIT -->\n'
    )
    html = html.replace("</head>", og + "</head>", 1)
    open(p, "w", encoding="utf-8").write(html)
    # validate JSON round-trips
    json.loads(ld)
    print("✅ index.html: LocalBusiness + OG injected")

def main():
    normalize_site_metadata()
    print("✅ Canonicals and site metadata normalized")
    open(os.path.join(SITE, "robots.txt"), "w", encoding="utf-8").write(ROBOTS)
    print("✅ robots.txt written")
    open(os.path.join(SITE, "sitemap.xml"), "w", encoding="utf-8").write(build_sitemap())
    print(f"✅ sitemap.xml written ({len(PAGES)} URLs)")
    open(os.path.join(SITE, "llms.txt"), "w", encoding="utf-8").write(LLMS)
    print("✅ llms.txt written")
    inject_index()
    print("\nDone. Next: ./deploy.sh")

if __name__ == "__main__":
    main()
