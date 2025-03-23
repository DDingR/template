import os
import re


def main():
    symbols_folder_path = '/home/chackl/FORSCHUNG/Templates/include_symbols/'
    symbols_files = [
        'MySymbols_GeneralDefinitions.tex',
        'MySymbols_GeneralMath.tex',
        'MySymbols_ControlSystems.tex',
        'MySymbols_ThreePhaseSystems.tex',
        'MySymbols_GridConnection.tex',
        'MySymbols_PowerElectronics.tex',
        'MySymbols_ElectricalDrives.tex',
        'MySymbols_WindTurbines.tex',
        'MySymbols_MechatronicSystems.tex',
        'MySymbols_Friction.tex',
        'MySymbols_MPC.tex',
        'MySymbols_PowerSystems.tex',
        'MySymbols_Sensors.tex',
        'MySymbols_MultilevelConverters.tex'
    ]
    # extract path of LMRES-templates repo from mylmrestemplatespathdefinition.tex:
    with open(os.path.join(os.path.dirname(__file__), 'LMRES_PathDefinitions_Template.tex')) as f:
        for line in f:
            erg = re.findall(r'LMRESTEMPLATESPATH}{([^{]*)}', line)
            if len(erg) > 0:
                symbols_folder_path = os.path.join(erg[0], 'include_symbols')

    output = []  # list that will be written as output file
    level = 0  # used for setting section, subsection ...
    flag_tab_on = False
    for file in symbols_files:  # scan each specified file
        if os.path.isdir(os.path.join(symbols_folder_path, file)):
            pass  # folder
        elif (file.split(".")[-1] == "py"):
            pass  # py-file
        elif (file.split(".")[-1] == "tex"):
            print('extracting from ' + file)
            output.append('\clearpage \\section{' + file.replace('_', '\_') + '}')
            level = 1
            with open(os.path.join(symbols_folder_path, file)) as f:  # open file
                for line in f:  # read line in file
                    if ('newcommand' in line):  # check for "newcommand" in line
                        if (line[0] == '%'):  # skip totally comment lines
                            continue
                        if flag_tab_on:  # print \begin{longtable} if it's the first entry of a table
                            pass
                        else:
                            output.append("\\begin{longtable}{|p{6cm}|p{3cm}|p{6cm}|} \hline")
                            flag_tab_on = True  # set true if the first table's entry is printed
                        re_erg = re.findall('{([^}]*)}', line)  # find whats between the { }
                        symbol = re_erg[0]  # between the first brackets is our symbol
                        re_erg2 = re.findall('newcommand\*?[^{]*{([^%]*)}', line.replace('{'+ symbol +'}',''))
                        symbol_definition = re_erg2[0]  # between the second brackets is our symbol definition
                        code_comment_split = line.split('%')  # check if there is a comment at the end of the line
                        if (len(code_comment_split) > 1):
                            comment = code_comment_split[
                                1].strip()  # get text after % and neglect whitespaces at beginning and end
                        else:
                            comment = ''
                        # ATTENTION: COMMENTS MUST BE IN LATEX FORMAT (e.g. with symbols in math mode!)
                        # if '}' in comment:
                        #    comment = 'comment ignored'
                        # comment=comment.replace('_', '\\_')
                        # comment=comment.replace('=', '$=$')
                        # for symbol in re.findall(r"\\[a-zA-Z]+", comment):
                        #    if '$'+symbol+'$' not in comment:
                        #       comment=comment.replace(symbol, '$'+symbol+'$')
                        symbol_macro = symbol.split("\\")[1]  # without \ at the beginning
                        symbol_latex = symbol  # with \
                        num_args = re.findall('\[([0-9])\]', line)  # check for symbols with options
                        if len(num_args) > 0:
                            cnt = 0
                            for dummy_arg in gen_dummy_arg():
                                symbol_definition = symbol_definition.replace('#' + str(cnt+1), ' ' + dummy_arg)
                                cnt += 1
                                if cnt == float(num_args[0]):
                                    break
                        tab_line = symbol_macro + " & $" + symbol_definition + "$ & " + comment + " \\\\ \hline"
                        output.append(tab_line)
                    else:
                        re_erg = re.findall('%[ ]*([a-z,A-Z]+.*)', line)
                        if (len(re_erg) > 0 and line[0] == '%'):  # find a comment line -> we will take it as new heading in latex
                            if flag_tab_on:  # end table environment if needed
                                output.append('\\end{longtable}')
                                flag_tab_on = False
                            if 'START' in re_erg[0]:  # if we find START in line, it will be a heading
                                re_erg = re.findall('% *([a-zA-Z]+.*[a-zA-Z]+).*START',
                                                    line)  # take only the comment without START and %
                                headline = re_erg[0].replace('_', '\\_')
                                headline = re_erg[0].replace('+-', 'plus-minus')
                                if level == 1:
                                    output.append('\\subsection{' + headline + '}')
                                    level += 1
                                else:
                                    output.append('\\subsubsection{' + headline + '}')
                                    level += 1
                            elif 'END' in re_erg[0]:  # END in line closes a heading hierarchy
                                level -= 1
                            else:  # just a comment line without START or END
                                headline = re_erg[0].replace('_', '\\_')
                                headline = headline.replace('+-', 'plus-minus')
                                if level == 1:  # maximum depth is level = 3: paragraph
                                    output.append('\\subsection{' + headline + '}')
                                elif level == 2:  # maximum depth is level = 2: subsubsection
                                    output.append('\\subsubsection{' + headline + '}')
                                else:
                                    output.append('\\paragraph{' + headline + '}')
        if flag_tab_on:  # close table environment at the end of each file
            output.append('\\end{longtable}')
            flag_tab_on = False
    with open("LMRES_Table_of_Symbols.tex", "w") as outfile:  # write output to file
        outfile.write("\n".join(output))

def gen_dummy_arg():
    """
    Returns a character that is used as dummy argument.
    """
    for i in sorted('abcdefghijklmnopqrstuvwxyz', reverse=True):
        yield i


if __name__ == '__main__':
    main()
