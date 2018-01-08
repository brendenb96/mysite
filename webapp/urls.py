
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
	url(r'^login/$',views.login_user,name="login_user"),
	url(r'^logout/$', auth_views.logout, name='logout'),
	url(r'^$',views.index,name='index'),
	#url(r'^(?P<elements>\w+?)/$',views.index,name='index'),
	url(r'^minerform/$',views.minerform,name='mineform'),
	url(r'^copyright/$',views.copyright,name='copyright'),
	url(r'^force_refresh/$',views.force_refresh,name='force_refresh'),
	url(r'^delete_miner/',views.delete_miner,name='delete_miner'),
	url(r'^change_pools/',views.change_pools,name='change_pools'),
	url(r'^refresh_one/',views.refresh_one,name='refresh_one'),
	url(r'^thanks/$',views.thanks,name="thanks"),
	]
