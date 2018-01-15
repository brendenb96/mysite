# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.db import models
from django.views import View
from webapp.models import Miner
from forms import MinerForm
from d3_miner_scraper import *
from time import sleep
from django.shortcuts import render_to_response,redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

deleted = False
added = False
pool_change = False
force_ref = False
HASH_BENCHMARK = 15000

def login_user(request):
    logout(request)
    username = password = ''
    if request.POST:
        username = request.POST['inputUsername']
        password = request.POST['inputPassword']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('/')
    return render(request,'webapp/login.html')

def thanks(request):
	return render(request, 'webapp/logout.html')


@login_required(login_url='/login/')
def overview(request):
	global HASH_BENCHMARK
	global deleted
	global added
	global pool_change
	global force_ref

	template_dict = {}
	query_list = Miner.objects.all()
	print query_list
	sum = 0.0
	counter = 0.0
	average_hash = 0.0
	high_hash = 0.0
	low_hash = 10000000000000000000.0
	has_miners = False
	for miner in query_list:
		has_miners = True
		if miner.hash_rate > high_hash:
			high_hash = miner.hash_rate
		if miner.hash_rate < low_hash:
			low_hash = miner.hash_rate

		sum = sum + miner.hash_rate
		counter = counter + 1.0
	if counter != 0.0:
		average_hash = str(sum/counter)

	if low_hash == 10000000000000000000.0:
		low_hash = 0.0


	template_dict['eff'] = "{0:.2f}".format((float(average_hash)/HASH_BENCHMARK)*100)
	template_dict['object_list'] = query_list
	template_dict['avg_hash'] = average_hash
	template_dict['min_hash'] = low_hash
	template_dict['max_hash'] = high_hash
	template_dict['miners'] = query_list
	template_dict['user'] = request.user.get_short_name()
	template_dict['has_miners'] = has_miners
	template_dict['refresh_redirect'] = '/overview'

	efficiency = (float(average_hash)/HASH_BENCHMARK)*100

	if efficiency < 70.0:
		template_dict['slow_hash'] = True
	else:
		template_dict['slow_hash'] = False

	if deleted:
		template_dict['deleted'] = True
		deleted = False
	else:
	 	template_dict['deleted'] = False

	if added:
		template_dict['added'] = True
		added = False
	else:
	 	template_dict['added'] = False

	if pool_change:
		template_dict['pool_change'] = True
		pool_change = False
	else:
	 	template_dict['pool_change'] = False

	if force_ref:
		template_dict['force_ref'] = True
		force_ref = False
	else:
	 	template_dict['force_ref'] = False

	return render(request,'webapp/template.html',template_dict)

@login_required(login_url='/login/')
def index(request):
	global HASH_BENCHMARK
	global deleted
	global added
	global pool_change
	global force_ref

	template_dict = {}
	query_list = Miner.objects.all()
	print query_list
	sum = 0.0
	counter = 0.0
	average_hash = 0.0
	high_hash = 0.0
	low_hash = 10000000000000000000.0
	has_miners = False
	for miner in query_list:
		has_miners = True
		if miner.hash_rate > high_hash:
			high_hash = miner.hash_rate
		if miner.hash_rate < low_hash:
			low_hash = miner.hash_rate

		sum = sum + miner.hash_rate
		counter = counter + 1.0
	if counter != 0.0:
		average_hash = str(sum/counter)

	if low_hash == 10000000000000000000.0:
		low_hash = 0.0


	template_dict['eff'] = "{0:.2f}".format((float(average_hash)/HASH_BENCHMARK)*100)
	template_dict['object_list'] = query_list
	template_dict['avg_hash'] = average_hash
	template_dict['min_hash'] = low_hash
	template_dict['max_hash'] = high_hash
	template_dict['miners'] = query_list
	template_dict['user'] = request.user.get_short_name()
	template_dict['has_miners'] = has_miners
	template_dict['refresh_redirect'] = '/'

	efficiency = (float(average_hash)/HASH_BENCHMARK)*100

	if efficiency < 70.0:
		template_dict['slow_hash'] = True
	else:
		template_dict['slow_hash'] = False

	if deleted:
		template_dict['deleted'] = True
		deleted = False
	else:
	 	template_dict['deleted'] = False

	if added:
		template_dict['added'] = True
		added = False
	else:
	 	template_dict['added'] = False

	if pool_change:
		template_dict['pool_change'] = True
		pool_change = False
	else:
	 	template_dict['pool_change'] = False

	if force_ref:
		template_dict['force_ref'] = True
		force_ref = False
	else:
	 	template_dict['force_ref'] = False

	return render(request,'webapp/overview.html',template_dict)

@login_required(login_url='/login/')
def addminer(request):
	return render(request,'webapp/addminer.html')

@login_required(login_url='/login/')
def minerform(request):
	global added
	template_dict = {}
	template_dict['user'] = request.user.get_short_name()
    # if this is a POST request we need to process the form data
	if request.method == 'POST':
		form = MinerForm(request.POST)
		if form.is_valid():
			added = True
			final_form = form.save(commit=False)
			update_one_db(final_form.ip, final_form.username, final_form.password, final_form.sshpassword, final_form.type)
			return redirect('/')
		else:
			template_dict['form'] = form
			template_dict['invalid'] = True
			return render(request, 'webapp/minerform.html', template_dict)

    # if a GET (or any other method) we'll create a blank form
	else:
		form = MinerForm()
		template_dict['form'] = form
		template_dict['invalid'] = False

	return render(request, 'webapp/minerform.html', template_dict)

@login_required(login_url='/login/')
def copyright(request):
	template_dict = {}
	template_dict['user'] = request.user.get_short_name()
	return render(request,'webapp/copyright.html', template_dict)

@login_required(login_url='/login/')
def force_refresh(request):
	global force_ref
	update_db()
	force_ref = True
	return redirect('/')

@login_required(login_url='/login/')
def refresh_one(request):
	update_one_entry()
	return redirect('/')

@login_required(login_url='/login/')
def delete_miner(request):
	global deleted
	deleted = True

	result = None
	if request.method == 'POST':
		for i in range(30):
			title = str(i) + 'delete'
			if title in request.POST:
				result = i

		if result != None:
			print "deleting " + str(result)
			delete_one_db(result)
	return redirect('/')

@login_required(login_url='/login/')
def change_pools(request):
	global pool_change
	if request.method == 'POST':
		target_miner = None
		target_id = None
		for i in range(30):
			title = str(i) + 'changepool'
			if title in request.POST:
				target_id = i

		query_list = Miner.objects.all()
		for miner in query_list:
			if miner.id == target_id:
				target_miner = miner

		target_id = str(target_id)
		pool_num = request.POST['pool']
		pool_arg = request.POST[target_id+'pool']
		pool_user = request.POST[target_id+'poolworker']
		pool_pass = request.POST[target_id+'poolpassword']
		set_miner_conf(target_miner.ip,'root',target_miner.sshpassword,pool_num,pool_arg,pool_user,pool_pass)
		pool_change = True

	return redirect('/')
