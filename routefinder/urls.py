from django.conf.urls import patterns, url


from . import views

urlpatterns = [

    url('^find$', views.find, name='find')


]
