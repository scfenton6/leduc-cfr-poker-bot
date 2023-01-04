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
each of the players' pocket hand to make up for their hand. The ranks work as in Texas Hold'Em, with pairs beating high cards. When the flop is dealt, there's a second betting round, in which the same rules 
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

## The code

The CFR implementation for Leduc poker is stored in the files `leduc_cfr.py` and `game_utils.py`. `leduc_game.py` simulates
a game consisting of `n_rounds` rounds of Leduc poker between two players whose strategies are given, and returns an array 
storing the accumulated utility of the first player for each iteration of the game.

In `cfr_vs_others.py`, two bots are created: `random_strat`, whose actions are totally random, and `honest_strat`, which plays
aggressively when having a strong hand and passively when having a weak one. Both bots are put to play for `n_rounds=10000`
iterations against our CFR bot, and our bot clearly dominates the two others, beating `random_strat` at a rate of 0.5 chips per
round and beating `honest_strat` at a rate of 0.1 chips per round, as we can see in the graph below:


![Alt text](https://github.com/scfenton6/leduc-cfr-poker-bot/blob/main/earnings_graph.png?raw=true "Optional Title")



