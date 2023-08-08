"""
Support function for generating a latex table from a pandas dataframe
This function negates the need for additional dependencies
"""

########################################################################################
def print_latex(df, title):
    column_names = df.columns
    format_str = "l" + ("|r" * (len(column_names)-1))
    print("\\begin{table}[h!]")
    print(" \\begin{center}")
    print("   \\caption{" + title + "}")
    print("   \\label{tab:projit_table}")
    print("   \\begin{tabular}{" + format_str + "} ")
    print("   \\hline")
    headers = "    "
    first = True
    for col in column_names:
        if first:
            headers = headers + "\t " + clean_data_for_latex(col)
        else:
            headers = headers + "\t& " + clean_data_for_latex(col)
        first = False
    headers = headers + "\\\\"
    print(headers)
    print("   \\hline")
    for i in range(len(df)):
        row = "      "
        first = True
        for col in column_names:
            if first:
                row = row + "\t" + clean_data_for_latex(df.loc[i,col])
            else: 
                row = row + "\t&" + clean_data_for_latex(df.loc[i,col])
            first = False
        row = row +  "\\\\"
        print(row)
    print("    \\end{tabular}")
    print("  \\end{center}")
    print("\\end{table}")


def clean_data_for_latex(input):
    """
    This utility function is required because some strings might contain LaTeX special
      characters, and therefor need to be escaped before latex rendering will function.
    """
    strdata = str(input)
    strdata = strdata.replace("%","\\%")
    strdata = strdata.replace("$","\\$")
    strdata = strdata.replace("#","\\#")
    strdata = strdata.replace("^","\\^")
    strdata = strdata.replace("&","\\&")
    strdata = strdata.replace("_","\\_")
    strdata = strdata.replace("{","\\{")
    strdata = strdata.replace("}","\\}")
    return strdata


