# Contributing to SkillsGuild

Contribute focused, reusable AI workflows, not a generic collection of prompts. Each contribution must have clear inputs, output, boundaries and a realistic usage example in the pull request.

1. Fork this repository and create a branch.
2. Add `skills/<category>/<unique-skill-name>/SKILL.md` and `metadata.json`. Categories are `algotrading`, `hr`, and `content`.
3. Use the SKILL.md and metadata examples in `src/contributing.html`. Set `status` to `community`; frontmatter `name` must match the folder name.
4. Run `npm run validate` and `npm run build` using Node.js 22 or newer. No package installation is required.
5. Open a pull request with the use case, an example input, expected output and checks performed.

## Card preview image

Include `preview.svg`, `preview.png`, `preview.jpg` or `preview.webp` in the skill folder, then set `image` to that filename and `image_alt` to a plain description in `metadata.json`. Use a landscape image around 3:2 with a simple object illustration that closely represents what the skill does. Prefer pencil-and-watercolour artwork on a soft pastel background. Keep all lettering, numbers, captions and branding out of the image; the card title and description explain the skill. Illustrations must not imply live trading results. Images are optional; the website uses a text-free folder illustration when none is supplied. The image is included in the download and served with a content hash so updates reach visitors.

Cards allocate 8% of their height to the title, 67% to the image, and 25% to the description and actions. Keep descriptions concise; readers can open the full skill for detail.

Keep skills under the MIT licence. Do not submit secrets, personal information, copied proprietary material, hidden files or symlinks. Files are limited to 1 MB each. Declare any tools, scripts, network access or paid dependencies. The build packages files but never executes contributor scripts.

Maintainers review instructions and supporting code before merging. Automated structural validation is not a safety certification. Only merged changes on `main` publish through the configured GitHub Pages workflow. Suggest new categories through an issue.

## Algo Trading contributions

Set `topic` to `setup`, `data`, `signals`, `options`, `backtesting`, `regimes`, `execution` or `risk`. Include `requires` (an array of actual dependencies), `sources` (objects with `title` and HTTPS `url`) and `verified_at` (the source-check date). Keep instructions focused, usually 200–400 words, with explicit inputs, output files, formulas/API steps and meaningful checks. Cite primary documentation for API facts; label configurable trading thresholds as examples.

State signal timing, missing-data treatment and execution scope. Use synthetic fixtures in the public repo. Do not include account data or licensed historical feeds. Fee schedules need effective dates and provenance; sample fees must be conspicuously marked synthetic. Run any included helpers and behavioral tests, then remove generated outputs and Python caches before submitting. The build publishes supporting files beside SKILL.md so relative references work.
