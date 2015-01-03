from django.conf.urls import patterns, url
from summary import views
from django.views.decorators.cache import cache_page
   
urlpatterns = patterns('',
          url(r'^$', views.index, name='index'),
          url(r'get_profile/$', views.get_profile, name='get_profile'),
          url(r'profile/(?P<steam_id>\d{17})/$', cache_page(60*30)(views.profile), name='profile'),
          url(r'gameInfo/(?P<steam_id>\d{17})/(?P<app_id>\d+)/$', views.game, name='game'),
		  url(r'privacy/', views.privacy, name='privacy'),
		  url(r'about/', views.about, name='about'))
