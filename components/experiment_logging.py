'''
Script to create a logger that saves data at various points of the experiment
'''
import os
import json
import csv

class ExpLogger:
    def __init__(self, exp_name, exp_time, setup_files=True, problem_data_file=None, runtime_data_file=None, folder_name="log"):
        self.exp_name = exp_name
        self.exp_time = exp_time
        self.folder_name = folder_name
        if not os.path.exists(self.folder_name):
            os.makedirs(self.folder_name)

        if setup_files:
            if problem_data_file is not None:
                self.problem_data_file = problem_data_file
            else:
                self.problem_data_file = f"{self.folder_name}/problem_data.csv"
            if runtime_data_file is not None:
                self.runtime_data_file = runtime_data_file
            else:
                self.runtime_data_file = f"{self.folder_name}/runtime_data.csv"
            self.setup_files()
  
    def setup_files(self):
        self.write_to_csv_file(self.problem_data_file, self.exp_name, self.exp_time)
        self.append_to_csv_file(self.problem_data_file, "Object", "Value")
        self.write_to_csv_file(self.runtime_data_file, "Process", "Runtime (s)")
    
    def save_optimization_data(self, data):
        with open(f'{self.folder_name}/opt_data.json', 'w') as fp:
            json.dump(data, fp)

    def write_to_csv_file(self, filepath, name, value):
        with open(filepath, 'w', newline='') as csv_file:
            csv_file_append = csv.writer(csv_file)
            csv_file_append.writerow([name, value])

    def append_to_csv_file(self, filepath, name, value):
        with open(filepath, 'a', newline='') as csv_file:
            csv_file_append = csv.writer(csv_file)
            csv_file_append.writerow([name, value])
            
    def save_runtime(self, process, runtime):
        self.append_to_csv_file(self.runtime_data_file, process, runtime)
    
    def save_data(self,name, value):
        self.append_to_csv_file(self.problem_data_file, name, value)
    
    def print_runtime_latex(self, save=True):
        latex_code = "\\begin{table}[h!]\n\\centering\n\\begin{tabular}{"

        with open(self.runtime_data_file, 'r') as csv_file:
            reader = csv.reader(csv_file)
            headers = next(reader)
            num_columns = len(headers)
            latex_code += '|'.join(['c'] * num_columns) + "}\n\\hline\n"

            # Add headers
            latex_code += " & ".join(headers) + " \\\\\n\\hline\n"

            # Add rows
            for row in reader:
                latex_code += " & ".join(row) + " \\\\\n"
            latex_code += "\\hline\n"

        latex_code += "\\end{tabular}\n\\caption{Caption here}\n\\label{table:label_here}\n\\end{table}"
        if save:
            with open("log/runtime_table.txt", "w") as fp:
                fp.write(latex_code)
        return latex_code

    def print_problem_data_latex(self, save=True):
        latex_code = "\\begin{table}[h!]\n\\centering\n\\begin{tabular}{"

        with open(self.problem_data_file, 'r') as csv_file:
            reader = csv.reader(csv_file)
            headers = next(reader)
            num_columns = len(headers)
            latex_code += '|'.join(['c'] * num_columns) + "}\n\\hline\n"

            # Add headers
            latex_code += " & ".join(headers) + " \\\\\n\\hline\n"

            # Add rows
            for row in reader:
                latex_code += " & ".join(row) + " \\\\\n"
            latex_code += "\\hline\n"

        latex_code += "\\end{tabular}\n\\caption{Caption here}\n\\label{table:label_here}\n\\end{table}"
        # print(latex_code)
        if save:
            with open("log/problem_data_table.txt", "w") as fp:
                fp.write(latex_code)
        return latex_code


