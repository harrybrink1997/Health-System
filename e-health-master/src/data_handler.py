import pickle
import os.path


def load_data(filename):
    #print("Loading data from %s..."%filename)
    try:
        pickle_off = open(get_path(filename), "rb")
        data = pickle.load(pickle_off)
    except:
        return []
    return data


def save_data(filename, data):
    #print("Saving data into %s..."%filename)
    pickling_on = open(get_path(filename), "wb")
    pickle.dump(data, pickling_on)
    pickling_on.close()


def get_path(filename):
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(my_path, "../data/%s"%filename)
    return path


def show_data(filename):
    try:
        pickle_off = open(get_path(filename), "rb")
        data = pickle.load(pickle_off)
    except:
        return []
    for row in data:
        print(row)

show_data('appointment.pickle')