from src.base import *


class RatingManager(BaseManager):

    def __init__(self):
        self.ratings = []

    def add_rating(self, data):
        self.ratings.append(eval(data['type'])(data))
        self.save_data()

    def load_data(self):
        rows = load_data('rating.pickle')
        for data in rows:
            self.ratings.append(eval(data['type'])(data))

    def save_data(self):
        data = []
        for rating in self.ratings:
            data.append(rating.data())
        save_data('rating.pickle', data)


class Rating(BaseObject):

    def __init__(self, data):
        self.score = data['score']
        self.comment = data['comment']
        self.patient = data['patient']


class HealthProviderRating(Rating):

    def __init__(self, data):
        super().__init__(data)
        self.health_provider = data['health_provider']


class HealthCentreRating(Rating):

    def __init__(self, data):
        super().__init__(data)
        self.health_centre = data['health_centre']