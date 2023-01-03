import game_utils as gu
import numpy as np
from random import shuffle

deck = np.array(['K', 'K', 'Q', 'Q', 'J', 'J'])

def leduc_round(iter_number, hero_strat, villain_strat):
    shuffle(deck)
    history = ""
    hero = iter_number % 2
    villain = 1 - hero

    while not gu.is_terminal(history):
        if gu.is_chance_node(history):
            history += 'd'

        curr_player = gu.get_active_player(history)  # player who has to make an action; e.g. if curr_player=0 and hero=1 then villain has to make an action
        card_player = deck[curr_player] 
        curr_strat = hero_strat if curr_player==hero else villain_strat  # strategy of player that has to make an action

        if 'd' in history: # if we're in a post-flop situation
            curr_player_action = curr_strat(history, card_player, deck[2])  # take flop into account to come up with an action
        else:
            curr_player_action = curr_strat(history, card_player)

        history += curr_player_action

    # return hero's utility
    if gu.get_active_player(history) == hero:  # if hero is the last player to make a move before showdown 
        return gu.terminal_util(history, deck[hero], deck[villain], deck[2])  # then return his utility

    else:  # if last player to make a move before showdown is villain
        return -1 * gu.terminal_util(history, deck[villain], deck[hero], deck[2])  # then hero's utility is minus villain's utility

def simulate_poker_game(hero_strats, villain_strats, n_rounds = 10):
    accum_util_record = np.zeros(n_rounds)
    accum_util = 0
    for it in range(n_rounds):
        accum_util += leduc_round(it, hero_strats, villain_strats)
        accum_util_record[it] = accum_util
    return accum_util_record
    









