import copy as cp
import sys
from ipdb import set_trace as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
import glob
from PIL import Image, ImageOps
import _pickle as pickle
from matplotlib.ticker import (AutoMinorLocator, MultipleLocator,
        FormatStrFormatter, AutoMinorLocator)
from matplotlib.collections import PatchCollection
import imageio
import sys
sys.path.append('..')

TILESIZE = 50
GRID_LINES = False

main_dir = os.path.dirname(os.path.dirname(os.path.realpath("__file__")))
robo_figure = main_dir + '/quadruped_s_track/robot.png'

def draw_maze(maze):
    tiles = []
    xs = np.linspace(0, maze.len_x*TILESIZE, maze.len_x+1)
    ys = np.linspace(0, maze.len_y*TILESIZE, maze.len_y+1)
    w, h = xs[1] - xs[0], ys[1] - ys[0]

    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    ax.set_xlim(xs[0], xs[-1])
    ax.set_ylim(ys[0], ys[-1])
    ax.invert_yaxis()

    # draw the grid
    for i, x in enumerate(xs[:-1]):
        for j, y in enumerate(ys[:-1]):
            # st()
            if maze.map[j,i]=='*':
                tiles.append(patches.Rectangle((x, y), w, h, fill=True, color='black', alpha=.5))
            elif (j,i) in maze.int:
                tiles.append(patches.Rectangle((x, y), w, h, fill=True, color='blue', alpha=.3))
                # axs[k].text(x+tilesize/2, y+TILESIZE/2, maze.int[(j,i)])
            elif (j,i) in maze.goal:
                tiles.append(patches.Rectangle((x, y), w, h, fill=True, color='yellow', alpha=.3))
                # axs[k].text(x+tilesize/2, y+TILESIZE/2, 'T')
            elif i % 2 == j % 2:
                tiles.append(patches.Rectangle((x, y), w, h, fill=True, color='black', alpha=.1))
                # if (j,i) in maze.init:
                    # axs[k].text(x+tilesize/2, y+TILESIZE/2, 'S')
            elif maze.map[j,i]==' ':
                tiles.append(patches.Rectangle((x, y), w, h, fill=True, color='black', alpha=.2))
                # if (j,i) in maze.init:
                    # axs[k].text(x+tilesize/2, y+TILESIZE/2, 'S')
    # grid lines
    # for x in xs:
    #     axs[k].plot([x, x], [ys[0], ys[-1]], color='black', alpha=.33, linestyle=':')
    # for y in ys:
    #     axs[k].plot([xs[0], xs[-1]], [y, y], color='black', alpha=.33, linestyle=':')

    ax.add_collection(PatchCollection(tiles, match_original=True))


def draw_cuts(maze):
    rectangles = []
    for cut in maze.active_cuts:
        cut_a = cut[0]
        cut_b = cut[1]

        if cut_a[0] == cut_b[0]:
            xloc = (cut_a[0] + cut_b[0])/2*TILESIZE + TILESIZE/2 - 2.5
            yloc = (cut_a[1] + cut_b[1])/2*TILESIZE
            height = TILESIZE
            width = 5
        elif cut_a[1] == cut_b[1]:
            xloc = (cut_a[1] + cut_b[1])/2*TILESIZE
            yloc = (cut_a[0] + cut_b[0])/2*TILESIZE + TILESIZE/2 - 2.5
            height = 5
            width = TILESIZE

        rectangle = patches.Rectangle((xloc,yloc),width,height,linewidth=1,edgecolor='black',facecolor='black')
        rectangles.append(rectangle)
    ax.add_collection(PatchCollection(rectangles, match_original=True))


def draw_timestamp(t, merge = False):
    if merge:
        ax.text(0.5,0.7,t, transform=plt.gcf().transFigure,fontsize='large',
             bbox={"boxstyle" : "circle", "color":"white", "ec":"black"})
    else:
        ax.text(0.3,0.7,t, transform=plt.gcf().transFigure,fontsize='large',
             bbox={"boxstyle" : "circle", "color":"white", "ec":"black"})

def draw_robot(robot_data, theta_d):
    # st()
    robot_loc = robot_data[-1][-1]
    x = robot_loc[0] * TILESIZE
    z = robot_loc[1] * TILESIZE
    rob_fig = Image.open(robo_figure)
    rob_fig = ImageOps.flip(rob_fig)
    rob_fig = rob_fig.rotate(theta_d, expand=False)
    offset = 0.1
    ax.imshow(rob_fig, zorder=1, interpolation='bilinear', extent=[z+10, z+TILESIZE-10, x+5, x+TILESIZE-5])


def animate_images(output_dir):
    # Create the frames
    frames = []
    imgs = glob.glob(output_dir+'plot_'"*.png")
    imgs.sort()
    for i in imgs:
        new_frame = Image.open(i)
        frames.append(new_frame)

    # Save into a GIF file that loops forever
    frames[0].save(output_dir + 'png_to_gif.gif', format='GIF',
            append_images=frames[1:],
            save_all=True,
            duration=200, loop=3)


    # Build GIF
    # with imageio.get_writer(output_dir +'mygif.gif', mode='I') as writer:
    #     for frame in frames:
    #         # image = imageio.imread(filename)
    #         writer.append_data(frame)

def traces_to_animation(filename, output_dir):
    # extract traces from pickle file
    with open(filename, 'rb') as pckl_file:
        traces = pickle.load(pckl_file)

    t_start = 0
    t_end = len(traces)
    maze = traces[0].maze
    global ax
    fig, ax = plt.subplots()

    t_array = np.arange(t_end)
    # plot map once
    for t in t_array:
        plt.gca().cla()
        draw_maze(traces[t].maze)
        draw_cuts(traces[t].maze)
        robot_data = traces[t].agent
        theta_d = 0
        draw_robot(robot_data, theta_d)
        plot_name = str(t).zfill(5)
        img_name = output_dir+'/plot_'+plot_name+'.png'
        fig.savefig(img_name, dpi=1200)
    animate_images(output_dir)

def angle(traces, t):
    # st()
    map = traces[0].game.maze.map
    car_data = traces[t].car
    y_tile = car_data[0][1]
    x_tile = car_data[0][2]
    dir = map[(y_tile,x_tile)]

    dir_dict = {'→' : 0, '←' : 180, '↑': 270, '↓': 90, '*': 0, ' ': 0}
    # st()
    if dir != '+':
        angle = dir_dict[dir]
    else:
        if map[(traces[t-1].car[0][2],traces[t-1].car[0][1])] != '+':
            angle = dir_dict[map[(traces[t-1].car[0][2],traces[t-1].car[0][1])]]
        elif map[(traces[t+1].car[0][2],traces[t+1].car[0][1])] != '+':
            angle = dir_dict[map[(traces[t+1].car[0][2],traces[t+1].car[0][1])]]
        elif map[(traces[t+2].car[0][2],traces[t+2].car[0][1])] != '+':
            angle = dir_dict[map[(traces[t+2].car[0][2],traces[t+2].car[0][1])]]
        elif map[(traces[t-2].car[0][2],traces[t-2].car[0][1])] != '+':
            angle = dir_dict[map[(traces[t-2].car[0][2],traces[t-2].car[0][1])]]

    return angle


def make_animation():
    output_dir = os.getcwd()+'/animations/gifs/'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    traces_file = os.getcwd()+'/saved_traces/sim_trace.p'
    traces_to_animation(traces_file, output_dir)

if __name__ == '__main__':
    make_animation()
    # st()
