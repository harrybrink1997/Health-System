from src.base import *


class HealthCentreManager(BaseManager):

    def __init__(self):
        self.health_centres = []
        self.load_data()

    def add_health_centre(self, data):
        self.health_centres.append(eval(data['type'])(data))
        self.save_data()

    def get_health_centre(self, abn):
        for health_centre in self.health_centres:
            if health_centre.abn == abn:
                return health_centre
        return None

    def search_suburb(self, suburb):
        result = []
        for health_centre in self.health_centres:
            #print(health_centre.suburb, suburb)
            if suburb.lower() in health_centre.suburb.lower():
                result.append(health_centre.data())
        #print(result)
        return result

    def search_health_centre(self, name):
        result = []
        for health_centre in self.health_centres:
            if name.lower() in health_centre.name.lower():
                result.append(health_centre.data())
        return result

    def get_services(self, health_centre_abn):
        result = []
        for health_centre in self.health_centres:
            if health_centre.abn == health_centre_abn:
                for service in health_centre.services:
                    data = {**health_centre.data(), **service.data()}
                    result.append(data)
        return result

    def load_data(self):
        rows = load_data('health_centre.pickle')
        for data in rows:
            self.health_centres.append(eval(data['type'])(data))

    def save_data(self):
        data = []
        for health_centre in self.health_centres:
            data.append(health_centre.data())
        save_data('health_centre.pickle', data)


class HealthCentre(BaseObject):

    def __init__(self, data):
        self.abn = data['abn']
        self.name = data['name']
        self.suburb = data['suburb']
        self.phone = data['phone']
        self.services = data['services']
        self.ratings = data['ratings']

    def add_rating(self, email, rating):
        self.ratings[email] = rating


class MedicalCentre(HealthCentre):

    def __init__(self, data):
        super().__init__(data)


class Hospital(HealthCentre):

    def __init__(self, data):
        super().__init__(data)


class Service(BaseObject):

    def __init__(self, name, price):
        self.name = name
        self.price = price
