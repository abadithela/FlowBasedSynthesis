import sys
sys.path.append("..")
from utils.setup_logger import get_runtime_dict_from_log

gridsizes = [3,4,5,10,15, 20]

# Single intermediate:
NUM_INTS = [1]

for num_ints in NUM_INTS:
    reach_reactive_log = "reachability_"+str(num_ints)+"_reactive_log"
    reach_reactive_log = "run_60s_reachability_reactive_log"
    # get_runtime_dict_from_log(reach_reactive_log, gridsizes)


    reach_static_log = "reachability_"+str(num_ints)+"_static_log"
    reach_static_log = "run_60s_reachability_static_log"
    get_runtime_dict_from_log(reach_static_log, gridsizes)

    # reaction_reactive_log = "reaction_"+str(num_ints)+"_reactive_log"
    # get_runtime_dict_from_log(reaction_reactive_log, gridsizes)

    # reaction_static_log = "reaction_"+str(num_ints)+"_static_log"
    # get_runtime_dict_from_log(reaction_static_log, gridsizes)

    # safety_reactive_log = "safety_"+str(num_ints)+"_reactive_log"
    # get_runtime_dict_from_log(safety_reactive_log, gridsizes)

    # safety_static_log = "safety_"+str(num_ints)+"_static_log"
    # get_runtime_dict_from_log(safety_static_log, gridsizes)

    