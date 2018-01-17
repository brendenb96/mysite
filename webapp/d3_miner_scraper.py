#!/usr/bin/env python

import os
import sys
import pprint
import sqlite3
import json
from optparse import OptionParser
import requests
from requests.auth import HTTPDigestAuth
import subprocess

DB_NAME = '/home/brenden/Programs/mysite/db.sqlite3'
#DB_NAME = '/var/www/mysite/db.sqlite3'

TEMP_HI = 75
TEMP_LO = 30
HASH_LO = 15000
UP_LO = 1


def update_db():

    ## SUDO CODE
    # Scrape each miner for the info by looping through db of miners
    # For miner in miner_group
    # scrape miner
    # update db with new info

    global DB_NAME
    global TEMP_HI
    global TEMP_LO
    global HASH_LO

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    all_ips = cursor.execute("SELECT ip FROM webapp_miner").fetchall()
    all_passwords = cursor.execute("SELECT password FROM webapp_miner").fetchall()
    all_sshpasswords = cursor.execute("SELECT sshpassword FROM webapp_miner").fetchall()
    all_users = cursor.execute("SELECT username FROM webapp_miner").fetchall()
    all_types = cursor.execute("SELECT type FROM webapp_miner").fetchall()
    cursor.execute("DELETE FROM webapp_miner")

    counter = 0
    for machine in all_ips:
        ip_dest = machine[0].encode("utf-8")
        type = all_types[counter][0].encode("utf-8")
        username = all_users[counter][0].encode("utf-8")
        password = all_passwords[counter][0].encode("utf-8")
        ssh_password = all_sshpasswords[counter][0].encode("utf-8")
        error_webpage = False
        
        print "Using IP Address: %s" %ip_dest
        print "Username: %s" %username
        print "Password: %s" %password

        status_page = "http://"+ip_dest+"/cgi-bin/get_miner_status.cgi"
        system_page = "http://"+ip_dest+"/cgi-bin/get_system_info.cgi"
        config_page = "http://"+ip_dest+"/cgi-bin/get_miner_conf.cgi"


        try:
            session = requests.Session()
            miner_status_page = session.get(status_page, auth=HTTPDigestAuth(username,password), timeout=5)
            miner_status_content = miner_status_page.json()

            miner_system_page = session.get(system_page, auth=HTTPDigestAuth(username,password), timeout=5)
            miner_system_content = miner_system_page.json()

            miner_config_page = session.get(config_page, auth=HTTPDigestAuth(username,password), timeout=5)
            miner_config_content = miner_config_page.json()
        except Exception as err:
            error_webpage = True

        if error_webpage:
            ip = ip_dest
            pool_one = "Couldn't Update"
            pool_two = "Couldn't Update"
            pool_three = "Couldn't Update"
            hash_rate = "0.00"
            name = "ERROR: Couldn't Update Miner"
            uptime = "XX:XX"
            chain1_temp = "0"
            chain2_temp = "0"
            chain3_temp = "0"
            asic1 = "Couldn't Update"
            asic2= "Couldn't Update"
            asic3 = "Couldn't Update"
            pool_one_worker = "Couldn't Update"
            pool_two_worker = "Couldn't Update"
            pool_three_worker = "Couldn't Update"

            pool_one_password = "Couldn't Update"
            pool_two_password = "Couldn't Update"
            pool_three_password = "Couldn't Update"

            bitmain_freq = "True"
            bitmain_vil = "0"

            has_error = True

        else:
            ip = ip_dest
            pool_one = miner_config_content['pools'][0]['url']
            pool_two = miner_config_content['pools'][1]['url']
            pool_three = miner_config_content['pools'][2]['url']
            hash_rate = miner_status_content['summary']['ghsav']
            name = miner_system_content['hostname']
            uptime = miner_system_content['uptime']
            chain1_temp = miner_status_content['devs'][0]['freq'].split(',')[9].split('=')[1]
            chain2_temp = miner_status_content['devs'][0]['freq'].split(',')[10].split('=')[1]
            chain3_temp = miner_status_content['devs'][0]['freq'].split(',')[11].split('=')[1]
            asic1 = miner_status_content['devs'][0]['chain_acs']
            asic2= miner_status_content['devs'][1]['chain_acs']
            asic3 = miner_status_content['devs'][2]['chain_acs']

            pool_one_worker = miner_config_content['pools'][0]['user']
            pool_two_worker = miner_config_content['pools'][1]['user']
            pool_three_worker = miner_config_content['pools'][2]['user']

            pool_one_password = miner_config_content['pools'][0]['pass']
            pool_two_password = miner_config_content['pools'][1]['pass']
            pool_three_password = miner_config_content['pools'][2]['pass']

            bitmain_vil = miner_config_content['bitmain-use-vil']
            bitmain_freq = miner_config_content['bitmain-freq']

            has_error = False 

            if pool_one.rstrip() == '':
                pool_one = 'NONE'
                pool_one_worker = 'NONE'
                pool_one_password = 'NONE'
            if pool_two.rstrip() == '':
                pool_two = 'NONE'
                pool_two_worker = 'NONE'
                pool_two_password = 'NONE'
            if pool_three.rstrip() == '':
                pool_three = 'NONE'
                pool_three_worker = 'NONE'
                pool_three_password = 'NONE'

            if chain1_temp > TEMP_HI or chain1_temp < TEMP_LO:
                has_error = True

            if chain2_temp > TEMP_HI or chain2_temp < TEMP_LO:
                has_error = True

            if chain3_temp > TEMP_HI or chain3_temp < TEMP_LO:
                has_error = True

            if float(hash_rate) < HASH_LO:
                has_error = True

            try:
                if ':' in uptime:
                    has_error = False
                else:
                    if int(uptime) < UP_LO:
                        has_error = True
            except Exception as e:
                pass


        print ip
        print pool_one
        print pool_two
        print pool_three
        print hash_rate
        print type
        print name
        print chain1_temp
        print chain2_temp
        print chain3_temp
        print uptime

        # print miner_status_content
        # print miner_system_content
        # print miner_config_content

        insert_pass = True
        insert_tries = 0
        error_msg = None
        while(insert_pass and insert_tries <= 30):
            try:
                insert_tries = insert_tries + 1
                cursor.execute("INSERT INTO webapp_miner VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", 
                    [insert_tries,name,ip,pool_one,pool_two,pool_three,float(hash_rate),type,password,username,
                    int(chain1_temp),int(chain2_temp),int(chain3_temp),uptime,asic1,asic2,asic3,
                    pool_one_password,pool_one_worker,pool_three_password,pool_three_worker,pool_two_password,
                    pool_two_worker,bitmain_freq,bitmain_vil,ssh_password,has_error])
                insert_pass = False
            except Exception as e:
                error_msg = e
                pass

        if insert_tries >= 30:
            print "Couldn't add miner"
            print error_msg

        counter = counter + 1


    conn.commit()
    conn.close()

    return 0

def update_one_db(ip_dest, username, password, sshpassword, type_miner):

    ## SUDO CODE
    # Scrape each miner for the info by looping through db of miners
    # For miner in miner_group
    # scrape miner
    # update db with new info

    global DB_NAME
    global TEMP_HI
    global TEMP_LO
    global HASH_LO

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    error_webpage = False
    
    print "Using IP Address: %s" %ip_dest
    print "Username: %s" %username
    print "Password: %s" %password

    status_page = "http://"+ip_dest+"/cgi-bin/get_miner_status.cgi"
    system_page = "http://"+ip_dest+"/cgi-bin/get_system_info.cgi"
    config_page = "http://"+ip_dest+"/cgi-bin/get_miner_conf.cgi"


    try:
        session = requests.Session()
        miner_status_page = session.get(status_page, auth=HTTPDigestAuth(username,password),timeout=5)
        miner_status_content = miner_status_page.json()

        miner_system_page = session.get(system_page, auth=HTTPDigestAuth(username,password), timeout=5)
        miner_system_content = miner_system_page.json()

        miner_config_page = session.get(config_page, auth=HTTPDigestAuth(username,password), timeout=5)
        miner_config_content = miner_config_page.json()
    except Exception as err:
        error_webpage = True

    
    if error_webpage:
        ip = ip_dest
        pool_one = "Couldn't Update"
        pool_two = "Couldn't Update"
        pool_three = "Couldn't Update"
        hash_rate = "0.00"
        type = type_miner
        name = "ERROR: Couldn't Update Miner"
        uptime = "XX:XX"
        chain1_temp = "0"
        chain2_temp = "0"
        chain3_temp = "0"
        asic1 = "Couldn't Update"
        asic2= "Couldn't Update"
        asic3 = "Couldn't Update"
        bitmain_freq = "True"
        bitmain_vil = "0"

        pool_one_worker = 'none'
        pool_two_worker = 'none'
        pool_three_worker = 'none'

        pool_one_password = 'none'
        pool_two_password =  'none'
        pool_three_password = 'none'

        has_error = True

    else:
        ip = ip_dest
        pool_one = miner_config_content['pools'][0]['url']
        pool_two = miner_config_content['pools'][1]['url']
        pool_three = miner_config_content['pools'][2]['url']

        pool_one_worker = miner_config_content['pools'][0]['user']
        pool_two_worker = miner_config_content['pools'][1]['user']
        pool_three_worker = miner_config_content['pools'][2]['user']

        pool_one_password = miner_config_content['pools'][0]['pass']
        pool_two_password = miner_config_content['pools'][1]['pass']
        pool_three_password = miner_config_content['pools'][2]['pass']

        hash_rate = miner_status_content['summary']['ghsav']
        type = miner_system_content['minertype']
        name = miner_system_content['hostname']
        uptime = miner_system_content['uptime']
        try:
            chain1_temp = miner_status_content['devs'][0]['freq'].split(',')[9].split('=')[1]
            chain2_temp = miner_status_content['devs'][0]['freq'].split(',')[10].split('=')[1]
            chain3_temp = miner_status_content['devs'][0]['freq'].split(',')[11].split('=')[1]
            asic1 = miner_status_content['devs'][0]['chain_acs']
            asic2= miner_status_content['devs'][1]['chain_acs']
            asic3 = miner_status_content['devs'][2]['chain_acs']
        except Exception:
            chain1_temp = "0"
            chain2_temp = "0"
            chain3_temp = "0"
            asic1 = "No Pool"
            asic2= "No Pool"
            asic3 = "No Pool"

        bitmain_vil = miner_config_content['bitmain-use-vil']
        bitmain_freq = miner_config_content['bitmain-freq']

        has_error = False 

        if pool_one.rstrip() == '':
            pool_one = 'NONE'
        if pool_two.rstrip() == '':
            pool_two = 'NONE'
        if pool_three.rstrip() == '':
            pool_three = 'NONE'

    print "updating one"
    print ip
    print pool_one
    print pool_two
    print pool_three
    print hash_rate
    print type
    print name
    print chain1_temp
    print chain2_temp
    print chain3_temp
    print uptime

    # print miner_status_content
    # print miner_system_content
    # print miner_config_content

    insert_pass = True
    insert_tries = 0
    error_msg = None
    while(insert_pass and insert_tries <= 30):
        try:
            insert_tries = insert_tries + 1
            cursor.execute("INSERT INTO webapp_miner VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", 
            [insert_tries,name,ip,pool_one,pool_two,pool_three,float(hash_rate),type,password,username,
            int(chain1_temp),int(chain2_temp),int(chain3_temp),uptime,asic1,asic2,asic3,
            pool_one_password,pool_one_worker,pool_three_password,pool_three_worker,pool_two_password,
            pool_two_worker,bitmain_freq,bitmain_vil,sshpassword,has_error])
            insert_pass = False
        except Exception as e:
            error_msg = e
            pass

    if insert_tries >= 30:
        print "Couldn't add miner"
        print error_msg

    try:
        conn.commit()
        print "commit successful"
    except Exception as e:
        print e

    conn.close()

    return 0

def update_one_entry(ip_dest, username, password, type_miner):

    ## SUDO CODE
    # Scrape each miner for the info by looping through db of miners
    # For miner in miner_group
    # scrape miner
    # update db with new info

    global DB_NAME
    global TEMP_HI
    global TEMP_LO
    global HASH_LO

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    error_webpage = False
    
    print "Using IP Address: %s" %ip_dest
    print "Username: %s" %username
    print "Password: %s" %password

    status_page = "http://"+ip_dest+"/cgi-bin/get_miner_status.cgi"
    system_page = "http://"+ip_dest+"/cgi-bin/get_system_info.cgi"
    config_page = "http://"+ip_dest+"/cgi-bin/get_miner_conf.cgi"


    try:
        session = requests.Session()
        miner_status_page = session.get(status_page, auth=HTTPDigestAuth(username,password))
        miner_status_content = miner_status_page.json()

        miner_system_page = session.get(system_page, auth=HTTPDigestAuth(username,password))
        miner_system_content = miner_system_page.json()

        miner_config_page = session.get(config_page, auth=HTTPDigestAuth(username,password))
        miner_config_content = miner_config_page.json()
    except Exception as err:
        error_webpage = True

    if error_webpage:
        ip = ip_dest
        pool_one = "Couldn't Update"
        pool_two = "Couldn't Update"
        pool_three = "Couldn't Update"
        hash_rate = "0.00"
        type = type_miner
        name = "ERROR: Couldn't Update Miner"
        uptime = "XX:XX"
        chain1_temp = "0"
        chain2_temp = "0"
        chain3_temp = "0"
        asic1 = "Couldn't Update"
        asic2= "Couldn't Update"
        asic3 = "Couldn't Update"
        bitmain_freq = "True"
        bitmain_vil = "0"
        pool_one_worker = 'none'
        pool_two_worker = 'none'
        pool_three_worker = 'none'

        pool_one_password = 'none'
        pool_two_password =  'none'
        pool_three_password = 'none'

        has_error = True

    else:
        ip = ip_dest
        pool_one = miner_config_content['pools'][0]['url']
        pool_two = miner_config_content['pools'][1]['url']
        pool_three = miner_config_content['pools'][2]['url']

        pool_one_worker = miner_config_content['pools'][0]['user']
        pool_two_worker = miner_config_content['pools'][1]['user']
        pool_three_worker = miner_config_content['pools'][2]['user']

        pool_one_password = miner_config_content['pools'][0]['pass']
        pool_two_password = miner_config_content['pools'][1]['pass']
        pool_three_password = miner_config_content['pools'][2]['pass']

        hash_rate = miner_status_content['summary']['ghsav']
        type = miner_system_content['minertype']
        name = miner_system_content['hostname']
        uptime = miner_system_content['uptime']
        try:
            chain1_temp = miner_status_content['devs'][0]['freq'].split(',')[9].split('=')[1]
            chain2_temp = miner_status_content['devs'][0]['freq'].split(',')[10].split('=')[1]
            chain3_temp = miner_status_content['devs'][0]['freq'].split(',')[11].split('=')[1]
            asic1 = miner_status_content['devs'][0]['chain_acs']
            asic2= miner_status_content['devs'][1]['chain_acs']
            asic3 = miner_status_content['devs'][2]['chain_acs']
        except Exception:
            chain1_temp = "0"
            chain2_temp = "0"
            chain3_temp = "0"
            asic1 = "No Pool"
            asic2= "No Pool"
            asic3 = "No Pool"

        bitmain_vil = miner_config_content['bitmain-use-vil']
        bitmain_freq = miner_config_content['bitmain-freq']

        has_error = False 

        if pool_one.rstrip() == '':
            pool_one = 'NONE'
        if pool_two.rstrip() == '':
            pool_two = 'NONE'
        if pool_three.rstrip() == '':
            pool_three = 'NONE'

    print "updating one"
    print ip
    print pool_one
    print pool_two
    print pool_three
    print hash_rate
    print type
    print name
    print chain1_temp
    print chain2_temp
    print chain3_temp
    print uptime

    # print miner_status_content
    # print miner_system_content
    # print miner_config_content

    error_msg = None
    try:
        insert_tries = insert_tries + 1
        cursor.execute("UPDATE webapp_miner SET pool_one=?,pool_two=?,pool_three=?,hash_rate=?,chain1_temp=?,chain2_temp=?,\
            chain3_temp=?,uptime=?,asic1=?,asic2=?,asic3=?,pool_one_password=?,pool_one_worker=?,pool_three_password=?,pool_three_worker=?,pool_two_password=?,\
        pool_two_worker=?",[pool_one,pool_two,pool_three,float(hash_rate),int(chain1_temp),int(chain2_temp),int(chain3_temp),
        uptime,asic1,asic2,asic3,pool_one_password,pool_one_worker,pool_three_password,pool_three_worker,pool_two_password,pool_two_worker])       
        insert_pass = False
    except Exception as e:
        error_msg = e
        print "Couldn't add miner"
        print error_msg

    conn.commit()
    conn.close()

    return 0

def delete_db(database):

    ## SUDO CODE
    # Scrape each miner for the info by looping through db of miners
    # For miner in miner_group
    # scrape miner
    # update db with new info

    global DB_NAME
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM webapp_miner")
    conn.commit()
    conn.close()

def delete_one_db(id):

    ## SUDO CODE
    # Scrape each miner for the info by looping through db of miners
    # For miner in miner_group
    # scrape miner
    # update db with new info

    global DB_NAME
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM webapp_miner where id=?",[id])
    conn.commit()
    conn.close()

    return 0

def communicate(command):
    """ sends commands to machine """
    return subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True).communicate()


def set_miner_conf(ip, username, password, pool_number, pool_arg, pool_user, pool_pass):
    # ip = '172.16.1.76'
    # username = 'root'
    # password = 'admin'
    # pool_number = 1
    # pool_arg = 'stratum+tcp://stratum-dash.antpool.com:6099'
    # pool_user = 'Hunts4.D7'
    # pool_pass = 'x'
    in_file = '/tmp/temp_cgminer.conf'
    out_file = '/tmp/temp_cgminer_good.conf'

        # sshpass -p "admin" scp root@172.16.1.76:/config/cgminer.conf testing2
    
    #get_remote_string = 'sshpass -p "%s" rsync -avz root@%s:/config/cgminer.conf %s'%(password, ip, in_file)
    get_remote_string = 'sshpass -p "%s" scp -o StrictHostKeyChecking=no %s@%s:/config/cgminer.conf %s'%(password, username, ip, in_file)
    put_remote_string = 'sshpass -p "%s" scp -o StrictHostKeyChecking=no %s %s@%s:/config/cgminer.conf'%(password, out_file, username, ip)
    run_remote_string = "sshpass -p '%s' ssh -o StrictHostKeyChecking=no %s@%s '/etc/init.d/cgminer.sh restart'"%(password, username, ip)
    perm_string = "chmod 7777 /tmp/temp_cgminer.conf"

    print get_remote_string
    print put_remote_string
    print run_remote_string

    resp = communicate(get_remote_string)
    print resp
    #communicate(perm_string)
    
    json_data=open(in_file).read()
    miner_config_content = json.loads(json_data)

    if pool_number == '1':
        miner_config_content['pools'][0]['url'] = pool_arg
        miner_config_content['pools'][0]['user'] = pool_user
        miner_config_content['pools'][0]['pass'] = pool_pass

    if pool_number == '2':
        miner_config_content['pools'][1]['url'] = pool_arg
        miner_config_content['pools'][1]['user'] = pool_user
        miner_config_content['pools'][1]['pass'] = pool_pass

    if pool_number == '3':
        miner_config_content['pools'][2]['url'] = pool_arg
        miner_config_content['pools'][2]['user'] = pool_user
        miner_config_content['pools'][2]['pass'] = pool_pass

    with open(out_file, 'w') as outfile:
        json.dump(miner_config_content, outfile)

    communicate(put_remote_string)
    resp = communicate(run_remote_string)
    print "****************"
    print resp

    return 0
