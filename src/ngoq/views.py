from django.shortcuts import render_to_response
from django.template.context import RequestContext

def main(request):
    data = {}
    return render_to_response('main.html',data,context_instance=RequestContext(request))
