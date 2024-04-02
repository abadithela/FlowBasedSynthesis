'''
Script to create a logger that saves data at various points of the experiment
'''
import os
import json
import csv
from pdb import set_trace as st
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
            self.opt_data_file = f"{self.folder_name}/opt_data.json"
            self.setup_files()
  
    def setup_files(self):
        self.write_to_csv_file(self.problem_data_file, self.exp_name, self.exp_time)
        self.append_to_csv_file(self.problem_data_file, "Object", "Value")
        self.write_to_csv_file(self.runtime_data_file, "Process", "Runtime (s)")
    
    def save_optimization_data(self, data, fn=None):
        
        if fn:
            with open(f'{self.folder_name}/{fn}.json', 'w') as fp:
                json.dump(data, fp)
        else:
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
    
    def read_data_from_csv_file(self, file, data):
        with open(file, 'r') as csv_file:
            reader = csv.reader(csv_file)
            # Add rows
            for row in reader:
                for k in data:
                    if k in row:
                        self.runtime_dict[k] = str(row[-1])
    
    def read_data_from_json_file(self, file, data):
        with open(file, 'r') as f:
            content = json.load(f)
            # Add rows
            for key, val in content.items():
                for k in data:
                    if k == key:
                        self.runtime_dict[k] = str(val)

    def print_table(self, save=True, dynamic=False):
        '''
        For dynamic examples, we save a few extra variables
        '''
        latex_code = ""
        prob_data_columns = ["Buchi (Product)", "Transition System", "Gsys", "G"]
        if dynamic:
            graph_runtime_columns = ["b_prod", "Gsys", "G","Tester Controller"]
        else:
            graph_runtime_columns = ["b_prod", "Gsys", "G"]
        if dynamic:
            opt_columns = ["runtime", "n_bin_vars", "n_cont_vars", "n_constrs","n_cex", "flow", "ncuts"]
        else:
            opt_columns = ["runtime", "n_bin_vars", "n_cont_vars", "n_constrs","flow", "ncuts"]
        self.runtime_dict = dict()
        for k in prob_data_columns:
            self.runtime_dict[k] = None
            
        for k in graph_runtime_columns:
            self.runtime_dict[k] = None

        for k in opt_columns:
            self.runtime_dict[k] = None
        try:
            latex_code +=  " & ".join(list(self.runtime_dict.keys())) + " \\\\\n"
        except:
            st()

        self.read_data_from_csv_file(self.problem_data_file, prob_data_columns)
        self.read_data_from_csv_file(self.runtime_data_file, graph_runtime_columns)
        self.read_data_from_json_file(self.opt_data_file, opt_columns)
        
        latex_code += " & ".join(list(self.runtime_dict.values())) + " \\\\\n"
        latex_code += "\\hline\n"

        if save:
            with open(f"{self.folder_name}/experiment_table.txt", "w") as fp:
                fp.write(latex_code)
        return latex_code


