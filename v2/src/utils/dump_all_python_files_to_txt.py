import os

def dump_all_python_files_to_txt(root_dir, output_file="project_dump.txt"):
    with open(output_file, "w", encoding="utf-8") as out:
        for dirpath, _, filenames in os.walk(root_dir):
            for filename in filenames:
                if filename.endswith(".py"):
                    file_path = os.path.join(dirpath, filename)
                    relative_path = os.path.relpath(file_path, root_dir)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        out.write(f"\n# === FILE: {relative_path} ===\n")
                        out.write(content)
                        out.write("\n" + "=" * 80 + "\n")
                    except Exception as e:
                        out.write(f"\n# === ERROR reading {relative_path}: {e} ===\n")

    print(f"[DONE] Python files saved to: {output_file}")

# Run the script for your current project
if __name__ == "__main__":
    dump_all_python_files_to_txt(root_dir=".")
