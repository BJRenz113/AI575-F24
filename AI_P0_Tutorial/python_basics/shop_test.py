import shop

shop_name = 'the Berkeley Bowl'
fruit_prices = {'apples': 1.00, 'oranges': 1.50, 'pears': 1.75}
berkeley_shop = shop.FruitShop(shop_name, fruit_prices)
apple_price = berkeley_shop.get_cost_per_pound('apples')
print(apple_price)
print('Apples cost $%.2f at %s.' % (apple_price, shop_name))

other_name = 'the Stanford Mall'
other_fruit_prices = {'kiwis': 6.00, 'apples': 4.50, 'peaches': 8.75}
other_fruit_shop = shop.FruitShop(other_name, other_fruit_prices)
other_price = other_fruit_shop.get_cost_per_pound('apples')
print(other_price)
print('Apples cost $%.2f at %s.' % (other_price, other_name))
print("My, that's expensive!")
