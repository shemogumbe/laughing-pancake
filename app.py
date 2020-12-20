import csv
import io
import os
import re
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
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


def _get_data_filter(query, countries, departments, products, from_date, to_date):
    if countries:
        query = query.filter(FinancialData.country.in_(countries))
    if departments:
        query = query.filter(FinancialData.department.in_(departments))
    if products:
        query = query.filter(FinancialData.product.in_(products))
    if from_date:
        query = query.filter(FinancialData.date >= str(from_date))
    if to_date:
        query = query.filter(FinancialData.date < str(to_date))
    return query


def _get_line_graph_data(countries, departments, products, from_date, to_date):
    query = db.session.query(
        FinancialData.date,
        func.sum(FinancialData.gross_sales).label("gross_sales"),
        func.sum(FinancialData.sales).label("sales"),
        func.sum(FinancialData.cogs).label("cogs"),
        func.sum(FinancialData.profit).label("profit"),
    )
    query = _get_data_filter(
        query,
        countries=countries,
        departments=departments,
        products=products,
        from_date=from_date,
        to_date=to_date,
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


def get_table_data(countries, departments, products, from_date, to_date):
    query = FinancialData.query
    query = _get_data_filter(
        query,
        countries=countries,
        departments=departments,
        products=products,
        from_date=from_date,
        to_date=to_date,
    )
    return query.order_by(FinancialData.date.desc()).all()


@app.route("/")
def home():

    selected_departments = request.args.getlist("department")
    selected_countries = request.args.getlist("country")
    selected_products = request.args.getlist("product")
    from_date = request.args.get("from")
    if from_date:
        from_date = datetime.fromisoformat(from_date)
    to_date = request.args.get("to")
    if to_date:
        to_date = datetime.fromisoformat(to_date)

    table = get_table_data(
        countries=selected_countries,
        departments=selected_departments,
        products=selected_products,
        from_date=from_date,
        to_date=to_date,
    )

    graph = _get_line_graph_data(
        countries=selected_countries,
        departments=selected_departments,
        products=selected_products,
        from_date=from_date,
        to_date=to_date,
    )
    products = _get_all_products()
    departments = _get_all_departments()
    countries = _get_all_countries()

    return render_template(
        "home.jinja2",
        table=[list(i.to_dict().values()) for i in table],
        graph=graph,
        # country
        all_countries=[x.country for x in countries],
        selected_countries=selected_countries,
        # department
        all_departments=[x.department for x in departments],
        selected_departments=selected_departments,
        # product
        all_products=[x.product for x in products],
        selected_products=selected_products,
        # date
        from_date=from_date.strftime("%Y-%m-%d") if from_date else "",
        to_date=to_date.strftime("%Y-%m-%d") if to_date else "",
        # for the graph axes when date time is selected
        from_date_milliseconds=from_date.timestamp() * 1000 if from_date else None,
        to_date_milliseconds=to_date.timestamp() * 1000 if to_date else None,
        # get args
        get_args=request.query_string.decode(),
    )


@app.route(
    "/upload",
    methods=(
        "GET",
        "POST",
    ),
)
def upload_data():
    message = ""
    if request.method == "POST":
        local_file_content = request.files.get("local_file_upload")
        if request.form.get("clear_data") == "true":
            db.session.query(FinancialData).delete()
            message = "successfully cleared data in the database"
        elif local_file_content:
            regex = r"[\$,\ -]"
            data = []

            stream = io.StringIO(
                local_file_content.stream.read().decode(), newline=None
            )

            for row in csv.DictReader(stream, skipinitialspace=True):
                row = {key.strip(): value.strip() for key, value in row.items()}
                discount_band = row.get("Discount Band")
                if discount_band == "None":
                    discount_band = None
                manufacturing_price = re.sub(
                    regex, "", row.get("Manufacturing Price", "")
                )
                manufacturing_price = (
                    float(manufacturing_price) if manufacturing_price else None
                )
                sale_price = re.sub(regex, "", row.get("Sale Price", ""))
                sale_price = float(sale_price) if sale_price else None
                gross_sales = re.sub(regex, "", row.get("Gross Sales", ""))
                ross_sales = float(gross_sales) if gross_sales else None
                discounts = re.sub(regex, "", row.get("Discounts", ""))
                discounts = float(discounts) if discounts else None
                sales = re.sub(regex, "", row.get("Sales", ""))
                sales = float(sales) if sales else None
                cogs = re.sub(regex, "", row.get("COGS", ""))
                cogs = float(cogs) if cogs else None
                profit = re.sub(regex, "", row.get("Profit", ""))
                if profit:
                    if profit.startswith("("):
                        profit = "-" + profit[1:-1]
                    profit = float(profit)
                else:
                    profit = None

                data.append(
                    FinancialData(
                        department=row.get("Department"),
                        country=row.get("Country"),
                        product=row.get("Product"),
                        discount_band=discount_band,
                        units_sold=row.get("Units Sold"),
                        manufacturing_price=manufacturing_price,
                        sale_price=sale_price,
                        gross_sales=gross_sales,
                        discounts=discounts,
                        sales=sales,
                        cogs=cogs,
                        profit=profit,
                        date=datetime.strptime(row.get("Date"), "%m/%d/%Y"),
                    )
                )

            db.session.bulk_save_objects(data)

            message = "successfully uploaded CSV data, go home to view"
        db.session.commit()
    return render_template("upload.jinja2", message=message)


if __name__ == "__main__":
    app.run()
