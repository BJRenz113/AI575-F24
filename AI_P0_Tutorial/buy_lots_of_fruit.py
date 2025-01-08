"""
buy_lots_of_fruit.py
-----------------
Licensing Information:  You are free to use or extend these projects for
educational purposes provided that (1) you do not distribute or publish
solutions, (2) you retain this notice, and (3) you provide clear
attribution to UC Berkeley, including a link to http://ai.berkeley.edu.

Attribution Information: The Pacman AI projects were developed at UC Berkeley.
The core projects and autograders were primarily created by John DeNero
(denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
Student side autograding was added by Brad Miller, Nick Hay, and
Pieter Abbeel (pabbeel@cs.berkeley.edu).
"""

# To run this script, type
#
#   python buy_lots_of_fruit.py
#
# Once you have correctly implemented the buy_lots_of_fruit function,
# the script should produce the output:
#
# Cost of [('apples', 2.0), ('pears', 3.0), ('limes', 4.0)] is 12.25


FRUIT_PRICES = {'apples': 2.00,
                'oranges': 1.50,
                'pears': 1.75,
                'limes': 0.75,
                'strawberries': 1.00}


def buy_lots_of_fruit(order_list):
    """

    :param: order_list: List of (fruit, numPounds) tuples
    :return: Returns cost of order
    """
    total_cost = 0.0
    for fruit, cost in order_list:
        if fruit in FRUIT_PRICES:
            total_cost += FRUIT_PRICES[fruit] * cost
        else:
            print(f"Error: Fruit not in Fruit Price List")
            return None
    return total_cost


# Main Method
if __name__ == '__main__':
    # This code runs when you invoke the script from the command line
    ORDER_LIST = [('apples', 2.0), ('pears', 3.0), ('limes', 4.0)]
    print('Cost of', ORDER_LIST, 'is', buy_lots_of_fruit(ORDER_LIST))
