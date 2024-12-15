import os
from typing import Set


def collect_files_by_category(files: Set[str], keywords: Set[str]) -> Set[str]:
    """
    Collect files with filter keywords in their paths.

    Args:
        files (Set[str]): file paths.
        keywords (Set[str]): Keywords to search

    Returns:
        Set[str]: Filtered set of files
    """
    return {
        file for file in files if any(keyword in file.lower() for keyword in keywords)
    }


def process_language_directory(lang_dir: str, lang: str, filter_keywords: dict) -> dict:
    """
    Process files for given language

    Args:
        lang_dir (str): Path to language directory.
        lang (str): Language name
        filter_keywords (dict): Keywords to filter

    Returns:
        dict: Dict with filtered file counts and sets.
    """
    lang_code_files = set()
    language_repositories = set([f"data/{lang}" + dir for dir in os.listdir(lang_dir)])
    for root, _, files in os.walk(lang_dir):
        for file_name in files:
            if file_name.endswith("." + lang):
                lang_code_files.add(os.path.join(root, file_name))

    categorized_files = {category: set() for category in filter_keywords}
    remaining_files = lang_code_files.copy()
    for category, keywords in filter_keywords.items():
        categorized_files[category] = collect_files_by_category(
            remaining_files, keywords
        )
        remaining_files -= categorized_files[category]

    lang_filtered_code_files = remaining_files
    total_removed_files = set().union(*categorized_files.values())
    removed_files_count = len(total_removed_files)

    print(f"Language: {lang}")
    print(f"  Total repositories: {len(language_repositories)}")
    print(f"  Total code files: {len(lang_code_files)}")
    for category, files in categorized_files.items():
        print(f"  {category.capitalize()} files: {len(files)}")
    print(f"  Filtered code files: {len(lang_filtered_code_files)}")
    print(f"  Total removed files: {removed_files_count}")
    assert len(lang_code_files) == removed_files_count + len(
        lang_filtered_code_files
    ), "Mismatch: Total files != Filtered + Removed"
    print("-" * 40)
    return {
        "code_files": lang_code_files,
        "filtered_code_files": lang_filtered_code_files,
        "repositories": language_repositories,
        **categorized_files,
    }


def process_contracts_in_directory(dir_base_path: str, filter_keywords: dict) -> None:
    """
    Obtain stats about contracts in given directory.

    Args:
        dir_base_path (str): Base directory path
    """
    if not os.path.isdir(dir_base_path):
        print(f"Error: Directory '{dir_base_path}' does not exist.")
        return

    # Initialize overall counters
    all_files = {
        "code_files": set(),
        "filtered_code_files": set(),
        "repositories": set(),
    }
    for category in filter_keywords:
        all_files[category] = set()

    for lang in os.listdir(dir_base_path):
        lang_dir = os.path.join(dir_base_path, lang)
        if not os.path.isdir(lang_dir):
            print(f"Skipping non-directory entry: {lang}")
            continue

        lang_files = process_language_directory(lang_dir, lang, filter_keywords)
        for category, files in lang_files.items():
            all_files[category].update(files)

    # Log overall results
    print("Overall Statistics:")
    print(f"Total repositories: {len(all_files['repositories'])}")
    print(f"  Total code files: {len(all_files['code_files'])}")
    for category in filter_keywords:
        print(f"  Total {category.capitalize()} files: {len(all_files[category])}")
    print(f"  Total filtered code files: {len(all_files['filtered_code_files'])}")
    print(
        f" Total removed files: {len(all_files['code_files']) - len(all_files['filtered_code_files'])}"
    )


def main():
    data_dir = "data"
    filter_keywords = {
        "test": {"test"},
        "utility": {"util"},
        "type": {"type"},
        "config": {"config", "cfg"},
        "offchain": {"offchain"},
        "blueprint": {"blueprint"},
    }
    process_contracts_in_directory(data_dir, filter_keywords)


if __name__ == "__main__":
    main()
