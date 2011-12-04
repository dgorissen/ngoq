from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
     url(r'^$', 'ngoq.views.main', name='main'),
     url(r'data$', 'ngoq.views.get_data_json', name='datajson'),
     url(r'data/(?P<id>[a-zA-Z0-9_\-\\]+)$', 'ngoq.views.get_record_json', name='recjson'),
)