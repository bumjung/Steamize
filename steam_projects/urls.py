from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
	url(r'^inventory/', include('inventory.urls')),
	url(r'^summary/', include('summary.urls')),
	url(r'^$', include('summary.urls'))
)
