import csv
import random
import math
import time
# Ant Colony Optimization (ACO)
# The Ant Colony Optimization algorithm is inspired by the behavior of ants moving between destinations, dropping
# pheromones and acting on pheromones that they come across. The emergent behavior is ants converging to paths of
# least resistance.

# Set the number of nodes in the data set
# Best total distance for 5 nodes: 19
# Best total distance for 48 nodes: 33523


NODE_COUNT = 5
# Initialize the 2D matrix for storing distances between nodes
node_distances = []
# Read node distance data set store it in matrix
with open('nodes-' + str(NODE_COUNT) + '.csv') as file:
    reader = csv.reader(file, quoting=csv.QUOTE_NONNUMERIC)
    for row in reader:
        node_distances.append(row)

# Set the probability of ants choosing a random node to visit (0.0 - 1.0)
RANDOM_NODE_FACTOR = 0.2

# Set the weight for pheromones on path for selection
ALPHA = 1
# Set the weight for heuristic of path for selection
BETA = 2


# The Ant class encompasses the idea of an ant in the ACO algorithm.
# Ants will move to different nodes and leave pheromones behind. Ants will also make a judgement about which
# node to visit next. And lastly, ants will have knowledge about their respective total distance travelled.
# - Memory: In the ACO algorithm, this is the list of nodes already visited.
# - Best fitness: The shortest total distance travelled across all nodes.
# - Action: Choose the next destination to visit and drop pheromones along the way.
class Ant:

    # The ant is initialized to a random node with no previously visited nodes
    def __init__(self, a):
        self.visited_nodes = [a]


    # Select an node using a random chance or ACO function
    def visit_node(self, pheromone_trails):
        if random.random() < RANDOM_NODE_FACTOR:
            self.visited_nodes.append(self.visit_random_node())
        else:
            self.visited_nodes.append(
                self.roulette_wheel_selection(self.visit_probabilistic_node(pheromone_trails)))

    # Select an node using a random chance
    def visit_random_node(self):  ##------------------------------------------------------------------------------------------- blad nr 1 nie zwraca node
        all_nodes = set(range(0, NODE_COUNT))
        possible_nodes = all_nodes - set(self.visited_nodes)
        random_index = random.randint(0, len(possible_nodes) - 1)
        random_node = list(possible_nodes)[random_index]
        return random_node

    # Calculate probabilities of visiting adjacent unvisited nodes
    def visit_probabilistic_node(self, pheromone_trails):
        current_node = self.visited_nodes[-1]
        all_nodes = set(range(0, NODE_COUNT))
        possible_nodes = all_nodes - set(self.visited_nodes)
        possible_indexes = []
        possible_probabilities = []
        total_probabilities = 0
        for node in possible_nodes:
            possible_indexes.append(node)
            pheromones_on_path = math.pow(pheromone_trails[current_node][node], ALPHA)
            heuristic_for_path = math.pow(1 / node_distances[current_node][node], BETA)
            probability = pheromones_on_path * heuristic_for_path
            possible_probabilities.append(probability)
            total_probabilities += probability
        possible_probabilities = [probability / total_probabilities for probability in possible_probabilities]
        return [possible_indexes, possible_probabilities, len(possible_nodes)]

    # Select an node using the probabilities of visiting adjacent unvisited nodes
    @staticmethod
    def roulette_wheel_selection(probabilities):
        slices = []
        total = 0
        possible_indexes = probabilities[0]
        possible_probabilities = probabilities[1]
        possible_nodes_count = probabilities[2]
        for i in range(0, possible_nodes_count):
            slices.append([possible_indexes[i], total, total + possible_probabilities[i]])
            total += possible_probabilities[i]
        spin = random.random()
        result = [s[0] for s in slices if s[1] < spin <= s[2]]
        return result[0]

    # Get the total distance travelled by this ant
    def get_distance_travelled(self):
        total_distance = 0
        for a in range(1, len(self.visited_nodes)):
            total_distance += node_distances[self.visited_nodes[a]][self.visited_nodes[a-1]]################### zamien a i a-1 miejscami
        return total_distance

    def print_info(self):
        print('Ant ', self.__hash__())
        print('Total nodes: ', len(self.visited_nodes))
        print('Total distance: ', self.get_distance_travelled())



# The ACO class encompasses the functions for the ACO algorithm consisting of many ants and nodes to visit
# The general lifecycle of an ant colony optimization algorithm is as follows:

# - Initialize the pheromone trails: This involves creating the concept of pheromone trails between nodes
# and initializing their intensity values.

# - Setup the population of ants: This involves creating a population of ants where each ant starts at a different
# node.

# - Choose the next visit for each ant: This involves choosing the next node to visit for each ant. This will
# happen until each ant has visited all nodes exactly once.

# - Update the pheromone trails: This involves updating the intensity of pheromone trails based on the ants’ movements
# on them as well as factoring in evaporation of pheromones.

# - Update the best solution: This involves updating the best solution given the total distance covered by each ant.

# - Determine stopping criteria: The process of ants visiting nodes repeats for a number of iterations. One
# iteration is every ant visiting all nodes exactly once. The stopping criteria determines the total number of
# iterations to run. More iterations will allow ants to make better decisions based on the pheromone trails.
class ACO:

    def __init__(self, number_of_ants_factor):
        self.number_of_ants_factor = number_of_ants_factor
        # Initialize the array for storing ants
        self.ant_colony = []
        # Initialize the 2D matrix for pheromone trails
        self.pheromone_trails = []
        # Initialize the best distance in swarm
        self.best_distance = math.inf
        self.best_ant = None

    # Initialize ants at random starting locations
    def setup_ants(self, number_of_ants_factor, a):
        number_of_ants = round(NODE_COUNT * number_of_ants_factor)
        self.ant_colony.clear()
        for i in range(0, number_of_ants):
            self.ant_colony.append(Ant(a))############################ return ant_colony ?????

    # Initialize pheromone trails between nodes
    def setup_pheromones(self):
        for r in range(0, len(node_distances)):
            pheromone_list = []
            for i in range(0, len(node_distances)):
                pheromone_list.append(1)
            self.pheromone_trails.append(pheromone_list)

    # Move all ants to a new node
    def move_ants(self, ant_population, b):
        for ant in ant_population:
            ant.visited_nodes.append(b)

    # Determine the best ant in the colony - after one tour of all nodes
    def get_best(self, ant_population):################################################################################# brak poprzedniej mrowki
        for ant in ant_population:
            distance_travelled = ant.get_distance_travelled()
            if distance_travelled < self.best_distance:
                self.best_distance = distance_travelled################# Czy na pewno ?
                self.best_ant = ant
        return self.best_ant

    # Update pheromone trails based ant movements - after one tour of all nodes
    def update_pheromones(self, evaporation_rate):##------------------------------------------------------------------- Blad nr 2 Feromony caly czas sa te same
        # EWAPORACJA
        for x in range(0, NODE_COUNT):
            for y in range(0, NODE_COUNT):
                self.pheromone_trails[x][y] = self.pheromone_trails[x][y] * evaporation_rate

        for ant in self.ant_colony:
            for node in range(0, len(ant.visited_nodes) - 1):
                for x in range(0, NODE_COUNT):
                    for y in range(0, NODE_COUNT):
                        if ant.visited_nodes[node] == x and ant.visited_nodes[node + 1] == y:
                            self.pheromone_trails[x][y] += 1 / ant.get_distance_travelled()
                            self.pheromone_trails[y][x] += 1 / ant.get_distance_travelled()


    # Tie everything together - this is the main loop
    def solve(self, TOTAL_ITERATIONS, evaporation_rate):
        a = int(input("Podaj Punkt A: "))
        b = int(input("Podaj Punkt B: "))
        start = time.time()
        self.setup_pheromones()  # Inicjalizacja ścieżek feromonóœ
        for i in range(0, TOTAL_ITERATIONS):
            self.setup_ants(NUMBER_OF_ANTS_FACTOR, a)  # Utworzenie populacji mrówek
            self.move_ants(self.ant_colony, b)
            self.update_pheromones(evaporation_rate)  # Aktualizacja feromonów
            self.best_ant = self.get_best(self.ant_colony)  # Aktualizacja najlepszego rozwiązania
            print(i, ' Best distance: ', self.best_ant.get_distance_travelled())
        end = time.time()
        print("\nTIME:")
        print(end - start)


# Set the percentage of ants based on the total number of nodes
NUMBER_OF_ANTS_FACTOR = 0.5
# Set the number of tours ants must complete
TOTAL_ITERATIONS = 10000
# Set the rate of pheromone evaporation (0.0 - 1.0)
EVAPORATION_RATE = 0.5
aco = ACO(NUMBER_OF_ANTS_FACTOR)
aco.solve(TOTAL_ITERATIONS, EVAPORATION_RATE)