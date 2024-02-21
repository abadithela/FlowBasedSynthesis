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
from network import MazeNetwork

TILESIZE = 50
GRID_LINES = False

main_dir = os.path.dirname(os.path.dirname(os.path.realpath("__file__")))
output_dir = os.getcwd()+'/imgs/'

def draw_maze(maze, maze_name, merge = False):
    global ax
    fig, ax = plt.subplots()
    size = max(maze.keys())
    z_min = 0
    z_max = (size[0]+1) * TILESIZE
    x_min = 0
    x_max = (size[1]+1) * TILESIZE

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(z_min, z_max)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    # ax.crop((x_min, z_min, x_max, z_max))

    # fill in the road regions
    road_tiles = []
    x_tiles = np.arange(0,size[0]+2)*TILESIZE
    z_tiles = np.arange(0,size[1]+2)*TILESIZE
    for i in np.arange(0,size[0]+1):
        for k in np.arange(0,size[1]+1):
            print('{0},{1}'.format(i,k))
            left = z_tiles[k]
            bottom = x_tiles[i]
            width = TILESIZE
            height = TILESIZE
            if maze[(i,k)] != '*':
                # ax.add_patch(Rectangle((x, y), w, h, fill=True, color='black', alpha=.5))
                tile = patches.Rectangle((left, bottom),width,height, fill=True,color='black', alpha=.1)
                if i % 2 == k % 2: # racing flag style
                    tile = patches.Rectangle((left, bottom),width,height, fill=True, color='gray', alpha=.1)
                road_tiles.append(tile)
            elif maze[(i,k)] == '*':
                tile = patches.Rectangle((left, bottom),width,height,fill=True,linewidth=1,facecolor='k', alpha=0.8)
                road_tiles.append(tile)
            if maze[(i,k)] != ' ' and maze[(i,k)]!='*':
                right = left + width
                top = bottom + height
                ax.text(0.5*(left+right), 0.5*(bottom+top), maze[(i,k)],horizontalalignment='center',verticalalignment='center',fontsize=20, color='black')
    
    ax.add_collection(PatchCollection(road_tiles, match_original=True))
    # grid lines
    if GRID_LINES:
        for z in z_tiles:
            plt.plot([z, z], [x_tiles[0], x_tiles[-1]], color='black', alpha=.33, linestyle=':')
        for x in x_tiles:
            plt.plot([z_tiles[0], z_tiles[-1]], [x, x], color='black', alpha=.33, linestyle=':')
    plt.gca().invert_yaxis()
    save_figure(fig, maze_name)

def save_figure(figure, plot_name):
    img_name = output_dir+'/plot_'+plot_name+'.png'
    figure.savefig(img_name)

if __name__ == '__main__':
    maze_name = "maze"
    mazefile = os.getcwd()+'/' + maze_name + '.txt'
    maze = MazeNetwork(mazefile)
    draw_maze(maze.map, maze_name)
    st()