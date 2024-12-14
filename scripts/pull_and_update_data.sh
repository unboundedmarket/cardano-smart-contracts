#!/bin/bash

# data
CSV_FILE="repositories.csv"

# check if file exists
if [ ! -f "$CSV_FILE" ]; then
    echo "Error: $CSV_FILE not found!"
    exit 1
fi

check_repo_public() {
    local repo_url=$1
    local status_code=$(curl -s -o /dev/null -w "%{http_code}" -L "$repo_url")
    echo "Status code: $status_code"
    if [ "$status_code" -eq 200 ]; then
        return 0
    else
        return 1
    fi
}

# Read repositories from CSV file
tail -n +2 "$CSV_FILE" | while IFS=',' read -r language github_url base_dir; do
    github_url=$(echo "$github_url" | xargs)
    base_dir=$(echo "$base_dir" | xargs)

    if [ -z "$github_url" ] || [ -z "$base_dir" ]; then
        continue
    fi

    # Extract repo name
    repo_name=$(basename -s .git "$github_url")

    # Target path
    full_path="$base_dir/$repo_name"

    echo "Checking if $github_url is available."
    if ! check_repo_public "$github_url"; then
        echo "Warning: Repoy $github_url not available. Skip."
        continue
    fi

    # check naming conflicts
    if [ -d "$full_path" ]; then
        echo "Repository $repo_name already exists at $full_path. Skip."
        continue
    fi

    # create if base dir doesn't exist
    if [ ! -d "$base_dir" ]; then
        mkdir -p "$base_dir"
    fi

    # Clone
    echo "Cloning $github_url into $full_path..."
    git clone "$github_url" "$full_path"
done