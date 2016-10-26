import numpy as np
import random
import math
import sys

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
        self.SEC = False
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
        
        self.known_maze = self.update_maze_info(self.location, self.heading, sensors, self.known_maze)
        
        '''
        if len(moves[0]) < 1:
            rotation = 'Reset'
            movement = 'Reset'
            self.location = [0, 0]
            self.heading = 'up'
        else:

            # flood in algorithm
            self.flood = self.flooding(self.location, self.known_maze)
            routes = self.get_routes(self.known_maze, self.flood)
            moves = self.get_moves(routes, self.location, self.heading)
            #moves = self.moves_refinement(moves)
            #moves = self.find_shortest_moves(moves)
            rotation = moves[0][0][0]
            movement = moves[0][0][1]
            '''
            
        # left-hand search
        if sensors[0] > 0:
            rotation = -90
            movement = 1
        elif sensors[1] > 0:
            rotation = 0
            movement = 1
        elif sensors[2] > 0:
            rotation = 90
            movement = 1
        else:
            rotation = 90
            movement = 0
        
        
        
        self.maze_plotter(self.known_maze, self.location, self.heading, [])
        self.heading, self.location = self.update_location_heading(self.location, self.heading, movement, rotation)
        print '============================================='
        
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
                    if(n[0] == d - 1 or n[1] == d - 1 or n[2] == d - 1 or n[3] == d - 1):
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
        
        out = [0, 0, 0, 0]
        neighbors = self.get_neighbors(loc, maze_info)
        
        for i in range(4):
            if neighbors[i] != None:
                out[i] = flood_values[neighbors[i][0]][neighbors[i][1]]
            else:
                out[i] = None
        return out
        
    def get_routes(self, maze_info, f):
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
                    # 'head' is the head of a route
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
    
    def get_moves(self, routes, loc, heading):
        
        moves = []
        for i in range(len(routes)):
            moves.append([])
            vec = self.direction_to_vector(heading)
            for j in range(len(routes[i]) - 1):
                disp = (routes[i][-(j + 2)][0] - routes[i][-(j + 1)][0], routes[i][-(j + 2)][1] - routes[i][-(j + 1)][1])
                move = self.get_one_move(vec, disp)
                moves[i].append(move)
                vec = self.perform_rotation(vec, -move[0]/180.*math.pi)
        
        return moves
        
    def get_one_move(self, vec, displacement):
        
        movement = 1
        temp = (vec[0] * displacement[1] - vec[1] * displacement[0]) / (vec[0] * vec[0] + vec[1] * vec[1])
        rotation = round(math.asin(temp) / math.pi * 180.)
        if rotation == 0. and vec != displacement:
            movement = -1
        
        return (-int(rotation), movement)
        
    def vector_to_direction(self, vec):
        
        if vec == (0, 1):
            heading = 'up'
        elif vec == (1, 0):
            heading = 'right'
        elif vec == (0, -1):
            heading = 'down'
        elif vec == (-1, 0):
            heading = 'left'
        
        return heading
        
    def direction_to_vector(self, heading):
        
        if heading == 'up':
            vec = (0, 1.)
        elif heading == 'right':
            vec = (1., 0)
        elif heading == 'down':
            vec = (0, -1.)
        elif heading == 'left':
            vec = (-1., 0)
        
        return vec
        
    def perform_rotation(self, vec1, rotation):
        '''
        The defination of rotation here is opposite to that in the robot
        rotation, because here it's in Cartesian coordinate system.
        '''
        
        c = math.cos(rotation)
        s = math.sin(rotation)
        vec2 = (round(c*vec1[0]-s*vec1[1]), round(s*vec1[0]+c*vec1[1]))
        
        return vec2
        
    def maze_plotter(self, maze_info, loc, heading, moves):
        
        l = len(maze_info)
        path = [[-1 for i in range(l)] for j in range(l)]
        path[loc[0]][loc[1]] = 0
        
        for i in range(len(moves)):
            head = [loc[0], loc[1]]
            vec = self.direction_to_vector(heading)
            value = 1
            for j in range(len(moves[i])):
                vec = self.perform_rotation(vec, -moves[i][j][0])
                for k in range(abs(moves[i][j][1])):
                    head[0] += int(vec[0] * math.copysign(1.0, moves[i][j][1]))
                    head[1] += int(vec[1] * math.copysign(1.0, moves[i][j][1]))
                    path[head[0]][head[1]] = value
                    value += 1
        
        n = len(maze_info)
        for i in range(n):
            if i == 0:
                sys.stdout.write('*')
                for j in range(n):
                    bininfo = '000' + bin(maze_info[j][n - 1 - i])[2:]
                    if int(bininfo[-1]):
                        sys.stdout.write('   ')
                    else:
                        sys.stdout.write('***')
                    sys.stdout.write('*')
                sys.stdout.write('\n')
            sys.stdout.write('*')
            for j in range(n):
                bininfo = '000' + bin(maze_info[j][n - 1 - i])[2:]
                if path[j][n - 1 - i] == -1:
                    sys.stdout.write('   ')
                elif path[j][n - 1 - i] == 0:
                    sys.stdout.write(' 0 ')
                else:
                    #sys.stdout.write(' @ ')
                    sys.stdout.write(str(path[j][n - 1 - i]).zfill(3))
                    
                if int(bininfo[-2]):
                    sys.stdout.write(' ')
                else:
                    sys.stdout.write('*')
            sys.stdout.write('\n')
            sys.stdout.write('*')
            for j in range(n):
                bininfo = '000' + bin(maze_info[j][n - 1 - i])[2:]
                if int(bininfo[-3]):
                    sys.stdout.write('   ')
                else:
                    sys.stdout.write('***')
                sys.stdout.write('*')
            sys.stdout.write('\n')
            
    def update_location_heading(self, loc, head, right_movement, rotation):
        '''
        This function is used to update robot's own location information.
        The movement input here must be a right movement, in other words, it
        should not incur collision with the wall.
        '''
        
        vec = self.direction_to_vector(head)
        new_vec = self.perform_rotation(vec, -rotation)
        new_heading = self.vector_to_direction(new_vec)
        disp = (new_vec[0] * right_movement, new_vec[1] * right_movement)
        new_loc = [int(loc[0] + disp[0]), int(loc[1] + disp[1])]
        
        return new_heading, new_loc
        
    def update_maze_info(self, loc, heading, sensors, maze_info):
        
        l = len(maze_info)
        x = loc[0]
        y = loc[1]
        N = -1
        E = -1
        S = -1
        W = -1
        
        if heading == 'up':
            W = sensors[0]
            N = sensors[1]
            E = sensors[2]
        elif heading == 'right':
            N = sensors[0]
            E = sensors[1]
            S = sensors[2]
        elif heading == 'down':
            E = sensors[0]
            S = sensors[1]
            W = sensors[2]
        elif heading == 'left':
            S = sensors[0]
            W = sensors[1]
            N = sensors[2]
        
        if N != -1:
            maze_info[x][y + N] = maze_info[x][y + N] & 0b1110
            if y + N + 1 < l:
                maze_info[x][y + N + 1] = maze_info[x][y + N + 1] & 0b1011
            for i in range(N):
                maze_info[x][y + i] = maze_info[x][y + i] | 0b0001
                maze_info[x][y + i + 1] = maze_info[x][y + i + 1] | 0b0100
        if E != -1:
            maze_info[x + E][y] = maze_info[x + E][y] & 0b1101
            if x + E + 1 < l:
                maze_info[x + E + 1][y] = maze_info[x + E + 1][y] & 0b0111
            for i in range(E):
                maze_info[x + i][y] = maze_info[x + i][y] | 0b0010
                maze_info[x + i + 1][y] = maze_info[x + i + 1][y] | 0b1000
        if S != -1:
            maze_info[x][y - S] = maze_info[x][y - S] & 0b1011
            if y - S - 1 >= 0:
                maze_info[x][y - S - 1] = maze_info[x][y - S - 1] & 0b1110
            for i in range(S):
                maze_info[x][y - i] = maze_info[x][y - i] | 0b0100
                maze_info[x][y - i - 1] = maze_info[x][y - i - 1] | 0b0001
        if W != -1:
            maze_info[x - W][y] = maze_info[x - W][y] & 0b0111
            if x - W - 1 >= 0:
                maze_info[x - W - 1][y] = maze_info[x - W - 1][y] & 0b1101
            for i in range(W):
                maze_info[x - i][y] = maze_info[x - i][y] | 0b1000
                maze_info[x - i - 1][y] = maze_info[x - i - 1][y] | 0b0010
        
        return maze_info
        
    def moves_refinement(self, moves):
        '''
        This function combines multiple small strides to a larger one.
        '''
        
        for i in range(len(moves)):
            j = 0
            while j < len(moves[i]) - 1:
                if moves[i][j + 1][0] == 0 and moves[i][j][1] + moves[i][j + 1][1] <= 3 and moves[i][j][1] + moves[i][j + 1][1] >= -3:
                        moves[i][j] = (moves[i][j][0], moves[i][j][1] + moves[i][j + 1][1])
                        del moves[i][j + 1]
                else:
                    j += 1
                    
        return moves
        
    def find_shortest_moves(self, moves):
        
        l = []
        for i in range(len(moves)):
            l = l + [len(moves[i])]
        mi = min(l)
        n = 0
        while n < len(moves):
            if len(moves[n]) > mi:
                del moves[n]
            else:
                n += 1
                
        return moves
            
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
