Logical Pacman Python project for CPSC 471/510

This project handles the Wumpus world from
Chapter 7 of R&N AI:MI 3rd and 4th editions

Fork this project, clone your fork into your user space, make changes as needed, commit, and push to your fork.

For grading, I will run your code on a variety of mazes.

Exercise 1: Basic logic
----------

Changed to the cloned directory, and start python, and `from logic import *` from the command line.

`logic.py` was developed by the authors of AI:MA and contains many of the algorithms in the textbook.

 Test the following commands from the command line.  
```
tt_true(expr('P'))
tt_true(expr('~P'))
tt_true(expr('P | ~P'))
tt_true(expr('P & ~P'))
tt_entails(expr('P & Q'), expr('P'))
tt_entails(expr('P & Q'), expr('~(~P | ~Q)'))
tt_entails(expr('P & Q'), expr('P'))
tt_entails(expr('P & Q'), expr('~P'))
dpll_satisfiable(expr('P & Q'))
dpll_satisfiable(expr('P & ~Q'))
dpll_satisfiable(expr('P & Q & ~P'))
```
Where `&` is a conjuction (AND), `|` is a disjunction, and `~` is the negation (NOT).

Submit a screen shot of the output, and a brief explanation of why the output is as given.  

See the pseudo-code in textbook for each algorithm, and look at `logic.py`.

Counting looking over the pseudo-code and code, this exercise should take no more than *15-20 minutes*.  I don't want an extensive writeup, just get used to the form of the expressions.

Exercise 2: Pacman-based Wumpus World
----------

Get the gold that the Wumpus stole from innocent children, puppies, and grandmothers.  

Defend yourself from the bloodthirsty killer if necessary
using our humane immobilizer ray.

Run the interactive version with:
<pre><code>
python wumpus.py
</code></pre>
Use the -h option to view options.

A suggested trial that shows the layout is:
<pre><code>
python wumpus.py -z 2 -l wumpus2 -s
</code></pre>
Drop the `-s` to run in the dark cave mode, with only your logical wits to guide you.

Several layouts are stored in the `layouts` folder.

 * Use arrow `up` to go forward
 * `left`/`right` arrows to turn left or right
 * `s` or `h` to halt (should not be necessary)
 * `g` to grab bag of gold if present
 * `x` to shoot your one and only humane immobilizer ray
  * in the direction you are currently facing.

Use
<pre><code>
python wumpus.py -z 2 -l wumpus_maze -s -p GoForwardAgent
</code></pre>
To show the simple *Go forward when possible, turn right if not* agent defined in `pacman_agents.py`.   

`GoForwardAgent` is not very successful.

The shell of `LogicalAgent` is started in `pacmanAgents.py`.
<pre><code>
python wumpus.py -z 2 -l wumpus2 -s -p LogicalAgent
</code></pre>

The `LogicalAgent` was working well, and then some code got deleted.  
You need to fix this by adding appropriate code at the `#@TODO - ` tags in the `pacman_agents.py` code.

This version assumes a good localization system, and therefore does not use fluents and reasoning about location within the map.   
The knowledge base is changed to reflect knowledge at the current state (e.g. by removing the WA (Wumpus Active) proposition and adding ~WA) at the appropriate time when wumpus is immobilized.  

Some simple propositions (e.g. have_immobilizer and have_gold) are maintained outside the KB.  
This simplifies the reasoning complexity by reducing the number of logical atomics.

The KB is only used to reason about the position of deadly pits and the Wumpus.

You grade will be based on how well the Wumpus negotiates the provided layouts.  The solution should be able to consistently navigate `wumpus_tiny`, `wumpus`, `wumpus2`, and `wumpus_maze` layouts as specified by the `-l` option in
<pre><code>
python wumpus.py -z 2 -l wumpus_maze -s -p LogicalAgent
</code></pre>

By default the project uses dpll_satisfiable to check for entailment.
This is **sloooowwwwww**.  I *strongly* suggest that you follow the optional *pysat* installation
below, and change line 106 to `False`.  

Using the default `dpll_satisfiable`,
the code takes 36 seconds to execute `wumpus_tiny` on my laptop;
using `minisat` it takes 15-18 seconds.  
For the `wumpus2` layout, `dpll_satisfiable` takes 360 seconds,
 while `minisat` only takes 35 seconds.

Setup: Optional Install PySat
-----------------------------------------------------------
This project can make use of the light weight, open source, PySAT solver (http://https://pysathq.github.io).  
This is orders of magnitude faster than dpll_satisfiable, and is worth the effort to install.

<pre>
pip install python-sat
</pre>

When I ran, it took a while ...
<pre>
Collecting python-sat
  Downloading python-sat-0.1.7.dev19.tar.gz (3.6 MB)
     |████████████████████████████████| 3.6 MB 8.7 MB/s
Requirement already satisfied: six in /opt/anaconda3/lib/python3.9/site-packages (from python-sat) (1.16.0)
Building wheels for collected packages: python-sat
  Building wheel for python-sat (setup.py) ... -
</pre>

Give it some time to build and finish install.

`python test_pysat.py`

The three simple tests should pass.
If they do not, or you get unexpected behavior,
please contact your instructor.

Code Layout:
-----------

All student code is in `pacman_agents.py`.

* `get_action`
 * This method processes the newly visited states and percepts, and updates the knowledge base, and
 then processes the hybrid planning and reasoning system.
* `update_kb_visit`
 * This method adds propositions for visited cells and neighbors.  This approach incrementally
 builds the KB as the world is explored.
 * The method needs updates; see `#@TODO` flags
* `update_kb_percepts`
 * This methods adds propositions based on percepts in the current location
 * This method needs updates; see `#@TODO` flags
* `get_safe_plan`,`get_unsafe_plan`, `get_plan`
 * These methods return a guaranteed safe plan from the current location to the
 closest cell in the goal set.  
 * For `get_safe_plan` only unvisited locations known to be
 safe are added to the goal set.  
 * For `get_unsafe_plan`, we reason to see if we can prove
 cells are unsafe to exclude from goal set, but uncertain cells are added to the goal set.  A random
 subset of these cells are a chosen as the goal set, and sent to `get_plan`.
 These methods can be used as is, or you can modify if you want.
* `shot_available` and `plan_shot`
 * These are used to see if a Wumpus might be at a given location, plans a safe motion
 to the neighboring cell, and then shoots the humane immobilizer ray.  
 * The system updates the knowledge base on either
 a hit or miss.  
 * The `get_action` logic prefers to take an uncertain shot over a visit to an uncertain cell as this will add information to the KB without risking death, but may waste the only immobilizer shot.
 These methods can be used as is, or you can modify if you want.
* `is_location_safe`
 * This method checks if the location is safe.  The code includes checks based on
 data tracked, but unfortunately, the test that checks the KB for safety got deleted.  
 * Make sure you add the right question at the `#@TODO` flag
* `ask_entailed`
 * This method does the magic.  
 * The only change to do here is to change line 106 to `False` in order to use the `minisat` program after it is installed.
