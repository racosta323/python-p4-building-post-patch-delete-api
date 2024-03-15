#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from models import db, User, Review, Game

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return "Index for Game/Review/User API"

@app.route('/games')
def games():

    games = []
    for game in Game.query.all():
        game_dict = {
            "title": game.title,
            "genre": game.genre,
            "platform": game.platform,
            "price": game.price,
        }
        games.append(game_dict)

    response = make_response(
        games,
        200
    )

    return response

@app.route('/games/<int:id>')
def game_by_id(id):
    game = Game.query.filter(Game.id == id).first()
    
    game_dict = game.to_dict()

    response = make_response(
        game_dict,
        200
    )

    return response


##adding post request here since we'll be posting to all reviews (not just 1!)
@app.route('/reviews', methods=['GET', 'POST'])
def reviews():

    if request.method == 'GET':
        reviews = []
        for review in Review.query.all():
            review_dict = review.to_dict()
            reviews.append(review_dict)

        response = make_response(
            reviews,
            200
        )
        return response
    elif request.method == 'POST':
        #from attributes passed into request, make a new Review record
        new_review = Review(
            #get from the request form the key that corresponds to the passed in str
            score=request.form.get("score"),
            comment=request.form.get("comment"),
            game_id=request.form.get("game_id"),
            user_id=request.form.get("user_id"),
        )

        #add to db
        db.session.add(new_review)
        db.session.commit()

        #send a response back (as a dict)
        review_dict = new_review.to_dict()

        # 201 means a record has been successfully created
        response = make_response(review_dict,201)

        return response

#route is requested from client; accepts methods as default arg. By default, list only contains 'GET'
@app.route('/reviews/<int:id>', methods = ['GET', 'DELETE', 'PATCH'])
#first find id
def find_by_id(id):
    review = Review.query.filter(Review.id == id).first()

    if request.method == 'GET':
        #turn found review into dict
        review_dict = review.to_dict()

        #send a response
        response= make_response(review_dict, 200)

        #return a response
        return response

    elif request.method == 'DELETE':
        #can just delete using db.session
        db.session.delete(review)
        db.session.commit()

        #send a response back as dict
        response_body = {
            "delete successful": True,
            "message": "Review deleted."
        }

        response = make_response(response_body, 200)
        return response
    elif request.method == 'PATCH':
        #request is from a form
        #use setattr to update the record's attributes
        for attr in request.form:
            #first arg is the object you are looking through; the found review
            #second arg is the attribute -- in this case, the keys of the request
            #third arg is the updated value -- 
            setattr(review, attr, request.form.get(attr))

        #update db
        db.session.add(review)
        db.session.commit()

        #send response (as a dict)
        review_dict = review.to_dict()
        response = make_response(review.to_dict(), 200)
        return response


@app.route('/users')
def users():

    users = []
    for user in User.query.all():
        user_dict = user.to_dict()
        users.append(user_dict)

    response = make_response(
        users,
        200
    )

    return response

if __name__ == '__main__':
    app.run(port=5555, debug=True)
