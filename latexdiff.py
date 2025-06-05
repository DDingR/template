"""
latexdiff.py
- COMMIT1: new commit hash.
- COMMIT2: old commit hash.

OUTPUT:
- diff.pdf

- Myeongseok Ryu
- dding_98@kaist.ac.kr
- 2025.04.14
"""

import os
import subprocess
import glob

TEX_FILE_NAME = "manuscript.tex"
CURRENT_DIR = os.getcwd()

SAVE_DIR = "."

def run_terminal_command(command):
    print(f"$ {command}")
    result = os.system(f"{command}")
    # result = subprocess.run([f"{command}"], cwd={CURRENT_DIR}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if result != 0:
        raise RuntimeError(f"Command '{command}' failed with exit code {result}. Please check the command and try again.")
    

def compile_tex(file_name):
    run_terminal_command(f"pdflatex -interaction=batchmode {file_name}")
    run_terminal_command(f"bibtex {file_name[:-4]}.aux")
    run_terminal_command(f"pdflatex -interaction=batchmode {file_name}")
    run_terminal_command(f"pdflatex -interaction=batchmode {file_name}")

def clean_up():
    print("Cleaning up...")

    file_list = ["tmp1.tex", "tmp2.tex", "diff.tex", "tmp1.pdf", "tmp2.pdf", "*.aux", "*.log", "*.out", "*.bbl", "*.blg", "*.run.xml", "*.toc", "*.synctex.gz", "*.fdb_latexmk", "*.fls", "*.spl", "*.dvi"]
    for file in file_list:
        if glob.glob(os.path.join(CURRENT_DIR, file)):
            run_terminal_command(f"cd \"{CURRENT_DIR}\" && rm {file}")
        else:
            # print(f"File {file} does not exist, skipping removal.")
            pass

    print("Cleanup complete.")
    
def main():
    print(f"""  
╔═══════════════════════════════════════════════╗
║             LaTeXDiff Visualizer              ║
║         Git-based LaTeX Difference Tool       ║
╠═══════════════════════════════════════════════╣
║ Developed by Myeongseok Ryu on April 14, 2025 ║
║ Contact: dding_98@kaist.ac.kr                 ║
║ Version 1.1 (Date: May 25, 2025)              ║   
╚═══════════════════════════════════════════════╝

DISCRIPTION:
  - Compare your LaTeX documents across Git commits
    and visualize the changes with elegance.
          
Let's begin! (Your running in {CURRENT_DIR})
        """)

    try:
        # -----------------------------
        # Get input arguments
        # -----------------------------
        tex_file_name = input(f"Enter the tex file name (default: {TEX_FILE_NAME}): ")

        if tex_file_name == "":
            tex_file_name = TEX_FILE_NAME

        print(f"""  
OPTIONS:
  - r: current working tree (unsaved changes)
  - h: HEAD (latest commit)
  - p: previous commit of selected one

    """)

        commit1     = input(f"Enter the first commit hash of new one (r/h/SHA): ")
            
        if commit1 == "":
            raise ValueError("Please enter the commit hash.")
        elif commit1 == "p":
            raise ValueError("option p is not available for the first commit.")
        elif commit1 == "h":
            commit1 = "HEAD"
        elif commit1 == "r":
            commit1 = "r"
        
        commit2     = input(f"Enter the second commit hash of old one (h/p/SHA): ")

        if commit2 == "":
            raise ValueError("Please enter the second commit hash.")
        elif commit2 == "p":
            if commit1 == "r":
                commit2 = subprocess.check_output(["git", "rev-parse", "HEAD^"]).decode("utf-8").strip()
            else:
                commit2 = subprocess.check_output(["git", "rev-parse", f"{commit1}^"]).decode("utf-8").strip()
        elif commit2 == "h":
            commit2 = "HEAD"

        print(f"""
╔═══════════════════════════════════════════════╗
║                 Confirmation                  ║
╠═══════════════════════════════════════════════╣             
║ You have selected:                            ║
║  - New commit: {commit1}                      
║  - Old commit: {commit2}                      
║  - LaTeX file: {tex_file_name}                
╚═══════════════════════════════════════════════╝

Please confirm the above information is correct and press Enter to continue or Ctrl+C to exit.
""")    
        input("Press Enter to continue...")

        # -----------------------------
        # checkout the commit
        # -----------------------------
        if commit1 == "r":
            run_terminal_command(f"cp {tex_file_name} tmp1.tex")
        else:
            run_terminal_command(f"git show {commit1}:{tex_file_name} > tmp1.tex")
            run_terminal_command(f"git show {commit1}:{tex_file_name} > tmp1.tex")

        run_terminal_command(f"git show {commit2}:{tex_file_name} > tmp2.tex")

        # compile_tex("tmp1.tex")
        # compile_tex("tmp2.tex")
        run_terminal_command(f"latexdiff --flatten tmp2.tex tmp1.tex > diff.tex")
        compile_tex("diff.tex")

        # -----------------------------
        # Terminate the process and Clean up
        # -----------------------------
        print("\n")
        print("Successfully generated the diff.tex file and compiled it to PDF.")
        clean_up()

        print(f"""
╔═══════════════════════════════════════════════╗
║             Successfully Generated!           ║
╠═══════════════════════════════════════════════╣             
║ The LaTeX diff PDF file is ready:             ║
║  - {CURRENT_DIR}/diff.pdf                
║ All temporary files have been cleaned up.     ║
╚═══════════════════════════════════════════════╝
""")

        print("Done! ")
    
    except Exception as e:
        print(f"""
╔═══════════════════════════════════════════════╗
║         Failed to Generate LaTeX Diff!        ║
╠═══════════════════════════════════════════════╣             
║ An error occurred:                            ║   
║   - {e}                                      
║ All temporary files have been cleaned up.     ║
╠═══════════════════════════════════════════════╣
║ Please check the input and try again.         ║
║ If the problem persists, please contact the   ║
║ developer at the email below.                 ║
║   - Myeongseok Ryu (dding_98@kaist.ac.kr)     ║
╚═══════════════════════════════════════════════╝
""")
        clean_up()

if __name__ == "__main__":
    main()