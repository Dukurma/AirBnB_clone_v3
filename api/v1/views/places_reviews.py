#!/usr/bin/python3
"""Creates a new view for Review object that handles all
   RESTFUL API actions"""
from flask import jsonify, request
from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest
from api.v1.views import app_views
from models import storage
from models.place import Place
from models.review import Review
from models.user import User


@app_views.route('/places/<place_id>/reviews', methods=['GET', 'POST'])
@app_views.route('reviews/<review_id>', methods=['GET', 'DELETE', 'PUT'])
def handle_reviews(place_id=None, review_id=None):
    """Handles reviews endpoint"""
    handlers = {
        'GET': get_reviews,
        'DELETE': remove_review,
        'POST': add_review,
        'PUT': update_review
    }
    if request.method in handlers:
        return handlers[request.method](place_id, review_id)
    else:
        raise MethodNotAllowed(list(handlers.keys()))


def get_reviews(place_id=None, review_id=None):
    """Gets review with given id"""
    if place_id:
        place = storage.get(Place, place_id)
        if place:
            reviews = []
            for review in place.reviews:
                reviews.append(review.to_dict())
            return jsonify(reviews)
        elif review_id:
            review = storage.get(Review, review_id)
            if review:
                return jsonify(review.to_dict())
            raise NotFound()


def remove_review(place_id=None, review_id=None):
    """Removes a review with given id"""
    review = storage.get(Review, review_id)
    if review:
        storage.delete(review)
        storage.save()
        return jsonify({}), 200
    raise NotFound()


def add_review(place_id=None, review_id=None):
    """Adds new review"""
    place = storage.get(Place, place_id)
    if not place:
        raise NotFound()
    data = request.get_json()
    if type(data) is not dict:
        raise BadRequest(description='Missing user_id')
    user = storage.get(User, data['user_id'])
    if not user:
        raise NotFound()
    if 'text' not in data:
        raise BadRequest(description='Missing text')
    data['place_id'] = place_id
    new_review = Review(**data)
    new_review.save()
    return jsonify(new_review.to_dict()), 201


def update_review(lace_id=None, review_id=None):
    """Updates review with given id"""
    xkeys = ('id', 'user_id', 'place_id', 'created_at', 'updated_at')
    if review_id:
        review = storage.get(Review, review_id)
        if review:
            data = request.get_json()
            if type(data) is not dict:
                raise BadRequest(description='Not a JSON')
            for key, value in data.items():
                if key not in xkeys:
                    setattr(review, key, value)
            review.save()
            return jsonify(review.to_dict()), 200
        raise NotFound()
