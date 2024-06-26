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
        """override on_price_tick from PriceListener and calculate current
        market price of product and checks whether target reached market price"""
        try:
            # We will get market price using any third party APIS.Now statically assign price as market price
            market_price = price
            logging.info(f"Current market price of {product_id}: {market_price}")
            if market_price >= price:
                logging.info("Target price reached or exceeded!")
            else:
                logging.info("Target price not reached yet.")
            return market_price
        except Exception as e:
            print(f"Error fetching market price for {product_id}: {e}")

    def add_order(self, action, product_id, amount, limit):
        order = {'action': action, 'product_id': product_id, 'amount': amount, 'limit': limit}
        self.held_orders.append(order)

    def execute_held_orders(self):
        #can run this function on any timely basis
        executed_orders = []
        for order in self.held_orders:
            try:
                market_price = self.on_price_tick(order['product_id'], order['limit'])
                if market_price:
                    if order['action'] == "BUY" and market_price <= order['limit']:
                        self.execution_client.buy(order['product_id'], order['amount'])
                        logging.info('Bought order of product {}'.format(order['product_id']))
                        executed_orders.append(order)
                    elif order['action'] == "SELL" and market_price >= order['limit']:
                        self.execution_client.sell(order['product_id'], order['amount'])
                        logging.info('Sold order of product {}'.format(order['product_id']))
                        executed_orders.append(order)
            except ExecutionException as e:
                logging.warning('{} Order failed for product {}'.format(order['action'], order['product_id']))
                logging.warning('Fail reason: {}'.format(e))
        for order in executed_orders:
            self.held_orders.remove(order)




