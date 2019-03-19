from src.base import *


class EmploymentManager(BaseManager):

    def __init__(self):
        self.employments = []
        self.load_data()

    def add_employment(self, data):
        for employment in self.employments:
            if employment.health_provider == data['health_provider'] and employment.health_centre == data['health_centre']:
                return
        self.employments.append(eval(data['type'])(data))
        self.save_data()

    def search_employment(self, health_provider, health_centre):
        for employment in self.employments:
            if employment.health_provider == health_provider and employment.health_centre == health_centre:
                return employment
        return None

    def get_employers(self, health_provider):
        results = []
        for employment in self.employments:
            if employment.health_provider == health_provider:
                results.append(employment)
        return results

    def get_employees(self, health_centre):
        results = []
        for employment in self.employments:
            if employment.health_centre == health_centre:
                results.append(employment)
        return results

    def get_hour_fee(self, health_centre, health_provider):
        for employment in self.employments:
            if employment.health_centre == health_centre and employment.health_provider == health_provider:
                return employment.fee

    def load_data(self):
        rows = load_data('employment.pickle')
        for data in rows:
            self.employments.append(eval(data['type'])(data))

    def save_data(self):
        data = []
        for employment in self.employments:
            data.append(employment.data())
        save_data('employment.pickle', data)


class Employment(BaseObject):

    def __init__(self, data):
        self.fee = data['fee']
        self.health_provider = data['health_provider']
        self.health_centre = data['health_centre']


class CasualEmployment(Employment):

    def __init__(self, data):
        super().__init__(data)
        self.hour_rate = data['hour_rate']


class PartTimeEmployment(Employment):

    def __init__(self, data):
        super().__init__(data)
        self.daily_rate = data['daily_rate']


class FullTimeEmployment(Employment):

    def __init__(self, data):
        super().__init__(data)
        self.annual_salary = data['annual_salary']