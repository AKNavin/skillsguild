# SkillsGuild.in

An open-source library of downloadable AI skills for Algo Trading, Human Resources and Content.

The catalogue includes a focused Kite Connect collection for authentication, data, stock signals, options, backtesting, regimes, execution state and risk. Each download includes SKILL.md, metadata and the MIT licence. Selected skills also contain runnable offline reference helpers and synthetic fixtures. All website and skill sources are in this repository.

Read [the website brief](BRIEF.md), [the Algo Trading guide](ALGO-GUIDE.md), and [validation coverage](VALIDATION.md). Published `llms.txt`, `algotrading.md` and individual `library/<category>/<skill>/SKILL.md` URLs let users direct their AI to the relevant instructions. The algo bundle contains all Algo Trading instructions and supporting code, without card artwork.

## Local development

Requires Node.js 22 or newer. No third-party packages are required.

```sh
npm run validate
npm run build
npm run dev
```

Open the printed local URL. The catalogue has business tabs, a brief explanation of skills, search and topic filters. Desktop screens show eight compact cards per row, with fewer columns on smaller screens. Each card has a text-free illustration, a short description, and Copy link and Download actions; its title or image opens the full instructions.

## Contributions

See [CONTRIBUTING.md](CONTRIBUTING.md). Skills live under `skills/<category>/<name>/`. The build discovers folders, validates metadata and generates the catalogue and ZIP packages automatically.

## Publishing

The Sites deployment uses `dist/` and the private project identity in `.openai/hosting.json`.

For the public community site, GitHub Pages can build and publish `dist/` with `.github/workflows/pages.yml`. Select GitHub Actions as the publishing source in repository Settings → Pages. Pull requests run structural validation; pushes to main build and deploy. The public repository does not need the private `.openai` directory.

Set `repository` in `site.config.json` to the real `owner/repository` before publishing. Set up SkillsGuild.in only after registering it in your own registrar account. Domain registration and DNS setup are separate from this code.

The catalogue is generated at deployment time. An approved contribution appears after its merge and successful deployment. The Sites copy requires a separate deployment when the community source changes.

## Licence

MIT. Inspect downloaded instructions and code before using them with private data or connected tools.
