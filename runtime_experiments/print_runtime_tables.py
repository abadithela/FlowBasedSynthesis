import sys
sys.path.append("..")
from utils.setup_logger import get_runtime_dict_from_log

gridsizes = [5,10,15, 20]

# Single intermediate:
NUM_INTS = [3]

for num_ints in NUM_INTS:
    reach_reactive_log = "run2_60s_reachability_"+str(num_ints)+"_reactive_log"
    get_runtime_dict_from_log(reach_reactive_log, gridsizes)
 
    reach_static_log = "run2_60s_reachability_"+str(num_ints)+"_static_log"
    get_runtime_dict_from_log(reach_static_log, gridsizes)

    reaction_static_log = "run2_60s_reaction_"+str(num_ints)+"_static_log"
    get_runtime_dict_from_log(reaction_static_log, gridsizes)

    reaction_reactive_log = "run2_60s_reaction_"+str(num_ints)+"_reactive_log"
    get_runtime_dict_from_log(reaction_reactive_log, gridsizes)

    safety_reactive_log = "run2_60s_safety_"+str(num_ints)+"_reactive_log"
    get_runtime_dict_from_log(safety_reactive_log, gridsizes)

    safety_static_log = "run2_60s_safety_"+str(num_ints)+"_static_log"
    get_runtime_dict_from_log(safety_static_log, gridsizes)

    