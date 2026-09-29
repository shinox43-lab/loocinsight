# LOOC Insight website source

This repository contains the static WordPress export used by the LOOC Insight
Cloudflare Pages site. The deployable website is in `site/`; Cloudflare Pages
should use the `main` branch, no build command, and `site` as its build output
directory.

## Updating the site

Edit the relevant files under `site/` and push changes to `main` to trigger a
production deployment. Before publishing a refreshed WordPress export, run:

```sh
python3 geo-retrofit.py
python3 remove-injected-posts.py
python3 hide-search.py
```

The metadata retrofit maintains absolute canonical URLs, the sitemap, robots
rules, and homepage search metadata. The cleanup scripts remove known injected
post cards and hide the non-functional static search form.

For a manual deployment, install Wrangler and run `./deploy.sh`. Do not commit
the private `mirror/` source, local `.wrangler/` state, credentials, or a nested
`.git/` directory from an exported site.
