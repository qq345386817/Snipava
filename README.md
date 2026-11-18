# Snipava website

This repository builds the Snipava homepage, help, and privacy policy for the 11 app locales. The default English (US) pages are at `/`, `/help/`, and `/privacy/`. Other languages use a prefix such as `/zh-Hant/help/`. The language picker preserves the current page. Arabic pages use right-to-left layout. The site follows the system light or dark appearance and responds to changes while a page is open.

## Build and preview

Use Python 3.9 or later. The build uses the Python standard library. The generated `dist/` directory is ignored.

```sh
python3 build.py
python3 -m http.server 8080 --bind 127.0.0.1 --directory dist
```

## Production

Cloudflare Pages builds the `main` branch of `qq345386817/Snipava` from the repository root and serves `dist/` at [snipava.luopeike.com](https://snipava.luopeike.com/).

```sh
python3 build.py --origin https://snipava.luopeike.com --support-email cameoshell09@gmail.com
```

This build includes the sitemap, canonical URLs, locale alternates and the public support address on each Help page. The Cloudflare redirect for `snipava.pages.dev` preserves the requested path and query. The production sitemap is at `https://snipava.luopeike.com/sitemap.xml`.

## Update translations and assets

Update `content/copy.json` with a complete entry for each language. `content/locales.json` should match `Resources/Localization/locales.json` in the separate Snipava app checkout. Assets are served locally. The home page uses a real Snipava workspace capture with a synthetic sample. Store screenshot output lives in the app repository's ignored `.local/` directory.
