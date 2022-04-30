import numpy as np
import csv
import time
KNIGHT_MOVES = [(1, -2), (2, -1), (2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2)]
DEBUG = False
DEPTH = 20


class KnightTour:
    '''
    Consists of the board itself and an array of neurons
    '''
    def __init__(self, board_size):
        self.board_size = board_size
        self.board = []
        self.neural_network = []
        # create the board
        for i in range(self.board_size[0]):
            temp = []
            for j in range(self.board_size[1]):
                temp.append(set())
            self.board.append(temp)
        if DEBUG:
            self.print_board(self.board)

        self.init()

    def print_board(self, board):
        if len(board) == self.board_size[0]:
            for i in range(self.board_size[0]):
                print(board[i])

    def find_neighbours(self, pos):
        '''
        Returns all the positions which the knight can move
        givrn it's position.
        '''
        # create an empty set to store list of neighbours
        neighbours = set()
        # iterate through each possible legal move and make sure it is inside the board
        for (dx, dy) in KNIGHT_MOVES:
            new_x, new_y = pos[0]+dx, pos[1]+dy
            if 0 <= new_x < self.board_size[0] and 0 <= new_y < self.board_size[1]:
                neighbours.add((new_x, new_y))
        return neighbours

    def init(self):
        '''
        Finds all possible moves on this board and creates a neuron for each one
        '''
        neuron_num = 0
        for x1 in range(self.board_size[0]):
            for y1 in range(self.board_size[1]):
                i = x1 * self.board_size[1] + y1
                for (x2, y2) in self.find_neighbours((x1,y1)):
                    j = x2 * self.board_size[1] + y2
                    if j > i:
                        self.neural_network.append(Neuron())
                        self.board[x1][y1].add(neuron_num)
                        self.board[x2][y2].add(neuron_num)
                        self.neural_network[neuron_num].vertices.append({(x1, y1), (x2, y2)})
                        neuron_num += 1
        for i in range(len(self.neural_network)):
            vertex1, vertex2 = self.neural_network[i].vertices[0]
            neighbours = self.board[vertex1[0]][vertex1[1]].union(self.board[vertex2[0]][vertex2[1]]) - {i}
            self.neural_network[i].neighbours = neighbours

        if DEBUG:
            print("|-------------Initialisation-----------|")
            print("Neurons created:", len(self.neural_network))
            print("|-------------Sample-Neuron------------|")
            sample = np.random.randint(0, len(self.neural_network))
            print("Neuron Number:", sample)
            print("Vertices:", self.neural_network[sample].vertices)
            print("Neighbours:", (self.neural_network[sample].neighbours))
            print("Output:", (self.neural_network[sample].output))
            print("State:", (self.neural_network[sample].state))
            print("|--------------------------------------|")
            self.print_board(self.board)

    def initialise_neurons(self):
        for neuron in self.neural_network:
            neuron.init()
        if DEBUG:
            print('|--------initialize-neurons------------|')
            states = []
            for neuron in self.neural_network:
                states.append(neuron.state)
            print('states:',states)
            outputs = []
            for neuron in self.neural_network:
                outputs.append(neuron.output)
            print('outputs:',outputs)
            print("|--------------------------------------|")

    def update_neurons(self):
            """
            Updates the state and output of each neuron
            """
            number_of_changes = 0
            number_of_active = 0
            for neuron in (self.neural_network):
                sum_of_neighbours = 0
                for neighbour in neuron.neighbours:
                    sum_of_neighbours += self.neural_network[neighbour].output
                next_state = neuron.state + 4 - sum_of_neighbours - neuron.output
                '''
                hysteresis term
                any state over 3, the output will be 1
                any state under 0, output will be 0
                '''
                if (next_state > 3 ): neuron.output = 1
                elif (next_state < 0 ): neuron.output = 0
                # counts the number of changes between the next state and the current state.
                if (neuron.state != next_state): number_of_changes += 1
                neuron.state = next_state
                # counts the number of active neurons which are the neurons that their output is 1.  
                if ( neuron.output == 1): number_of_active += 1
            if DEBUG:
                print('____________________update________________________')
                print('States:',)
                for neuron in self.neural_network:
                    print(neuron.state, end=", ")
                print()
                print('Outputs:')
                for neuron in self.neural_network:
                    print(neuron.output, end=", ")
                print()

            return number_of_active, number_of_changes

    def get_active_neuron_indices(self):
        '''
        returns active neuron indices
        '''
        active_neuron_indices = []
        for i in range(len(self.neural_network)):
            if (self.neural_network[i].output == 1 ): active_neuron_indices.append(i)
        return active_neuron_indices
      
    def check_degree(self):
        """
        Returns True if all of the vertices have degree=2.
        for all active neurons updates the degree of its
        vertices and then checks if degree has any number
        other than 2.
        """
        active_neuron_indices = self.get_active_neuron_indices()
        # gets the index of active neurons.
        degree = np.zeros((self.board_size[0], self.board_size[1]), dtype=np.int16)
        for i in active_neuron_indices:
            vertex1, vertex2 = self.neural_network[i].vertices[0]
            degree[vertex1[0]][vertex1[1]] += 1
            degree[vertex2[0]][vertex2[1]] += 1

        if DEBUG:
            print('____________________check degree_______________________')
            print(degree)

        # if all the degrees=2 return True
        if degree[degree != 2].size == 0:
            return True
        return False

    def get_active_neurons_vertices(self):
        """
        Returns the vertices of the active neurons(neurons
        that have output=1).
        Used for drawing the edges of the graph in GUI.
        """
        # gets the index of active neurons.
        active_neuron_indices = self.get_active_neuron_indices()
        active_neuron_vertices = []
        for i in active_neuron_indices:
            active_neuron_vertices.append(self.neural_network[i].vertices[0])
        return active_neuron_vertices

    def get_solution(self):
            """
            Finds and prints the solution.
            """

            visited = []
            current_vertex = (0, 0)
            labels = np.zeros(self.board_size, dtype=np.int16)
            # gets the index of active neurons.
            active_neuron_indices = self.get_active_neuron_indices()
            neuron_vertices = []
            for neuron in self.neural_network:
                neuron_vertices.append(neuron.vertices[0])

            i = 0
            while len(active_neuron_indices) != 0:
                visited.append(current_vertex)
                labels[current_vertex] = i
                i += 1
                # finds the index of neurons that have this vertex(current_vertex).
                vertex_neighbours = list(self.board[current_vertex[0]][current_vertex[1]])
                # finds the active ones.
                # active neurons that have this vertex are the edges of the solution graph that
                # share this vertex.
                vertex_neighbours = np.intersect1d(vertex_neighbours, active_neuron_indices)
                # picks one of the neighbours(the first one) and finds the other vertex of
                # this neuron(or edge) and sets it as the current one
                current_vertex = list(neuron_vertices[vertex_neighbours[0]] - {current_vertex})[0]
                # removes the selected neighbour from all active neurons
                active_neuron_indices = np.setdiff1d(active_neuron_indices, [vertex_neighbours[0]])
            return labels

    def run_neural_network(self):
        '''
        finds a closed knights tour
        #todo flags to include open tours
        '''
        even = False
        time = 0
        while True:
            self.initialise_neurons()
            n = 0
            while True:            
                num_active, num_changes = self.update_neurons()
                print("|---------------Updates----------------|")
                print("Active:", num_active, "Changes:", num_changes)
                if num_changes == 0:
                    break
                if self.check_degree():
                    even = True
                    break
                n += 1
                if n == DEPTH:
                    break
            time += 1
            if even:
                print('all vertices have degree=2')
                if self.check_connected_components():
                    print('solution found!!')
                    self.get_solution()                    
                else:
                    even = False
            
    def check_connected_components(self):
        """
        Checks weather the solution is a knight's tour and it's not
        two or more independent hamiltonian graphs.
        """
        # gets the index of active neurons.
        active_neuron_indices = self.get_active_neuron_indices()
        # dfs through all active neurons starting from the first element.
        connected = self.dfs_through_neurons(neuron=active_neuron_indices[0], active_neurons=active_neuron_indices)
        if connected:
            return True
        return False     

    def dfs_through_neurons(self, neuron, active_neurons):
        """
        Performs a DFS algorithm from a starting active neuron visiting all active neurons. Neurons will slows be removed from
        the active neuron list as they are checked, so at the end we should have no active neighbours remaining. If we do it 
        means we have a hamiltonian graph, not a cycle.
        """
        # removes the neuron from the active neurons list.
        active_neurons.remove(neuron)
        # first finds the neighbours of this neuron and then finds which of them are active.
        active_neighbours = []
        neuron = self.neural_network[neuron]  
        for neighbour in neuron.neighbours:
            if neighbour in active_neurons:
                active_neighbours.append(neighbour)
                    
        # if there are no active neighbours, then the tour was completed
        if len(active_neighbours) == 0:
            # make sure that all of the active neurons have been visited
            # checks if there are active neighbours remaining
            if len(active_neurons) == 0:
                return True
            else: return False
        return self.dfs_through_neurons(active_neighbours[0], active_neurons)
        
class Neuron:
    '''
    A neuron in the neural network. Each neuron represents a legal move on the chessboard
    '''
    def __init__(self):
        self.vertices = []
        self.neighbours = []
        self.init()

    def init(self):
        '''
        initialise neuron to randomised values
        '''
        self.output = np.random.randint(2, dtype=np.int16)
        self.state = 0

header = ['m','n','time to complete ms']

board_size_x = 6
board_size_y = 6
start = 0
runTime = 0
previousTime = 0
runUpdate = True
tour = KnightTour((board_size_x, board_size_x))
for trial in range(50):
    for i in [0,2,4,6,8,10,12]:
        for j in range(7):
            del tour
            board_size_x = 6 + i
            board_size_y = 6 + j
            print("Solving", board_size_x, board_size_y)
            tour = KnightTour((board_size_x, board_size_y))
            even = False
            runUpdate = True
            count = 0
            runTime = 0
            while runUpdate == True:
                if count > 400000: 
                    logData = ['failed',board_size_x, board_size_y,(runTime/1000/1000),count]
                    print('Failed',board_size_x,board_size_y,'in',round((runTime/1000/1000),3),'ms in',count,'iterations')
                    with open('knights_tour_log.csv', 'a', encoding='UTF8', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(logData)  
                    break
                if start == 0: start = time.perf_counter_ns()
                elapsed = time.perf_counter_ns() - start
                start = time.perf_counter_ns()
                runTime += elapsed
                tour.initialise_neurons()
                n = 0
                while True:    
                    elapsed = time.perf_counter_ns() - start
                    start = time.perf_counter_ns()
                    runTime += elapsed    
                    if (runTime - previousTime) > 1000*1000*1000: 
                        print("Run Time:",round((runTime/1000/1000), 3),"ms")
                    previousTime = runTime    
                    num_active, num_changes = tour.update_neurons()
                    #print("|---------------Updates----------------|")
                    #print("Active:", num_active, "Changes:", num_changes)
                    if num_changes == 0:
                        break
                    if tour.check_degree():
                        even = True
                        break
                    n += 1
                    if n == DEPTH:
                        break
                    count += 1
                if even:
                    print('all vertices have degree=2')
                    if tour.check_connected_components():
                        elapsed = time.perf_counter_ns() - start
                        start = time.perf_counter_ns()
                        runTime += elapsed
                        print('Solved',board_size_x,board_size_y,'in',round((runTime/1000/1000),3),'ms in',count,'iterations')
                        print(tour.get_solution())
                        logData = ['solved',board_size_x, board_size_y,(runTime/1000/1000),count]
                        with open('knights_tour_log.csv', 'a', encoding='UTF8', newline='') as csvfile:
                            writer = csv.writer(csvfile)
                            writer.writerow(logData)   
                        start = 0
                        runUpdate = False
                    else:
                        even = False
