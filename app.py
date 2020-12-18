import os

from dotenv import load_dotenv
from flask import Flask, render_template, jsonify
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

load_dotenv()


app = Flask(__name__)
app.config.from_object(os.environ["APP_SETTINGS"])
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
from models import FinancialData


@app.route("/")
def home():
    data = FinancialData.query.order_by(FinancialData.date.desc()).all()
    return render_template(
        "hello.jinja2",
        data=[list(i.to_dict().values()) for i in data],
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
