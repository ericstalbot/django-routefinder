from django.conf.urls import patterns, url


from routefinder import views

urlpatterns = patterns('',

    url('^find$', views.find, name='find')


)
