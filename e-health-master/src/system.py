from src.health_centre_manager import *
from src.user_manager import *
from src.apointment_manager import *
from src.employment_manager import *
from src.medicine_manager import *


class HealthSystem(object):

    def __init__(self):
        self.health_centre_manager = HealthCentreManager()
        self.user_manager = UserManager()
        self.appointment_manager = AppointmentManager()
        self.employment_manager = EmploymentManager()
        self.medicine_manager = medicineManager()

    def get_user(self, email):
        return self.user_manager.get_user(email)

    def get_health_centre(self, abn):
        return self.health_centre_manager.get_health_centre(abn)

    def get_appointments(self, email):
        return self.appointment_manager.get_appointments(email)

    def validate_login(self, email, password):
        return self.user_manager.validate_login(email, password)

    def validate_registration(self, email, password, name, phone, tfn):
        return self.user_manager.validate_registration(email, password, name, phone, tfn)

    def add_user(self, data):
        self.user_manager.add_user(data)

    def add_health_centre(self, data):
        self.health_centre_manager.add_health_centre(data)

    def add_appointment(self, data):
        self.appointment_manager.add_appointment(data)

    def add_employment(self, data):
        self.employment_manager.add_employment(data)

    def add_medicine(self, data):
        self.medicine_manager.add_medicine(data)

    def search_health_centre(self, name):
        return self.health_centre_manager.search_health_centre(name)

    def search_health_provider(self, name):
        return self.user_manager.search_health_provider(name)

    def search_suburb(self, name):
        return self.health_centre_manager.search_suburb(name)

    def get_employers(self, health_provider):
        return self.employment_manager.get_employers(health_provider)

    def get_employees(self, health_centre):
        return self.employment_manager.get_employees(health_centre)

    def search_provider_of_service(self, service):
        return self.user_manager.search_service(service)

    def search_service(self, service):
        services = set(map(lambda x: x.get_type(), self.user_manager.users))
        services.remove('Patient')
        if service == '':
            return services
        else:
            for x in set(services):
                if service.lower() not in x.lower():
                    services.remove(x)
            return services

    def get_services(self, health_centre):
        return self.health_centre_manager.get_services(health_centre)

    def get_user_profile(self, id):
        info = self.get_user(id).data()
        contains = []
        employments = self.get_employers(id)
        for employment in employments:
            contains.append(self.get_health_centre(employment.health_centre).data())
        return info, contains

    def get_health_centre_profile(self, id):
        info = self.get_health_centre(id).data()
        contains = []
        employments = self.get_employees(id)
        for employment in employments:
            contains.append(self.get_user(employment.health_provider).data())

        services = self.get_services(id)
        contains += services
        return info, contains

    def get_booked_time(self, email):
        return self.appointment_manager.get_booked_time(email)

    def get_hour_fee(self, health_centre, health_provider):
        return self.employment_manager.get_hour_fee(health_centre, health_provider)

    def make_booking(self, start_time, end_time, patient, health_centre, health_provider):
        return self.appointment_manager.make_appointment(start_time, end_time, patient, health_centre, health_provider,
                                                         self.get_hour_fee(health_centre.abn, health_provider.email))

    def check_appointment_fee(self, start_time, end_time, patient, health_centre, health_provider):
        return self.appointment_manager.check_appointment_fee(start_time, end_time, patient, health_centre, health_provider,
                                                         self.get_hour_fee(health_centre.abn, health_provider.email))

    def get_medicines(self, medicines):
        return self.medicine_manager.get_medicines(medicines)

    def get_patient_history_with_health_provider(self, patient_email, provider_email):
        contains = self.get_user_profile(provider_email)[1]
        abns = list(map(lambda x: x['abn'], contains))
        return self.appointment_manager.get_history(patient_email, abns)

    def finish_appointment(self, time, email, notes):
        self.appointment_manager.finish_appointment(time, email, notes)

    def time_format(self, time: str):
        time = time[-11:]
        time = time[0:5] + ' ' + time[6:]
        return time

    def prescribe_medicine(self, time, health_provider, medicine):
        if self.medicine_manager.search_medicine(medicine):
            self.appointment_manager.prescribe_medicine(time, health_provider, medicine)
            return []
        return {'medicine': 'Medicine not found'}

    def get_appointment_medicines(self, time, health_provider):
        return self.appointment_manager.get_appointment_medicines(time, health_provider)

    def get_medicine_info(self, name):
        return self.medicine_manager.search_medicine(name).data()

    def give_referral(self, time, email, referred_email):
        return self.appointment_manager.give_referral(time, email, referred_email)

    def get_referred_provider(self, time, health_provider):
        return self.appointment_manager.get_referred_provider(time, health_provider)

    def get_patient_from_appointment(self, time, health_provider):
        return self.appointment_manager.get_patient(time, health_provider)

    def search_employment(self, health_provider, health_centre):
        return self.employment_manager.search_employment(health_provider, health_centre)