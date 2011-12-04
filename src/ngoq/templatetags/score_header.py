import re
from django import template
from django.conf import settings

numeric_test = re.compile("^\d+$")
register = template.Library()

def score_header(val):
    return val.replace("_"," ").capitalize()

register.filter('score_header', score_header)
