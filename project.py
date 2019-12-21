class Project:
    def __init__(self, name: str, link: str, status: int, budget_amount: float, budget_currency: float, bid_count: int):
        self.name = name
        self.link = link
        self.status = status
        self.budget_amount = budget_amount
        self.budget_currency = budget_currency
        self.bid_count = bid_count
