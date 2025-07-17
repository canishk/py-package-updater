import argparse

from py_package_upgrader.core import PyPackageUpgrader

def main():
    parser = argparse.ArgumentParser(description="Auto clean and upgrade Python packages.")
    parser.add_argument('--file', type=str, default='requirements.txt', help='Path to the requirements file.')
    parser.add_argument('--project', type=str, default='.', help='Path to the project directory.')
    parser.add_argument('--only', help="Comma-separated list of packages to upgrade only")
    parser.add_argument('--exclude',  help="Comma-separated list of packages to exclude")
    parser.add_argument('--dry-run', action='store_true', help='Perform a dry run without making changes.')
    parser.add_argument('--clean-only', action='store_true', help='Only clean unused packages without upgrading.')

    args = parser.parse_args()
    only = args.only.split(",") if args.only else None
    exclude = args.exclude.split(",") if args.exclude else None

    upgrader = PyPackageUpgrader(
        requirements_txt=args.file,
        project_path=args.project,
        only=only,
        exclude=exclude,
        dry_run=args.dry_run,
        clean_only=args.clean_only
    )
    
    upgrader.main()


if __name__ == "__main__":
    main()