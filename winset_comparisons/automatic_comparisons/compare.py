from utils import AugMazeNetwork, plot_sol
from find_tester_controller import TesterCtrl
from static_utils import solve_problem, get_graphs
from ipdb import set_trace as st
from utils import make_comparison_plots


def run_comparison():
    mazefile = 'maze.txt'
    maze = AugMazeNetwork(mazefile)
    tester = TesterCtrl(maze)
    initpos = maze.init
    output = tester.move(initpos)

    MAZEFILE = 'maze.txt'

    INIT = [maze.init]
    GOALS = maze.goal
    INTS = maze.int

    SYS_FORMULA = 'F(goal)'
    TEST_FORMULA = 'F(I)'

    virtual, system, b_pi, virtual_sys = get_graphs(SYS_FORMULA, TEST_FORMULA, MAZEFILE, INIT, INTS, GOALS)
    exit_status, flow_cuts, flow, bypass = solve_problem(virtual, system, b_pi, virtual_sys)
    print('exit status {0}'.format(exit_status))
    print(flow_cuts)

    make_comparison_plots(output, maze, flow_cuts)


if __name__ == "__main__":
    run_comparison()
