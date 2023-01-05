# CFR Leduc poker bot
This repository contains an implementation of a bot that uses Counterfactual Regret Minimization (CFR) to play the poker variant known as Leduc poker. To learn about the CFR algorithm, I followed the paper [An Introduction to Counterfactual Regret Minimization](http://modelai.gettysburg.edu/2013/cfr/cfr.pdf)(1), by Todd W. Neller
and Marc Lanctot. Besides covering the theory to understand CFR, this paper also presents C implementations of the algorithm for some simple imperfect information games, such as Rock, 
Paper, Scissors (RPS) or Kuhn Poker.

As we can read in (1): 
> Kuhn Poker is a simple 3-card poker game by Harold E. Kuhn. Two players each ante 1 chip, i.e.
bet 1 chip blind into the pot before the deal. Three cards, marked with numbers 1, 2, and 3, are
shuffled, and one card is dealt to each player and held as private information. Play alternates starting
with player 1. On a turn, a player may either pass or bet. A player that bets places an additional chip
into the pot. When a player passes after a bet, the opponent takes all chips in the pot. When there
are two successive passes or two successive bets, both players reveal their cards, and the player with
the higher card takes all chips in the pot.

## Leduc Poker 
In this repository I build upon (1) to implement a Leduc poker bot using CFR. Leduc poker adds one layer of complexity to Kuhn poker. In Leduc poker we have 6 cards, marked with numbers 1, 1, 2, 2, 3 and 3, and as in Kuhn poker, one card is dealt to each player 
and held as private information. When playing first or when facing a pass from the other player, a player can either pass or bet 2 chips. When facing a bet from the other player, a player
can either fold, call the 2 chips or raise to 4 chips. When facing a raise a player can either call or fold.

After the first betting round is finished and if no one has folded, one card is randomly chosen from the remaining 4 cards and dealt in the flop. The flop card is then combined with 
each of the players' pocket card to make up for their hand. The ranks work as in Texas Hold'Em, with pairs beating high cards. When the flop is dealt, there's a second betting round, in which the same rules 
as in the first betting round apply. If the showdown is reached, the player with the highest ranked hand wins the pot.

## Counterfactual Regret Minimization

#### Regret Matching and Minimization

The concept of regret matching is explained in (1) using Rock, 
Paper, Scissors as an example:
>Suppose we are playing RPS for money. Each player places a dollar on a table. If there is a winner, the
winner takes both dollars from the table. Otherwise, players retain their dollars. Further suppose that
we play rock while our opponent plays paper and wins, causing us to lose our dollar. Let our utility be
our net gain/loss in dollars. Then our utility for this play was -1. The utility for having instead played
paper and scissors against the opponent’s paper would have been 0 and +1, respectively.
We regret not having played paper and drawing, but we regret not having played scissors even
more, because our relative gain would have been even greater in retrospect. We here define regret of
not having chosen an action as the difference between the utility of that action and the utility of the
action we actually chose, with respect to the fixed choices of other players.

For sequential games such as Kuhn or Leduc poker, the Counterfactual Regret Minimization algorithm builds 
a tree in which each node represents a state of the game, with the leaves of the tree representing terminal 
states. Each node stores an array with the regrets of not having chosen each valid action for that state,
along with the probabilities of reaching that node. 

The strategies for each node are updated according to those regrets and reach probabilities. When two players 
using CFR to update their strategies play against each other, as the number of iterations tends to infinity the 
pair of strategies converges to a Nash equilibrium, in which no player can expect to improve play by changing strategy 
alone.

## Training our CFR bot

To train the CFR bot, we import the `leduc_cfr.py` file and execute its train function, passing it the parameter `n_iterations` to specify how many iterations we wanna train it for (the larger the number of iterations, the closer the two players conforming the bot will be to reaching a Nash equilibrium).

```python
import leduc_cfr

ev, i_map = leduc_cfr.train(n_iterations=100000)
```

`ev`, the first value that the `train` function returns, is the expected value of the first player to make a move in the CFR algorithm. At a Nash equilibrium, this value is around -0.06 (the reason being that the
first player to make a move in a poker game is always at a slight disadvantage for lacking information with respect to the second player), so this is a good indicator of how close to optimality our strategy is.

`i_map` is a dictionary where each key is a possible state in the game, and its corresponding value is the information set; an instance of the class InformationSet storing information associated to that game state, such as the regrets or the strategy.

We can now get retrieve the strategies stored in each information set for each game state to obtain a dictionary having game states as keys and their corresponding strategies as values, and export it to a json
file, which make up for our bot's strategy:

```python
import json

leduc_strats = {key: list(i_map[key].get_average_strategy()) for key in i_map}

with open('leduc_strats.json', 'w') as f:
    json.dump(leduc_strats, f)
```

We can also pretty print both of the CFR bot players' strategies along with their expected value by invoking the function display_results:

```python
leduc_cfr.display_results(ev, i_map)
```

## Comparing our CFR bot's performance against other bots

`leduc_game.py` is used to simulate `n_rounds` rounds of Leduc poker between two players whose strategies are given, and returns an array storing the accumulated gain for the first player in each iteration of the game.

We now implement two basic poker bots: : a random player `random_strat`, whose actions are totally random, and an honest player `honest_strat`, which plays aggressively when having a good enough hand, 
passively when having a medium hand, and passes or folds when they have a bad hand:


```python
from numpy.random import choice
import numpy as np
import game_utils as gu

def random_strat(history, card, flop=None):
    '''Strategy corresponding to a player whose actions are totally random'''
    valid_actions = gu.valid_actions(history)
    return choice(valid_actions)

def honest_strat(history, card, flop=None):
    def passive_move(history):
        if not history or history[-1]=='x' or history[-1]=='d':
            return 'x'
        elif history[-1] == 'b':
            return 'c'
        else:
            return 'f'

    def get_preflop_action(history, card):
        val_act = gu.valid_actions(history)
        if card == "J":
            return val_act[0]
        elif card == "K":
            return val_act[-1]
        elif card == "Q":
            return passive_move(history)

    def get_postflop_action(history, card, flop):
        val_act = gu.valid_actions(history)
        hand_rank = gu.rank(card+flop)
        if 1 <= hand_rank <=3:
            return val_act[-1]
        elif 4 <= hand_rank <=5:
            return passive_move(history)
        else:
            return val_act[-1]

    if flop:
        return get_postflop_action(history, card, flop)
    else:
        return get_preflop_action(history, card)
```

We also write a function that returns the CFR strategy corresponding to a given history and hand:

```python
import json

with open('leduc_strats.json') as f:
    leduc_strats = json.load(f)

def cfr_strat_as_function(history, card, flop=None):
    if flop:
        return choice(gu.valid_actions(history), p = leduc_strats[card+flop+" "+history])
    else:
        return choice(gu.valid_actions(history), p = leduc_strats[card+" "+history])
```

We now put the CFR bot to play against both bots and plot the results:

```python
import matplotlib.pyplot as plt
import leduc_game

n_rounds = 10000

accum_utils_vs_honest = leduc_game.simulate_poker_game(
    cfr_strat_as_function, 
    honest_strat,
    n_rounds
    )

accum_utils_vs_random = leduc_game.simulate_poker_game(
    cfr_strat_as_function, 
    random_strat,
    n_rounds
    )

xx = np.arange(0, n_rounds, dtype=int)
plt.plot(xx, accum_utils_vs_honest, label='CFR vs honest')
plt.plot(xx, accum_utils_vs_random, label='CFR vs random')
plt.legend(fontsize=7)
plt.show()
```

We can see that after `n_rounds=10000` iterations, our CFR bot clearly dominates the two others, beating `random_strat` at a rate of 0.5 chips per round and beating `honest_strat` at a rate of 0.1 chips per round, as the graph below shows:


![Alt text](https://github.com/scfenton6/leduc-cfr-poker-bot/blob/main/earnings_graph.png?raw=true "Optional Title")



