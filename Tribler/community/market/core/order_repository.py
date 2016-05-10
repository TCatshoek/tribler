from Tribler.community.market.core.tick import TraderId, OrderNumber, OrderId, Order


class OrderRepository(object):
    """A repository for orders in the portfolio"""

    def find_by_id(self, order_id):
        """
        Find an order by its identity

        :param order_id: The order id to look for
        :type order_id: OrderId
        :return: The order or null if it cannot be found
        :rtype: Order
        """
        return NotImplemented

    def add(self, order):
        """
        Add an order to the collection

        :param order: The order to add
        :type order: Order
        """
        return NotImplemented

    def update(self, order):
        """
        Update an order in the collection

        :param order: The order that has been updated
        :type order: Order
        """
        return NotImplemented

    def delete_by_id(self, order_id):
        """
        Return the next identity

        :param order_id: The order id for the order to delete
        :type order_id: OrderId
        """
        return NotImplemented

    def next_identity(self):
        """
        Return the next identity

        :return: The next available identity
        :rtype: OrderId
        """
        return NotImplemented


class MemoryOrderRepository(OrderRepository):
    """A repository for orders in the portfolio stored in memory"""

    def __init__(self, mid):
        """
        Initialise the MemoryOrderRepository

        :param mid: Hex encoded version of the public key of this node
        :type mid: str
        """
        super(MemoryOrderRepository, self).__init__()

        self._mid = mid
        self._next_id = 0  # Counter to keep track of the number of messages created by this repository

        self._asks = {}
        self._bids = {}
        self._orders = {}

    def find_by_id(self, order_id):
        """
        Find an order by its identity

        :param order_id: The order id to look for
        :type order_id: OrderId
        :return: The order or null if it cannot be found
        :rtype: Order
        """
        assert isinstance(order_id, OrderId), type(order_id)
        return self._orders.get(order_id)

    def add(self, order):
        """
        Add an order to the collection

        :param order: The order to add
        :type order: Order
        """
        assert isinstance(order, Order), type(order)
        self._orders[order.order_id] = order

    def update(self, order):
        """
        Update an order in the collection

        :param order: The order that has been updated
        :type order: Order
        """
        assert isinstance(order, Order), type(order)
        self._orders[order.order_id] = order

    def delete_by_id(self, order_id):
        """
        Return the next identity

        :param order_id: The order id for the order to delete
        :type order_id: OrderId
        """
        assert isinstance(order_id, OrderId), type(order_id)
        del self._orders[order_id]

    def next_identity(self):
        """
        Return the next identity

        :return: The next available identity
        :rtype: OrderId
        """
        self._next_id += 1
        return OrderId(TraderId(self._mid), OrderNumber(str(self._next_id)))