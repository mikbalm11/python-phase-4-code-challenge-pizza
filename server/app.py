#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


class RestaurantClass(Resource):
    def get(self):
        restaurant_list = [restaurant.to_dict(rules=("-restaurant_pizzas",)) for restaurant in Restaurant.query.all()]

        result = make_response(
            restaurant_list,
            200
        )

        return result

api.add_resource(RestaurantClass, "/restaurants")

class RestaurantById(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()

        if restaurant:

            result = make_response(
                restaurant.to_dict(), 
                200
            )

            return result

        else:

            result = make_response(
                {"error": "Restaurant not found"},
                404
            )

            return result

    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()

        if not restaurant:
            result = make_response(
                {"error": "Restaurant not found"},
                404
            )

            return result

        db.session.delete(restaurant)
        db.session.commit()

        result = make_response(
            {},
            204
        )

        return result

api.add_resource(RestaurantById, "/restaurants/<int:id>")

class PizzaClass(Resource):
    def get(self):
        all_pizzas = [pizza.to_dict(only=("id", "ingredients", "name"))for pizza in Pizza.query.all()]

        result = make_response(
            all_pizzas,
            200
        )

        return result

api.add_resource(PizzaClass, "/pizzas")

class RestaurantPizzasClass(Resource):
    def post(self):
        fields = request.get_json()

        try:
            new_restaurant_pizza = RestaurantPizza(
                price=fields["price"],
                pizza_id=fields["pizza_id"],
                restaurant_id=fields["restaurant_id"],
            )

            db.session.add(new_restaurant_pizza)
            db.session.commit()

            result = make_response(
                new_restaurant_pizza.to_dict(),
                201
            )

            return result

        except ValueError:
            result = make_response(
                {"errors": ["validation errors"]},
                400
            )

            return result

api.add_resource(RestaurantPizzasClass, "/restaurant_pizzas")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
