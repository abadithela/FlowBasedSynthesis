'''
Script to experiment data including runtimes.
'''

# from problem_data import * 
from pdb import set_trace as st
from components.experiment_logging import ExpLogger
import os
import datetime

def setup_logger(exp_name):
    logger = ExpLogger(exp_name, datetime.datetime.now())
    return logger

