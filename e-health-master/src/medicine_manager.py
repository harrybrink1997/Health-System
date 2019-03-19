from src.base import *


class medicineManager(BaseManager):
    def __init__(self):
        self.medicines = []
        self.load_data()

    def add_medicine(self, data):
        self.medicines.append(eval(data['type'])(data))
        self.save_data()

    def get_medicines(self, medicines):
        result = []
        for medicine in self.medicines:
            if medicine.name in medicines:
                result.append(medicine.data())
        return result

    def search_medicine(self, name):
        for medicine in self.medicines:
            if medicine.name == name:
                return medicine

    def load_data(self):
        rows = load_data('medicine.pickle')
        for data in rows:
            self.medicines.append(eval(data['type'])(data))

    def save_data(self):
        data = []
        for medicine in self.medicines:
            data.append(medicine.data())
        save_data('medicine.pickle', data)


class medicine(BaseObject):

    def __init__(self, data):
        self.code = data['code']
        self.name = data['name']
        self.ingredients = data['ingredients']
        self.price = data['price']
        self.directions = data['directions']
        self.warnings = data['warnings']


