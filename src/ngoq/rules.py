from functools import partial
from urllib2 import urlopen
from ngoq.util import lfu_cache
import csv
import settings
import os

class Rule():
    def __init__(self,name,fun,desc=""):
        self.name = name
        self.fun = fun
        self.description = desc
    def fire(self,rec,context=None):
        res = self.fun(rec,context=context)
        return float(res) if res else 0

class RuleEntry():
    def __init__(self,rule,weight=1,active=True):
        self.rule = rule
        self.weight = weight
        self.active = active

class RuleBase():
    def __init__(self,name="",desc=""):
        self.__rules = {}
        self.name = name
        self.desc = desc
    
    def add_rule(self,rule,weight=1):
        self.__rules[rule.name] = RuleEntry(rule,weight)
    
    def set_weight(self,name,weight):
        re = self.__rules[name]
        re.weight = weight

    def set_active(self,name,active):
        re = self.__rules[name]
        re.active = active

    def eval_rule(self,name,rec,context=None):
        re = self.__rules[name]
        if re.active:
            return re.rule.fire(rec,context=context)*re.weight
        else:
            return 0 
    
    def eval_rules(self,rec,context=None):
        return sum([self.eval_rule(n, rec, context=context) for n in self.__rules.keys()])

    def get_rules(self):
        return [(re.rule,re.weight,re.active) for re in self.__rules.values()]

@lfu_cache()
def load_class_data():
    class1 = []
    reader = csv.DictReader(open(os.path.join(settings.DATADIR,"ngoclass1.csv"), "rb"))
    for row in reader:
        class1.append(row)

    class2 = []
    reader = csv.DictReader(open(os.path.join(settings.DATADIR,"ngoclass2.csv"), "rb"))
    for row in reader:
        class2.append(row)

    return class1,class2

def get_rulebases():
    rb_avail = RuleBase(name="data_availibility")
    rb_qual = RuleBase(name="data_quality")
    rb_agg = RuleBase(name="data_aggregation")
    rb_std = RuleBase(name="data_std_compliance")
    
    def has_field(name,rec,context=None):
        return (name in rec and len(rec[name]) > 0)
    
    def check_manager(rec,context=None):
        return not (rec["Chairman"] == rec["Promoter Name 1"] == rec["Chief Functionary"])
    
    def check_cert(rec,context=None):
        url = rec.get("Registration Certificate URL",None)
        if not url:
            return 0
        else:
            try:
                code = urlopen(url).code
                if (code / 100 >= 4):
                    return 0
                else:
                    return 1
            except:
                return 0
    
    #def recs_for_field(field,val):
    
    def recs_for_field(data,field,value):
        matches = [rec for rec in data.values() if field in rec and rec[field].lower() == value.lower()]
        return matches
        
            
    r = Rule("check_phone", partial(has_field,"Phone number"),desc="Is there a phone number")
    rb_avail.add_rule(r)

    r = Rule("check_address", partial(has_field,"Address"),desc="Is there an address")
    rb_avail.add_rule(r)

    r = Rule("check_manager", check_manager,desc="Is the manager consistent")
    rb_agg.add_rule(r)

    r = Rule("check_registered", partial(has_field,"Registered"),desc="Are they registered")
    rb_avail.add_rule(r)
    
    r = Rule("check_regno", partial(has_field,"Registration No"),desc="Do they have a registration number")
    rb_avail.add_rule(r)

    r = Rule("check_cert_exists", partial(has_field,"Registration Certificate URL"),desc="Is there a registration URL")
    rb_avail.add_rule(r)

    r = Rule("check_cert", check_cert,desc="Is it a valid URL")
    #rb_qual.add_rule(r)

    def check_secots(rec,context=None):
        sec = rec.get("Sectors Working In","").split(",")
        return 0 < len(sec) < 5

    r = Rule("check_sectors", check_secots,desc="Too many sectors")
    rb_qual.add_rule(r)

    def check_names(rec,context=None):
        matches = recs_for_field(context, "Name", rec["Name"])
        return 0 if len(matches) > 0 else 1

    r = Rule("check_names", check_names,desc="Unique names")
    rb_agg.add_rule(r)

    def check_regdate(rec,context=None):
        d = rec["Date of Registration"]
        if len(d) >= 10:
            y = int(d[6:10])
            return 1900 < y < 2012
        else:
            return 0

    r = Rule("check_regdate", check_regdate,desc="Valid registration date")
    rb_qual.add_rule(r)

    def check_classification(rec,context=None):
        class1,class2 = load_class_data()
        cls = rec["Sectors Working In"].split(",")
        
        unks = [x for x in cls if x not in [c["sclass"] for c in class2]]
        
        return len(unks) < 1
        
    r = Rule("check_classification", check_classification,desc="Valid classifications")
    rb_std.add_rule(r)
    
    def check_dupe_fields(rec,context=None):
        fields = rec.keys()
        fields.remove("State")
        fields.remove("City of Registration")
        
        for f in fields:
            matches = recs_for_field(context, f, rec[f])
            if len(matches) > 10:
                return 0
            
        return 1
        
    r = Rule("check_dupe_fields", check_dupe_fields,desc="Repeated fields")
    rb_agg.add_rule(r)
    
    rulebases = {}
    rulebases[rb_avail.name] = rb_avail
    rulebases[rb_agg.name] = rb_agg
    rulebases[rb_std.name] = rb_std
    rulebases[rb_qual.name] = rb_qual

    return rulebases 

if __name__ == "__main__":
    print load_class_data()