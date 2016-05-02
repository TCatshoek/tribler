from .context import Tribler
from Tribler.community.market.core.tick import TraderId, MessageNumber, MessageId, Price
import unittest


class TickTestSuite(unittest.TestCase):
    """Tick test cases."""

    def test_trader_id(self):
        trader_id = TraderId('trader_id')
        trader_id2 = TraderId('trader_id')
        trader_id3 = TraderId('trader_id_2')
        self.assertEqual('trader_id', str(trader_id))
        self.assertTrue(trader_id == trader_id2)
        self.assertTrue(trader_id == trader_id)
        self.assertTrue(trader_id != trader_id3)
        self.assertFalse(trader_id == 6)
        self.assertEqual(trader_id.__hash__(), trader_id2.__hash__())
        self.assertNotEqual(trader_id.__hash__(), trader_id3.__hash__())

    def test_message_number(self):
        message_number = MessageNumber('message_number')
        message_number2 = MessageNumber('message_number')
        message_number3 = MessageNumber('message_number_2')
        self.assertEqual('message_number', str(message_number))
        self.assertTrue(message_number == message_number2)
        self.assertTrue(message_number == message_number)
        self.assertTrue(message_number != message_number3)
        self.assertFalse(message_number == 6)
        self.assertEqual(message_number.__hash__(), message_number2.__hash__())
        self.assertNotEqual(message_number.__hash__(), message_number3.__hash__())

    def test_message_id(self):
        trader_id = TraderId('trader_id')
        message_number = MessageNumber('message_number')
        message_number2 = MessageNumber('message_number2')
        message_id = MessageId(trader_id, message_number)
        message_id2 = MessageId(trader_id, message_number)
        message_id3 = MessageId(trader_id, message_number2)
        self.assertEqual(trader_id, message_id.trader_id)
        self.assertEqual(message_number, message_id.message_number)
        self.assertEqual('trader_id.message_number', str(message_id))
        self.assertTrue(message_id == message_id2)
        self.assertTrue(message_id == message_id)
        self.assertTrue(message_id != message_id3)
        self.assertFalse(message_id == 6)
        self.assertEqual(message_id.__hash__(), message_id2.__hash__())
        self.assertNotEqual(message_id.__hash__(), message_id3.__hash__())

    def test_price(self):

        # Object creation
        price = Price(63400)
        price2 = Price.from_float(6.34)
        price3 = Price.from_mil(63400)
        price4 = Price.from_float(18.3)
        price5 = Price(0)

        # Test for init validation
        with self.assertRaises(ValueError):
            Price(-1)

        # Test for conversions
        self.assertEqual(63400, int(price))
        self.assertEqual(63400, int(price2))
        self.assertEqual('6.3400', str(price))
        self.assertEqual('6.3400', str(price2))

        # Test for addition
        self.assertEqual(Price.from_float(24.64), price2 + price4)
        self.assertFalse(price4 is (price4 + price))
        price3 += price5
        self.assertEqual(Price.from_float(6.34), price3)

        # Test for subtraction
        self.assertEqual(Price.from_float(11.96), price4 - price2)
        self.assertFalse(price is (price - price))
        price3 -= price5
        self.assertEqual(Price.from_float(6.34), price3)
        with self.assertRaises(ValueError):
            price - price4

        # Test for comparison
        self.assertTrue(price2 < price4)
        self.assertTrue(price4 <= price4)
        self.assertTrue(price4 > price2)
        self.assertTrue(price4 >= price4)

        # Test for equality
        self.assertTrue(price == price3)
        self.assertTrue(price == price)
        self.assertTrue(price != price4)
        self.assertFalse(price == 6)

        # Test for hashes
        self.assertEqual(price.__hash__(), price3.__hash__())
        self.assertNotEqual(price.__hash__(), price4.__hash__())

if __name__ == '__main__':
    unittest.main()