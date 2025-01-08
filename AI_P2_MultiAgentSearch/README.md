
## Multi-Agent Search in Pacman Python project for CPSC 471/510

Fork this project into your private *COURSE* group, clone your fork into your user space, make changes as needed, commit, and push to your fork.

Directions are here, but can also be viewed at  http://ai.berkeley.edu/multiagent.html for basic description

> Note: We will use Python 3 and gitlab in this course!


For grading, I will have a script that clones your fork (main branch), and runs the auto grader script.

You can grade yourself using
<pre><code>
python autograder.py
</code></pre>

***
## Git Usage

In addition to the points assigned by the autograder I will be assigning points based on proper Git usage.

You must have at least 5 commits with reasonable commit messages spread across the project.
It is expected that you will have at least 1 commit after completing each question.

## Project 2: Multi-Agent Pacman

<div align="center">Version 3.003 Last Updated: 09/20/2024</div>

* * *

### Table of Contents

*   [Introduction](#Introduction)
*   [Welcome](#Welcome)
*   [Q1: Reflex Agent](#Q1)
*   [Q2: Minimax](#Q2)
*   [Q3: Alpha-Beta Pruning](#Q3)
*   [Q4: Expectimax](#Q4)
*   [Q5: Evaluation Function](#Q5)

* * *


<div align="center">

![](img/pacman_multi_agent.png)

Pacman, now with ghosts.
Minimax, Expectimax,
Evaluation.
</div>

### <a name="Introduction"></a>Introduction

In this project, you will design agents for the classic version of Pacman, including ghosts. Along the way, you will implement both minimax and expectimax search and try your hand at evaluation function design.

The code base has not changed much from the previous project, but please start with a fresh installation, rather than intermingling files from project 1.

As in project 1, this project includes an autograder for you to grade your answers on your machine. This can be run on all questions with the command:

<pre>python autograder.py</pre>

It can be run for one particular question, such as q2, by:

<pre>python autograder.py -q q2</pre>

It can be run for one particular test by commands of the form:

<pre>python autograder.py -t test_cases/q2/0-small-tree</pre>

By default, the autograder displays graphics with the `-t` option, but doesn't with the `-q` option. You can force graphics by using the `--graphics` flag, or force no graphics by using the `--no-graphics` flag.

See the autograder tutorial in Project 0 for more information about using the autograder.

The code for this project contains the following files:

<table class="intro" border="0" cellpadding="10">

<tbody>

<tr>

<td colspan="2"> <h4>Files you'll edit:</h4> </td>

</tr>

<tr>

<td>multi_agents.py</td>

<td>Where all of your multi-agent search agents will reside.</td>

</tr>
<tr>

<td colspan="2"> <h4>Files you'll want to review:</h4> </td>

</tr>

<tr>

<td>pacman.py</td>

<td>The main file that runs Pacman games. This file also describes a Pacman `GameState` type, which you will use extensively in this project</td>

</tr>

<tr>

<td>game.py</td>

<td>The logic behind how the Pacman world works. This file describes several supporting types like AgentState, Agent, Direction, and Grid.</td>

</tr>

<tr>

<td>util.py</td>

<td>Useful data structures for implementing search algorithms.</td>

</tr>

<tr>

<td colspan="2"> <h4>Files you can ignore:</h4></td>

</tr>

<tr>

<td>graphics_display.py</td>

<td>Graphics for Pacman</td>

</tr>

<tr>

<td>graphics_utils.py</td>

<td>Support for Pacman graphics</td>

</tr>

<tr>

<td>text_display.py</td>

<td>ASCII graphics for Pacman</td>

</tr>

<tr>

<td>ghost_agents.py</td>

<td>Agents to control ghosts</td>

</tr>

<tr>

<td>keyboard_agents.py</td>

<td>Keyboard interfaces to control Pacman</td>

</tr>

<tr>

<td>layout.py</td>

<td>Code for reading layout files and storing their contents</td>

</tr>

<tr>

<td>autograder.py</td>

<td>Project autograder</td>

</tr>

<tr>

<td>test_parser.py</td>

<td>Parses autograder test and solution files</td>

</tr>

<tr>

<td>test_classes.py</td>

<td>General autograding test classes</td>

</tr>

<tr>

<td>test_cases/</td>

<td>Directory containing the test cases for each question</td>

</tr>

<tr>

<td>multi_agent_test_classes.py</td>

<td>Project 2 specific autograding test classes</td>

</tr>

</tbody>

</table>

**Files to Edit and Submit:** You will fill in portions of `multi_agents.py` during the assignment. You should submit this file with your code and comments. Please _do not_ change the other files in this distribution or submit any of our original files other than this file.

**Evaluation:** Your code will be autograded for technical correctness. Please _do not_ change the names of any provided functions or classes within the code, or you will wreak havoc on the autograder. However, the correctness of your implementation -- not the autograder's judgements -- will be the final judge of your score. If necessary, we will review and grade assignments individually to ensure that you receive due credit for your work.

**Academic Dishonesty:** We will be checking your code against other submissions in the class for logical redundancy. If you copy someone else's code and submit it with minor changes, we will know. These cheat detectors are quite hard to fool, so please don't try. We trust you all to submit your own work only; _please_ don't let us down. If you do, we will pursue the strongest consequences available to us.

**Getting Help:** You are not alone! If you find yourself stuck on something, contact the course staff for help. I have office hours; please use them or drop me an email. If you can't make our office hours, let us know and we will schedule more. We want these projects to be rewarding and instructional, not frustrating and demoralizing. But, we don't know when or how to help unless you ask.

**Discussion:** Please be careful not to post spoilers.

***

### <a name="Welcome"></a>Multi-Agent Pacman

First, play a game of classic Pacman:

<pre>python pacman.py</pre>

Now, run the provided `ReflexAgent` in `multi_agents.py`:

<pre>python pacman.py -p ReflexAgent</pre>

Note that it plays quite poorly even on simple layouts:

<pre>python pacman.py -p ReflexAgent -l test_classic</pre>

Inspect its code (in `multi_agents.py`) and make sure you understand what it's doing.

***

### <a name="Q1"></a>Question 1 (4 points): Reflex Agent

Improve the `ReflexAgent` in `multi_agents.py` to play respectably. The provided reflex agent
 code provides some helpful examples of methods that query the `GameState` for information. A
  capable reflex agent will have to consider both food locations and ghost locations to perform
   well. Your agent should easily and reliably clear the `test_classic` layout:

<pre>python pacman.py -p ReflexAgent -l test_classic</pre>

Try out your reflex agent on the default `medium_classic` layout with one ghost or two (and
 animation
 off to speed up the display):

<pre>python pacman.py --frame_time 0 -p ReflexAgent -k 1</pre>

<pre>python pacman.py --frame_time 0 -p ReflexAgent -k 2</pre>

How does your agent fare? It will likely often die with 2 ghosts on the default board, unless your evaluation function is quite good.

_Note:_ As features, try the reciprocal of important values (such as distance to food) rather than just the values themselves.

_Note:_ The evaluation function you're writing is evaluating state-action pairs; in later parts of the project, you'll be evaluating states.

_Options:_ Default ghosts are random; you can also play for fun with slightly smarter directional ghosts using `-g DirectionalGhost`. If the randomness is preventing you from telling whether your agent is improving, you can use `-f` to run with a fixed random seed (same random choices every game). You can also play multiple games in a row with `-n`. Turn off graphics with `-q` to run lots of games quickly.

_Grading:_ we will run your agent on the `open_classic` layout 10 times. You will receive 0
 points if
 your agent times out, or never wins. You will receive 1 point if your agent wins at least 5 times, or 2 points if your agent wins all 10 games. You will receive an addition 1 point if your agent's average score is greater than 500, or 2 points if it is greater than 1000\. You can try your agent out under these conditions with

<pre>python autograder.py -q q1</pre>

To run it without graphics, use:

<pre>python autograder.py -q q1 --no-graphics</pre>

Don't spend too much time on this question, though, as the meat of the project lies ahead.

***

### <a name="Q2"></a>Question 2 (5 points): Minimax

Now you will write an adversarial search agent in the provided `MinimaxAgent` class stub in `multi_agents.py`. Your minimax agent should work with any number of ghosts, so you'll have to write an algorithm that is slightly more general than what you've previously seen in lecture. In particular, your minimax tree will have multiple min layers (one for each ghost) for every max layer.

Your code should also expand the game tree to an arbitrary depth. Score the leaves of your minimax tree with the supplied `self.evaluation_function`, which defaults to `score_evaluation_function`. `MinimaxAgent` extends `MultiAgentSearchAgent`, which gives access to `self.depth` and `self.evaluation_function`. Make sure your minimax code makes reference to these two variables where appropriate as these variables are populated in response to command line options.

_Important:_ A single search ply is considered to be one Pacman move and all the ghosts' responses, so depth 2 search will involve Pacman and each ghost moving two times.

_Grading_: We will be checking your code to determine whether it explores the correct number of game states. This is the only way reliable way to detect some very subtle bugs in implementations of minimax. As a result, the autograder will be _very_ picky about how many times you call `GameState.generate_successor`. If you call it any more or less than necessary, the autograder will complain. To test and debug your code, run

<pre>python autograder.py -q q2</pre>

This will show what your algorithm does on a number of small trees, as well as a pacman game. To run it without graphics, use:

<pre>python autograder.py -q q2 --no-graphics</pre>

_**Hints and Observations**_

*   The correct implementation of minimax will lead to Pacman losing the game in some tests. This is not a problem: as it is correct behaviour, it will pass the tests.
*   The evaluation function for the pacman test in this part is already written (`self.evaluation_function`). You shouldn't change this function, but recognize that now we're evaluating *states* rather than actions, as we were for the reflex agent. Look-ahead agents evaluate future states whereas reflex agents evaluate actions from the current state.
*   The minimax values of the initial state in the `minimax_classic` layout are 9, 8, 7, -492 for
 depths
 1, 2, 3 and 4 respectively. Note that your minimax agent will often win (665/1000 games for us) despite the dire prediction of depth 4 minimax.

    <pre>python pacman.py -p MinimaxAgent -l minimax_classic -a depth=4</pre>

*   Pacman is always agent 0, and the agents move in order of increasing agent index.
*   All states in minimax should be `GameStates`, either passed in to `get_action` or generated via `GameState.generate_successor`. In this project, you will not be abstracting to simplified states.
*   On larger boards such as `open_classic` and `medium_classic` (the default), you'll find Pacman
 to be
 good at not dying, but quite bad at winning. He'll often thrash around without making progress. He might even thrash around right next to a dot without eating it because he doesn't know where he'd go after eating that dot. Don't worry if you see this behavior, question 5 will clean up all of these issues.
*   When Pacman believes that his death is unavoidable, he will try to end the game as soon as possible because of the constant penalty for living. Sometimes, this is the wrong thing to do with random ghosts, but minimax agents always assume the worst:

    <pre>python pacman.py -p MinimaxAgent -l trapped_classic -a depth=3</pre>

    Make sure you understand why Pacman rushes the closest ghost in this case.

***

### <a name="Q3"></a>Question 3 (5 points): Alpha-Beta Pruning

Make a new agent that uses alpha-beta pruning to more efficiently explore the minimax tree, in `AlphaBetaAgent`. Again, your algorithm will be slightly more general than the pseudocode from lecture, so part of the challenge is to extend the alpha-beta pruning logic appropriately to multiple minimizer agents.

You should see a speed-up (perhaps depth 3 alpha-beta will run as fast as depth 2 minimax
). Ideally, depth 3 on `small_classic` should run in just a few seconds per move or faster.

<pre>python pacman.py -p AlphaBetaAgent -a depth=3 -l small_classic</pre>

The `AlphaBetaAgent` minimax values should be identical to the `MinimaxAgent` minimax values
, although the actions it selects can vary because of different tie-breaking behavior. Again, the
 minimax values of the initial state in the `minimax_classic` layout are 9, 8, 7 and -492 for
  depths 1
 , 2, 3 and 4 respectively.

_Grading_: Because we check your code to determine whether it explores the correct number of states, it is important that you perform alpha-beta pruning without reordering children. In other words, successor states should always be processed in the order returned by `GameState.get_legal_actions`. Again, do not call `GameState.generate_successor` more than necessary.

**You must _not_ prune on equality in order to match the set of states explored by our autograder.** (Indeed, alternatively, but incompatible with our autograder, would be to also allow for pruning on equality and invoke alpha-beta once on each child of the root node, but this will _not_ match the autograder.)

The pseudo-code below represents the algorithm you should implement for this question.

<p align="center">
  <img src="img/alpha-beta-on-inequality.png" alt="alpha-beta on inequality">
</p>

To test and debug your code, run

<pre>python autograder.py -q q3</pre>

This will show what your algorithm does on a number of small trees, as well as a pacman game. To run it without graphics, use:

<pre>python autograder.py -q q3 --no-graphics</pre>

The correct implementation of alpha-beta pruning will lead to Pacman losing some of the tests. This is not a problem: as it is correct behaviour, it will pass the tests.

***

### <a name="Q4"></a>Question 4 (5 points): Expectimax

Minimax and alpha-beta are great, but they both assume that you are playing against an adversary who makes optimal decisions. As anyone who has ever won tic-tac-toe can tell you, this is not always the case. In this question you will implement the `ExpectimaxAgent`, which is useful for modeling probabilistic behavior of agents who may make suboptimal choices.

As with the search and constraint satisfaction problems covered so far in this class, the beauty of these algorithms is their general applicability. To expedite your own development, we've supplied some test cases based on generic trees. You can debug your implementation on small the game trees using the command:

<pre>python autograder.py -q q4</pre>

Debugging on these small and manageable test cases is recommended and will help you to find bugs quickly. **Make sure when you compute your averages that you use floats.** Integer division in Python truncates, so that `1/2 = 0`, unlike the case with floats where `1.0/2.0 = 0.5`.

Once your algorithm is working on small trees, you can observe its success in Pacman. Random
 ghosts are of course not optimal minimax agents, and so modeling them with minimax search may
  not be appropriate. `ExpectimaxAgent`, will no longer take the min over all ghost actions, but
   the expectation according to your agent's model of how the ghosts act. To simplify your code
   , assume you will only be running against an adversary which chooses amongst their `get_legal_action`'s uniformly at random.

To see how the ExpectimaxAgent behaves in Pacman, run:

<pre>python pacman.py -p ExpectimaxAgent -l minimax_classic -a depth=3</pre>

You should now observe a more cavalier approach in close quarters with ghosts. In particular, if Pacman perceives that he could be trapped but might escape to grab a few more pieces of food, he'll at least try. Investigate the results of these two scenarios:

<pre>python pacman.py -p AlphaBetaAgent -l trapped_classic -a depth=3 -q -n 10</pre>

<pre>python pacman.py -p ExpectimaxAgent -l trapped_classic -a depth=3 -q -n 10</pre>

You should find that your `ExpectimaxAgent` wins about half the time, while your `AlphaBetaAgent` always loses. Make sure you understand why the behavior here differs from the minimax case.

The correct implementation of expectimax will lead to Pacman losing some of the tests. This is not a problem: as it is correct behaviour, it will pass the tests.

***

### <a name="Q5"></a>Question 5 (6 points): Evaluation Function

Write a better evaluation function for pacman in the provided function
 `better_evaluation_function`. The evaluation function should evaluate states, rather than
  actions like your reflex agent evaluation function did. You may use any tools at your disposal
   for evaluation, including your search code from the last project. With depth 2 search, your
    evaluation function should clear the `small_classic` layout with one random ghost more than half
     the time and still run at a reasonable rate (to get full credit, Pacman should be averaging around 1000 points when he's winning).

<pre>python autograder.py -q q5</pre>

Grading: the autograder will run your agent on the `small_classic` layout 10 times. We will assign
 points to your evaluation function in the following way:

*   If you win at least once without timing out the autograder, you receive 1 points. Any agent not satisfying these criteria will receive 0 points.
*   +1 for winning at least 5 times, +2 for winning all 10 times
*   +1 for an average score of at least 500, +2 for an average score of at least 1000 (including scores on lost games)
*   +1 if your games take on average less than 30 seconds on the autograder machine. The autograder is run on EC2, so this machine will have a fair amount of resources, but your personal computer could be far less performant (netbooks) or far more performant (gaming rigs).
*   The additional points for average score and computation time will only be awarded if you win at least 5 times.

#### Hints and Observations

*   As for your reflex agent evaluation function, you may want to use the reciprocal of important values (such as distance to food) rather than the values themselves.
*   One way you might want to write your evaluation function is to use a linear combination of features. That is, compute values for features about the state that you think are important, and then combine those features by multiplying them by different values and adding the results together. You might decide what to multiply each feature by based on how important you think it is.

* * *

### Submission

You should make at least one commit per question.

You're not done yet!

Make sure to commit your code and push to your personal fork.
