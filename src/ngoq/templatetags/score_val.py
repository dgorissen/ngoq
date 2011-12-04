import re
from django import template
from django.conf import settings

numeric_test = re.compile("^\d+$")
register = template.Library()



def score_val(rec,arg):
    """Removes all values of arg from the given string"""
    return rec[arg]

register.filter('score_val', score_val)