# Chess profile

This profile uses two small, repository-hosted GIFs, native Markdown project entries, and still-image alternatives. No external widgets or paid services are needed. The header and calendar share a thin border, the same width, and a restrained green palette. Images are capped at 840 display pixels and shrink with GitHub's content column.

## Choose your featured projects

Edit [`profile.json`](profile.json) on GitHub. The `projects` array holds exactly three repositories, in display order:

```json
{
  "projects": [
    {"repo": "harshagarwal4761/YourFirstRepo"},
    {"repo": "harshagarwal4761/YourSecondRepo"},
    {"repo": "harshagarwal4761/YourThirdRepo"}
  ]
}
```

Use public repository names in `owner/repository` format. You can also supply optional `title` and `description` fields for custom wording. When omitted, they come from the repository's public metadata; the language is fetched automatically. Empty descriptions get a short neutral fallback.

Saving this file to `main` starts the refresh workflow. It regenerates the links and descriptions between the project markers in `README.md`, usually within a few minutes. Keep those markers intact. You may edit the rest of the README directly. This controls the README's Selected work section; GitHub's separate pinned repositories are managed through Customize your pins on your profile.

## Refresh and animation

`.github/workflows/refresh-profile.yml` runs daily at 03:23 UTC, on renderer/configuration changes, and manually from Actions → Refresh chess profile → Run workflow. It uses the built-in repository token and public GitHub metadata. Stats are daily snapshots. Keep this repository public for free standard GitHub-hosted Actions usage. GitHub may pause scheduled workflows after a long period of inactivity.

The decorative knight follows legal moves across the real contribution calendar; the generator does not invent historical contributions. GIFs use a stable palette and changed-frame compression (`disposal=1`). The knight's scan is a slow loop and the calendar avoids flashing or pulsing effects. PNG links provide a still alternative.

To run locally, use Python 3.12+, Pillow 12.3.0, and an authenticated GitHub CLI:

```sh
python scripts/render_profile.py
```

Colors, spacing, typography, and animation live in `scripts/render_profile.py`. Older artwork remains in `assets/` as an archive and is not loaded by the current README.
