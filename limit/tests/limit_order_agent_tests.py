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

    def test_price_tick_buy_IBM_below_100(self):
        self.agent.on_price_tick('IBM', 99)
        self.execution_client.buy.assert_called_with('IBM', 1000)

    def test_buy_below_limit(self):
        self.agent.on_price_tick('IBM', 99.00)
        self.execution_client.buy.assert_called()

    def test_buy_above_limit(self):
        self.agent.on_price_tick('IBM', 101.00)
        self.execution_client.buy.assert_not_called()

    def test_add_order(self):
        self.agent.add_order('BUY', 'AAPL', 500, 150)
        self.assertEqual(len(self.agent.held_orders), 1)
        self.assertEqual(self.agent.held_orders[0]['product_id'], 'AAPL')

    def test_execute_held_orders_buy(self):
        self.agent.add_order('BUY', 'AAPL', 500, 180)
        self.agent.market_price = self.agent.on_price_tick('AAPL', 180)
        self.agent.execute_held_orders()
        if self.agent.market_price and self.agent.market_price <= 180:
            self.execution_client.buy.assert_called_with('AAPL', 500)
            self.assertEqual(len(self.agent.held_orders), 0)
        else:
            self.execution_client.buy.assert_not_called()

    def test_execute_held_orders_sell(self):
        self.agent.add_order('SELL', 'GOOG', 300, 145)
        self.agent.market_price = self.agent.on_price_tick('GOOG', 145)
        self.agent.execute_held_orders()
        if self.agent.market_price and self.agent.market_price >= 130:
            self.execution_client.sell.assert_called_with('GOOG', 300)
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




