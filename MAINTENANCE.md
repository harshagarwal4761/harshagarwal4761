# Chess profile

All images are generated in this repository. There are no paid widgets, image services, or subscriptions.

The workflow in `.github/workflows/refresh-profile.yml` runs daily at 03:23 UTC (08:53 India time), or manually from Actions → Refresh chess profile → Run workflow. It uses a standard GitHub-hosted runner in this public repository, which GitHub provides free. Keep it public to retain that free hosting arrangement.

The workflow uses the built-in repository token; no personal access token is required. It queries public repository totals, follower counts, and GitHub's contribution calendar. Counts are a daily snapshot, not a live counter. GitHub may pause scheduled workflows after 60 days of repository inactivity; they can be re-enabled in Actions.

The knight is decorative and follows legal knight moves across the activity calendar. The renderer never creates or modifies historical contributions. The generator's bot commits may appear in repository history as normal refresh commits.

Edit `README.md` for wording and project links. Edit `scripts/render_profile.py` for card colors, headings, and animation. The PNG versions provide still alternatives to each GIF. The original banner is retained in `assets/chess-banner.*`.

To generate locally, install Python 3.12+, Pillow 12.3.0, and the GitHub CLI, sign in with `gh auth login`, then run `python scripts/render_profile.py`.

GitHub references:
- https://docs.github.com/en/billing/concepts/product-billing/github-actions
- https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule
