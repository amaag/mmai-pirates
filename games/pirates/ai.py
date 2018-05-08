# This is where you build your AI for the Pirates game.

from joueur.base_ai import BaseAI

# <<-- Creer-Merge: imports -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
# you can add additional import(s) here
# <<-- /Creer-Merge: imports -->>




class RoleBase():
    
    def __init__(self, AI, unit):
        self.AI = AI
        self.unit_id = unit.id
    

    def __str__(self):
        return("Role: unit = {}".format(self.unit_id))


    def fitness(AI, unit):
        return 0
        

    def effectiveness(self):
        return 0
    
    def execute(self):
        return(True)

    def get_unit(self):
        return(self.AI.game.get_game_object(self.unit_id))
        

class RecoverRole(RoleBase):

    def __init__(self, AI, unit):
        super().__init__(AI, unit)
        self.is_deposited = False

    def __str__(self):
        return("RecoverRole: unit = {}".format(self.get_unit().id))


    def fitness(AI, unit):
        
        if((unit is None) or (unit.tile is None)):
            return 0;
        
        path_to_port = AI.find_path(unit.tile, AI.player.port.tile, unit)
        if(len(path_to_port) < (AI.ship_moves + 1)):
            return(1-(unit.ship_health / AI.game.ship_health))
            
        else:
            return 0


    def effectiveness(self):
        if(is_deposited):
            return 1
        else:
            return 0
    
    def execute(self):
        
        unit = self.get_unit()

        # if this role's unit is dead...
        if(
            (unit.tile is None) or
            (unit.ship_health == 0) or
            (unit.ship_health == self.AI.game.ship_health)
        ):
            # return that the role is completed
            return True;

        # don't block the port
        if(unit.tile == self.AI.player.port.tile):
            print("MOVING OFF PORT")
            path = self.AI.find_path(self.AI.player.port.tile, self.AI.player.opponent.port.tile, unit)
            if(len(path) > 0):
                self.AI.move_to(unit, path[0])


        if(self.AI.move_to(unit, self.AI.player.port.tile, 1)):
            unit.rest()
            if(unit.ship_health == self.AI.game.ship_health):
                return True
            else:
                return False
            
        else:
            return False


class GoldRunnerRole(RoleBase):

    def __init__(self, AI, unit):
        super().__init__(AI, unit)
        self.is_deposited = False

    def __str__(self):
        return("GoldRunnerRole: unit = {}".format(self.get_unit().id))


    def fitness(AI, unit):
        if(unit.gold == 0):
            return 0
            
        else:
            #TODO: should we consider crew health? distance from the port?
            return(max(unit.gold / 600, 1) * (unit.ship_health / AI.game.ship_health))

    def effectiveness(self):
        if(is_deposited):
            return 1
        else:
            return 0
    
    def execute(self):
        
        unit = self.get_unit()
        
        # if this role's unit is dead...
        if(
            (unit.tile is None) or
            (unit.ship_health == 0)
        ):
            # return that the role is completed
            return True;

        if(self.AI.move_to(unit, self.AI.player.port.tile)):
            unit.deposit()
            return True
            
        else:
            return False


class ShipKillerRole(RoleBase):
    
    shipTargets = dict()
    

    def __init__(self, AI, unit):
        super().__init__(AI, unit)
        self.kill_count = 0
        self.turn_count = 0
        self.target_id = None

    def __del__(self):
        self.untarget()

    def __str__(self):
        return("ShipKillerRole: unit = {}, target = {}".format(self.get_unit().id, self.target_id))


    def fitness(AI, unit):
        
        # unit is dead
        if(unit.tile is None):
            return 0
          
        # unit has no ship  
        if(unit.ship_health == 0):
            return 0
            
        # no target available
        if(ShipKillerRole.get_best_target_for_unit(AI, unit) is None):
            return 0
            
            
        return 1
        
    def effectiveness(self):
        if(self.turn_count == 0):
            return 0
        else:
            return(self.kill_count / self.turn_count)
    
    
    def execute(self):
        unit = self.get_unit()
        target = self.AI.game.get_game_object(self.target_id)
        self.turn_count += 1

        if(target is None):
            target = self.get_best_target()
            self.target(target)

        if(target is not None):
    
            # Find a path to this merchant
            # TODO: intercept path
            if(self.AI.move_to(unit, target.tile, self.AI.game._ship_range)):
    
                unit.attack(target.tile, "ship")
                unit.log("attacking: {}".format(target.tile))
                
            # if we killed the ship...
            if(target.ship_health == 0):
                self.target(None)
                self.kill_count += 1

                #return goal is complete
                return(True)
                
            # otherwise, if we did not kill the ship
            else:
                # return goal not complete
                return(False)
                
        else:
            # nothing to target
            return True
            
        

    def get_best_target(self):
        return(ShipKillerRole.get_best_target_for_unit(self.AI, self.get_unit()))

    def get_best_target_for_unit(AI, unit):
                                    # Look for a merchant ship
        merchant = None
        max_fitness = 0
        for target in AI.game.units:
            fitness = ShipKillerRole.target_fitness(AI, unit, target)
            if(fitness > max_fitness):
                max_fitness = fitness
                merchant = target

        return(merchant)
        
    def target_fitness(AI, unit, target):
        # calculate distance func
        # calculate penalty for being otherwise targeted
        # calculate weighting for owner (i.e. player vs. merchant)

        if(
            ((target.target_port is None) and (target.owner != AI.player.opponent)) or
            (target.ship_health == 0) or
            (target.tile is None)
        ):
            return 0


            
        targetWeight = ShipKillerRole.shipTargets.get(target.id, 0)

        return 1/(1+abs(targetWeight - 1))


    def target(self, target):
        
        if(target is None):
            self.untarget()
            return
        
        if(self.target_id != target.id):
            self.untarget()
            ShipKillerRole.shipTargets[target.id] = ShipKillerRole.shipTargets.get(target.id, 0) + 1
            target.log("ID: {}".format(target.id))
            self.target_id = target.id
    
    def untarget(self):
        if(self.target_id is not None):
            ShipKillerRole.shipTargets[self.target_id] = ShipKillerRole.shipTargets.get(self.target_id, 1) - 1
            self.target_id = None
        


class AI(BaseAI):
    """ The basic AI functions that are the same between games. """

    def __init__(self, game):
        BaseAI.__init__(self, game)

        self.goals = dict()
        self.last_turn = -1
        self.phase = 0



    def get_name(self):
        """ This is the name you send to the server so your AI will control the player named this string.

        Returns
            str: The name of your Player.
        """
        # <<-- Creer-Merge: get-name -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        return "Pirates Python Player" # REPLACE THIS WITH YOUR TEAM NAME
        # <<-- /Creer-Merge: get-name -->>

    def start(self):
        """ This is called once the game starts and your AI knows its playerID and game. You can initialize your AI here.
        """
        # <<-- Creer-Merge: start -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        # replace with your start logic
        # <<-- /Creer-Merge: start -->>

    def game_updated(self):
        """ This is called every time the game's state updates, so if you are tracking anything you can update it here.
        """
        # <<-- Creer-Merge: game-updated -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        # replace with your game updated logic
        # <<-- /Creer-Merge: game-updated -->>

    def end(self, won, reason):
        """ This is called when the game ends, you can clean up your data and dump files here if need be.

        Args:
            won (bool): True means you won, False means you lost.
            reason (str): The human readable string explaining why you won or lost.
        """
        # <<-- Creer-Merge: end -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        # replace with your end logic
        # <<-- /Creer-Merge: end -->>


    def run_turn(self):
        """ This is called every time it is this AI.player's turn.

        Returns:
            bool: Represents if you want to end your turn. True means end your turn, False means to keep your turn going and re-call this function.
        """
        # <<-- Creer-Merge: runTurn -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        # Put your game logic here for runTurn
        
        if(self.last_turn != self.game.current_turn):
            self.last_turn = self.game.current_turn
            self.phase = 0

        if(self.phase == 0):

            for goal_id in self.goals:
                print("GOAL[{}]: {}".format(goal_id, self.goals[goal_id]))
                
                
            for unit in self.player.units:
                
    
                if(
                    (unit.id not in self.goals) or
                    (self.goals[unit.id] is None)
                ):
                    # goals[unit.id] = None

                    # CLAIMING FOR goldrunner
    
                    # if(unit.gold > 0):
                    #     goals[unit.id] = "goldrunner"
    
    
                    # CLAIMING FOR shipkiller
    
                    # else:
                    
                    if(GoldRunnerRole.fitness(self, unit) > 0):
                        print("CLAIMING: {} for GoldRunnerRole".format(unit.id))
                        self.goals[unit.id] = GoldRunnerRole(self, unit)
                    
                    if(ShipKillerRole.fitness(self, unit) > 0):
                        print("CLAIMING: {} for ShipKillerRole".format(unit.id))
                        self.goals[unit.id] = ShipKillerRole(self, unit)



            self.phase += 1            
            return(False)
        
        elif(self.phase == 1):

            for unit in self.player.units:
                
                goal = self.goals.get(unit.id, None)
    
                unit.log(
                    "MINE" + 
                    "goal: {}\n".format(goal) +
                    # "acted: {}\n".format(unit.acted) +
                    "crew: {}\n".format(unit.crew) +
                    "crew_health: {}\n".format(unit.crew_health) +
                    "gold: {}\n".format(unit.gold) +
                    # "moves: {}\n".format(unit.moves) +
                    # "owner: {}\n".format(unit.owner) +
                    # "path: {}\n".format(unit.path) +
                    "ship_health: {}\n".format(unit.ship_health) +
                    # "stunturns: {}\n".format(unit.stunturns) +
                    # "targetport: {}\n".format(unit.targetport) +
                    # "tile: {}\n".format(unit.tile) +
                    ""
                    )
    
                # GOAL: shipkiller
    
                if(goal is not None):
                    if(goal.execute()):
                        self.goals[unit.id] = None
    
            self.phase += 1            
            return(False)
        



        print("TRYING TO BUILD A CREW WITH {}/{} gold".format(self.player.gold, self.game.crew_cost))
        if(
            (self.player.port.tile.unit is None) and
            (self.player.gold >= self.game.crew_cost)
        ):
            self.player.port.spawn("crew")
            print("BUILDING A CREW")
    
        print("TRYING TO BUILD A SHIP WITH {}/{} gold".format(self.player.gold, self.game.ship_cost))
        while(
            (self.player.gold >= self.game.ship_cost) and
            (self.player.port.spawn("ship"))
        ):
            print("BUILDING A SHIP")
            path = self.find_path(self.player.port.tile, self.player.opponent.port.tile, self.player.port.tile.unit)
            if(len(path) > 0):
                print("MOVING NEW SHIP TO {}, {}".format(path[0].x, path[0].y))
                self.player.port.tile.unit.move(path[0])
            
        return(True)
        

        # for unit in self.game.units:            
        #     unit.log(
        #         "crew: {}\n".format(unit.crew) +
        #         "crew_health: {}\n".format(unit.crew_health) +
        #         "gold: {}\n".format(unit.gold) +
        #         # "moves: {}\n".format(unit.moves) +
        #         "owner: {}\n".format(unit.owner) +
        #         #"path: {}\n".format(unit.path) +
        #         "ship_health: {}\n".format(unit.ship_health) +
        #         # "stunturns: {}\n".format(unit.stunturns) +
        #         # "targetport: {}\n".format(unit.targetport) +
        #         # "tile: {}\n".format(unit.tile) +
        #         ""
        #         )
            
        
                
                

                # print("MERCHANT we are about to move to: {}".format(merchant.tile))
                # # Find a path to this merchant
                # if(self.move_to(unit, merchant.tile, self.game._ship_range)):
            
                #     unit.attack(merchant.tile, "ship")
                #     unit.log("attacking: {}".format(merchant.tile))
                    
                # if(merchant.ship_health == 0):
                #     goals[unit.id]["type"] = "unassigned"
        

            # GOAL: goldrunner
            
            # elif(goal["type"] == "goldrunner"):
            #     if(self.move_to(unit, self.player.port.tile)):
            #         unit.deposit()
            #         goals[unit.id]["type"] = "unassigned"
        
        
        # if len(self.player._units) == 0:
            # Spawn a crew if we have no units
        # elif self.player._units[0]._ship_health == 0:
            # Spawn a ship so our crew can sail

                
        # elif self.player._units[0]._ship_health < self.game._ship_health / 2.0:
        #     # Heal our unit if the ship is almost dead
        #     # Note: Crew also have their own health. Maybe try adding a check to see if the crew need healing?
        #     unit = self.player._units[0]

        #     # Find a path to our port so we can heal
        #     path = self.find_path(unit.tile, self.player.port.tile, unit)
        #     if len(path) > 0:
        #         # Move along the path if there is one
        #         unit.move(path[0])
        #     else:
        #         # Try to deposit any gold we have while we're here
        #         unit.deposit()

        #         # Try to rest
        #         unit.rest()
        # else:
            


        return True
        # <<-- /Creer-Merge: runTurn -->>

    def move_to(self, unit, goal, within = 0):
        path = self.find_path(unit.tile, goal, unit)
        i = 0
        while (
            (unit.moves > 0) and
            (len(path) - within > i)
        ):
            unit.move(path[i])
            i = i + 1
            
        if(len(path) - within <= i):
            return True
        else:
            return False

    def find_path(self, start, goal, unit):
        """A very basic path finding algorithm (Breadth First Search) that when given a starting Tile, will return a valid path to the goal Tile.
        Args:
            start (Tile): the starting Tile
            goal (Tile): the goal Tile
            unit (Unit): the Unit that will move
        Returns:
            list[Tile]: A list of Tiles representing the path, the the first element being a valid adjacent Tile to the start, and the last element being the goal.
        """

        if start == goal:
            # no need to make a path to here...
            return []

        # queue of the tiles that will have their neighbors searched for 'goal'
        fringe = []

        # How we got to each tile that went into the fringe.
        came_from = {}

        # Enqueue start as the first tile to have its neighbors searched.
        fringe.append(start)

        # keep exploring neighbors of neighbors... until there are no more.
        while len(fringe) > 0:
            
            # the tile we are currently exploring.
            inspect = fringe.pop(0)

            # cycle through the tile's neighbors.
            for neighbor in inspect.get_neighbors():
                # if we found the goal, we have the path!
                if neighbor == goal:
                    # Follow the path backward to the start from the goal and return it.
                    path = [goal]

                    # Starting at the tile we are currently at, insert them retracing our steps till we get to the starting tile
                    while inspect != start:
                        path.insert(0, inspect)
                        inspect = came_from[inspect.id]
                    return path
                # else we did not find the goal, so enqueue this tile's neighbors to be inspected

                # if the tile exists, has not been explored or added to the fringe yet, and it is pathable
                if neighbor and neighbor.id not in came_from and neighbor.is_pathable(unit):
                    # add it to the tiles to be explored and add where it came from for path reconstruction.
                    fringe.append(neighbor)
                    came_from[neighbor.id] = inspect

        # if you're here, that means that there was not a path to get to where you want to go.
        #   in that case, we'll just return an empty path.
        return []

    # <<-- Creer-Merge: functions -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
    # if you need additional functions for your AI you can add them here
    # <<-- /Creer-Merge: functions -->>
