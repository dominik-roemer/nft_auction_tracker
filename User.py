

class User:

    def __init__(self, coin=str, investment=float):
        self.coin = coin
        self.balance = investment
        self.profit_loss = 0
        self.investment = investment

    def deposit(self, amount=float):
        """add amount to balance"""
        self.balance += amount
        self.update_investment(amount)

    """private methods"""
    def update_investment(self, amount=float):
        """update the investment"""
        self.investment += amount

    def compute_profit_loss(self):
        self.profit_loss = self.balance/self.investment

