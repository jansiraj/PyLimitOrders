import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

from trading_framework.execution_client import ExecutionClient

from ..limit_order_agent import LimitOrderAgent


class LimitOrderAgentTest(unittest.TestCase):
    def setUp(self):
        self.execution_client = Mock(ExecutionClient)
        self.agent = LimitOrderAgent(execution_client=self.execution_client)

    def test_execute_held_orders_buy(self):
        self.agent.product_id = "IBM"
        self.agent.amount = 1000
        self.agent.limit = 100
        self.agent.add_order('BUY', self.agent.product_id, self.agent.amount, self.agent.limit)
        self.agent.market_price = self.agent.on_price_tick(self.agent.product_id, self.agent.limit)
        print(self.agent.market_price)
        self.agent.execute_held_orders()
        if self.agent.market_price and self.agent.market_price <= self.agent.limit:
            self.execution_client.buy.assert_called_with(self.agent.product_id, self.agent.amount)
            print("Bought the product {}".format(self.agent.product_id))
            self.assertEqual(len(self.agent.held_orders), 0)
        else:
            self.execution_client.buy.assert_not_called()

    def test_execute_held_orders_sell(self):
        self.agent.product_id = "GOOG"
        self.agent.amount = 300
        self.agent.limit = 145
        self.agent.add_order('SELL', self.agent.product_id, self.agent.amount, self.agent.limit)
        self.agent.market_price = self.agent.on_price_tick(self.agent.product_id, self.agent.limit)
        print(self.agent.market_price)
        self.agent.execute_held_orders()
        if self.agent.market_price and self.agent.market_price >= self.agent.limit:
            self.execution_client.sell.assert_called_with(self.agent.product_id, self.agent.amount)
            print("Sold the product {}".format(self.agent.product_id))
            self.assertEqual(len(self.agent.held_orders), 0)
        else:
            self.execution_client.sell.assert_not_called()


if __name__ == '__main__' and __package__ is None:
    file = Path(__file__).resolve()
    parent, top = file.parent, file.parents[3]
    sys.path.append(str(top))
if __name__ == '__main__':
    unittest.main()
    print( __package__)




