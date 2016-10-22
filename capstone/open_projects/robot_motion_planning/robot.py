import numpy as np
import random

class Robot(object):
    def __init__(self, maze_dim):
        '''
        Use the initialization function to set up attributes that your robot
        will use to learn and navigate the maze. Some initial attributes are
        provided based on common information, including the size of the maze
        the robot is placed in.
        '''

        self.location = [0, 0]
        self.heading = 'up'
        self.maze_dim = maze_dim
        
        #=======================================================================
        self.known_maze = np.ones((maze_dim, maze_dim), dtype = int) * 15
        self.known_maze[0][0] = 3
        self.known_maze[0][maze_dim - 1] = 6
        self.known_maze[maze_dim - 1][0] = 9
        self.known_maze[maze_dim - 1][maze_dim - 1] = 12
        for i in range(maze_dim - 2):
            self.known_maze[0][i + 1] = 7
            self.known_maze[maze_dim - 1][i + 1] = 13
            self.known_maze[i + 1][0] = 11
            self.known_maze[i + 1][maze_dim - 1] = 14
        self.flood = np.ones((maze_dim, maze_dim), dtype = int) * 15
        #=======================================================================

    def next_move(self, sensors):
        '''
        Use this function to determine the next move the robot should make,
        based on the input from the sensors after its previous move. Sensor
        inputs are a list of three distances from the robot's left, front, and
        right-facing sensors, in that order.

        Outputs should be a tuple of two values. The first value indicates
        robot rotation (if any), as a number: 0 for no rotation, +90 for a
        90-degree rotation clockwise, and -90 for a 90-degree rotation
        counterclockwise. Other values will result in no rotation. The second
        value indicates robot movement, and the robot will attempt to move the
        number of indicated squares: a positive number indicates forwards
        movement, while a negative number indicates backwards movement. The
        robot may move a maximum of three units per turn. Any excess movement
        is ignored.

        If the robot wants to end a run (e.g. during the first training run in
        the maze) then returing the tuple ('Reset', 'Reset') will indicate to
        the tester to end the run and return the robot to the start.
        '''
        
        #print '{}, {}'.format(self.location, self.heading)
        rotation = 0
        movement = 0
        #print self.location
        #print self.known_maze
        self.flood = self.flooding([0, 0], self.known_maze)
        tem = self.get_route(self.known_maze, self.flood)
        print tem
        
        return rotation, movement
        
    def flooding(self, robot_loc, maze_info):
        '''
        Given the current robot location, this function assign a flood value to
        each cell, which designate how far the 'water' flows using the Flooding
        Algorithm.
        '''
        
        flood = np.ones((self.maze_dim, self.maze_dim), dtype = int) * (-1)
        flood[robot_loc[0]][robot_loc[1]] = 0
        des = self.maze_dim / 2
        d = 1
        while True:
            for i in range(self.maze_dim):
                for j in range(self.maze_dim):
                    if(flood[i][j] != -1):
                        continue
                    n = self.get_neighbor_flood_value([i, j], self.known_maze, flood)
                    if(n[0]==d-1 or n[1]==d-1 or n[2]==d-1 or n[3]==d-1):
                        flood[i][j] = d
                    if(flood[des-1][des-1] != -1 or flood[des-1][des] != -1 or flood[des][des-1] != -1 or flood[des][des] != -1):
                        return flood
            d += 1
        
    def get_neighbors(self, loc, maze_info):
        '''
        This function outputs all the available neighbors for a given cell, as a
        list of tuples. (order: up, right, down, left)
        '''
        
        binary_info = '000' + bin(maze_info[loc[0]][loc[1]])[2:]
        if int(binary_info[-1]):
            u = (loc[0], loc[1] + 1)
        else:
            u = None
        if int(binary_info[-2]):
            r = (loc[0] + 1, loc[1])
        else:
            r = None
        if int(binary_info[-3]):
            d = (loc[0], loc[1] - 1)
        else:
            d = None
        if int(binary_info[-4]):
            l = (loc[0] - 1, loc[1])
        else:
            l = None
        return [u, r, d, l]
        
    def get_neighbor_flood_value(self, loc, maze_info, flood_values):
        '''
        This function returns all neighbor flood values.
        '''
        out = [0] * 4
        neighbors = self.get_neighbors(loc, maze_info)
        for i in range(4):
            if neighbors[i] != None:
                out[i] = flood_values[neighbors[i][0]][neighbors[i][1]]
            else:
                out[i] = None
        return out
        
    def get_route(self, maze_info, f):
        '''
        Given the flood values matrix, this function can generate routes leading
        to the destination.
        '''
        
        num_routes = 1
        
        center = self.maze_dim / 2 - 1
        
        for i in range(2):
            for j in range(2):
                if f[center + i][center + j] != -1:
                    N = f[center + i][center + j]
                    head = [(center + i, center + j)]
                    routes = [[(center + i, center + j)]]
        
        while (N > 0):
            N -= 1
            for i in range(num_routes):
                temp = self.get_neighbor_flood_value(head[i], maze_info, f)
                nei = self.get_neighbors(head[i], maze_info)
                ii = [x for x, y in enumerate(temp) if y == N]
                l = len(ii)
                if l > 1:
                    num_routes += l - 1
                    for j in range(l - 1):
                        routes.append(routes[i][:])
                        routes[-1].append(nei[ii[j + 1]])
                        head.append(nei[ii[j + 1]])
                head[i] = nei[ii[0]]
                routes[i].append(nei[ii[0]])
        return routes
        
        
