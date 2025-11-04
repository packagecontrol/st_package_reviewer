# PR Channel Action

This composite action diffs a Package Control channel registry between a PR’s base and head commits, crawls only the changed and added packages using your thecrawl, downloads each release archive, and runs `st_package_reviewer` on the extracted contents. The job fails if any crawl, download, unzip, or review step fails.

## Inputs

- `pr` (required): Full PR URL, e.g. `https://github.com/wbond/package_control_channel/pull/9236`.
- `file` (optional): Path to the channel or repository file inside the repo. Default: `repository.json`.
- `thecrawl` (optional): Path to a local `thecrawl` repo, or a git URL to clone a fork/branch/commit. Default: `https://github.com/packagecontrol/thecrawl`

You can pin a ref with `@ref` for HTTPS URLs, e.g.:
  - `https://github.com/packagecontrol/thecrawl.git@feature-branch`
  - `https://github.com/packagecontrol/thecrawl.git@v1.2.3`
  - `https://github.com/packagecontrol/thecrawl.git@abc1234`

## Example Usage

```yaml
name: Channel Diff and Review
on:
  pull_request:
    paths:
      - 'repository.json'

jobs:
  diff-and-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Diff and review changed/added packages
        uses: ./gh_action
        with:
          pr: ${{ github.event.pull_request.html_url }}
          file: repository.json
          # thecrawl: ../thecrawl                      # optional path
          # thecrawl: https://github.com/packagecontrol/thecrawl@my-branch   # optional URL with ref
```

## Notes

- The action ensures `uv` is available via `astral-sh/setup-uv`. GitHub’s hosted runners include `gh` (GitHub CLI) by default.
- If `thecrawl` is not provided, the action clones `https://github.com/packagecontrol/thecrawl`.
- Network access is required to fetch raw files, zipballs, and the GitHub API. For GitHub zipball downloads, the action falls back to `gh api` if `curl` fails.


## What It Does

- Resolves base/head repos and SHAs via `gh pr view`.
- Builds a registry JSON at both SHAs using your local or cloned `thecrawl` (`uv run -m scripts.generate_registry`).
- Diffs registries by package name; prints Removed/Changed/Added to stderr and emits changed+added names to stdout.
- For each changed/added package:
  - Runs `uv run -m scripts.crawl --registry <target-registry> --workspace <ws.json> --name <pkg>`.
  - Reads the workspace JSON and downloads each release zip.
  - Unpacks the zip and runs `uv run st_package_reviewer <extracted_dir>`.
  - Aggregates failures and fails the job if any occurred.
