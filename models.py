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

    def __init__(
        self,
        department,
        country,
        product,
        discount_band,
        units_sold,
        manufacturing_price,
        sale_price,
        gross_sales,
        discounts,
        sales,
        cogs,
        profit,
        date,
    ):
        self.department = department
        self.country = country
        self.product = product
        self.discount_band = discount_band
        self.units_sold = units_sold
        self.manufacturing_price = manufacturing_price
        self.sale_price = sale_price
        self.gross_sales = gross_sales
        self.discounts = discounts
        self.sales = sales
        self.cogs = cogs
        self.profit = profit
        self.date = date

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
