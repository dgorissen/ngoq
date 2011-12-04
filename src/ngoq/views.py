from django.shortcuts import render_to_response
from django.template.context import RequestContext
from openpyxl.reader.excel import load_workbook
import simplejson
from django.http import HttpResponse
import csv
from ngoq.util import lfu_cache
import logging
from ngoq.models import Rule
import settings
import os

# Get an instance of a logger
log = logging.getLogger(__name__)

def calc_color(score):
    
    if score < 2:
        color = "red"
    elif 2 < score < 5:
        color = "orange"
    else:
        color = "green"
    
    return color
    
def main(request):

    rbs = settings.RULEBASES

    if request.method == "POST":
        # update the weights / activeness
        active_rules = []
        for k,v in request.POST.items():
            if k.endswith("#chk"):
                rb,rn,_ = k.split("#")
                active_rules.append(rb + "_" + rn)
            elif k.endswith("#weight") and v:
                rb,rn,_ = k.split("#")
                rbs[rb].set_weight(rn, float(v))
            else:
                pass
        
        for n,rb in rbs.items():
            for r,w,a in rbs[n].get_rules():
                rb.set_active(r.name, (n + "_" + r.name) in active_rules)
    else:
        pass
    
    rules = []
    for n,rb in rbs.items():
        rules.append({"name": n, "rules":[{"name":r.name,"description":r.description,"weight":w,"active":a} for r,w,a in rb.get_rules()]})
    
    records = load_data()
    
    for n,rb in rbs.items():
        for rec in records.values():
            score = rb.eval_rules(rec, context=records)
            color = calc_color(score)
            rec[n] = score
            rec["color"] = color
            
    
    data = {"records":records.values(),
            "rules":rules}
    
    return render_to_response('main.html',data,context_instance=RequestContext(request))

def get_record_json(request,id):
    data = load_data()
    return HttpResponse(simplejson.dumps(data[id]))

def get_data_json(request):
    data = load_data()
    return HttpResponse(simplejson.dumps(data))
 
@lfu_cache()
def load_data():
    data = {}
    reader = csv.DictReader(open(os.path.join(settings.DATADIR,"partial.csv"), "rb"))
    for row in reader:
        del row[""]
        row["Id"] = row["Id"].replace("/","_")
        row["City"] = row["City"].capitalize() 
        data[row["Id"]] = row

    return data

if __name__ == "__main__":
    print load_data()