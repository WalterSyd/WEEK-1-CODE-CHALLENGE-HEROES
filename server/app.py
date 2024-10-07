#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os
import logging



BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False
logging.basicConfig(level=logging.DEBUG)

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'


#define a Get heroes view
@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    heroes_list = []
    for hero in heroes:
        #serialize it as such to return this exact format unlike to_dict() which returns detailed data
        heroes_list.append({'id': hero.id, 
                            'name': hero.name, 
                            'super_name': hero.super_name})
    return make_response(heroes_list, 200)


#Define a view to Get hero by id
@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero_by_id(id):
    # Checks for existence of hero using prim_key
    hero = Hero.query.get(id)
    if hero is None:
        return jsonify({'error': 'Hero not found'}), 404

    # If hero is found
    # create custom dict to make it more readable
    hero_dict = {
        "id": hero.id,
        "name": hero.name,
        "super_name": hero.super_name,
        # create a list of hero_powers under the hero dict
        "hero_powers": []
    }
    # iterate over hero_powers and create a dict for each
    for power in hero.hero_powers:
        power_dict = {
            "hero_id": power.hero_id,
            "id": power.id,
            "power_id": power.power_id,
            "strength": power.strength
        }
        # add power dict to hero dict to retrieve a hero and their powers
        hero_dict["hero_powers"].append(power_dict)

    return jsonify(hero_dict), 200



#Define a view to get powers
@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    powers_list = []
    #Loop through each power, format it as below and return a list of all powers
    for power in powers:
        powers_list.append({'description': power.description, 
                            'id': power.id, 
                            'name': power.name, })
    return make_response(powers_list, 200)


#Define view to get power by id
@app.route('/powers/<int:id>', methods=['GET'])
def get_power_by_id(id):
  power = Power.query.get(id)
  # Check for the existence of the power using the primary key
  if power is None:
      return jsonify({'error': 'Power not found'}), 404

  # If power is found, create a simplified dictionary
  power_dict = {
      "description": power.description,
      "id": power.id,
      "name": power.name
  }
  return jsonify(power_dict), 200

#Define view to update existing powers [PATCH]
@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    # Retrieve the power by ID and update the description of a power by its ID.
    power = Power.query.get(id)  
    if power is None:
        return jsonify({"error": "Power not found"}), 404  
    
    # Get the JSON data from the request
    data = request.get_json()  
    if 'description' in data:  
        # Validate the description length if description is present 
        if len(data['description']) < 20:
            return jsonify({"errors": ["validation errors"]}), 400
        
        # Update the description
        power.description = data['description']  
        db.session.commit()  # Commit the changes to the database
        return jsonify({
            "description": power.description,
            "id": power.id,
            "name": power.name,
            # "message": "Valid Updated Description"
        }), 200  


    return jsonify({"error": "No valid data provided"}), 400  # Return error if no valid data is provided


#Define view to create new powers [POST
@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    """Create a new hero_power entry."""
    try:
        data = request.get_json()  # Get the JSON data from the request

        # Validate required fields
        if 'strength' not in data or 'power_id' not in data or 'hero_id' not in data:
            return jsonify({"errors": ["Missing strength, power_id, or hero_id"]}), 400

        # Validate strength value
        if data['strength'] not in ['Strong', 'Weak', 'Average']:
            return jsonify({"errors": ["validation errors"]}), 400

        # Check if the Power and Hero exist
        power = Power.query.get(data['power_id'])
        hero = Hero.query.get(data['hero_id'])
        if power is None or hero is None:
            return jsonify({"errors": ["validation errors"]}), 400

        # Check if the hero_power already exists
        existing_hero_power = HeroPower.query.filter_by(hero_id=data['hero_id'], power_id=data['power_id']).first()
        if existing_hero_power is not None:
            return jsonify({"errors": ["Hero power already exists"]}), 400

        # Create a new HeroPower instance
        new_hero_power = HeroPower(
            strength=data['strength'],
            power_id=data['power_id'],
            hero_id=data['hero_id']
        )

        # Add and commit to the database
        db.session.add(new_hero_power)

        # Use try-except block for commit to catch database errors
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()  # Rollback in case of failure
            print(f"Database commit error: {e}")
            return jsonify({"errors": ["Database commit failed"]}), 500

        # Prepare the response with related Hero and Power data
        response_data = new_hero_power.to_dict()
        response_data['hero'] = hero.to_dict()
        response_data['power'] = power.to_dict()

        # Return the created HeroPower as a JSON response
        return jsonify(response_data), 200  # Return 200 OK status

    except Exception as e:
        # Print the exception for debugging purposes
        print(f"Unexpected error: {e}")
        return jsonify({"errors": ["Internal Server Error"]}), 500


if __name__ == '__main__':
    app.run(port=5555, debug=True)
