import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

load_dotenv()


app = Flask(__name__)
app.config.from_object(os.environ["APP_SETTINGS"])
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
from models import FinancialData


def _get_all_products():
    return (
        db.session.query(FinancialData.product)
        .distinct(FinancialData.product)
        .order_by(FinancialData.product)
        .all()
    )


def _get_all_departments():
    return (
        db.session.query(FinancialData.department)
        .distinct(FinancialData.department)
        .order_by(FinancialData.department)
        .all()
    )


def _get_all_countries():
    return (
        db.session.query(FinancialData.country)
        .distinct(FinancialData.country)
        .order_by(FinancialData.country)
        .all()
    )


def _get_financial_data():
    query = db.session.query(
        FinancialData.date,
        func.sum(FinancialData.gross_sales).label("gross_sales"),
        func.sum(FinancialData.sales).label("sales"),
        func.sum(FinancialData.cogs).label("cogs"),
        func.sum(FinancialData.profit).label("profit"),
    )
    query = query.group_by(FinancialData.date).order_by(FinancialData.date)

    gross_sales, sales, cogs, profit = [], [], [], []
    for _res in query.all():
        data_date = datetime.combine(_res.date, datetime.min.time())
        date_milliseconds = data_date.timestamp() * 1000
        gross_sales.append([date_milliseconds, _res.gross_sales])
        sales.append([date_milliseconds, _res.sales])
        cogs.append([date_milliseconds, _res.cogs])
        profit.append([date_milliseconds, _res.profit])

    return [
        dict(name="Gross Sales", data=gross_sales),
        dict(name="Sales", data=sales),
        dict(name="COGS", data=cogs),
        dict(name="Profit", data=profit),
    ]


@app.route("/")
def home():
    table = FinancialData.query.order_by(FinancialData.date.desc()).all()
    financial = _get_financial_data()

    products = _get_all_products()
    departments = _get_all_departments()
    countries = _get_all_countries()

    return render_template(
        "home.jinja2",
        table=[list(i.to_dict().values()) for i in table],
        financial=financial,
        all_countries=[x.country for x in countries],
        selected_countries=[],
        all_departments=[x.department for x in departments],
        selected_departments=[],
        all_products=[x.product for x in products],
        selected_products=[],
    )


if __name__ == "__main__":
    app.run()
