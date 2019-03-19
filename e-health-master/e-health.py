from flask import Flask, redirect, request, render_template, url_for
from flask_login import LoginManager,login_user, current_user, login_required, logout_user, UserMixin, login_manager
from src.system import *
from functools import wraps

app = Flask(__name__)

system = HealthSystem()

login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'e-health'


def patient_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.get_type() == 'Patient':
            return redirect(url_for('page_not_found'))
        return f(*args, **kwargs)
    return decorated_function


def health_provider_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.get_type() == 'Patient':
            return redirect(url_for('page_not_found'))
        return f(*args, **kwargs)
    return decorated_function


@login_manager.user_loader
def load_user(id):
    return get_user(id)


def is_user(id):
    return '@' in id


def get_user(email):
    return system.get_user(email)

@app.route('/', methods=['POST', 'GET'])
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        errors = system.validate_login(request.form['email'], request.form['password'])
        if not errors:
            login_user(get_user(request.form['email']))
            return redirect('/home')
        else:
            return render_template('login.html', errors=errors)
    return render_template('login.html')


@app.route('/add_hospital', methods=['POST', 'GET'])
@health_provider_required
def add_hospital():
    errors = {}
    if request.method == "POST":
        hospital = system.get_health_centre(request.form['hospital'])
        if hospital is not None:
            if system.search_employment(current_user.get_id(), request.form['hospital']) is not None:
                errors['hospital'] = "Employment already exists"
            else:
                system.add_employment({"type": "CasualEmployment", "health_provider": current_user.get_id(), "health_centre": request.form['hospital'], "fee": 50, "hour_rate": 50})
                return render_template("add_successful.html")
        else:
            errors['hospital'] = "Hospital not found"
    return render_template('add_hospital.html', errors=errors)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        if "choose" in request.form:
            errors = {}
            if "type" not in request.form:
                errors['radio'] = "Please choose the type of user you want to register for "
                return render_template('register.html', errors=errors)
            else:
                return render_template('register.html', type=request.form['type'], errors=errors)
        else:
            errors = system.validate_registration(request.form['email'], request.form['password'], request.form['name'], request.form['phone'], request.form['tfn'])
            if not errors:
                info = {'type': request.form['type'], 'tfn': request.form['tfn'], 'name': request.form['name'],
                     'phone': request.form['phone'], 'email': request.form['email'], 'password': request.form['password'], 'refers': {}, 'ratings': {}}
                if request.form['type'] == 'Specialist':
                    info['expertise'] = request.form['expertise']
                print(info)
                system.add_user(info)
                return redirect(url_for('login'))
            else:
                return render_template('register.html', errors=errors)

    return render_template('register.html')


@app.route('/home', methods=['POST', 'GET'])
@login_required
def home():
    if request.method == 'POST':
        if request.form['button'] == 'logout':
            logout_user()
            return redirect('/')

    return render_template('home.html')


@app.route('/404')
@app.errorhandler(404)
def page_not_found(e=None):
    return render_template('404.html'), 404


@app.route('/search', methods=['GET', 'POST'])
@patient_required
def search():
    if request.method == 'POST':
        errors = {}
        if 'service_type' in request.form:
            results = system.search_provider_of_service(request.form['service_type'])
            return render_template('search.html', results=results, errors=errors)

        if 'search' in request.form:
            if 'select' not in request.form:
                results = []
                errors['radio'] = 'Please select a field to search'
            elif request.form['select'] == 'health_centre':
                results = system.search_health_centre(request.form['name'])
            elif request.form['select'] == 'health_provider':
                results = system.search_health_provider(request.form['name'])
            elif request.form['select'] == 'suburb':
                results = system.search_suburb(request.form['name'])
            elif request.form['select'] == 'service' or 'service_type' in request.form:
                services = system.search_service(request.form['name'])
                results = services
                return render_template('search.html', services=services, errors=errors, results = results)

            return render_template('search.html', results=results, errors=errors)
        elif 'details' in request.form:
            return redirect(url_for('profile', id=request.form['details']))

    return render_template('search.html')


@app.route('/profile/<id>', methods=['GET', 'POST'])
@login_required
def profile(id):
    if id != current_user.get_id() and is_user(id) and system.get_user(id).get_type() == current_user.get_type() \
            and id != current_user.email:
        return redirect(url_for('page_not_found'))
    history = []
    if is_user(id):
        info, contains = system.get_user_profile(id)
        if info['type'] == 'Patient':
            history = system.get_patient_history_with_health_provider(id, current_user.email)
    else:
        info, contains = system.get_health_centre_profile(id)

    if request.method == 'POST':
        if 'refer' in request.form:
            referred_email = request.form['referred']
            user = system.get_user(referred_email)
            if user is not None and user.get_type() != 'Patient':
                patient = system.get_user(id)
                patient.refers[current_user.email] = referred_email
            else:
                errors = {'refer': 'Health Provider not exists'}
                return render_template('profile.html', info=info, contains=contains, errors=errors, history=history)

        elif 'appointment' in request.form:
            if is_user(id):
                return redirect(url_for('book_appointment', abn=request.form['appointment'], email=id))
            else:
                return redirect(url_for('book_appointment', email=request.form['appointment'], abn=id))
        elif 'rate' in request.form:
            if is_user(id):
                system.get_user(id).add_rating(current_user.email, int(request.form['rating']))
            else:
                system.get_health_centre(id).add_rating(current_user.email, int(request.form['rating']))
        elif 'service' in request.form:
            service = request.form['service']
            return render_template('profile.html', info=info, contains=contains, history=history)
    
    return render_template('profile.html', info=info, contains=contains, history=history)


@app.route('/book_appointment/<abn>With<email>', methods=['GET', 'POST'])
@patient_required
def book_appointment(abn, email):
    def time_slot_generator():
        result = []
        for i in range(9, 19):
            if len(str(i)) == 1:
                result.append('0' + str(i) + ':00')
                result.append('0' + str(i) + ':30')
            else:
                result.append(str(i) + ':00')
                result.append(str(i) + ':30')
        return result

    def time_increment(time):
        if time[-2:] == '30':
            time = str(int(time[:-3]) + 1) + ':00'
        else:
            time = time[:-2] + str(int(time[-2:]) + 30)
        if len(time) == 4:
            time = '0' + time
        return time

    errors = {}
    booked_time = []
    unavailable_slots = []

    if is_user(email):
        booked_time = system.get_booked_time(email)
        unavailable_slots = [x[0] for x in booked_time]
        print(unavailable_slots)

    services = None
    if get_user(email).get_type() == 'Pathologist':
        services = system.get_services(abn)

    slots = time_slot_generator()

    for slot in slots:
        if slot in unavailable_slots:
            slots.remove(slot)

    if request.method == 'POST':
        if "search" in request.form:
            start_date = request.form['start']
            unavailable_slots = []
            for time in booked_time:
                if time[0][:5] == start_date[5:]:
                    unavailable_slots.append(time[0][6:])
            for slot in list(slots):
                if slot in unavailable_slots:
                    slots.remove(slot)

            return render_template('book.html', health_provider=get_user(email).data(),
                                   health_centre=system.get_health_centre(abn).data(), start=start_date,
                                   booked_time=booked_time, errors=errors, services=services, slots=slots, book=True)
        else:
            slot = request.form['slot']
            if len(slot) == 4:
                slot = '0' + slot
            start = request.form['start_date'] + 'T' + slot
            end = request.form['start_date'] + 'T' + time_increment(slot)

            if 'slot' in request.form:
                errors = system.check_appointment_fee(start, end, current_user,
                                             system.get_health_centre(abn), system.get_user(email))

                if not isinstance(errors, dict):
                    system.make_booking(start, end, current_user,
                                        system.get_health_centre(abn), system.get_user(email))
                    return render_template('booking_successful.html', start=start, end=end)

    return render_template('book.html', health_provider=get_user(email).data(),
                           health_centre=system.get_health_centre(abn).data(),
                           booked_time=booked_time, errors=errors, services=services)


@app.route('/appointments', methods=['GET', 'POST'])
@login_required
def display_appointments():
    appointments = list(filter(lambda x: not x['finished'], system.get_appointments(current_user.email)))
    if request.method == 'POST':
        if 'start' in request.form:
            id = system.get_patient_from_appointment(request.form['start'], current_user.email)
            history = system.get_patient_history_with_health_provider(id, current_user.email)
            print(history)
            return render_template('start_appointment.html', time=request.form['start'], history=history)
        elif 'finalise' in request.form:
            system.finish_appointment(request.form['time'], current_user.email, request.form['notes'])
            return redirect(url_for('display_appointments'))
        elif 'add' in request.form:
            id = system.get_patient_from_appointment(request.form['time'], current_user.email)
            history = system.get_patient_history_with_health_provider(id, current_user.email)
            errors = system.prescribe_medicine(request.form['time'], current_user.email, request.form['medicine'])
            return render_template('start_appointment.html', time=request.form['time'],
                                   medicines=system.get_appointment_medicines(request.form['time'], current_user.email),
                                   errors=errors, history=history)
        elif 'med_info' in request.form:
            return redirect(url_for('medicine_info', name=request.form['med_info']))
        elif 'refer' in request.form:
            id = system.get_patient_from_appointment(request.form['time'], current_user.email)
            history = system.get_patient_history_with_health_provider(id, current_user.email)
            referred_email = request.form['referred']
            user = system.get_user(referred_email)
            errors = {}
            if user is not None and user.get_type() != 'Patient':
                system.give_referral(request.form['time'], current_user.email, referred_email)
            else:
                errors = {'refer': 'Health Provider not exists'}
            return render_template('start_appointment.html', time=request.form['time'],
                                   medicines=system.get_appointment_medicines(request.form['time'], current_user.email),
                                   errors=errors, history=history,
                                   referred=system.get_referred_provider(request.form['time'], current_user.email))

    for i in range(len(appointments)):
        appointments[i]['appointment_type'] = get_user(appointments[i]['health_provider']).get_type()

    return render_template('display_appointments.html', appointments=appointments)


@app.route('/history', methods=['GET', 'POST'])
@login_required
def display_history():
    appointments = list(filter(lambda x: x['finished'], system.get_appointments(current_user.email)))
    if request.method == 'POST':
        if 'start_time' in request.form:
            start_time = request.form['start_time']
            for appointment in appointments:
                if system.time_format(appointment['start_time']) == start_time:
                    medicines = system.get_medicines(appointment['medicines'])
                    notes = appointment['notes']
                    return render_template('display_history_details.html', notes=notes, medicines=medicines)
    return render_template('display_history.html', appointments=appointments)


@app.route('/referrals', methods=['GET', 'POST'])
@patient_required
def display_referrals():
    referrals = []
    for i in current_user.refers:
        referrals.append((get_user(i).name, i, get_user(current_user.refers[i]).name, current_user.refers[i]))
    return render_template('display_referrals.html', referrals=referrals)


@app.route('/medicine/<name>', methods=['GET', 'POST'])
def medicine_info(name):
    data = system.get_medicine_info(name)
    return render_template('medicine_info.html', data=data)


app.run(port=5559, debug=True)
