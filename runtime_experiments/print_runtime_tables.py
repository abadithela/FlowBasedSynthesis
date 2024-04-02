from utils.setup_logger import get_runtime_dict_from_log

gridsizes = [5,10,15, 20, 25, 30]

# Single intermediate:
NUM_INTS = [1,2,3]

for num_ints in NUM_INTS:
    reach_reactive_log = "reachability_"+str(NUM_INTS)+"_reactive_log"
    get_runtime_dict_from_log(reach_reactive_log, gridsizes)

    reach_static_log = "reachability_"+str(NUM_INTS)+"_static_log"
    get_runtime_dict_from_log(reach_static_log, gridsizes)

    reaction_reactive_log = "reaction_"+str(NUM_INTS)+"_reactive_log"
    get_runtime_dict_from_log(reaction_reactive_log, gridsizes)

    reaction_static_log = "reaction_"+str(NUM_INTS)+"_static_log"
    get_runtime_dict_from_log(reaction_static_log, gridsizes)

    safety_reactive_log = "safety_"+str(NUM_INTS)+"_reactive_log"
    get_runtime_dict_from_log(safety_reactive_log, gridsizes)

    safety_static_log = "safety_"+str(NUM_INTS)+"_static_log"
    get_runtime_dict_from_log(safety_static_log, gridsizes)

    