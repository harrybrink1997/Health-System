from flask_login import UserMixin
from src.base import *


class UserManager(BaseManager):

    def __init__(self):
        self.users = []
        self.load_data()

    def add_user(self, data):
        self.users.append(eval(data['type'])(data))
        self.save_data()

    def get_user(self, email):
        for user in self.users:
            if user.email == email:
                return user
        return None

    def validate_login(self, email, password):
        errors = {}
        user = self.get_user(email)
        if email == '':
            errors['email'] = "Email is empty"
        elif user is None:
            errors['email'] = "Email not found"
        elif user.password != password:
            errors['password'] = "Wrong password"
        if password == '':
            errors['password'] = "Password is empty"

        return errors

    def validate_registration(self, email, password, name, phone, tfn):
        errors = {}
        user = self.get_user(email)
        if email == '':
            errors['email'] = "Email is empty"
        elif '@' not in email:
            errors['email'] = "Email is invalid"
        elif user is not None:
            errors['email'] = 'Email already exists'
        if password == '':
            errors['password'] = "Password is empty"
        if name == '':
            errors['name'] = 'Name is empty'
        if phone == '':
            errors['phone'] = 'Phone is empty'
        if tfn == '':
            errors['tfn'] = 'TFN is empty'
        return errors

    def search_health_provider(self, name):
        result = []
        for user in self.users:
            if name.lower() in user.name.lower() and user.get_type() != 'Patient':
                result.append(user.data())
        return result

    def search_service(self, service):
        result = []
        for user in self.users:
            if user.get_type() == service:
                result.append(user.data())
        return result

    def load_data(self):
        rows = load_data('user.pickle')
        for data in rows:
            self.users.append(eval(data['type'])(data))

    def save_data(self):
        data = []
        for user in self.users:
            data.append(user.data())
        save_data('user.pickle', data)


class User(UserMixin, BaseObject):

    def __init__(self, data): # tfn, name, phone, email, password
        self.email = data['email']
        self.password = data['password']
        self.name = data['name']
        self.phone = data['phone']
        self.tfn = data['tfn']

    def get_id(self):
        return self.email

    def __str__(self):
        return str(self.__dict__)


class Patient(User):

    def __init__(self, data): # tfn, name, phone, email, password, history
        super().__init__(data)
        self.refers = data['refers']


#p = Patient({'type': 'Patient', 'tfn':123, 'name':'jack', 'phone':'0512131231', 'email':'a@gmail.com', 'password':'123', 'refers': [{'dog':'cat'}]})

class HealthProvider(User):

    def __init__(self, data):
        super().__init__(data)
        self.ratings = data['ratings']
        if len(self.ratings) == 0:
            self.ratings['None'] = 0

    def add_rating(self, email, rating):
        self.ratings[email] = rating

    @abstractmethod
    def get_appointment_type(self):
        pass


class Pharmacist(HealthProvider):

    def __init__(self, data):
        super().__init__(data)

    def get_appointment_type(self):
        return 'GeneralAppointment'


class Nurse(HealthProvider):

    def __init__(self, data):
        super().__init__(data)

    def get_appointment_type(self):
        return 'GeneralAppointment'


class GPDoctor(HealthProvider):

    def __init__(self, data):
        super().__init__(data)

    def get_appointment_type(self):
        return 'GeneralAppointment'


class Specialist(HealthProvider):

    def __init__(self, data):
        super().__init__(data)
        self.expertise = data['expertise']

    def get_appointment_type(self):
        return 'SpecialistAppointment'


class Pathologist(HealthProvider):
    def __init__(self, data):
        super().__init__(data)

    def get_appointment_type(self):
        return 'ServiceAppointment'
