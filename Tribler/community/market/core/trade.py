from message import TraderId, MessageNumber, Message, MessageId
from order import OrderId, OrderNumber
from price import Price
from quantity import Quantity
from timestamp import Timestamp


class Trade(Message):
    """Abstract class representing a trade."""

    def __init__(self, message_id, order_id, recipient_order_id, timestamp):
        """
        Initialise the trade

        Don't use this method directly

        :param message_id: A message id to identify the trade
        :param order_id: A order id to identify the order
        :param recipient_order_id: A order id to identify the traded party
        :param timestamp: A timestamp wen this trade was created
        :type message_id: MessageId
        :type order_id: OrderId
        :type recipient_order_id: OrderId
        :type timestamp: Timestamp
        """
        super(Trade, self).__init__(message_id, timestamp)

        assert isinstance(order_id, OrderId), type(order_id)
        assert isinstance(recipient_order_id, OrderId), type(recipient_order_id)

        self._order_id = order_id
        self._recipient_order_id = recipient_order_id

    @classmethod
    def propose(cls, message_id, order_id, recipient_order_id, price, quantity, timestamp):
        """
        Propose a trade

        :param message_id: A message id to identify the trade
        :param order_id: A order id to identify the order
        :param recipient_order_id: A order id to identify the traded party
        :param price: A price for the trade
        :param quantity: A quantity to be traded
        :param timestamp: A timestamp wen this trade was created
        :type message_id: MessageId
        :type order_id: OrderId
        :type recipient_order_id: OrderId
        :type timestamp: Timestamp
        :return: A proposed trade
        :rtype: ProposedTrade
        """
        return ProposedTrade(
            message_id,
            order_id,
            recipient_order_id,
            price,
            quantity,
            timestamp
        )

    @classmethod
    def accept(cls, message_id, timestamp, proposed_trade):
        """
        Accept a trade

        :param message_id: A message id to identify the trade
        :param timestamp: A timestamp when the trade was accepted
        :param proposed_trade: A proposed trade that needs to be accepted
        :type message_id: MessageId
        :type timestamp: Timestamp
        :type proposed_trade: ProposedTrade
        :return: An accepted trade
        :rtype: AcceptedTrade
        """
        assert isinstance(proposed_trade, ProposedTrade), type(proposed_trade)

        return AcceptedTrade(
            message_id,
            proposed_trade.order_id,
            proposed_trade.recipient_order_id,
            proposed_trade.price,
            proposed_trade.quantity,
            timestamp
        )

    @classmethod
    def decline(cls, message_id, timestamp, proposed_trade):
        """
        Decline a trade

        :param message_id: A message id to identify the trade
        :param timestamp: A timestamp when the trade was declined
        :param proposed_trade: A proposed trade that needs to be declined
        :type message_id: MessageId
        :type timestamp: Timestamp
        :type proposed_trade: ProposedTrade
        :return: A declined trade
        :rtype: DeclinedTrade
        """
        assert isinstance(proposed_trade, ProposedTrade), type(proposed_trade)

        return DeclinedTrade(
            message_id,
            proposed_trade.order_id,
            proposed_trade.recipient_order_id,
            timestamp
        )

    @classmethod
    def counter(cls, message_id, quantity, timestamp, proposed_trade):
        """
        Counter a trade

        :param message_id: A message id to identify the trade
        :param quantity: The quantity to use for the counter offer
        :param timestamp: A timestamp when the trade was countered
        :param proposed_trade: A proposed trade that needs to be countered
        :type message_id: MessageId
        :type quantity: Quantity
        :type timestamp: Timestamp
        :type proposed_trade: ProposedTrade
        :return: A counter trade
        :rtype: CounterTrade
        """
        assert isinstance(proposed_trade, ProposedTrade), type(proposed_trade)

        return CounterTrade(
            message_id,
            proposed_trade.recipient_order_id,
            proposed_trade.order_id,
            proposed_trade.price,
            quantity,
            timestamp
        )

    @property
    def order_id(self):
        """
        Return the order id

        :return: The order id
        :rtype: OrderId
        """
        return self._order_id

    @property
    def recipient_order_id(self):
        """
        Return the order id of the party to trade with

        :return: The order id
        :rtype: OrderId
        """
        return self._recipient_order_id

    def to_network(self):
        return NotImplemented


class ProposedTrade(Trade):
    """Class representing a proposed trade."""

    def __init__(self, message_id, order_id, recipient_order_id, price, quantity, timestamp):
        """
        Initialise a proposed trade

        Don't use this method directly

        :param message_id: A message id to identify the trade
        :param order_id: A order id to identify the order
        :param recipient_order_id: A order id to identify the traded party
        :param price: A price for the trade
        :param quantity: A quantity to be traded
        :param timestamp: A timestamp wen this trade was created
        :type message_id: MessageId
        :type order_id: OrderId
        :type recipient_order_id: OrderId
        :type price: Price
        :type quantity: Quantity
        :type timestamp: Timestamp
        """
        super(ProposedTrade, self).__init__(message_id, order_id, recipient_order_id, timestamp)

        assert isinstance(price, Price), type(price)
        assert isinstance(quantity, Quantity), type(quantity)

        self._price = price
        self._quantity = quantity

    @classmethod
    def from_network(cls, data):
        """
        Restore a proposed trade from the network

        :param data: object with (trader_id, message_number, order_number, recipient_trader_id, recipient_order_number, price, quantity, timestamp) properties
        :return: Restored proposed trade
        :rtype: ProposedTrade
        """
        assert hasattr(data, 'trader_id'), isinstance(data.trader_id, TraderId)
        assert hasattr(data, 'message_number'), isinstance(data.message_number, MessageNumber)
        assert hasattr(data, 'order_number'), isinstance(data.order_number, OrderNumber)
        assert hasattr(data, 'recipient_trader_id'), isinstance(data.recipient_trader_id, TraderId)
        assert hasattr(data, 'recipient_order_number'), isinstance(data.recipient_order_number, OrderNumber)
        assert hasattr(data, 'price'), isinstance(data.price, Price)
        assert hasattr(data, 'quantity'), isinstance(data.quantity, Quantity)
        assert hasattr(data, 'timestamp'), isinstance(data.timestamp, Timestamp)

        return cls(
            MessageId(data.trader_id, data.message_number),
            OrderId(data.trader_id, data.order_number),
            OrderId(data.recipient_trader_id, data.recipient_order_number),
            data.price,
            data.quantity,
            data.timestamp
        )

    @property
    def price(self):
        """
        Return the price

        :return: The price
        :rtype: Price
        """
        return self._price

    @property
    def quantity(self):
        """
        Return the quantity

        :return: The quantity
        :rtype: Quantity
        """
        return self._quantity

    def to_network(self):
        """
        Return network representation of a proposed trade

        :return: tuple(<destination public identifiers>),tuple(<trader_id>, <message_number>, <order_number>, <recipient_trader_id>, <recipient_order_number>, <price>, <quantity>, <timestamp>)
        :rtype: tuple, tuple
        """
        return tuple(
            [self._recipient_order_id.trader_id]
        ), (
                   self._order_id.trader_id,
                   self._message_id.message_number,
                   self._order_id.order_number,
                   self._recipient_order_id.trader_id,
                   self._recipient_order_id.order_number,
                   self._price,
                   self._quantity,
                   self._timestamp
               )


class AcceptedTrade(Trade):
    """Class representing an accepted trade."""

    def __init__(self, message_id, order_id, recipient_order_id, price, quantity, timestamp):
        """
        Initialise an accepted trade

        Don't use this method directly

        :param message_id: A message id to identify the trade
        :param order_id: A order id to identify the order
        :param recipient_order_id: A order id to identify the traded party
        :param price: A price for the trade
        :param quantity: A quantity to be traded
        :param timestamp: A timestamp wen this trade was created
        :type message_id: MessageId
        :type order_id: OrderId
        :type recipient_order_id: OrderId
        :type price: Price
        :type quantity: Quantity
        :type timestamp: Timestamp
        """
        super(AcceptedTrade, self).__init__(message_id, order_id, recipient_order_id, timestamp)

        assert isinstance(price, Price), type(price)
        assert isinstance(quantity, Quantity), type(quantity)

        self._price = price
        self._quantity = quantity

    @classmethod
    def from_network(cls, data):
        """
        Restore an accepted trade from the network

        :param data: object with (trader_id, message_number, order_number, recipient_trader_id, recipient_order_number, price, quantity, timestamp) properties
        :return: Restored accepted trade
        :rtype: AcceptedTrade
        """
        assert hasattr(data, 'trader_id'), isinstance(data.trader_id, TraderId)
        assert hasattr(data, 'message_number'), isinstance(data.message_number, MessageNumber)
        assert hasattr(data, 'order_number'), isinstance(data.order_number, OrderNumber)
        assert hasattr(data, 'recipient_trader_id'), isinstance(data.recipient_trader_id, TraderId)
        assert hasattr(data, 'recipient_order_number'), isinstance(data.recipient_order_number, OrderNumber)
        assert hasattr(data, 'price'), isinstance(data.price, Price)
        assert hasattr(data, 'quantity'), isinstance(data.quantity, Quantity)
        assert hasattr(data, 'timestamp'), isinstance(data.timestamp, Timestamp)

        return cls(
            MessageId(data.trader_id, data.message_number),
            OrderId(data.trader_id, data.order_number),
            OrderId(data.recipient_trader_id, data.recipient_order_number),
            data.price,
            data.quantity,
            data.timestamp
        )

    @property
    def price(self):
        """
        Return the price

        :return: The price
        :rtype: Price
        """
        return self._price

    @property
    def quantity(self):
        """
        Return the quantity

        :return: The quantity
        :rtype: Quantity
        """
        return self._quantity

    def to_network(self):
        """
        Return network representation of an accepted trade

        :return: tuple(<destination public identifiers>),tuple(<trader_id>, <message_number>, <order_number>, <recipient_trader_id>, <recipient_order_number>, <price>, <quantity>, <timestamp>)
        :rtype: tuple, tuple
        """
        return tuple(), (
            self._order_id.trader_id,
            self._message_id.message_number,
            self._order_id.order_number,
            self._recipient_order_id.trader_id,
            self._recipient_order_id.order_number,
            self._price,
            self._quantity,
            self._timestamp
        )


class DeclinedTrade(Trade):
    """Class representing a declined trade."""

    def __init__(self, message_id, order_id, recipient_order_id, timestamp):
        """
        Initialise a declined trade

        Don't use this method directly

        :param message_id: A message id to identify the trade
        :param order_id: A order id to identify the order
        :param recipient_order_id: A order id to identify the order
        :param timestamp: A timestamp wen this trade was created
        :type message_id: MessageId
        :type order_id: OrderId
        :type recipient_order_id: OrderId
        :type timestamp: Timestamp
        """
        super(DeclinedTrade, self).__init__(message_id, order_id, recipient_order_id, timestamp)

    @classmethod
    def from_network(cls, data):
        """
        Restore a declined trade from the network

        :param data: object with (trader_id, message_number, order_number, recipient_trader_id, recipient_order_number, timestamp) properties
        :return: Restored declined trade
        :rtype: DeclinedTrade
        """
        assert hasattr(data, 'trader_id'), isinstance(data.trader_id, TraderId)
        assert hasattr(data, 'message_number'), isinstance(data.message_number, MessageNumber)
        assert hasattr(data, 'order_number'), isinstance(data.order_number, OrderNumber)
        assert hasattr(data, 'recipient_trader_id'), isinstance(data.recipient_trader_id, TraderId)
        assert hasattr(data, 'recipient_order_number'), isinstance(data.recipient_order_number, OrderNumber)
        assert hasattr(data, 'timestamp'), isinstance(data.timestamp, Timestamp)

        return cls(
            MessageId(data.trader_id, data.message_number),
            OrderId(data.trader_id, data.order_number),
            OrderId(data.recipient_trader_id, data.recipient_order_number),
            data.timestamp
        )

    def to_network(self):
        """
        Return network representation of a declined trade

        :return: tuple(<destination public identifiers>),tuple(<trader_id>, <message_number>, <order_number>, <recipient_trader_id>, <recipient_order_number>, <timestamp>)
        :rtype: tuple, tuple
        """
        return tuple(
            [self._recipient_order_id.trader_id]
        ), (
                   self._order_id.trader_id,
                   self._message_id.message_number,
                   self._order_id.order_number,
                   self._recipient_order_id.trader_id,
                   self._recipient_order_id.order_number,
                   self._timestamp
               )


class CounterTrade(Trade):
    """Class representing a counter trade."""

    def __init__(self, message_id, order_id, recipient_order_id, price, quantity, timestamp):
        """
        Initialise a counter trade

        Don't use this method directly

        :param message_id: A message id to identify the trade
        :param order_id: A order id to identify the order
        :param recipient_order_id: A order id to identify the traded party
        :param price: A price for the trade
        :param quantity: A quantity to be traded
        :param timestamp: A timestamp wen this trade was created
        :type message_id: MessageId
        :type order_id: OrderId
        :type recipient_order_id: OrderId
        :type price: Price
        :type quantity: Quantity
        :type timestamp: Timestamp
        """
        super(CounterTrade, self).__init__(message_id, order_id, recipient_order_id, timestamp)

        assert isinstance(price, Price), type(price)
        assert isinstance(quantity, Quantity), type(quantity)

        self._price = price
        self._quantity = quantity

    @classmethod
    def from_network(cls, data):
        """
        Restore a counter trade from the network

        :param data: object with (trader_id, message_number, order_number, recipient_trader_id, recipient_order_number, price, quantity, timestamp) properties
        :return: Restored counter trade
        :rtype: CounterTrade
        """
        assert hasattr(data, 'trader_id'), isinstance(data.trader_id, TraderId)
        assert hasattr(data, 'message_number'), isinstance(data.message_number, MessageNumber)
        assert hasattr(data, 'order_number'), isinstance(data.order_number, OrderNumber)
        assert hasattr(data, 'recipient_trader_id'), isinstance(data.recipient_trader_id, TraderId)
        assert hasattr(data, 'recipient_order_number'), isinstance(data.recipient_order_number, OrderNumber)
        assert hasattr(data, 'price'), isinstance(data.price, Price)
        assert hasattr(data, 'quantity'), isinstance(data.quantity, Quantity)
        assert hasattr(data, 'timestamp'), isinstance(data.timestamp, Timestamp)

        return cls(
            MessageId(data.trader_id, data.message_number),
            OrderId(data.trader_id, data.order_number),
            OrderId(data.recipient_trader_id, data.recipient_order_number),
            data.price,
            data.quantity,
            data.timestamp
        )

    @property
    def price(self):
        """
        Return the price

        :return: The price
        :rtype: Price
        """
        return self._price

    @property
    def quantity(self):
        """
        Return the quantity

        :return: The quantity
        :rtype: Quantity
        """
        return self._quantity

    def to_network(self):
        """
        Return network representation of a counter trade

        :return: tuple(<destination public identifiers>),tuple(<trader_id>, <message_number>, <order_number>, <recipient_trader_id>, <recipient_order_number>, <price>, <quantity>, <timestamp>)
        :rtype: tuple, tuple
        """
        return tuple(
            [self._recipient_order_id.trader_id]
        ), (
                   self._order_id.trader_id,
                   self._message_id.message_number,
                   self._order_id.order_number,
                   self._recipient_order_id.trader_id,
                   self._recipient_order_id.order_number,
                   self._price,
                   self._quantity,
                   self._timestamp
               )