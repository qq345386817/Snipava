#!/usr/bin/env python3
"""Build the same three pages at stable URLs for all supported locales."""
import argparse
from html import escape
import json
from pathlib import Path
import re
import shutil
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
MANIFEST = json.loads((ROOT / "content/locales.json").read_text())
DEFAULT = MANIFEST["default"]
PAGES = ("home", "help", "privacy")
NOT_FOUND = """<!doctype html>
<html lang="en-US">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<meta name="robots" content="noindex">
<title>Page not found | Snipava</title>
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>
<main class="frame page">
  <h1>Page not found</h1>
  <p class="lead"><a href="/">Return to Snipava</a></p>
</main>
</body>
</html>
"""


def route(locale, page):
    parts = ([locale] if locale != DEFAULT else []) + ([page] if page != "home" else [])
    return "/" + "/".join(parts) + ("/" if parts else "")


def page_html(language, copy, page, origin, support_email):
    locale = language["id"]
    t = lambda key: escape(copy[key])
    nav_labels = {"home": "nav_home", "help": "nav_help", "privacy": "nav_privacy"}
    title = {"home": "title", "help": "help_title", "privacy": "privacy_title"}
    intro = {"home": "intro", "help": "help_intro", "privacy": "privacy_intro"}
    here = route(locale, page)
    current = ' aria-current="page"'
    nav = "".join(
        f'<a href="{route(locale, key)}"{current if page == key else ""}>{t(label)}</a>'
        for key, label in nav_labels.items()
    )
    others = "".join(
        f'<li><a href="{route(item["id"], page)}" lang="{item["id"]}" dir="{item["direction"]}"'
        f' hreflang="{item["id"]}"{current if item["id"] == locale else ""}>'
        f'{escape(item["name"])}</a></li>'
        for item in MANIFEST["languages"]
    )
    if origin:
        alternates = "".join(
            f'<link rel="alternate" hreflang="{item["id"]}" href="{origin}{route(item["id"], page)}">'
            for item in MANIFEST["languages"]
        )
        alternates += f'<link rel="alternate" hreflang="x-default" href="{origin}{route(DEFAULT, page)}">'
        canonical = f'<link rel="canonical" href="{origin}{here}">{alternates}'
    else:
        canonical = ""
    if page == "home":
        cards = "".join(
            f'<article><h3>{t(key)}</h3><p>{t(key + "_copy")}</p></article>'
            for key in ("text", "edit", "stitch")
        )
        content = f'''
        <div class="hero">
          <div>
            <h1>{t(title[page])}</h1>
            <p class="lead">{t(intro[page])}</p>
            <div class="actions">
              <a class="button primary" href="#features">{t("primary")}</a>
              <a class="button" href="{route(locale, "help")}">{t("secondary")}</a>
            </div>
          </div>
          <figure class="product"><img src="/assets/workspace.jpg" width="940" height="803" alt="{t("preview")}"></figure>
        </div>
        <section id="features" aria-labelledby="features-title">
          <h2 id="features-title">{t("features")}</h2><div class="features">{cards}</div>
        </section>'''
    elif page == "help":
        contact = f'<p class="support"><a href="mailto:{escape(support_email)}">{escape(support_email)}</a></p>' if support_email else ""
        questions = "".join(
            f'<details><summary>{t(key + "_q")}</summary><p>{t(key + "_a")}</p></details>'
            for key in ("mac", "mobile", "redact", "stitch")
        )
        content = f'''
        <h1>{t(title[page])}</h1><p class="lead">{t(intro[page])}</p>
        <div class="help-layout">
          <div class="faq">{questions}{contact}</div>
          <aside class="policy-card">
            <h2>{t("nav_privacy")}</h2><p>{t("privacy_intro")}</p>
            <a href="{route(locale, "privacy")}">{t("privacy_title")}</a>
          </aside>
        </div>'''
    else:
        sections = "".join(
            f'<section><h2>{t(key)}</h2><p>{t(key + "_copy")}</p></section>'
            for key in ("processing", "storage", "sharing", "website")
        )
        content = f'<h1>{t(title[page])}</h1><p class="lead">{t(intro[page])}</p><article class="policy">{sections}</article>'
    return f'''<!doctype html>
<html lang="{locale}" dir="{language["direction"]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<meta name="description" content="{t(intro[page])}">
<title>{t(title[page])} | Snipava</title>
{canonical}
<link rel="stylesheet" href="/assets/site.css">
<script src="/assets/site.js" defer></script>
</head>
<body>
<a class="skip" href="#main">{t("skip")}</a>
<header class="frame header">
  <a class="wordmark" href="{route(locale, "home")}">Snipava</a>
  <nav>{nav}</nav>
  <details class="language">
    <summary aria-label="{t("language")}">{escape(language["name"])}</summary>
    <ul>{others}</ul>
  </details>
</header>
<main class="frame page page-{page}" id="main">{content}</main>
<footer class="frame footer">
  <a class="wordmark" href="{route(locale, "home")}">Snipava</a>
  <div>{nav}</div>
</footer>
</body>
</html>
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--origin", default="", help="Production HTTPS origin for canonical URLs and sitemap")
    parser.add_argument("--support-email", default="", help="Public support address shown on Help pages")
    args = parser.parse_args()
    if args.support_email and not re.fullmatch(r"[A-Za-z0-9._+%-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", args.support_email):
        parser.error("--support-email must be an email address")
    origin = args.origin.removesuffix("/")
    parsed = urlsplit(origin)
    if origin and (parsed.scheme != "https" or not parsed.hostname or parsed.netloc != parsed.hostname or parsed.path or parsed.query or parsed.fragment):
        parser.error("--origin must be an HTTPS origin")
    translations = json.loads((ROOT / "content/copy.json").read_text())
    assert set(translations) == {item["id"] for item in MANIFEST["languages"]}, "Locale mismatch"
    default_keys = translations[DEFAULT].keys()
    output = ROOT / "dist"
    output.mkdir(exist_ok=True)
    public = ROOT / "public"
    if public.is_dir():
        shutil.copytree(public, output, dirs_exist_ok=True)
    shutil.copytree(ROOT / "assets", output / "assets", dirs_exist_ok=True)
    urls = []
    for language in MANIFEST["languages"]:
        locale = language["id"]
        copy = translations[locale]
        assert copy.keys() == default_keys and all(copy.values()), f"Incomplete copy for {locale}"
        for page in PAGES:
            path = route(locale, page)
            folder = output / path.lstrip("/")
            folder.mkdir(parents=True, exist_ok=True)
            (folder / "index.html").write_text(page_html(language, copy, page, origin, args.support_email), encoding="utf-8")
            urls.append(origin + path)
    robot = "User-agent: *\nAllow: /\n"
    sitemap = output / "sitemap.xml"
    if origin:
        robot += f"Sitemap: {origin}/sitemap.xml\n"
        entries = "".join(f"<url><loc>{escape(url)}</loc></url>" for url in urls)
        sitemap.write_text(f'<?xml version="1.0" encoding="utf-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{entries}</urlset>\n')
    else:
        sitemap.unlink(missing_ok=True)
    (output / "robots.txt").write_text(robot)
    (output / "404.html").write_text(NOT_FOUND, encoding="utf-8")
    print(f"Built {len(urls)} pages in {output}")


if __name__ == "__main__":
    main()
