#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False



db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

# seeing if i can hack restful api
# rstaurant page to see all restaurants
class Restaurants(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return jsonify([restaurant.to_dict(only=("id", "name", "address")) for restaurant in restaurants])
api.add_resource(Restaurants, "/restaurants")

# instead of seeing all restaurants maybe i can see a specific restaurant
class RestaurantById(Resource):
    # i read or view a specific restaurant
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            return jsonify(restaurant.to_dict(
                only=("id", "name", "address", "restaurant_pizzas.pizza")
            ))
        return make_response(jsonify({"error": "Restaurant not found"}), 404)
    
    #  i delete a specific restaurant
    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return make_response("", 204)  
        return make_response(jsonify({"error": "Restaurant not found"}), 404)
api.add_resource(RestaurantById, "/restaurants/<int:id>")

# i can see all pizzas
class Pizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return jsonify([pizza.to_dict(only=("id", "name", "ingredients")) for pizza in pizzas])
api.add_resource(Pizzas, "/pizzas")
# i can update a pizza in a restaurant
class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()

        try:
            # check if required fields are missing
            if "restaurant_id" not in data or "pizza_id" not in data or "price" not in data:
                return make_response(jsonify({"errors": ["validation errors"]}), 400)

            # validate restaurant & pizza existence
            restaurant = Restaurant.query.get(data["restaurant_id"])
            pizza = Pizza.query.get(data["pizza_id"])

            if not restaurant or not pizza:
                return make_response(jsonify({"errors": ["validation errors"]}), 400)

            # create new RestaurantPizza
            restaurant_pizza = RestaurantPizza(
                price=data["price"],
                restaurant_id=data["restaurant_id"],
                pizza_id=data["pizza_id"],
            )

            db.session.add(restaurant_pizza)
            db.session.commit()

            # return response in expected format
            return make_response(jsonify(restaurant_pizza.to_dict(
                only=("id", "price", "pizza", "restaurant", "pizza_id", "restaurant_id")
            )), 201)  

        except ValueError as e:
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

        except Exception as e:
            print(f"Error: {e}")  
            return make_response(jsonify({"errors": ["Internal server error"]}), 500)

api.add_resource(RestaurantPizzas, "/restaurant_pizzas")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
