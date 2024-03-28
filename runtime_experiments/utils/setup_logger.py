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

def setup_logger(exp_name, maze_dims=[], test_type="static", nruns=25, obs_coverage=15):
    logger = Random_RT_Logger(exp_name, maze_dims = maze_dims, nruns=nruns, obs_coverage = obs_coverage, test_type=test_type)
    return logger