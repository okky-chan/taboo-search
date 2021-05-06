import copy,random,datetime
import matplotlib.pyplot as plt


city_list = [[1, (1150.0, 1760.0)], [2, (630.0, 1660.0)], [3, (40.0, 2090.0)], [4,(750.0, 1100.0)],
              [5, (750.0, 2030.0)], [6, (1030.0, 2070.0)], [7, (1650.0, 650.0)], [8, (1490.0, 1630.0)],
              [9, (790.0, 2260.0)], [10, (710.0, 1310.0)], [11, (840.0, 550.0)], [12, (1170.0, 2300.0)],
              [13, (970.0, 1340.0)], [14, (510.0, 700.0)], [15, (750.0, 900.0)], [16, (1280.0, 1200.0)],
              [17,(230.0, 590.0)], [18, (460.0, 860.0)], [19, (1040.0, 950.0)], [20, (590.0, 1390.0)],
              [21, (830.0, 1770.0)], [22, (490.0, 500.0)], [23, (1840.0, 1240.0)], [24, (1260.0, 1500.0)],
              [25, (1280.0, 790.0)], [26, (490.0, 2130.0)], [27, (1460.0, 1420.0)], [28, (1260.0, 1910.0)],
              [29, (360.0, 1980.0)]
             ]


class Taboo_search:
    def __init__(self,city_list,is_random = True):
        self.city_list = city_list   #City List
        self.candidate_count = 100   #Candidate set length 
        self.taboo_list_length = 10
        self.iteration_count = 100   #Iterations (for loop Taboo Search)
        self.min_route,self.min_cost = self.random_first_full_road() if is_random else self.greedy_first_full_road()
        self.taboo_list = []


    #Calculate the distance between two cities
    def city_distance(self,city1,city2):
        distance = ( (float(city1[1][0] - city2[1][0]))**2 + (float(city1[1][1] - city2[1][1]))**2 )**0.5
        return distance

    #Get the shortest distance among neighboring cities of the current city
    def next_shotest_road(self,city1,other_cities):
        tmp_min = 999999
        tmp_next = None
        for i in range(0,len(other_cities)):
            distance = self.city_distance(city1,other_cities[i])
            #print(distance)
            if distance < tmp_min:
                tmp_min = distance
                tmp_next = other_cities[i]
        return tmp_next,tmp_min


    #Randomly generate initial lines
    def random_first_full_road(self):
        cities = copy.deepcopy(self.city_list)
        cities.remove(cities[0])
        route = copy.deepcopy(cities)
        random.shuffle(route)
        cost = self.route_cost(route)
        return route,cost

    #Acquire the initial line according to the greedy algorithm
    def greedy_first_full_road(self):
        remain_city = copy.deepcopy(self.city_list)
        current_city = remain_city[0]
        road_list = []
        remain_city.remove(current_city)
        all_distance = 0
        while len(remain_city) > 0:
            next_city,distance = self.next_shotest_road(current_city,remain_city)
            all_distance += distance
            road_list.append(next_city)
            remain_city.remove(next_city)
            current_city = next_city
        all_distance += self.city_distance(self.city_list[0],road_list[-1])
        return road_list,round(all_distance,2)

    # Random exchange 2 city locations
    def random_swap_2_city(self,route):
        #print(route)
        road_list = copy.deepcopy(route)
        two_rand_city = random.sample(road_list,2)
        #print(two_rand_city)
        index_a = road_list.index(two_rand_city[0])
        index_b = road_list.index(two_rand_city[1])
        road_list[index_a] = two_rand_city[1]
        road_list[index_b] = two_rand_city[0]
        return road_list,sorted(two_rand_city)

    #Calculate the line path length
    def route_cost(self,route ):
        road_list = copy.deepcopy(route)
        current_city = self.city_list[0]
        while current_city in road_list:
            road_list.remove(current_city)
        all_distance = 0
        while len(road_list) > 0 :
            distance = self.city_distance(current_city,road_list[0])
            all_distance += distance
            current_city = road_list[0]
            road_list.remove(current_city)
        all_distance += self.city_distance(current_city,self.city_list[0])
        return round(all_distance,2)

    #Get the next line
    def single_search(self,route):
        #Generate candidate set list and its corresponding mobile list
        candidate_list = []
        candidate_move_list = []
        while len(candidate_list) < self.candidate_count:
            tmp_route,tmp_move = self.random_swap_2_city(route)
            #print("tmp_route:",tmp_route)
            if tmp_route not in candidate_list:
                candidate_list.append(tmp_route)
                candidate_move_list.append(tmp_move)
        #Calculate the length of each path in the candidate set
        candidate_cost_list = []
        for candidate in candidate_list:
            candidate_cost_list.append(self.route_cost(candidate))
        #print(candidate_list)

        min_candidate_cost = min(candidate_cost_list)                           #The shortest path in the candidate set
        min_candidate_index = candidate_cost_list.index(min_candidate_cost)
        min_candidate = candidate_list[min_candidate_index]                     #The line corresponding to the shortest path in the candidate set
        move_city = candidate_move_list[min_candidate_index]

        if min_candidate_cost < self.min_cost:
            self.min_cost = min_candidate_cost
            self.min_route = min_candidate
            if move_city in self.taboo_list:                                    #Law of defiance, when the value caused by this movement is better, ignore the taboo list
                self.taboo_list.remove(move_city)
            if len(self.taboo_list) >= self.taboo_list_length:                  #Judge whether the length of the taboo list has reached the limit, if yes, remove the initial move
                self.taboo_list.remove(self.taboo_list[0])
            self.taboo_list.append(move_city)                                    #Add this move to the taboo list
            return min_candidate

        else:
            #When no better route is found, choose the second best route. If the second best route is in the taboo list, go to the next level, and so on, find a second best route
            if move_city in self.taboo_list:
                tmp_min_candidate = min_candidate
                tmp_move_city = move_city

                while move_city in self.taboo_list:
                    candidate_list.remove(min_candidate)
                    candidate_cost_list.remove(min_candidate_cost)
                    candidate_move_list.remove(move_city)

                    min_candidate_cost = min(candidate_cost_list)  # Shortest path in the candidate set
                    min_candidate_index = candidate_cost_list.index(min_candidate_cost)
                    min_candidate = candidate_list[min_candidate_index]  # The line corresponding to the shortest path in the candidate set
                    move_city = candidate_move_list[min_candidate_index]
                    if len(candidate_list) < 10:                   #Prevent from falling into an infinite loop, jumping out when the number of candidate sets is less than 10
                        min_candidate = tmp_min_candidate
                        move_city = tmp_move_city
            if len(self.taboo_list) >= self.taboo_list_length:  # Determine whether the length of the taboo list has reached the limit, if so, remove the initial move
                self.taboo_list.remove(self.taboo_list[0])
            self.taboo_list.append(move_city)
            return min_candidate

    #Perform taboo_search until the termination condition is reached: loop 100 times
    def taboo_search(self):
        route = copy.deepcopy(self.min_route)
        for i in range(self.iteration_count):
            route = self.single_search(route)
        new_route = [self.city_list[0]]
        new_route.extend(self.min_route)
        new_route.append(self.city_list[0]) #Insert the first city information before and after
        return new_route,self.min_cost


#Draw route map
def draw_line_pic(route,cost,duration,desc):
    x = []
    y = []
    for item in route:
        x.append(item[1][0])
        y.append(item[1][1])
    x0 = [x[0],]
    y0 = [y[0],]
    plt.plot(x,y)
    plt.scatter(x0,y0,marker="o",c="r")
    for a, b in zip(x0, y0):
        plt.text(a, b, (a, b), ha='center', va='bottom', fontsize=10)
    plt.title("Taboo Search Algorithm (Okky) - ("+desc +" = "+ str(cost) + ")")
    plt.show()



if __name__ == "__main__":
    ts_random = Taboo_search(city_list)
    ts_greedy = Taboo_search(city_list,is_random=False)
    start_time1 = datetime.datetime.now()
    route_random,cost_random = ts_random.taboo_search()
    end_time1 = datetime.datetime.now()
    duration1 = (end_time1 - start_time1).seconds
    route_greedy,cost_greedy = ts_greedy.taboo_search()
    end_time2 = datetime.datetime.now()
    duration2 = (end_time2 - end_time1).seconds
    draw_line_pic(route_random,cost_random,duration1,"Random")
    draw_line_pic(route_greedy,cost_greedy,duration2,"Greedy")
