#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<EOF
Usage: $0 --pr <pr_url> [--file <path>] [--thecrawl <path-or-url[@ref]>]

Arguments:
  --pr        GitHub Pull Request URL (e.g. https://github.com/wbond/package_control_channel/pull/9236)
  --file      Path within the repo to the channel JSON (default: repository.json)
  --thecrawl  Path to local thecrawl repo or URL to clone (supports @ref to pin, default: https://github.com/packagecontrol/thecrawl)

Requires: gh, uv
EOF
}

PR_URL=""
REL_PATH="repository.json"
THECRAWL="https://github.com/packagecontrol/thecrawl"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --pr)
      PR_URL="$2"; shift 2;;
    --file)
      REL_PATH="$2"; shift 2;;
    --thecrawl)
      THECRAWL="$2"; shift 2;;
    -h|--help)
      usage; exit 0;;
    *)
      echo "Unknown argument: $1" >&2; usage; exit 2;;
  esac
done

if [[ -z "$PR_URL" ]]; then
  echo "Error: --pr is required" >&2; usage; exit 2
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "Error: gh (GitHub CLI) is required" >&2; exit 2
fi
if ! command -v uv >/dev/null 2>&1; then
  echo "Error: uv is required" >&2; exit 2
fi

# Robust ZIP downloader with fallback to gh for GitHub zipball URLs
download_zip() {
  local url="$1" dest="$2"
  mkdir -p "$(dirname "$dest")"
  rm -f "$dest.part" "$dest"
  # First try curl with retries
  if curl -fSL --retry 3 --retry-all-errors --connect-timeout 15 --max-time 600 \
      -o "$dest.part" "$url"; then
    mv "$dest.part" "$dest"
    return 0
  fi
  rm -f "$dest.part"
  # Fallback for codeload.github.com/<owner>/<repo>/zip/<ref>
  if [[ "$url" =~ ^https://codeload\.github\.com/([^/]+)/([^/]+)/zip/(.+)$ ]]; then
    local owner="${BASH_REMATCH[1]}" repo="${BASH_REMATCH[2]}" ref="${BASH_REMATCH[3]}"
    echo "    curl failed; using gh api zipball for $owner/$repo@$ref" >&2
    if gh api -H "Accept: application/octet-stream" \
        "repos/${owner}/${repo}/zipball/${ref}" > "$dest.part"; then
      mv "$dest.part" "$dest"
      return 0
    fi
    rm -f "$dest.part"
  fi
  return 1
}

# Normalize relative path (strip leading ./)
REL_PATH="${REL_PATH#./}"

echo "::group::Fetching PR metadata"
echo "Resolving PR metadata via gh: $PR_URL" >&2

# Derive base repo from PR URL (owner/repo)
BASE_NWO=$(echo "$PR_URL" | awk -F/ '{print $4"/"$5}')
# Head repo from PR data (may be same as base)
HEAD_NWO=$(gh pr view "$PR_URL" --json headRepository -q '.headRepository.nameWithOwner')
BASE_SHA=$(gh pr view "$PR_URL" --json baseRefOid -q .baseRefOid)
HEAD_SHA=$(gh pr view "$PR_URL" --json headRefOid -q .headRefOid)

if [[ -z "$BASE_NWO" || -z "$BASE_SHA" || -z "$HEAD_SHA" ]]; then
  echo "::error ::Error: failed to resolve PR details via gh" >&2
  echo "  PR:        $PR_URL" >&2
  echo "  base nwo:  ${BASE_NWO:-<empty>}" >&2
  echo "  base sha:  ${BASE_SHA:-<empty>}" >&2
  echo "  head nwo:  ${HEAD_NWO:-<empty>} (may match base)" >&2
  echo "  head sha:  ${HEAD_SHA:-<empty>}" >&2
  echo "Hint:" >&2
  echo "  - Commands used: 'gh pr view <url> --json baseRefOid,headRefOid,headRepository'" >&2
  exit 2
fi

# Fallback: if HEAD_NWO is empty, assume same as base (same-repo PR)
if [[ -z "$HEAD_NWO" ]]; then
  HEAD_NWO="$BASE_NWO"
fi

BASE_URL="https://raw.githubusercontent.com/${BASE_NWO}/${BASE_SHA}/${REL_PATH}"
HEAD_URL="https://raw.githubusercontent.com/${HEAD_NWO}/${HEAD_SHA}/${REL_PATH}"

echo "Base URL:   $BASE_URL" >&2
echo "Target URL: $HEAD_URL" >&2
echo "::endgroup::"

# Locate or clone thecrawl
resolve_crawler_path() {
  if [[ -n "$THECRAWL" ]]; then
    if [[ "$THECRAWL" =~ ^https?:// || "$THECRAWL" =~ ^git@ ]]; then
      local repo_path="${GITHUB_WORKSPACE:-$PWD}/.thecrawl"
      # For HTTPS URLs, allow trailing @ref
      local url_base="$THECRAWL"
      local ref=""
      if [[ "$url_base" =~ ^https?://.+@.+$ ]]; then
        ref="${url_base##*@}"
        url_base="${url_base%*@$ref}"
      fi

      if [[ -d "$repo_path/.git" ]]; then
        # Existing clone: update remote and optionally checkout ref
        git -C "$repo_path" remote set-url origin "$url_base" >/dev/null 2>&1 || true
        if [[ -n "$ref" ]]; then
          echo "Checking out thecrawl ref '$ref' in $repo_path" >&2
          git -C "$repo_path" fetch --depth 1 origin "$ref" >&2
          git -C "$repo_path" checkout -q FETCH_HEAD >&2
        fi
        echo "$repo_path"; return
      fi

      if [[ -n "$ref" ]]; then
        echo "Cloning thecrawl $url_base at ref '$ref' into $repo_path" >&2
        git init -q "$repo_path" >&2
        git -C "$repo_path" remote add origin "$url_base" >&2
        git -C "$repo_path" fetch --depth 1 origin "$ref" >&2
        git -C "$repo_path" checkout -q FETCH_HEAD >&2
      else
        echo "Cloning thecrawl from $url_base into $repo_path" >&2
        git clone --depth 1 "$url_base" "$repo_path" >&2
      fi
      echo "$repo_path"; return
    fi
    echo "$THECRAWL"; return
  fi
  echo "Error: could not resolve thecrawl path" >&2
  return 2
}

echo "::group::Getting thecrawl"
CRAWLER_REPO=$(resolve_crawler_path)
if [[ ! -d "$CRAWLER_REPO" ]]; then
  echo "::error ::Error: could not find or clone thecrawl" >&2
  exit 2
fi

echo "Using thecrawl at: $CRAWLER_REPO" >&2
echo "::endgroup::"

TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

BASE_REG="$TMPDIR/base_registry.json"
HEAD_REG="$TMPDIR/head_registry.json"

echo "::group::Generating base registry…" >&2
(cd "$CRAWLER_REPO" && uv run -m scripts.generate_registry -c "$BASE_URL" -o "$BASE_REG")
echo "::endgroup::"

echo "::group::Generating target registry…" >&2
(cd "$CRAWLER_REPO" && uv run -m scripts.generate_registry -c "$HEAD_URL" -o "$HEAD_REG")
echo "::endgroup::"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# Invoke Python diff to print results and collect changed+added package names
mapfile -t PKGS < <(python3 "$SCRIPT_DIR/diff_repository.py" --base-file "$BASE_REG" --target-file "$HEAD_REG" --print-changed-added \
  | tr -d '\r' \
  | sed '/^$/d')

if [[ ${#PKGS[@]} -eq 0 ]]; then
  echo "::notice ::No changed or added packages to crawl." >&2
  exit 0
fi

echo "Crawling ${#PKGS[@]} package(s) from target registry…" >&2
failures=0
for pkg in "${PKGS[@]}"; do
  [[ -z "$pkg" ]] && continue
  echo "::group::Crawling: $pkg" >&2
  # Use workspace file output for robust parsing
  wsdir="$TMPDIR/workspaces"
  mkdir -p "$wsdir"
  wsfile="$wsdir/${pkg}.json"
  set +e
  (cd "$CRAWLER_REPO" && uv run -m scripts.crawl --registry "$HEAD_REG" --workspace "$wsfile" --name "$pkg" 2> >(cat >&2))
  STATUS=$?
  set -e
  if [[ $STATUS -ne 0 || ! -s "$wsfile" ]]; then
    echo "::error ::! Crawl failed for $pkg" >&2
    failures=$((failures+1))
    continue
  fi

  # Extract release URLs (and versions) from workspace
  mapfile -t RELS < <(python3 "$SCRIPT_DIR/parse_workspace.py" "$wsfile" "$pkg")
  if [[ ${#RELS[@]} -eq 0 ]]; then
    echo "::error  ::! No releases found for $pkg" >&2
    failures=$((failures+1))
    continue
  fi
  echo "::endgroup::"

  i=0
  for rec in "${RELS[@]}"; do
    url="${rec%%$'\t'*}"
    ver="${rec#*$'\t'}"
    # if no tab present, ver==url; fix that
    if [[ "$ver" == "$url" ]]; then ver=""; fi

    i=$((i+1))
    disp_ver="$ver"
    [[ -z "$disp_ver" ]] && disp_ver="r$i"
    # sanitize for filesystem path
    safe_ver=$(printf "%s" "$disp_ver" | tr -d '\r' | sed 's/[^A-Za-z0-9._-]/_/g')

    workdir="$TMPDIR/review/$pkg/$safe_ver"
    mkdir -p "$workdir"

    zipfile="$workdir/pkg.zip"
    echo "::group::Downloading $pkg-$disp_ver" >&2
    echo "  Downloading release $disp_ver: $url" >&2
    if ! download_zip "$url" "$zipfile"; then
      echo "::error  ::! Download failed for $pkg@$disp_ver" >&2
      failures=$((failures+1))
      continue
    fi

    echo "  Unpacking…" >&2
    # Prefer unzip; fallback to Python zipfile
    if command -v unzip >/dev/null 2>&1; then
      if ! unzip -q -o "$zipfile" -d "$workdir"; then
        echo "::error  ::! Unzip failed for $pkg@$disp_ver" >&2
        failures=$((failures+1))
        continue
      fi
    else
      python3 - "$zipfile" "$workdir" <<'PY'
import sys, zipfile, os
zf = zipfile.ZipFile(sys.argv[1])
zf.extractall(sys.argv[2])
PY
      if [[ $? -ne 0 ]]; then
        echo "::error  ::! Unzip failed for $pkg@$disp_ver (python)" >&2
        failures=$((failures+1))
        continue
      fi
    fi

    # Determine the top-level extracted directory
    topdir=$(find "$workdir" -mindepth 1 -maxdepth 1 -type d | head -n1)
    if [[ -z "$topdir" ]]; then
      echo "::error  ::! Could not locate extracted folder for $pkg@$disp_ver" >&2
      failures=$((failures+1))
      continue
    fi
    echo "::endgroup::"

    echo "::group::Reviewing $pkg-$safe_ver" >&2
    echo "  Reviewing with st_package_reviewer: $topdir" >&2
    if ! uv run st_package_reviewer "$topdir" | awk '
      /^Reporting [0-9]+ errors:/   { mode = "error";   next }
      /^Reporting [0-9]+ warnings:/ { mode = "warning"; next }
      /^- / && mode {
        sub(/^- /, "");
        print "::" mode " title=CHECK ::" $0;
        next;
      }
      { mode = ""; print }
    ';
    then
      echo "  ! Review failed for $pkg@$disp_ver" >&2
      failures=$((failures+1))
      continue
    fi
    echo "::endgroup::"
  done
done

if [[ $failures -gt 0 ]]; then
  echo "::error ::Completed with $failures failure(s)." >&2
  exit 1
else
  echo "::notice title=PASS ::Completed successfully." >&2
  exit 0
fi
