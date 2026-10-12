# Contributing to SkillsGuild

Contribute focused, reusable AI workflows, not a generic collection of prompts. Each contribution must have clear inputs, output, boundaries and a realistic usage example in the pull request.

1. Fork this repository and create a branch.
2. Add `skills/<category>/<unique-skill-name>/SKILL.md` and `metadata.json`. Categories are `algotrading`, `hr`, and `content`.
3. Use the SKILL.md and metadata examples in `src/contributing.html`. Set `status` to `community`; frontmatter `name` must match the folder name.
4. Run `npm run validate` and `npm run build` using Node.js 22 or newer. No package installation is required.
5. Open a pull request with the use case, an example input, expected output and checks performed.

Keep skills under the MIT licence. Do not submit secrets, personal information, copied proprietary material, hidden files or symlinks. Files are limited to 1 MB each. Declare any tools, scripts, network access or paid dependencies. The build packages files but never executes contributor scripts.

Maintainers review instructions and supporting code before merging. Automated structural validation is not a safety certification. Only merged changes on `main` publish through the configured GitHub Pages workflow. Suggest new categories through an issue.
