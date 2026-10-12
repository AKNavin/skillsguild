# SkillsGuild.in

An open-source library of downloadable AI skills for Algo Trading, Human Resources and Content.

The first collection contains six original starter skills. Each download includes SKILL.md, metadata and the MIT licence. All website and skill sources are in this repository.

## Local development

Requires Node.js 22 or newer. No third-party packages are required.

```sh
npm run validate
npm run build
npm run dev
```

Open the printed local URL. The catalogue starts directly beneath the Algo Trading, HR and Content business tabs and search. Cards allocate 8% to the title, 67% to a workflow image and 25% to the description and actions. Visitors can view instructions or download the ZIP from each card.

## Contributions

See [CONTRIBUTING.md](CONTRIBUTING.md). Skills live under `skills/<category>/<name>/`. The build discovers folders, validates metadata and generates the catalogue and ZIP packages automatically.

## Publishing

The Sites deployment uses `dist/` and the private project identity in `.openai/hosting.json`.

For the public community site, GitHub Pages can build and publish `dist/` with `.github/workflows/pages.yml`. Select GitHub Actions as the publishing source in repository Settings → Pages. Pull requests run structural validation; pushes to main build and deploy. The public repository does not need the private `.openai` directory.

Set `repository` in `site.config.json` to the real `owner/repository` before publishing. Set up SkillsGuild.in only after registering it in your own registrar account. Domain registration and DNS setup are separate from this code.

The catalogue is generated at deployment time. An approved contribution appears after its merge and successful deployment. The Sites copy requires a separate deployment when the community source changes.

## Licence

MIT. Inspect downloaded instructions and code before using them with private data or connected tools.
