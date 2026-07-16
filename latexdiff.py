"""
latexdiff.py
- COMMIT1: new commit hash.
- COMMIT2: old commit hash.
- Local file comparison is also supported.

OUTPUT:
- diff_COMMIT1_COMMIT2.pdf
- diff_LOCAL1_LOCAL2.pdf for local file comparison

VERSION HISTORY:
- Version 1.0 (Date: 2025.04.14)
    - Initial release of the LaTeX diff tool.
    - Supports comparing LaTeX documents across Git commits.
    - Generates a PDF file showing the differences.
- Version 1.1 (Date: 2025.05.25)
    - fix some bugs.
- Version 1.2 (Date: 2025.06.08)
    - The output file name is now COMMIT1_COMMIT2.pdf
    - So, you can recognize which commits are compared.
- Version 1.3 (Date: 2025.06.23)
    - When fail to finish the program, diff.tex will remain in the current directory.
    - You can compile it manually.
- Version 2.0 (Date: 2025.08.07)
    - Windows compatibility.
- Version 2.1
    - Add local file selection option.
- Myeongseok Ryu
- dding_98@kaist.ac.kr
- 2025.04.14
"""

import os
import subprocess
import glob
import shutil

TEX_FILE_NAME = "manuscript.tex"
CURRENT_DIR = os.getcwd()
SAVE_DIR = "."


def run_terminal_command(command, shell=True):
    print(f"$ {command}")
    result = subprocess.run(command, shell=shell)
    if result.returncode != 0:
        raise RuntimeError(f"Command '{command}' failed with exit code {result.returncode}.")


def compile_tex(file_name):
    run_terminal_command(f"pdflatex -interaction=batchmode {file_name}")
    run_terminal_command(f"bibtex {file_name[:-4]}.aux")
    run_terminal_command(f"pdflatex -interaction=batchmode {file_name}")
    run_terminal_command(f"pdflatex -interaction=batchmode {file_name}")


def clean_up():
    print("Cleaning up...")

    patterns = [
        "tmp1.tex", "tmp2.tex", "tmp1.pdf", "tmp2.pdf",
        "*.aux", "*.log", "*.out", "*.bbl", "*.blg", "*.run.xml",
        "*.toc", "*.synctex.gz", "*.fdb_latexmk", "*.fls", "*.spl", "*.dvi"
    ]

    for pattern in patterns:
        for file_path in glob.glob(os.path.join(CURRENT_DIR, pattern)):
            try:
                os.remove(file_path)
            except Exception:
                pass

    print("Cleanup complete.")


def select_local_file(prompt_msg="Select a LaTeX file"):
    """
    Select a local .tex file using tkinter file dialog.
    If tkinter is unavailable, fall back to manual path input.
    """
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        file_path = filedialog.askopenfilename(
            title=prompt_msg,
            filetypes=[
                ("LaTeX files", "*.tex"),
                ("All files", "*.*")
            ]
        )

        root.destroy()

        if not file_path:
            raise ValueError("No local file was selected.")

        return file_path

    except Exception as e:
        print(f"File dialog unavailable or canceled: {e}")
        file_path = input(f"{prompt_msg}. Enter local tex file path manually: ").strip().strip('"')
        if not file_path:
            raise ValueError("No local file path was entered.")
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Local file does not exist: {file_path}")
        return file_path


def write_git_file_to_tmp(commit_hash, tex_file_name, tmp_file_name):
    content = subprocess.check_output(
        ["git", "show", f"{commit_hash}:{tex_file_name}"]
    ).decode("utf-8", errors="replace")

    with open(tmp_file_name, "w", encoding="utf-8") as f:
        f.write(content)


def copy_local_file_to_tmp(local_file_path, tmp_file_name):
    if not os.path.isfile(local_file_path):
        raise FileNotFoundError(f"Local file does not exist: {local_file_path}")

    shutil.copyfile(local_file_path, tmp_file_name)


def safe_name_from_source(source):
    """
    Make source name safe for output file.
    """
    if source == "r":
        return "WORKTREE"
    if source == "HEAD":
        return "HEAD"
    if source.startswith("LOCAL:"):
        base = os.path.basename(source.replace("LOCAL:", ""))
        base = os.path.splitext(base)[0]
        return f"LOCAL_{base}"

    return source[:6]


def main():
    print(f"""  
╔═══════════════════════════════════════════════╗
║             LaTeXDiff Visualizer              ║
║         Git-based LaTeX Difference Tool       ║
╠═══════════════════════════════════════════════╣
║ Developed by Myeongseok Ryu on April 14, 2025 ║
║ Contact: dding_98@kaist.ac.kr                 ║
║ Version 2.1                                   ║
╚═══════════════════════════════════════════════╝

DESCRIPTION:
  - Compare your LaTeX documents across Git commits.
  - Compare current working tree with Git commits.
  - Compare selected local LaTeX files.

Let's begin! (You're running in {CURRENT_DIR})
""")

    commit1 = ""
    commit2 = ""
    save_tex = "diff_failed.tex"

    try:
        tex_file_name = input(f"Enter the tex file name in Git repository (default: {TEX_FILE_NAME}): ").strip() or TEX_FILE_NAME

        print("""
OPTIONS:
  - r: current working tree, using the tex file path above
  - h: HEAD, latest commit
  - p: previous commit of selected first source
  - f: select local tex file
  - SHA: specific Git commit hash
""")

        commit1 = input("Enter the first source of new one (r/h/f/SHA): ").strip()

        if not commit1:
            raise ValueError("Please enter the first source.")
        elif commit1 == "p":
            raise ValueError("option p is not available for the first source.")
        elif commit1 == "h":
            commit1 = "HEAD"
        elif commit1 == "f":
            local_file_1 = select_local_file("Select NEW LaTeX file")
            commit1 = "LOCAL:" + local_file_1
        elif commit1 == "r":
            pass
        else:
            pass

        commit2 = input("Enter the second source of old one (h/p/f/SHA): ").strip()

        if not commit2:
            raise ValueError("Please enter the second source.")
        elif commit2 == "p":
            if commit1.startswith("LOCAL:"):
                raise ValueError("option p is not available when the first source is a local file.")
            base_commit = "HEAD" if commit1 == "r" else commit1
            commit2 = subprocess.check_output(
                ["git", "rev-parse", f"{base_commit}^"]
            ).decode().strip()
        elif commit2 == "h":
            commit2 = "HEAD"
        elif commit2 == "f":
            local_file_2 = select_local_file("Select OLD LaTeX file")
            commit2 = "LOCAL:" + local_file_2
        else:
            pass

        print(f"""
╔═══════════════════════════════════════════════╗
║                 Confirmation                  ║
╠═══════════════════════════════════════════════╣             
║ You have selected:                            ║
║  - New source: {commit1}
║  - Old source: {commit2}
║  - Git LaTeX file path: {tex_file_name}
╚═══════════════════════════════════════════════╝

Please confirm the above information is correct and press Enter to continue or Ctrl+C to exit.
""")
        input("Press Enter to continue...")

        # Prepare new file as tmp1.tex
        if commit1 == "r":
            shutil.copyfile(tex_file_name, "tmp1.tex")

        elif commit1.startswith("LOCAL:"):
            copy_local_file_to_tmp(commit1.replace("LOCAL:", ""), "tmp1.tex")

        else:
            write_git_file_to_tmp(commit1, tex_file_name, "tmp1.tex")

        # Prepare old file as tmp2.tex
        if commit2.startswith("LOCAL:"):
            copy_local_file_to_tmp(commit2.replace("LOCAL:", ""), "tmp2.tex")

        else:
            write_git_file_to_tmp(commit2, tex_file_name, "tmp2.tex")

        # create diff.tex
        # run_terminal_command("latexdiff --flatten tmp2.tex tmp1.tex > diff.tex")
        run_terminal_command("latexdiff --flatten --math-markup=off tmp2.tex tmp1.tex > diff.tex")
        # run_terminal_command("latexdiff --flatten --math-markup=whole tmp2.tex tmp1.tex > diff.tex")
        compile_tex("diff.tex")

        new_name = safe_name_from_source(commit1)
        old_name = safe_name_from_source(commit2)
        save_PDF = f"diff_{new_name}_{old_name}.pdf"

        shutil.move("diff.pdf", save_PDF)

        print("\nSuccessfully generated the diff.tex file and compiled it to PDF.")
        clean_up()

        print(f"""
╔═══════════════════════════════════════════════╗
║             Successfully Generated!           ║
╠═══════════════════════════════════════════════╣             
║ The LaTeX diff PDF file is ready:             ║
║  - {os.path.join(CURRENT_DIR, save_PDF)}
║ All temporary files have been cleaned up.     ║
╚═══════════════════════════════════════════════╝
""")

        print("Done!")

    except Exception as e:
        print(f"""
╔═══════════════════════════════════════════════╗
║         Failed to Generate LaTeX Diff!        ║
╠═══════════════════════════════════════════════╣             
║ An error occurred:                            ║   
║   - {e}
╠═══════════════════════════════════════════════╣
║ If diff.tex exists, it will be saved for      ║
║ manual compilation.                           ║
╚═══════════════════════════════════════════════╝
""")

        try:
            new_name = safe_name_from_source(commit1) if commit1 else "NEW"
            old_name = safe_name_from_source(commit2) if commit2 else "OLD"
            save_tex = f"diff_{new_name}_{old_name}.tex"

            if os.path.exists("diff.tex"):
                shutil.move("diff.tex", save_tex)
                print(f"Saved the diff file as {save_tex} for manual compilation.")
            else:
                print("diff.tex was not generated.")
        except Exception as save_error:
            print(f"Failed to preserve diff.tex: {save_error}")

        clean_up()


if __name__ == "__main__":
    main()