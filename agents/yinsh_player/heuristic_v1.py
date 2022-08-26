
# IMPORTS AND CONSTANTS ----------------------------------------------------------------------------------------------#


import time, random
from Yinsh.yinsh_model import YinshGameRule
from copy import deepcopy
from collections import deque
from queue import PriorityQueue

V_LINE_POS = [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 7)]
H_D_LINE_POS = [(1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5), (8, 5), (9, 5)]

THINKTIME = 0.95


# FUNCTIONS ----------------------------------------------------------------------------------------------------------#


# Defines this agent.
class myAgent():
    def __init__(self, _id):
        print("INIT")
        self.id = _id  # Agent needs to remember its own id.
        self.game_rule = YinshGameRule(2)  # Agent stores an instance of GameRule, from which to obtain functions.
        self.all_line = self.GetAllLine()
        # More advanced agents might find it useful to not be bound by the functions in GameRule, instead executing
        # their own custom functions under GetActions and DoAction.

    # Generates actions from this state.
    def GetActions(self, state):
        return self.game_rule.getLegalActions(state, self.id)

    # Carry out a given action on this state and return successor state, whether my agent add score and whether opponent add score
    def DoAction(self, state, action):
        my_agent_id = self.id
        oppo_agent_id = 1 if my_agent_id==0 else 0
        my_agent_score = state.agents[my_agent_id].score
        oppo_agent_score = state.agents[oppo_agent_id].score

        succ_state = self.game_rule.generateSuccessor(state, action, my_agent_id)
        is_my_score_add = succ_state.agents[my_agent_id].score > my_agent_score
        is_oppo_score_add = succ_state.agents[oppo_agent_id].score > oppo_agent_score

        return succ_state, is_my_score_add, is_oppo_score_add

    # Generates all the lines on board
    def GetAllLine(self):
        h_line = [self.game_rule.positionsOnLine(point, 'h') for point in H_D_LINE_POS]
        d_line = [self.game_rule.positionsOnLine(point, 'd') for point in H_D_LINE_POS]
        v_line = [self.game_rule.positionsOnLine(point, 'v') for point in V_LINE_POS]
        return h_line + d_line + v_line

    # Take a list of actions and an initial state
    # Return the optimal action
    def SelectAction(self, actions, game_state):

        # start_time = time.time()
        curr_state = deepcopy(game_state)
        valid_actions = self.GetActions(curr_state)

        pq = PriorityQueue()

        heuristic_val_list = []
        for action in valid_actions:
            copy_state = deepcopy(curr_state)
            succ_state, is_my_score_add, is_oppo_score_add = self.DoAction(copy_state, action)
            if is_my_score_add:
                return action
            if is_oppo_score_add:
                continue
            else:
                heuristic_val = self.balanced_heuristic(succ_state)
                if heuristic_val not in heuristic_val_list:
                    pq.put((heuristic_val, action))
                    heuristic_val_list.append(heuristic_val)

        if pq.qsize():
            return pq.get()[1]

        return random.choice(actions)

    # Balanced heuristic by considering the opponent and my agent
    def balanced_heuristic(self, game_state):
        my_agent_id = self.id
        my_agent_point = 0
        oppo_agent_id = 1 if my_agent_id==0 else 0
        oppo_agent_point = 0

        game_board = game_state.board

        for line in self.all_line:
            my_agent_point += self.cal_point(game_board, line, my_agent_id)
            oppo_agent_point += self.cal_point(game_board, line, oppo_agent_id)

        diff_point = oppo_agent_point - my_agent_point

        return diff_point

    # Offensive heuristic by considering my agent only
    def offensive_heuristic(self, game_state):
        my_agent_id = self.id
        my_agent_point = 0
        game_board = game_state.board

        for line in self.all_line:
            my_agent_point += self.cal_point(game_board, line, my_agent_id)

        return - my_agent_point

    # Defensive heuristic by considering the opponent only
    def defensive_heuristic(self, game_state):
        my_agent_id = self.id
        oppo_agent_id = 1 if my_agent_id==0 else 0
        oppo_agent_point = 0
        game_board = game_state.board

        for line in self.all_line:
            oppo_agent_point += self.cal_point(game_board, line, oppo_agent_id)

        return oppo_agent_point

    # Computes the point of this agent
    def cal_point(self, game_board, line, agent_id):
        point = 0
        factor = 1

        for pos in line:
            pos_num = game_board[pos]
            if pos_num == 5:
                continue
            elif pos_num == agent_id * 2 + 1:
                point += factor * 0.5
                factor *= 2
            elif pos_num == agent_id * 2 + 2:
                point += factor
                factor *= 2
            else:
                factor = 1

            if factor > 16:
                factor = 16

        return point

# END FILE -----------------------------------------------------------------------------------------------------------#
