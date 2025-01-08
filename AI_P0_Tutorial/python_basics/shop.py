class FruitShop:

    def __init__(self, name, fruit_prices):
        """
            name: Name of the fruit shop

            fruit_prices: Dictionary with keys as fruit
            strings and prices for values e.g.
            {'apples':2.00, 'oranges': 1.50, 'pears': 1.75}
        """
        self.fruitPrices = fruit_prices
        self.name = name
        print('Welcome to %s fruit shop' % name)

    def get_cost_per_pound(self, fruit):
        """
            fruit: Fruit string
        Returns cost of 'fruit', assuming 'fruit'
        is in our inventory or None otherwise
        """
        if fruit not in self.fruitPrices:
            print("Sorry we don't have %s" % fruit)
            return None
        return self.fruitPrices[fruit]

    def get_price_of_order(self, order_list):
        """
            order_list: List of (fruit, num_pounds) tuples

        Returns cost of order_list. If any of the fruit are
        """
        total_cost = 0.0
        for fruit, num_pounds in order_list:
            cost_per_pound = self.get_cost_per_pound(fruit)
            if cost_per_pound is not None:
                total_cost += num_pounds * cost_per_pound
        return total_cost

    def get_name(self):
        return self.name

    def __str__(self):
        return "<FruitShop: %s>" % self.get_name()
