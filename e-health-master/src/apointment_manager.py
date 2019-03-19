from src.base import *
from _datetime import datetime


class AppointmentManager(BaseManager):
    def __init__(self):
        self.appointments = []
        self.load_data()

    def add_appointment(self, data):
        self.appointments.append(eval(data['type'])(data))
        self.save_data()

    def get_booked_time(self, email):
        result = []
        for appointment in self.appointments:
            if appointment.health_provider == email or appointment.patient == email:
                result.append((self.time_format(appointment.start_time), self.time_format(appointment.end_time)))
        return result

    def get_appointments(self, email):
        result = []
        for appointment in self.appointments:
            if appointment.health_provider == email or appointment.patient == email:
                data = appointment.data()
                data['start_time'] = self.time_format(data['start_time'])
                data['end_time'] = self.time_format(data['end_time'])
                result.append(data)
        return result

    def make_appointment(self, start_time, end_time, patient, health_centre, health_provider, hour_fee):
        date_format = "%Y-%m-%dT%H:%M"
        start = datetime.strptime(start_time, date_format)
        end = datetime.strptime(end_time, date_format)
        hours = (end - start).total_seconds() / 3600
        data = {'type': health_provider.get_appointment_type(), 'start_time': start_time, 'end_time': end_time,
                'patient': patient.email, 'health_centre': health_centre.abn,
                'health_provider': health_provider.email, 'fee': hours * hour_fee, 'notes': '',
                'medicines': []
                }
        print(health_provider.email)
        print(patient.refers)
        if health_provider.email in patient.refers.values():
            for email in patient.refers.keys():
                if health_provider.email == patient.refers[email]:
                    data['referrer'] = email

        self.add_appointment(data)

    def check_appointment_fee(self, start_time, end_time, patient, health_centre, health_provider, hour_fee):
        errors = self.validate_appointment(start_time, end_time, patient, health_centre, health_provider)
        if len(errors) != 0:
            return errors
        date_format = "%Y-%m-%dT%H:%M"
        start = datetime.strptime(start_time, date_format)
        end = datetime.strptime(end_time, date_format)
        hours = (end - start).total_seconds() / 3600
        return hours * hour_fee

    def validate_appointment(self, start_time, end_time, patient, health_centre, health_provider):
        errors = {}
        date_format = "%Y-%m-%dT%H:%M"

        try:
            start = datetime.strptime(start_time, date_format)
        except:
            errors['start'] = 'Start time invalid'

        try:
            end = datetime.strptime(end_time, date_format)
        except:
            errors['end'] = 'End time invalid'

        if len(errors) != 0:
            return errors

        start = datetime.strptime(start_time, date_format)
        end = datetime.strptime(end_time, date_format)

        if start >= end:
            errors['period'] = 'End time before start time'
        for appointment in self.appointments:
            if appointment.health_provider == health_provider.email or appointment.patient == patient.email:
                print(appointment.start_time, appointment.end_time)
                appointment_start, appointment_end = datetime.strptime(appointment.start_time, date_format), \
                                                     datetime.strptime(appointment.end_time, date_format)
                if not (end <= appointment_start or start >= appointment_end):
                    errors['overlap'] = 'Period not available. Either patient or health_provider is not free'

        if start_time[5:10] != end_time[5:10]:
            if health_centre.get_type() == 'MedicalCentre':
                errors['closed'] = 'Medical centre does not open 24 hours'

        return errors

    def get_history(self, patient_email, abns):
        result = []
        for appointment in self.appointments:
            if appointment.health_centre in abns and appointment.patient == patient_email:
                result.append(appointment)
        return result

    def finish_appointment(self, time, email, notes):
        for appointment in self.appointments:
            if appointment.health_provider == email and self.time_format(appointment.start_time) == time:
                appointment.notes = notes
                appointment.finished = True
                self.save_data()
                return

    def prescribe_medicine(self, time, email, medicine):
        for appointment in self.appointments:
            if appointment.health_provider == email and self.time_format(appointment.start_time) == time:
                appointment.medicines[medicine] = False
                self.save_data()
                return

    def give_referral(self, time, email, referred_email):
        for appointment in self.appointments:
            if appointment.health_provider == email and self.time_format(appointment.start_time) == time:
                appointment.refer = referred_email
                self.save_data()
                return

    def get_appointment_medicines(self, time, email):
        for appointment in self.appointments:
            if appointment.health_provider == email and self.time_format(appointment.start_time) == time:
                return appointment.medicines

    def get_referred_provider(self, time, email):
        for appointment in self.appointments:
            if appointment.health_provider == email and self.time_format(appointment.start_time) == time:
                return appointment.refer

    def get_patient(self, time, email):
        for appointment in self.appointments:
            if appointment.health_provider == email and self.time_format(appointment.start_time) == time:
                return appointment.patient

    def time_format(self, time: str):
        time = time[-11:]
        time = time[0:5] + ' ' + time[6:]
        return time

    def load_data(self):
        rows = load_data('appointment.pickle')
        for data in rows:
            self.appointments.append(eval(data['type'])(data))

    def save_data(self):
        data = []
        for appointment in self.appointments:
            data.append(appointment.data())
        save_data('appointment.pickle', data)


class Appointment(BaseObject):
    def __init__(self, data):
        self.start_time = data['start_time']
        self.end_time = data['end_time']
        self.patient = data['patient']
        self.fee = data['fee']
        self.health_centre = data['health_centre']
        self.notes = data['notes']
        self.health_provider = data['health_provider']
        self.medicines = {}
        for medicine in data['medicines']:
            self.medicines[medicine] = False  # not prepared yet
        self.finished = False
        self.refer = None


class GeneralAppointment(Appointment):  # GP or Nurse

    def __init__(self, data):
        super().__init__(data)


class ServiceAppointment(Appointment):  # Service (Pathology, X ray..)

    def __init__(self, data):
        super().__init__(data)
        print(data)
        self.referrer = data['referrer']


class SpecialistAppointment(Appointment):  # Specialist

    def __init__(self, data):
        super().__init__(data)
        self.referrer = data['referrer']
        self.medicines = {}
        for medicine in data['medicines']:
            self.medicines[medicine] = False  # not prepared yet
