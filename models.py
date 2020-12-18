from app import db


class FinancialData(db.Model):
    __tablename__ = "financial_data"

    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String())
    country = db.Column(db.String())
    product = db.Column(db.String())
    discount_band = db.Column(db.String())
    units_sold = db.Column(db.Float())
    manufacturing = db.Column(db.Integer())
    sales_price = db.Column(db.Integer())
    gross_price = db.Column(db.Integer())
    discounts = db.Column(db.Integer())
    sales = db.Column(db.Integer())
    cogs = db.Column(db.Integer())
    profit = db.Column(db.Integer())
    date = db.Column(db.Date())

    def __init__(self, url, result_all, result_no_stop_words):
        self.url = url
        self.result_all = result_all
        self.result_no_stop_words = result_no_stop_words

    def __repr__(self):
        return f"table name {self.__tablename__} id: {self.id}"
