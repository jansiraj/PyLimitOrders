import logging

from trading_framework.execution_client import ExecutionClient, ExecutionException
from trading_framework.price_listener import PriceListener



class LimitOrderAgent(PriceListener):

    def __init__(self, execution_client: ExecutionClient) -> None:
        """

        :param execution_client: can be used to buy or sell - see ExecutionClient protocol definition
        """
        super().__init__()
        self.execution_client = execution_client
        self.held_orders = []


    def on_price_tick(self, product_id: str, price: float):
        # see PriceListener protocol and readme file
        if product_id == 'IBM' and price < 100:
            self.execution_client.buy('IBM', 1000)

    def add_order(self, action, product_id, amount, limit):
        order = {'action': action, 'product_id': product_id, 'amount': amount, 'limit': limit}
        self.held_orders.append(order)

    def execute_held_orders(self, product_id, price):
        executed_orders = []
        for order in self.held_orders:
            try:
                if order['product_id'] == product_id and (order['action'] == "BUY" and price <= order['limit']):
                    self.execution_client.buy(product_id, order['amount'])
                    logging.info('Bought order of product {} for {} amount'.format(product_id, order['amount']))
                    executed_orders.append(order)
                elif order['product_id'] == product_id and (order['action'] == "SELL" and price >= order['limit']):
                    self.execution_client.sell(product_id, order['amount'])
                    logging.info('Sold order of product {} for {} amount'.format(product_id, order['amount']))
                    executed_orders.append(order)
            except ExecutionException as e:
                logging.warning('{} Order failed for product {} and amount {}'.format(order['action'],
                                                                                      product_id, order['amount']))
                logging.warning('Fail reason: {}'.format(e))
        for order in executed_orders:
            self.held_orders.remove(order)


