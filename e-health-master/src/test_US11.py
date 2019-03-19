import pytest
from system import *

# Sample system
system = HealthSystem()

# Sample health centres
Liverpool = {'abn': '8765', 'suburb': 'Liverpool', 'name': 'Liverpool Hospital', 'phone': '09876543', 'services': [], 'ratings': '0', 'type': 'Hospital'} 
UNSW_Health_Service = {'abn': '9854', 'suburb': 'Kensington', 'name': 'UNSW_Health_Service', 'phone': '9876543', 'services':[],'ratings':'5','type':'Hospital'}

system.add_health_centre(Liverpool)
system.add_health_centre(UNSW_Health_Service)

# Testing searching by suburb "Liverpool" returns ONLY Liverpool Hospital 

def test_correct_search_return():
    Liverpool_Hospital = system.get_health_centre('Liverpool')
    assert Liverpool_Hospital.name == 'Liverpool Hospital'
    assert Liverpool_Hospital.suburb == 'Liverpool'
