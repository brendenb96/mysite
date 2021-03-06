# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.db import models
from django.views import View
from webapp.models import Miner
from forms import MinerForm
from d3_miner_scraper import *
from time import sleep
from random import randint
import time
import json
from django.shortcuts import render_to_response,redirect
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

deleted = False
added = False
pool_change = False
force_ref = False
restart = False

restart_fail = False
pool_change_fail = False

force_ref_one = False
force_ref_one_fail = False

HASH_BENCHMARK = 15000
MAX_MINERS = 30

def handler500(request):
    return render(request, 'webapp/custom500.html', status=500)

def handler404(request):
    return render(request, 'webapp/custom404.html', status=404)
   
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
	template_dict['avg_hash'] = round(average_hash,2)
	template_dict['min_hash'] = round(low_hash,2)
	template_dict['max_hash'] = round(high_hash,2)
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
	global pool_change_fail
	global pool_change
	global force_ref
	global restart_fail
	global restart
	global force_ref_one
	global force_ref_one_fail
	
	JSON_FILENAME = "/var/www/databases/data.json"

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
		average_hash = sum/counter

	if low_hash == 10000000000000000000.0:
		low_hash = 0.0

	average_hash = "{0:.2f}".format(average_hash)
	template_dict['eff'] = "{0:.2f}".format((float(average_hash)/HASH_BENCHMARK)*100)
	template_dict['object_list'] = query_list
	template_dict['miners'] = query_list
	template_dict['avg_hash'] = average_hash
	template_dict['min_hash'] = low_hash
	template_dict['max_hash'] = high_hash
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
         
	if restart:
	    template_dict['restart'] = True
	    restart = False
	    if restart_fail:
	        template_dict['restart_fail'] = True
	        restart_fail = False
	    else:
	    	template_dict['restart_fail'] = False
	else:
	    template_dict['restart'] = False
	    
	if force_ref_one:
	    template_dict['force_ref_one'] = True
	    force_ref_one = False
	    if force_ref_one_fail:
	        template_dict['force_ref_one_fail'] = True
	        force_ref_one_fail = False
	    else:
	    	template_dict['force_ref_one_fail'] = False
	else:
	    template_dict['force_ref_one'] = False

	if added:
		template_dict['added'] = True
		added = False
	else:
	 	template_dict['added'] = False

	if pool_change:
		template_dict['pool_change'] = True
		pool_change = False
		if pool_change_fail:
			template_dict['pool_change_fail'] = True
			pool_change_fail = False
		else:
			template_dict['pool_change_fail'] = False
	else:
	 	template_dict['pool_change'] = False

	if force_ref:
		template_dict['force_ref'] = True
		force_ref = False
	else:
	 	template_dict['force_ref'] = False
	 	
	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		ip = x_forwarded_for.split(',')[0]
	else:
		ip = request.META.get('REMOTE_ADDR')
		
	template_dict['user_ip'] = ip
	
	################## CHANGE THIS FOR EACH SETUP ########################
	template_dict['internal_ip'] = '192.168.0'
	######################################################################

	empty_json = False
	
	try:
		with open(JSON_FILENAME, 'r') as json_data:
			data = json.load(json_data)
	except ValueError:
		print "EMPTY JSON"
		data = []
		empty_json = True
		
	if not empty_json:
		if data[-1]['date'] < (int(time.time()) - 50):
			js = {}
			js['date'] = int(time.time())
			js['units'] = int(float(average_hash))
			
			data.append(js)
			
			with open(JSON_FILENAME, 'w') as json_data:
				json.dump(data, json_data)
				
	else:
		js = {}
		js['date'] = int(time.time())
		js['units'] = int(float(average_hash))
		
		data.append(js)
		
		with open(JSON_FILENAME, 'w') as json_data:
			json.dump(data, json_data)
		

	return render(request,'webapp/overview.html',template_dict)

@login_required(login_url='/login/')
def addminer(request):
	if 'overview' in request.META['HTTP_REFERER']:
		template_to_return = 'webapp/template.html'
	else:
		template_to_return = 'webapp/overview.html'

	return render(request,template_to_return)

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
	if 'overview' in request.META['HTTP_REFERER']:
		to_return = '/overview'
	else:
		to_return = '/'

	return redirect(to_return)

@login_required(login_url='/login/')
def refresh_one(request):
	global force_ref_one
	global force_ref_one_fail
	
	force_ref_one = True
	
	if request.method == 'POST':
	    for i in range(MAX_MINERS):
	        title = str(i) + 'update'
	        if title in request.POST:
	            result = i
	            
	    
	miner = Miner.objects.filter(id=result)[0]
	
	force_ref_one_fail = update_one_entry(miner.ip, miner.username, miner.password, miner.id)
	return redirect('/')

@login_required(login_url='/login/')
def delete_miner(request):
	global deleted
	deleted = True

	if 'overview' in request.META['HTTP_REFERER']:
		to_return = '/overview'
	else:
		to_return = '/'

	result = None
	if request.method == 'POST':
		for i in range(MAX_MINERS):
			title = str(i) + 'delete'
			if title in request.POST:
				result = i
                

		if result != None:
			print "deleting " + str(result)
			delete_one_db(result)
	return redirect(to_return)

@login_required(login_url='/login/')
def change_pools(request):
	global pool_change
	global pool_change_fail
    
	if request.method == 'POST':
		target_miner = None
		target_id = None
		for i in range(MAX_MINERS):
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
		pool_change_fail = set_miner_conf(target_miner.ip,'root',target_miner.sshpassword,pool_num,pool_arg,pool_user,pool_pass)
		pool_change = True

	return redirect('/')
    
@login_required(login_url='/login/')
def restart_miner(request):
    global restart
    global restart_fail
    
    restart = True

    if 'overview' in request.META['HTTP_REFERER']:
        to_return = '/overview'
    else:
        to_return = '/'

    result = None
    if request.method == 'POST':
        for i in range(MAX_MINERS):
            title = str(i) + 'restart'
            if title in request.POST:
                result = i

        miner = Miner.objects.filter(id=result)[0]
        if result != None:
            print "restarting" + str(result)
            restart_fail = restart_machine(miner.ip, miner.username, miner.password)
    return redirect(to_return)
   
@login_required(login_url='/login/')
def stats(request):
	template_dict = {}
	template_dict['user'] = request.user.get_short_name()
	return render(request,'webapp/stats.html', template_dict)

def data(request):
	filename = '/var/www/databases/data.json'
	datastore = []
# 	if filename:
# 		js = open(filename).read()
# 		datastore = json.loads(js)
	time = 1517166640
	for i in range(100):
		js = {}
		hash = randint(0,14999) + randint(0,99)/100
		time = time + (3600*24)
		js['date'] = time
		js['units'] = hash
		datastore.append(js)
		
        
	return JsonResponse(datastore, safe=False)

def count(request):
	filename = '/var/www/databases/counts.json'
	datastore = []
	if filename:
		js = open(filename).read()
		datastore = json.loads(js)
	
# 	count1 = randint(10,30)
# 	count2 = randint(10,30)
# 	count3 = randint(10,30)
# 	
# 	js = {}
# 	js['labels'] = "Antminer L3"
# 	js['count'] = count1
# 	datastore.append(js)
# 	
# 	js = {}
# 	js['labels'] = "Antminer D3"
# 	js['count'] = count2
# 	datastore.append(js)
# 	
# 	js = {}
# 	js['labels'] = "Antminer S9"
# 	js['count'] = count3
# 	datastore.append(js)
		
        
	return JsonResponse(datastore, safe=False)
