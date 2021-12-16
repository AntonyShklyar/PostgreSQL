#!/usr/bin/python

if false:
        BD clusters:
        s39bd1iz01.iz.com
        s39bd1iz02.iz.com
        s39bd2iz01.iz.com
        s39bd2iz02.iz.com
        and
        s39crsvn01.vn.com
        s39crsvn02.vn.com
        and
        s39crsin01.in.com
        s39crsin02.in.com
	
#massive - selection of an array of hypervisor IP addresses depending on the contour
#backup - backup to the mounted spheres of the OCOD and RCOD
#sync - synchronization of the contents of the mounted ball of the OCOD and RCOD
#search - checking 'sync' trigger conditions
#mounts - checking if the ball is mounted

import os
import shutil
import socket
import numpy as np
import pwd
import grp
import subprocess
import time
import datetime

#Creating a log file for long-term storage of script events
if not os.path.exists('/var/log/debugdb.log'): open("/var/log/debugdb.log", "w+")
#If the size of 1 GB is exceeded, the debug.log is deleted and recreated
if not os.path.getsize('/var/log/debugdb.log')/(1024*1024*1024)==0: os.remove('/var/log/debugdb.log')
shutil.copyfile("/var/log/backupdb.log", "/var/log/debugdb.log") 
#Creating a log file to store the events of one script launch
os.remove('/var/log/backupdb.log'); open("/var/log/backupdb.log", "w+")
if set('01').issubset(socket.gethostname()):
	dir1='/mnt/dbbackup/OCOD/'
        dir2='/mnt/dbbackup/RCOD/'
elif set('02').issubset(socket.gethostname()):
	dir1='/mnt/dbbackup/RCOD/'
        dir2='/mnt/dbbackup/OCOD/'
def massive(IP=[]):
	if set('01').issubset(socket.gethostname()):
        	IPIZ = ['10.111.15.54', '10.111.15.63']
                IPVN = ['10.111.16.54', '10.111.16.63']
                IPIN = ['10.111.17.54', '10.111.17.63']
        elif set('02').issubset(socket.gethostname()):
        	IPIZ = ['10.111.15.63', '10.111.15.54']
                IPVN = ['10.111.16.63', '10.111.16.54']
                IPIN = ['10.111.17.63', '10.111.17.54']	
	if socket.gethostname().find('vp.com') >= 0:
		for i in IPVN:
			IP.append(i)
	elif socket.gethostname().find('ac.com') >= 0:
                for i in IPIZ:
                        IP.append(i)
	else:
		for i in IPIN:
                        IP.append(i)
	return IP
#massive()
def backup(var):
	if not os.path.isdir('/var/lib/postgresql/wal_archive/'): os.mkdir('/var/lib/postgresql/wal_archive/'); uid = pwd.getpwnam("postgres").pw_uid; os.chown('/var/lib/postgresql/wal_archive/', uid, -1)
	if var==1 and set('01').issubset(socket.gethostname()): path='/mnt/dbbackup/OCOD/'
	elif var==1 and set('02').issubset(socket.gethostname()): path='/mnt/dbbackup/RCOD/'
	elif var==2 and set('01').issubset(socket.gethostname()): path='/mnt/dbbackup/RCOD/'
	elif var==2 and set('02').issubset(socket.gethostname()): path='/mnt/dbbackup/OCOD/'
	if os.path.exists(path + 'temp/' + 'base.tar.gz'): os.remove(path + 'temp/' + 'base.tar.gz')
	IP=['s39bd1iz01.ac.com', 's39bd1iz02.ac.com', 's39bd2iz01.ac.com', 's39bd2iz02.ac.com', 's39crsvn01.vp.com', 's39crsvn02.vp.com', 's39crsin01.in.com', 's39ccrsin02.in.com']
        a=socket.gethostname()
        m=0
	statcor=os.system('systemctl status corosync')
	statpace=os.system('systemctl status pacemaker')
	for i in IP:
		m=1
		if i==a:
			if statcor==0 and statpace==0:
                                if var==1:
					start_time = time.time()
					exit_code = os.system('sudo su - postgres -c "pg_basebackup -D /mnt/dbbackup/OCOD/temp -Ft -z -Z 9 -P --xlog"')
                                        if exit_code==0:
                                            os.system('echo $(date +"%Y%m%d-%H%M%S")     PostgreSQL Database Backup Successful >> /var/log/backupdb.log')
                                        else:
                                            os.system('echo $(date +"%Y%m%d-%H%M%S")     PostgreSQL Database Backup Unsuccessful >> /var/log/backupdb.log')
                                        TIME='-' + str(round(((time.time() - start_time)/60)+30)).split('.')[0]                                	
					if not (statcor==0 and statpace==0):
                                        	os.system('echo $(date +"%Y%m%d-%H%M%S") PostgreSQL DB is not running >> /var/log/backupdb.log')
                                        #Deleting an incorrectly created backup due to the disabling of corosync and pacemaker services during the creation of the backup
                                        	os.remove(path + 'base.tar.gz')
						os.system('echo $(date +"%Y%m%d-%H%M%S")     An incorrectly created backup copy of the database has been deleted $( if [[ ($var = 1) && $(hostname | grep 01) ]]; then echo OCOD; elif [[ ($var = 1) && $(hostname | grep 02) ]]; then echo RCOD; elif [[ ($var = 2) && $(hostname | grep 01) ]]; then echo OCOD; elif [[ ($var = 2) && $(hostname | grep 02) ]]; then echo RCOD; fi) >> /var/log/backupdb.log')
                                        #Program termination due to disconnection of corosync and pacemaker services during backup creation
                                        	exit()
                                        else:
                                                pipe=os.popen('echo $(uname -n)-$(date +"%Y%m%d-%H%M%S").tar.gz')
                                                bdarch=pipe.read()
                                                bdarch=bdarch.replace("\n","")
                                                os.rename(path + 'temp/' + 'base.tar.gz', path + 'temp/' + bdarch)
                                                os.rename(path + 'temp/' + bdarch, path + bdarch)
                                                os.system('sleep 1m')
                                                shutil.rmtree('/tmp/wal', ignore_errors=True)
                                                os.mkdir('/tmp/wal')
                                                subprocess.call(["find", "/var/lib/postgresql/9.6/main/pg_xlog/", "-maxdepth", "1", "-mmin", TIME, "-type", "f", "-exec", "cp", "-pr", "{}", "/tmp/wal", ";"])
                                                return bdarch
				else:
					start_time = time.time()
                                        exit_code = os.system('sudo su - postgres -c "pg_basebackup -D /mnt/dbbackup/RCOD/temp -Ft -z -Z 9 -P --xlog"')
                                        if exit_code==0:
                                            os.system('echo $(date +"%Y%m%d-%H%M%S")     PostgreSQL Database Backup Successful >> /var/log/backupdb.log')
                                        else:
                                            os.system('echo $(date +"%Y%m%d-%H%M%S")     PostgreSQL Database Backup Unsuccessful >> /var/log/backupdb.log')
                                        TIME='-' + str(round(((time.time() - start_time)/60)+30)).split('.')[0]
                                        if not (statcor==0 and statpace==0):
                                                os.system('echo $(date +"%Y%m%d-%H%M%S") PostgreSQL DB is not running >> /var/log/backupdb.log')
                                        #Deleting an incorrectly created backup due to the disabling of corosync and pacemaker services during the creation of the backup
                                                os.remove(path + 'base.tar.gz')
                                                os.system('echo $(date +"%Y%m%d-%H%M%S")     An incorrectly created backup copy of the database has been deleted $( if [[ ($var = 1) && $(hostname | grep 01) ]]; then echo OCOD; elif [[ ($var = 1) && $(hostname | grep 02) ]]; then echo RCOD; elif [[ ($var = 2) && $(hostname | grep 01) ]]; then echo OCOD; elif [[ ($var = 2) && $(hostname | grep 02) ]]; then echo RCOD; fi) >> /var/log/backupdb.log')
                                        #Program termination due to disconnection of corosync and pacemaker services during backup creation
                                                exit()
                                        else:
                                                pipe=os.popen('echo $(uname -n)-$(date +"%Y%m%d-%H%M%S").tar.gz')
                                                bdarch=pipe.read()
                                                bdarch=bdarch.replace("\n","")
                                                os.rename(path + 'temp/' + 'base.tar.gz', path + 'temp/' + bdarch)
                                                os.rename(path + 'temp/' + bdarch, path + bdarch)
                                                os.system('sleep 1m')
                                                shutil.rmtree('/tmp/wal', ignore_errors=True)
                                                os.mkdir('/tmp/wal')
                                                subprocess.call(["find", "/var/lib/postgresql/9.6/main/pg_xlog/", "-maxdepth", "1", "-mmin", TIME, "-type", "f", "-exec", "cp", "-pr", "{}", "/tmp/wal", ";"])
                                                return bdarch
			elif not (statcor==0 and statpace==0):
                                os.system('echo $(date +"%Y%m%d-%H%M%S") PostgreSQL DB is not running >> /var/log/backupdb.log')
                                #Program termination due to inoperability of corosync and pacemaker services
                                exit()
	postgre=os.system('systemctl status postgresql')
	if postgre==0:
		if var==1:
			start_time = time.time()
                	exit_code = os.system('sudo su - postgres -c "pg_basebackup -D /mnt/dbbackup/OCOD/temp -Ft -z -Z 9 -P --xlog"')
                        if exit_code==0:
                            os.system('echo $(date +"%Y%m%d-%H%M%S")     PostgreSQL Database Backup Successful >> /var/log/backupdb.log')
                        else:
                            os.system('echo $(date +"%Y%m%d-%H%M%S")     PostgreSQL Database Backup Unsuccessful >> /var/log/backupdb.log')                	
                        TIME='-' + str(round(((time.time() - start_time)/60)+30)).split('.')[0]
                	if not postgre==0:
                		os.system('echo $(date +"%Y%m%d-%H%M%S") PostgreSQL DB is not running >> /var/log/backupdb.log')
                   		#Deleting an incorrectly created backup due to the disabling of corosync and pacemaker services during the creation of the backup
                        	os.remove(path + 'base.tar.gz')
                        	os.system('echo $(date +"%Y%m%d-%H%M%S")     An incorrectly created backup copy of the database has been deleted $( if [[ ($var = 1) && $(hostname | grep 01) ]]; then echo OCOD; elif [[ ($var = 1) && $(hostname | grep 02) ]]; then echo RCOD; elif [[ ($var = 2) && $(hostname | grep 01) ]]; then echo OCOD; elif [[ ($var = 2) && $(hostname | grep 02) ]]; then echo RCOD; fi) >> /var/log/backupdb.log')
                        	#Program termination due to disconnection of corosync and pacemaker services during backup creation
                        	exit()
                	elif socket.gethostname().find('zbx') < 0:
                		pipe=os.popen('echo $(uname -n)-$(date +"%Y%m%d-%H%M%S").tar.gz')
                        	bdarch=pipe.read()
                        	bdarch=bdarch.replace("\n","")
                        	os.rename(path + 'temp/' + 'base.tar.gz', path + 'temp/' + bdarch)
                                os.rename(path + 'temp/' + bdarch, path + bdarch)
                        	os.system('sleep 1m')
                        	shutil.rmtree('/tmp/wal', ignore_errors=True)
                        	os.mkdir('/tmp/wal')
                        	subprocess.call(["find", "/var/lib/postgresql/9.6/main/pg_xlog/", "-maxdepth", "1", "-mmin", TIME, "-type", "f", "-exec", "cp", "-pr", "{}", "/tmp/wal", ";"])
                        	return bdarch
        	else:
        		start_time = time.time()
                	exit_code = os.system('sudo su - postgres -c "pg_basebackup -D /mnt/dbbackup/RCOD/temp -Ft -z -Z 9 -P --xlog"')
                        if exit_code==0:
                            os.system('echo $(date +"%Y%m%d-%H%M%S")     PostgreSQL Database Backup Successful >> /var/log/backupdb.log')
                        else:
                            os.system('echo $(date +"%Y%m%d-%H%M%S")     PostgreSQL Database Backup Unsuccessful >> /var/log/backupdb.log')
                	TIME='-' + str(round(((time.time() - start_time)/60)+30)).split('.')[0]
                	if not postgre==0:
                		os.system('echo $(date +"%Y%m%d-%H%M%S") PostgreSQL DB is not running >> /var/log/backupdb.log')
                        	#Deleting an incorrectly created backup due to the disabling of corosync and pacemaker services during the creation of the backup
                        	os.remove(path + 'base.tar.gz')
                        	os.system('echo $(date +"%Y%m%d-%H%M%S")     An incorrectly created backup copy of the database has been deleted $( if [[ ($var = 1) && $(hostname | grep 01) ]]; then echo OCOD; elif [[ ($var = 1) && $(hostname | grep 02) ]]; then echo RCOD; elif [[ ($var = 2) && $(hostname | grep 01) ]]; then echo OCOD; elif [[ ($var = 2) && $(hostname | grep 02) ]]; then echo RCOD; fi) >> /var/log/backupdb.log')
                        	#Program termination due to disconnection of corosync and pacemaker services during backup creation
                        	exit()
                	elif socket.gethostname().find('zbx') < 0:
				pipe=os.popen('echo $(uname -n)-$(date +"%Y%m%d-%H%M%S").tar.gz')
                        	bdarch=pipe.read()
                        	bdarch=bdarch.replace("\n","")
                        	os.rename(path + 'temp/' + 'base.tar.gz', path + 'temp/' + bdarch)
                                os.rename(path + 'temp/' + bdarch, path + bdarch)
                        	os.system('sleep 1m')
                       		shutil.rmtree('/tmp/wal', ignore_errors=True)
                        	os.mkdir('/tmp/wal')
                        	subprocess.call(["find", "/var/lib/postgresql/9.6/main/pg_xlog/", "-maxdepth", "1", "-mmin", TIME, "-type", "f", "-exec", "cp", "-pr", "{}", "/tmp/wal", ";"])
                        	return bdarch
	elif not postgres==0:
                                os.system('echo $(date +"%Y%m%d-%H%M%S") PostgreSQL DB is not running >> /var/log/backupdb.log')
                                #Program termination due to inoperability of corosync and pacemaker services
                                exit()
def sync(a1, a2):
	if a1==0:
		var1='/mnt/dbbackup/OCOD/'
                var2='/mnt/dbbackup/RCOD/'
		if a2==0:
			ls = subprocess.Popen(("ls", "-rI", "wal*", var2), stdout=subprocess.PIPE); a = subprocess.check_output(('grep', 'tar.gz'), stdin=ls.stdout); ls.wait()
			a=a.split("\n")
			for i in a: 
				if i==a[len(a)-1]: a.remove(i)
			ls = subprocess.Popen(("ls", "-rI", "wal*", var1), stdout=subprocess.PIPE); b = subprocess.check_output(('grep', 'tar.gz'), stdin=ls.stdout); ls.wait() 
			b=b.split("\n")
                        for i in b:
                                if i==b[len(b)-1]: b.remove(i)
			ls = subprocess.Popen(("ls", "-rI", "wal*", var1), stdout=subprocess.PIPE); output = subprocess.check_output(('grep', 'tar.gz'), stdin=ls.stdout); ls.wait(); c=len(output.splitlines())
			ls = subprocess.Popen(("ls", "-rI", "wal*", var2), stdout=subprocess.PIPE); output = subprocess.check_output(('grep', 'tar.gz'), stdin=ls.stdout); ls.wait(); d=len(output.splitlines())
                else:
			ls = subprocess.Popen(("ls", "-t", var2), stdout=subprocess.PIPE); a = subprocess.check_output(('grep', 'wal'), stdin=ls.stdout); ls.wait()
			a=a.split("\n")
                        for i in a:
                                if i==a[len(a)-1]: a.remove(i)
			ls = subprocess.Popen(("ls", "-t", var1), stdout=subprocess.PIPE); b = subprocess.check_output(('grep', 'wal'), stdin=ls.stdout); ls.wait()
			b=b.split("\n")
                        for i in b:
                                if i==b[len(b)-1]: b.remove(i)
			ls = subprocess.Popen(("ls", "-t", var1), stdout=subprocess.PIPE); output = subprocess.check_output(('grep', 'wal'), stdin=ls.stdout); ls.wait(); c=len(output.splitlines())
			ls = subprocess.Popen(("ls", "-t", var2), stdout=subprocess.PIPE); output = subprocess.check_output(('grep', 'wal'), stdin=ls.stdout); ls.wait(); d=len(output.splitlines())
        else:
                var1='/mnt/dbbackup/RCOD/'
                var2='/mnt/dbbackup/OCOD/'
                if a2==0:
                        ls = subprocess.Popen(("ls", "-rI", "wal*", var2), stdout=subprocess.PIPE); a = subprocess.check_output(('grep', 'tar.gz'), stdin=ls.stdout); ls.wait()
			a=a.split("\n")
                        for i in a:
                                if i==a[len(a)-1]: a.remove(i)
			ls = subprocess.Popen(("ls", "-rI", "wal*", var1), stdout=subprocess.PIPE); b = subprocess.check_output(('grep', 'tar.gz'), stdin=ls.stdout); ls.wait() 
			b=b.split("\n")
                        for i in b:
                                if i==b[len(b)-1]: b.remove(i)
			ls = subprocess.Popen(("ls", "-rI", "wal*", var1), stdout=subprocess.PIPE); output = subprocess.check_output(('grep', 'tar.gz'), stdin=ls.stdout); ls.wait(); c=len(output.splitlines())
			ls = subprocess.Popen(("ls", "-rI", "wal*", var2), stdout=subprocess.PIPE); output = subprocess.check_output(('grep', 'tar.gz'), stdin=ls.stdout); ls.wait(); d=len(output.splitlines())
                else:
			ls = subprocess.Popen(("ls", "-t", var2), stdout=subprocess.PIPE); a = subprocess.check_output(('grep', 'wal'), stdin=ls.stdout); ls.wait()
			a=a.split("\n")
                        for i in a:
                                if i==a[len(a)-1]: a.remove(i)
			ls = subprocess.Popen(("ls", "-t", var1), stdout=subprocess.PIPE); b = subprocess.check_output(('grep', 'wal'), stdin=ls.stdout); ls.wait()
			b=b.split("\n")
                        for i in b:
                                if i==b[len(b)-1]: b.remove(i)
			ls = subprocess.Popen(("ls", "-t", var1), stdout=subprocess.PIPE); output = subprocess.check_output(('grep', 'wal'), stdin=ls.stdout); ls.wait(); c=len(output.splitlines())
			ls = subprocess.Popen(("ls", "-t", var2), stdout=subprocess.PIPE); output = subprocess.check_output(('grep', 'wal'), stdin=ls.stdout); ls.wait(); d=len(output.splitlines())
	if c==0:
		for j in a: subprocess.call(['cp', var2+j, var1])
        for j in a:
		e=0
                for k in b:
			if not j == k:
				e += 1
                                if e < len(b): 
					continue
                                elif e==len(b):
					exit_code = subprocess.call(['cp', var2+j, var1])
					if exit_code==0: 
						os.system('echo $(date +"%Y%m%d-%H%M%S")     Synchronization of archive $(echo $j) of the backup copy of the DB PostgreSQL RCOD and OCOD Successfully >> /var/log/backupdb.log')
					else:
						os.system('echo $(date +"%Y%m%d-%H%M%S")     Synchronization of archive $(echo $j) of the backup copy of the DB PostgreSQL RCOD and OCOD Unsuccessfully >> /var/log/backupdb.log')	
			else:
				exit_code = subprocess.call(['diff', var2+j, var1+k])
				if not exit_code==0:
                                	if len(b)==1: break
                                        b.remove(k)
                                	break
                                else:
					exit_code = subprocess.call(['cp', var2+j, var1])
					if exit_code==0:
                                                os.system('echo $(date +"%Y%m%d-%H%M%S")     Synchronization of archive $(echo $j) of the backup copy of the DB PostgreSQL RCOD and OCOD Successfully >> /var/log/backupdb.log')
                                        else:
                                                os.system('echo $(date +"%Y%m%d-%H%M%S")     Synchronization of archive $(echo $j) of the backup copy of the DB PostgreSQL RCOD and OCOD Unsuccessfully >> /var/log/backupdb.log')
					if len(b)==1: break
                                        b.remove(k)
                                        break
	if a1==1:
		if a2==0:
			ls = subprocess.Popen(("ls", "-rI", "wal*", var1), stdout=subprocess.PIPE); b = subprocess.check_output(('grep', 'tar.gz'), stdin=ls.stdout); ls.wait()
			b=b.split("\n")
                        for i in b:
                               	if i==b[len(b)-1]: b.remove(i)
			ls = subprocess.Popen(("ls", "-I", "wal*", var1), stdout=subprocess.PIPE); output = subprocess.check_output(('grep', 'tar.gz'), stdin=ls.stdout); ls.wait(); c=len(output.splitlines())
		else:
			ls = subprocess.Popen(("ls", "-t", var1), stdout=subprocess.PIPE); b = subprocess.check_output(('grep', 'wal'), stdin=ls.stdout); ls.wait()
			b=b.split("\n")
                        for i in b:
                                if i==b[len(b)-1]: b.remove(i)
			ls = subprocess.Popen(("ls", "-t", var1), stdout=subprocess.PIPE); output = subprocess.check_output(('grep', 'wal'), stdin=ls.stdout); ls.wait(); c=len(output.splitlines())
        else:
		if a2==0:
                        ls = subprocess.Popen(("ls", "-rI", "wal*", var1), stdout=subprocess.PIPE); b = subprocess.check_output(('grep', 'tar.gz'), stdin=ls.stdout); ls.wait()
                        b=b.split("\n")
                        for i in b:
                                if i==b[len(b)-1]: b.remove(i)
                        ls = subprocess.Popen(("ls", "-I", "wal*", var1), stdout=subprocess.PIPE); output = subprocess.check_output(('grep', 'tar.gz'), stdin=ls.stdout); ls.wait(); c=len(output.splitlines())
                else:
                        ls = subprocess.Popen(("ls", "-t", var1), stdout=subprocess.PIPE); b = subprocess.check_output(('grep', 'wal'), stdin=ls.stdout); ls.wait()
                        b=b.split("\n")
                        for i in b:
                                if i==b[len(b)-1]: b.remove(i)
                        ls = subprocess.Popen(("ls", "-t", var1), stdout=subprocess.PIPE); output = subprocess.check_output(('grep', 'wal'), stdin=ls.stdout); ls.wait(); c=len(output.splitlines())
	if c > d:
		for j in b:
			e=0
			for k in a:
				if not j==k:
					e += 1
					if e < d:
						continue
					elif e==d:
						exit_code = subprocess.call(['cp', var1+j, var2])
						if exit_code==0:
							os.system('echo $(date +"%Y%m%d-%H%M%S")     Synchronization of archive $(echo $j) of the backup copy of the DB PostgreSQL RCOD and OCOD Successfully >> /var/log/backupdb.log')
						else:
							os.system('echo $(date +"%Y%m%d-%H%M%S")     Synchronization of archive $(echo $j) of the backup copy of the DB PostgreSQL RCOD and OCOD Unsuccessfully >> /var/log/backupdb.log')
						break
def search():
	ls = subprocess.Popen(("ls", "-I", "wal*", "/mnt/dbbackup/RCOD/"), stdout=subprocess.PIPE); a = subprocess.check_output(('grep', 'tar.gz'), stdin=ls.stdout); ls.wait(); a=len(a.splitlines())
	ls = subprocess.Popen(("ls", "-I", "wal*", "/mnt/dbbackup/OCOD/"), stdout=subprocess.PIPE); b = subprocess.check_output(('grep', 'tar.gz'), stdin=ls.stdout); ls.wait(); b=len(b.splitlines())
	ls = subprocess.Popen(("ls", "/mnt/dbbackup/RCOD/"), stdout=subprocess.PIPE); c = subprocess.check_output(('grep', 'wal'), stdin=ls.stdout); ls.wait(); c=len(c.splitlines())
        ls = subprocess.Popen(("ls", "/mnt/dbbackup/OCOD/"), stdout=subprocess.PIPE); d = subprocess.check_output(('grep', 'wal'), stdin=ls.stdout); ls.wait(); d=len(d.splitlines())
	for i in range(2):
		if i==1 and set('zbx').issubset(socket.gethostname()): break
                if i==0:
                        if a==b: 
				continue
                        elif a>b:
                                sync(0,0)
                                continue
                        elif a<b:
                                sync(1,0)
                                continue
                        fi
                elif i==1:
                        if c==d:
                                break
                        elif c>d:
                                sync(0,1)
                        elif c<d:
                                sync(1,1)
def mounts(g):
	try:
        	ls = subprocess.Popen(("mount"), stdout=subprocess.PIPE); mount = subprocess.check_output(("grep", g), stdin=ls.stdout); ls.wait(); n=5
        except subprocess.CalledProcessError, e:
        	n=1
	return n
var=0
my_array=massive()
for g in my_array:
        var += 1
        #Checking the availability of hypervisor servers with ICMP backup storages
	mount = subprocess.Popen(("ping", "-c4", g), stdout=subprocess.PIPE); exit_code = subprocess.check_output(("sed", "-n", '1,/^---/d;s/%.*//;s/.*, //g;p;q'), stdin=mount.stdout); mount.wait()
        if int(exit_code.replace("\n","")) == 100:
                if var==1:
                        os.system('echo $(date +"%Y%m%d-%H%M%S")     Server with storage $(if [[ $(hostname | grep 01) ]]; then echo OCOD; elif [[ $(hostname | grep 02) ]]; then echo RCOD; fi) is not available       >> /var/log/backupdb.log')
                        continue
                else:
                        os.system('echo $(date +"%Y%m%d-%H%M%S")     Server with storage $(if [[ $(hostname | grep 01) ]]; then echo OCOD; elif [[ $(hostname | grep 02) ]]; then echo RCOD; fi) is not available       >> /var/log/backupdb.log')
                        break
        else:
                os.system('echo $(date +"%Y%m%d-%H%M%S")   $( if [[ ($var = 1) && $(hostname | grep 01) ]]; then echo Server with storage of OCOD is available; elif [[ ($var = 1) && $(hostname | grep 02) ]]; then echo Server with storage of RCOD is available; elif [[ ($var = 2) && $(hostname | grep 01) ]]; then echo Server with storage of OCOD is available; elif [[ ($var = 2) && $(hostname | grep 02) ]]; then echo Server with storage of RCOD is available; fi)      >> /var/log/backupdb.log')
                if var==1:
                        #Mounting storages on a server with a database, if not mounted
                        #Checking the ability to write to storages mounted on a server with a database
                        exit_code = subprocess.call(["touch", dir1+'test'])
			if mounts(g)==1:
                                os.system('mount -a')
                                if mounts(g)==1:
                                        os.system('echo $(date +"%Y%m%d-%H%M%S")   Problems with the operation of the smbd service on the server with the repository of $(if [[ $(hostname | grep 01) ]]; then echo OCOD; elif [[ $(hostname | grep 02) ]]; then echo RCOD; fi) >> /var/log/backupdb.log')
                                        continue
                                else:
                                        os.system('echo $(date +"%y%m%d-%h%m%s")   PostgreSQL database backup storage is $(if [[ $(hostname | grep 01) ]]; then echo OCOD; elif [[ $(hostname | grep 02) ]]; then echo RCDO; fi) mounted successfully   >> /var/log/backupdb.log')
                                        bdarch=backup(1)
                        elif exit_code != 0:
                                os.system('echo $(date +"%Y%m%d-%H%M%S")   Problems with the operation of the smbd service on the server with the repository of $(if [[ $(hostname | grep 01) ]]; then echo OCOD; elif [[ $(hostname | grep 02) ]]; then echo RCOD; fi) >> /var/log/backupdb.log')
                                continue
                        elif exit_code == 0:
                                bdarch=backup(1)
	 	if var==2:
                        #Mounting storages on a server with a database, if not mounted
                        #Checking the ability to write to storages mounted on a server with a database
                        exit_code = subprocess.call(["touch", dir2+'test'])
                        ls = subprocess.Popen(("mount"), stdout=subprocess.PIPE); mount = subprocess.check_output(("grep", g), stdin=ls.stdout); ls.wait();
			if mounts(g)==1:
                                os.system('mount -a')
                                if mounts(g)==1:
                                        os.system('echo $(date +"%Y%m%d-%H%M%S")   Problems with the operation of the smbd service on the server with the repository of $(if [[ $(hostname | grep 01) ]]; then echo RCOD; elif [[ $(hostname | grep 02) ]]; then echo OCOD; fi) >> /var/log/backupdb.log')
                                        exit()
                                elif 'bdarch' in locals() and os.path.exists(dir1+bdarch)==1:
                                        #Replication (copying of the created backup) to the backup storage
                                        exit_code = subprocess.call(['cp', dir1+bdarch, dir2])
					if exit_code==0:
						os.system('echo $(date +"%Y%m%d-%H%M%S")        Replicating a PostgreSQL database backup to another data center storage Successfully         >> /var/log/backupdb.log')
                                        else:
						os.system('echo $(date +"%Y%m%d-%H%M%S")        Replicating a PostgreSQL database backup to another data center storage Unsuccessfully       >> /var/log/backupdb.log')
					if set('zbx').issubset(socket.gethostname())==0: subprocess.call(['cp', dir1+'wal_'+bdarch, dir2])
                                        search()
                                        break
                                else:
                                    os.system('echo $(date +"%y%m%d-%h%m%s")   PostgreSQL database backup storage is $(if [[ $(hostname | grep 01) ]]; then echo RCOD; elif [[ $(hostname | grep 02) ]]; then echo OCOD; fi) mounted successfully   >> /var/log/backupdb.log')
                                        #Creating a backup copy in the backup storage, since there is no copy in the main storage
                                    backup(2)
                        elif exit_code != 0:
                                #Creating a backup copy to the backup storage because the main storage is unavailable
                                exit()
                        elif 'bdarch' in locals() and os.path.exists(dir1+bdarch)==1:
                                        #Replication (copying of the created backup) to the backup storage
				exit_code = subprocess.call(['cp', dir1+bdarch, dir2])
				if exit_code==0:
			        	os.system('echo $(date +"%Y%m%d-%H%M%S")        Replicating a PostgreSQL database backup to another data center storage Successfully         >> /var/log/backupdb.log')
                            	else:
					os.system('echo $(date +"%Y%m%d-%H%M%S")        Replicating a PostgreSQL database backup to another data center storage Unsuccessfully       >> /var/log/backupdb.log')
				if set('zbx').issubset(socket.gethostname())==0: subprocess.call(['cp', dir1+'wal_'+bdarch, dir2])
                                search()
                                break
                        else:
                             #Creating a backup copy in the backup storage, since there is no copy in the main storage
                             backup(2)
