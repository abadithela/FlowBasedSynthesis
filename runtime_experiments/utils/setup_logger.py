'''
Script to experiment data including runtimes. 
'''

from pdb import set_trace as st
from components.experiment_logging import ExpLogger
import os
import datetime
import numpy as np
import json

class Random_RT_Logger:
    def __init__(self, exp_name, exp_time=datetime.datetime.now(), maze_dims = [], nruns=25, obs_coverage = 15, test_type="static"):
        self.nruns = nruns
        self.exp_name = exp_name
        self.exp_time=exp_time
        self.obs_coverage = obs_coverage
        self.test_type = test_type
        self.instance_loggers = dict()
        self.folder_name = exp_name + "_" + self.test_type + "_log"
        self.maze_dims = maze_dims
        self.instance_loggers = dict()
        self.log = dict()
        self.setup_loggers()
        
    def setup_loggers(self):
        if self.maze_dims == []:
            self.instance_loggers["single_maze"] = dict()
            self.log["single_maze"] = dict()
            for k in range(1,self.nruns+1):
                instance_log_folder = f"{self.folder_name}/instance_{k}_log"
                self.instance_loggers["single_maze"][k] = ExpLogger(self.exp_name, self.exp_time, setup_files = True, folder_name=instance_log_folder)
                self.log["single_maze"] = {"num_not_solved": 0, "opt_runtimes":[], "graph_runtimes":[]}
                # self.log["single_maze"] = dict()
        else:
            for gridsize in self.maze_dims:
                self.instance_loggers[f"maze_{gridsize}"] = dict()
                self.log[f"maze_{gridsize}"] = dict()
                for k in range(1,self.nruns+1):
                    instance_log_folder = f"{self.folder_name}/gridsize_{gridsize}/instance_{k}_log"
                    self.instance_loggers[f"maze_{gridsize}"][k] = ExpLogger(self.exp_name, self.exp_time, setup_files = True, folder_name=instance_log_folder)
                    self.log[f"maze_{gridsize}"] = {"num_not_solved": 0, "opt_runtimes":[], "graph_runtimes":[]}
                    # self.log[f"maze_{gridsize}"] = dict()
    
    def get_instance_logger(self, instance, gridsize = None):
        if gridsize:
            return self.instance_loggers[f"maze_{gridsize}"][instance]
        else:
            return self.instance_loggers["single_maze"][instance]

    def set_formulas(self, sys_formula, test_formula):
        self.sys_formula = sys_formula
        self.test_formula = test_formula    

    def experiment_info_to_file(self):
        '''
        Save problem data other such as static / reactive / no. of runs / obs_coverage / 
        and the grid sizes / specification type.
        '''
        with open(f"{self.folder_name}/experiment_data.txt", "w") as f:
            f.write("No. of random Instances: ", self.nruns, "\n")
            f.write("Obstacle coverage: ", self.obs_coverage, "\n")
            f.write("Test type: ", self.test_type, "\n")
            f.write("Mazes: ", self.maze_dims,"\n")
            #f.write("INTS: ", self.ints,"\n")
            f.write("SYS_FORMULA: ", self.sys_formula,"\n")
            f.write("TEST_FORMULA: ", self.test_formula,"\n")

    def add_solve_status(self, gridsize, exit_status):
        if gridsize in self.maze_dims:
            log = self.log[f"maze_{gridsize}"]
        else:
            log = self.log["single_maze"]

        if exit_status == 'not solved':
            print('Not solved')
            log["num_not_solved"] += 1
        
    def compute_runtime_metrics(self, gridsize=None):
        if gridsize:
            self.log[f"maze_{gridsize}"]["avg_opt_rt"] = np.mean(self.log[f"maze_{gridsize}"]['opt_runtimes'])
            self.log[f"maze_{gridsize}"]["std_opt_rt"] = np.std(self.log[f"maze_{gridsize}"]['opt_runtimes'])
            self.log[f"maze_{gridsize}"]["avg_graph_rt"] = np.mean(self.log[f"maze_{gridsize}"]['graph_runtimes'])
            self.log[f"maze_{gridsize}"]["std_graph_rt"] = np.std(self.log[f"maze_{gridsize}"]['graph_runtimes'])
        else:
            self.log["single_maze"]["avg_opt_rt"] = np.mean(self.log["single_maze"]['opt_runtimes'])
            self.log["single_maze"]["std_opt_rt"] = np.std(self.log["single_maze"]['opt_runtimes'])
            self.log["single_maze"]["avg_graph_rt"] = np.mean(self.log["single_maze"]['graph_runtimes'])
            self.log["single_maze"]["std_graph_rt"] = np.std(self.log["single_maze"]['graph_runtimes'])
    
    def save_experiment_data(self):
        for size in self.maze_dims:
            self.compute_runtime_metrics(size)

        with open(f'{self.folder_name}/runtime_data.json', 'w') as fp:
            json.dump(self.log, fp)

    def print_to_table(self):
        print_runtime_in_latex_table(self.folder_name, self.log)

def setup_logger(exp_name, maze_dims=[], test_type="static", nruns=25, obs_coverage=15):
    logger = Random_RT_Logger(exp_name, maze_dims = maze_dims, nruns=nruns, obs_coverage = obs_coverage, test_type=test_type)
    return logger

# \begin{tabular}{lSSSS}
# \toprule
# & \multicolumn{2}{c}{A} & \multicolumn{2}{c}{Most Mon} \\
# \cmidrule(r){2-3}\cmidrule(l){4-5}
# Methods & {Time [\si{\second}]} & {RunCount}  & {Time [\si{\second}]} & {RunCount} \\
# \midrule
# C & 12.3 & 5 & 34.6 & 7 \\
# D & 1.35 & 5 & 4.93 & 7 \\
# \bottomrule
# \end{tabular}

def print_runtime_in_latex_table(folder_name, runtime_data):
    runtime_data_file = f"{folder_name}/runtime_data.json"
    runtime_latex_output_file = f"{folder_name}/runtime_table.txt"
    with open(runtime_data_file, 'r') as f:
        runtime_data = json.load(f)
    columns = list(runtime_data.keys())
    num_columns = len(columns)*3 # One for each element (no.solved, graph runtimes, opt runtimes)
    
    latex_code = ""
    top_column_code = ""
    for maze in columns:
        top_column_code += "& \\multicolumn{"+"3}{c" +"}{"+maze[-1]+"$\\times$ "+maze[-1]+"}"
    top_column_code += " \\\\\hline\n"
    latex_code += top_column_code

    # for k in range(1, len(columns)+1):
    #     kmin = 
    #     \cmidrule(lr){2-4}
    #     \cmidrule(lr){5-7}
    #     \cmidrule(lr){8-10}
    
    latex_code += "&"
    headers = ["{Solved}", "{G}", "{Opt}"]
    latex_code += '&'.join(headers * len(columns)) + "\n\\\\\hline\n"
    
    # Add headers
    # latex_code += " & ".join(headers) + " \\\\\n\\hline\n"
    # Add rows
    row = []
    for key, data in runtime_data.items():
        num_not_solved = str(data["num_not_solved"]) 
        graph_rt =  str(format(data["avg_graph_rt"], '.4f')) + "$\,\pm\,$ " + str(format(data["std_graph_rt"], '.4f')) 
        opt_rt =  str(format(data["avg_opt_rt"], '.4f')) + "$\,\pm\,$" + str(format(data["std_opt_rt"], '.4f'))
        row.extend([num_not_solved, graph_rt, opt_rt])
    latex_code += "&"
    latex_code += " & ".join(row) + " \\\\\n"
    latex_code += "\\hline\n"
    # latex_code += "\\end{tabular}\n\\caption{Caption here}\n\\label{table:label_here}\n\\end{table}"
    with open(runtime_latex_output_file, "w") as fp:
        fp.write(latex_code)
    return latex_code
    

def print_runtime_table(log_folder):
    with open(f'{log_folder}/runtime_data.json', 'r') as fp:
        runtime_data = json.load(fp)
    print_runtime_in_latex_table(log_folder, runtime_data)


