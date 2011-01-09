from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('coffers.views',
    url(r'^$', 'default', name='coffers-default'),
    url(r'^saved/$', direct_to_template, {'template':'coffers/saved.html'}, name='coffers-saved'), 
)
