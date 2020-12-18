from app import db


class FinancialData(db.Model):
    __tablename__ = "financial_data"

    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String())
    country = db.Column(db.String())
    product = db.Column(db.String())
    discount_band = db.Column(db.String())
    units_sold = db.Column(db.Float())
    manufacturing_price = db.Column(db.Float())
    sale_price = db.Column(db.Float())
    gross_sales = db.Column(db.Float())
    discounts = db.Column(db.Float())
    sales = db.Column(db.Float())
    cogs = db.Column(db.Float())
    profit = db.Column(db.Float())
    date = db.Column(db.Date())

    def __init__(self, url, result_all, result_no_stop_words):
        self.url = url
        self.result_all = result_all
        self.result_no_stop_words = result_no_stop_words

    def __repr__(self):
        return f"table name {self.__tablename__} id: {self.id}"

    def to_dict(self):
        return {
            "department": self.department,
            "country": self.country,
            "product": self.product,
            "discount_band": self.discount_band,
            "units_sold": self.units_sold,
            "manufacturing_price": self.manufacturing_price,
            "sale_price": self.sale_price,
            "gross_sales": self.gross_sales,
            "discounts": self.discounts,
            "sales": self.sales,
            "cogs": self.cogs,
            "profit": self.profit,
            "date": self.date,
        }
