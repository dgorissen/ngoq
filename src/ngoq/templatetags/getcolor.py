import re
from django import template
from django.conf import settings

numeric_test = re.compile("^\d+$")
register = template.Library()

def getcolor(rec,arg):
    return rec["color_" + arg]

register.filter('getcolor', getcolor)
