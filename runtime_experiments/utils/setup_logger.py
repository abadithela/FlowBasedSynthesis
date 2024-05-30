'''
Script to experiment data including runtimes. 
'''

from pdb import set_trace as st
from components.experiment_logging import ExpLogger
import os
import datetime
import numpy as np
import csv
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

        with open(f'{self.folder_name}/runtime_data.json', 'a') as fp:
            json.dump(self.log, fp)

    def print_to_table(self):
        print_runtime_in_latex_table(self.folder_name, self.log)

def setup_logger(exp_name, maze_dims=[], test_type="static", nruns=25, obs_coverage=15):
    logger = Random_RT_Logger(exp_name, maze_dims = maze_dims, nruns=nruns, obs_coverage = obs_coverage, test_type=test_type)
    return logger

def print_runtime_in_latex_table(folder_name, runtime_data, filename=None):
    if filename:
        runtime_data_file = f"{folder_name}/{filename}"
    else:
        runtime_data_file = f"{folder_name}/runtime_data.json"
    
    runtime_latex_output_file = f"{folder_name}/runtime_table.txt"
    runtime_data = []
    with open(runtime_data_file, 'r') as f:
        runtime_data = json.load(f)

    columns = list(runtime_data.keys())
    num_columns = len(columns)*3 # One for each element (no.solved, graph runtimes, opt runtimes)

    latex_code = ""
    header_row = []
    row = []
    for key, data in runtime_data.items():
        percent_solved = "{:.4f}".format((20 - data["num_not_solved"])/20.0*100)
        opt_rt =  str(format(data["avg_opt_rt"], '.2f')) + "$\,\pm\,$" + str(format(data["std_opt_rt"], '.2f'))
        header_row.extend(["Opt_" + key, "\% Solved_"+key])
        row.extend([opt_rt, percent_solved])
    latex_code += "&"
    latex_code += " & ".join(header_row) + " \\\\\n"
    latex_code += " & ".join(row) + " \\\\\n"

    # printing graph runtimes
    header_row = []
    row = []
    for key, data in runtime_data.items():
        graph_rt =  str(format(data["avg_graph_rt"], '.3f')) + "$\,\pm\,$ " + str(format(data["std_graph_rt"], '.3f')) 
        header_row.extend(["Graph_" + key])
        row.extend([graph_rt])
    latex_code += "&"
    latex_code += " & ".join(header_row) + " \\\\\n"
    latex_code += " & ".join(row) + " \\\\\n"

    # printing percentage that are optimal:
    header_row = []
    row = []
    for key, data in runtime_data.items():
        if data["num_not_solved"] < 20:
            percent_solved = "{:.2f}".format(data["num_opt"]/(20.0 - data["num_not_solved"])*100)
        else:
            percent_solved = "0"
        header_row.extend(["Opt_" + key])
        row.extend([percent_solved])
    latex_code += "&"
    latex_code += " & ".join(header_row) + " \\\\\n"
    latex_code += " & ".join(row) + " \\\\\n"

    # latex_code += "\\end{tabular}\n\\caption{Caption here}\n\\label{table:label_here}\n\\end{table}"
    with open(runtime_latex_output_file, "w") as fp:
        fp.write(latex_code)
    return latex_code
    

def print_runtime_table(log_folder):
    with open(f'{log_folder}/runtime_data.json', 'r') as fp:
        runtime_data = json.load(fp)
    print_runtime_in_latex_table(log_folder, runtime_data)

# Write function to read runtime dictionary and save 
def get_runtime_dict_from_log(log_folder, gridsizes):
    runtime_dict = {}
    for size in gridsizes:
        runtime_dict["maze_"+str(size)] = dict()
        runtime_dict["maze_"+str(size)]["num_not_solved"] = 0
        runtime_dict["maze_"+str(size)]["Buchi (Product)"] = []
        runtime_dict["maze_"+str(size)]["T"] = []
        runtime_dict["maze_"+str(size)]["graph_data"] = []
        runtime_dict["maze_"+str(size)]["graph_runtimes"] = []
        runtime_dict["maze_"+str(size)]["opt_runtimes"] = []
        runtime_dict["maze_"+str(size)]["num_opt"] = 0

        for inst_no in range(1, 21):
            inst_log = "instance_"+str(inst_no) + "_log"
            opt_data_file = f"{log_folder}/gridsize_{size}/{inst_log}/opt_data.json"
            prob_data_file = f"{log_folder}/gridsize_{size}/{inst_log}/problem_data.csv"
            prob_runtime_data_file = f"{log_folder}/gridsize_{size}/{inst_log}/runtime_data.csv"

            if os.path.exists(opt_data_file):
                with open(opt_data_file, "r") as f:
                    opt_data = json.load(f)
                
                # if opt_data["status"] == "not_solved" or opt_data["exit status"] == "not solved"
                if opt_data["status"] == "not_solved":
                    runtime_dict["maze_"+str(size)]["num_not_solved"] += 1
                    runtime_dict["maze_"+str(size)]["opt_runtimes"].append(600) # Timed out
                else:
                    runtime_dict["maze_"+str(size)]["opt_runtimes"].append(opt_data["runtime"])
                
                if opt_data["status"] == "optimal":
                    runtime_dict["maze_"+str(size)]["num_opt"] += 1

                with open(prob_data_file) as csv_file:
                    csv_reader = csv.reader(csv_file)
                    rows = list(csv_reader)  
                    for row in rows:
                        if "Buchi (Product)" in row:
                            runtime_dict["maze_"+str(size)]["Buchi (Product)"].append(row[-1])
                        if "Transition System" in row:  
                            runtime_dict["maze_"+str(size)]["T"].append(row[-1]) # Graph data size
                        if "G" in row:
                            runtime_dict["maze_"+str(size)]["graph_data"].append(row[-1]) # Graph data size

                with open(prob_runtime_data_file) as csv_file:
                    csv_reader = csv.reader(csv_file)
                    rows = list(csv_reader)  
                runtime_dict["maze_"+str(size)]["graph_runtimes"].append(float(rows[-1][1]))

            else:
                runtime_dict["maze_"+str(size)]["num_not_solved"] += 1
                runtime_dict["maze_"+str(size)]["opt_runtimes"].append(600) # Timed out
                print("Instance ", inst_no, " of gridsize ", size, " in log folder ", log_folder, " does not exist. Counting as not solved (double-check).")

        # If not solved:

        runtime_dict[f"maze_{size}"]["avg_opt_rt"] = np.mean(runtime_dict[f"maze_{size}"]['opt_runtimes'])
        runtime_dict[f"maze_{size}"]["std_opt_rt"] = np.std(runtime_dict[f"maze_{size}"]['opt_runtimes'])
        runtime_dict[f"maze_{size}"]["avg_graph_rt"] = np.mean(runtime_dict[f"maze_{size}"]['graph_runtimes'])
        runtime_dict[f"maze_{size}"]["std_graph_rt"] = np.std(runtime_dict[f"maze_{size}"]['graph_runtimes'])
        
    with open(f'{log_folder}/parsed_runtime_data.json', 'w') as fp:
        json.dump(runtime_dict, fp)
    
    print_runtime_in_latex_table(log_folder, runtime_dict, "parsed_runtime_data.json")
    return runtime_dict

        
