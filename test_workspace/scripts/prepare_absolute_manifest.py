"""Generate an absolute-path manifest for the sample workspace."""
from pathlib import Path


def main() -> None:
    script_path = Path(__file__).resolve()
    repo_root = script_path.parents[2]
    manifests_dir = repo_root / "test_workspace" / "manifests"
    template_path = manifests_dir / "absolute_manifest.template.txt"
    output_path = manifests_dir / "absolute_manifest.txt"

    repo_root_str = str(repo_root.resolve())

    template = template_path.read_text(encoding="utf-8")
    content = template.replace("{repo_root}", repo_root_str)
    output_path.write_text(content, encoding="utf-8")

    print("Generated:", output_path)
    print("Preview:\n" + content)


if __name__ == "__main__":
    main()
