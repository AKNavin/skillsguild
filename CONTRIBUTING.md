# Contribute a reproducible strategy

Submit a GitHub pull request with a precise hypothesis, source, universe, ranking/entry/exit rules, execution timing, sizing, costs and data requirements. Include executable code, causal/accounting tests, a frozen configuration and a reproducible run manifest. Record failed and inconclusive findings as well as positive results.

Keep short instructions in SKILL.md and deterministic calculations in code. Do not submit generic skill recipes, credentials, account records or unlicensed raw datasets. Do not copy another research site's descriptions or results as if independently replicated.

Label selection, evaluation and forward periods accurately. Preserve dataset hashes, experiment counts and known biases. A community PR cannot run untrusted code against private data or broker credentials in CI; review code first, then run research in a controlled environment. The public checks require only synthetic fixtures and saved derived output.

Changes to broker adapters need mocked request/response tests, bounded rate handling, secret redaction and authentication-failure checks. Keep the local helper limited to history access. Strategy approval does not authorise live orders.
