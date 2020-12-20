import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

load_dotenv()


app = Flask(__name__)
app.config.from_object(os.environ["APP_SETTINGS"])
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
from models import FinancialData


def _get_financial_data():
    qry = db.session.query(
        FinancialData.date,
        func.sum(FinancialData.gross_sales).label("gross_sales"),
        func.sum(FinancialData.sales).label("sales"),
        func.sum(FinancialData.cogs).label("cogs"),
        func.sum(FinancialData.profit).label("profit"),
    )
    qry = qry.group_by(FinancialData.date).order_by(FinancialData.date)

    gross_sales, sales, cogs, profit = [], [], [], []
    for _res in qry.all():
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
    return render_template(
        "hello.jinja2",
        table=[list(i.to_dict().values()) for i in table],
        financial=financial,
    )


# @app.route("/data")
# def data():
#     data = FinancialData.query.all()
#     return jsonify(
#         {
#             "draw": 1,
#             "recordsTotal": len(data),
#             "recordsFiltered": len(data),
#             "data": [list(i.to_dict().values()) for i in data],
#         }
#     )


if __name__ == "__main__":
    app.run()
