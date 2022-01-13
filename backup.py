#!/usr/bin/python

'''
BD clusters:
    	s39bd1iz01.ac.com
        s39bd1iz02.ac.com
        s39bd2iz01.ac.com
        s39bd2iz02.ac.com
        and
        s39crsvn01.vp.com
        s39crsvn02.vp.com
        and
        s39crsin01.in.com
        s39crsin02.in.com
'''	
#massive - selection of an array of hypervisor IP addresses depending on the contour
#backup - backup to the mounted spheres of the OCOD and RCOD
#sync - synchronization of the contents of the mounted ball of the OCOD and RCOD
#search - checking 'sync' trigger conditions
#mounts - checking if the ball is mounted

import os
import shutil
import socket
import pwd
import grp
import subprocess
from datetime import datetime

def logs():
	#Creating a log file for long-term storage of script events
	open("/var/log/debugdb.log", "w+")
	#If the size of 1 GB is exceeded, the debug.log is deleted and recreated
	if not os.path.getsize('/var/log/debugdb.log')/(1024*1024*1024)==0: os.remove('/var/log/debugdb.log')
	shutil.copyfile("/var/log/backupdb.log", "/var/log/debugdb.log") 
	#Creating a log file to store the events of one script launch
	os.remove('/var/log/backupdb.log'); open("/var/log/backupdb.log", "w+")
def massive(IP=[]):
	if socket.gethostname().find('01') >= 0:
        	IPIZ = ['10.111.15.54', '10.111.15.63']
                IPVN = ['10.111.16.54', '10.111.16.63']
                IPIN = ['10.111.17.54', '10.111.17.63']
        else:
        	IPIZ = ['10.111.15.63', '10.111.15.54']
                IPVN = ['10.111.16.63', '10.111.16.54']
                IPIN = ['10.111.17.63', '10.111.17.54']	
	if socket.gethostname().find('vp.com') >= 0:
		[IP.insert(0,i) for i in IPVN]
	elif socket.gethostname().find('ac.com') >= 0:
                [IP.insert(0,i) for i in IPIZ]
	else:
		[IP.insert(0,i) for i in IPIN] 
	return IP
def path():
	IP=['s39bd1iz01.ac.com', 's39bd1iz02.ac.com', 's39bd2iz01.ac.com', 's39bd2iz02.ac.com', 's39crsvn01.vp.com', 's39crsvn02.vp.com', 's39crsin01.in.com', 's39ccrsin02.in.com']
	a=socket.gethostname()
	b=len(IP)-1
	t=0
	for i in IP:
		if i==a:
			var1='/mnt/dbbackup/OCOD/' + a
                	var2='/mnt/dbbackup/RCOD/' + a
			t=1
			return var1, var2, t
		elif IP.index(i)!=b:
			continue
		else:
			var1='/mnt/dbbackup/OCOD/'
                	var2='/mnt/dbbackup/RCOD/'
			return var1, var2, t
def checkservice():
	var1, var2, t = path()
	if t==1:
		if os.system('systemctl status corosync') == 0 and os.system('systemctl status pacemaker') == 0:
			return var1, var2, 0
		else:
			with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' corosync and pacemaker services are not running+'\n')
			exit()
	elif os.system('systemctl status postgresql') == 0:
		return var1, var2, 0
	else:
		with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' postgresql service is not running+'\n')
			exit()
def backup():
	var1, var2, t = checkservice()
	path = var1 if socket.gethostname().find('01') >= 0 else var2
	if socket.gethostname().find('zbx')==-1:
		if not os.path.isdir('/var/lib/postgresql/wal_archive/'): os.mkdir('/var/lib/postgresql/wal_archive/'); uid = pwd.getpwnam("postgres").pw_uid; os.chown('/var/lib/postgresql/wal_archive/', uid, -1)
	if os.path.exists(path + '/temp/' + 'base.tar.gz'): os.remove(path + '/temp/' + 'base.tar.gz')
	if t==0:
		start_time = time.time()
		process=subprocess.Popen(["pg_basebackup", "-D", path + '/temp/', "-Ft", "-z", "-Z", "9", "-P", "--xlog"],stdout=subprocess.PIPE, stderr=subprocess.STDOUT, preexec_fn=os.setuid(116)).wait();
                if process==0:
			with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' PostgreSQL Database Backup Successful'+'\n')
                else:
                       	with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' PostgreSQL Database Backup Unsuccessful'+'\n')
			return 1
                TIME='-' + str(round(((time.time() - start_time)/60)+30)).split('.')[0]                                	
		if t != 0:
			with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' PostgreSQL DB is not running'+'\n')
                        #Deleting an incorrectly created backup due to the disabling during the creation of the backup
                        os.remove(path + '/temp/' + 'base.tar.gz')
			test='OCOD' if socket.gethostname().find('01') >= 0 else 'RCOD'
			with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' An incorrectly created backup copy of the database has been deleted'+test+'\n')
                        #Program termination due to disconnection during backup creation
                        exit()
                elif socket.gethostname().find('zbx')==-1:
			b=subprocess.Popen('echo $(uname -n)-$(date +"%Y%m%d-%H%M%S").tar.gz', shell=True, stdout=subprocess.PIPE); bdarch = subprocess.check_output(('xargs', 'echo'),stdin=b.stdout).split("\n")[0]; b.wait() 
                        os.rename(path + '/temp/' + 'base.tar.gz', path + '/temp/' + bdarch)
                        os.rename(path + '/temp/' + bdarch, path + bdarch)
                        os.system('sleep 15m')
                        shutil.rmtree('/tmp/wal', ignore_errors=True)
                        os.mkdir('/tmp/wal')
			subprocess.call(["find", "/var/lib/postgresql/wal_archive/", "-maxdepth", "1", "-mmin", TIME, "-type", "f", "-exec", "cp", "-pr", "{}", "/tmp/wal", ";"])
                        subprocess.call(["find", "/var/lib/postgresql/9.6/main/pg_xlog/", "-maxdepth", "1", "-mmin", TIME, "-type", "f", "-exec", "cp", "-pr", "{}", "/tmp/wal", ";"])
                        return bdarch
def sync(var1, var2, a, b, c, d):
	if d==0:
		for i in a:
			subprocess.call(['cp', var1+i, var2])
			exit()
        for j in a:
		e=len(c)-1
                for k in b:
			if j != k:
                                if e < d.index(k): 
					continue
                                elif e == d.index(k):
					exit_code = subprocess.call(['cp', var1+j, var2])
					if exit_code == 0: 
						with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Synchronization of archive '+j+' of the backup copy of the DB PostgreSQL RCOD and OCOD Successfully'+'\n')
					else:
						with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Synchronization of archive '+j+' of the backup copy of the DB PostgreSQL RCOD and OCOD Unsuccessfully'+'\n')	
			else:
				exit_code = subprocess.call(['diff', var1+j, var2+k])
				if not exit_code==0:
					if os.path.getsize(var1+j) > os.path.getsize(var2+k):
						exit_code = subprocess.call(['cp', var1+j, var2])
					else:
						exit_code = subprocess.call(['cp', var2+k, var1])
                                	if len(d)==1: break
                                        d.remove(k)
                                else:
					if len(d)==1: break
                                        d.remove(k)
def search():
	var1, var2, t = path()
	for i in range(2):
		if i==1 and socket.gethostname().find('zbx') >= 0: break
                if i==0:
			ls = subprocess.Popen(("ls", "-rI", "wal*", var1), stdout=subprocess.PIPE); a = subprocess.check_output(('grep', 'tar.gz'), stdin=ls.stdout); ls.wait(); c=len(a.splitlines())
			ls = subprocess.Popen(("ls", "-rI", "wal*", var2), stdout=subprocess.PIPE); b = subprocess.check_output(('grep', 'tar.gz'), stdin=ls.stdout); ls.wait(); d=len(b.splitlines())
			while c != d:
                        	if c > d:
                                	sync(var1,var2,a,b,c,d)
					
                                	continue
                        	else:
                                	c,d = sync(var2,var1,b,a,d,c)
                                	continue
                elif socket.gethostname().find('zbx') >= 0:
			break
		else:
			ls = subprocess.Popen(("ls", "-t", var1), stdout=subprocess.PIPE); a = subprocess.check_output(('grep', 'wal'), stdin=ls.stdout); ls.wait(); c=len(c.splitlines())
        		ls = subprocess.Popen(("ls", "-t", var2), stdout=subprocess.PIPE); b = subprocess.check_output(('grep', 'wal'), stdin=ls.stdout); ls.wait(); d=len(d.splitlines())
                        while c != d:
                        	if c > d:
                                	c,d = sync(var1,var2,a,b,c,d)
                                	continue
                        	else:
                                	c,d = sync(var2,var1,b,a,d,c)
                                	continue
                        elif c>d:
                                c,d = sync(var1,var2)
                        else:
                                c,d = sync(var2,var1)
def mounts(var, g, path, s, test):
	#Mounting storages on a server with a database, if not mounted
        #Checking the ability to write to storages mounted on a server with a database
	exit_code = subprocess.call(["touch", path+'test'])
	try:
        	ls = subprocess.Popen(("mount"), stdout=subprocess.PIPE); mount = subprocess.check_output(("grep", g), stdin=ls.stdout); ls.wait(); n=5
        except subprocess.CalledProcessError, e:
        	n=1
	if n==1:
		b=subprocess.Popen(["mount", "//"+g+"/bkp"+path, s, "-o", "vers=3.0,credentials=/opt/creds/CredIZ"+test+".txt",rw,file_mode=0666,dir_mode=0777"]).wait();
                if b!=0 and var==1:
				with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Problems with the operation of the smbd service on the server with the repository of'+test+'\n')
                                return 1
		elif b!=0 and var==2:
				with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Problems with the operation of the smbd service on the server with the repository of'+ test +'\n')
                                exit()
                elif b==0 and var==1:
				with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' PostgreSQL database backup storage is'+test+'mounted successfully'+'\n')
				bdarch=backup()
 	else:
		if exit_code != 0 and var==1:
			with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Problems with the operation of the smbd service on the server with the repository of'+test+'\n')
			return 1
		elif exit_code != 0 and var==2:
                	with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Problems with the operation of the smbd service on the server with the repository of'+test+'\n')
                        exit()
                elif exit_code == 0 and var==1:
			bdarch=='1'
                        bdarch=backup()
		elif exit_code == 0 and var==2 and bdarch=='1':
			search()
		elif exit_code == 0 and var==2 and bdarch!='1':	
			bdarch=backup()
def networkavailable(var, g, test):
	#Checking the availability of hypervisor servers with ICMP backup storages
	test='OCOD' if (socket.gethostname().find('01') >= 0 and var==1) or (socket.gethostname().find('02') >= 0 and var==2) else 'RCOD'
	ping = subprocess.Popen(("ping", "-c4", g), stdout=subprocess.PIPE); exit_code = subprocess.check_output(("sed", "-n", '1,/^---/d;s/%.*//;s/.*, //g;p;q'), stdin=ping.stdout); ping.wait()
	if int(exit_code.replace("\n","")) == 100:
                if var==1:
			with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Server with storage'+test+'is not available'+'\n')
                        return 1
                else:
                        with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Server with storage'+test+'is not available'+'\n')
                        exit()
        else:
		with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Server with storage'+test+'is available'+'\n')
		return 0
var=0
my_array=massive()
for g in my_array:
        var += 1
	var1, var2, t = path()
	path = var1 if socket.gethostname().find('01') >= 0 else var2
	test='OCOD' if (socket.gethostname().find('01') >= 0 and var==1) or (socket.gethostname().find('02') >= 0 and var==2) else 'RCOD'
	if networkavailable(var, g, test) == 0:
		if mounts(var, g, path, s, test) == 0:	
			bdarch=backup()
		elif var==1:
			continue
                        elif exit_code != 0 and var==1:
                                with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Problems with the operation of the smbd service on the server with the repository of'+test+'\n')
                                bdarch='1'
				continue
			elif exit_code != 0 and var==2:
                                with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Problems with the operation of the smbd service on the server with the repository of'+test+'\n')
                                exit()
                        elif exit_code == 0 and var==1:
                                bdarch=backup()
			elif exit_code == 0 and var==2 and bdarch=='1':
				bdarch=backup()
			elif exit_code == 0 and var==2 and bdarch!='1':	
	 	if var==2:
                        #Mounting storages on a server with a database, if not mounted
                        #Checking the ability to write to storages mounted on a server with a database
                        exit_code = subprocess.call(["touch", dir2+'test'])
			if mounts(g)==1:
				test='RCOD' if socket.gethostname().find('01') >= 0 else 'OCOD'
                                os.system('mount -a')
                                if mounts(g)==1:
					with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Problems with the operation of the smbd service on the server with the repository of'+ test +'\n')
                                        exit()
                                elif 'bdarch' in locals() and os.path.exists(dir1+bdarch)==1:
                                        #Replication (copying of the created backup) to the backup storage
                                        exit_code = subprocess.call(['cp', dir1+bdarch, dir2])
					if exit_code==0:
						with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Replicating a PostgreSQL database backup to another data center storage Successfully '+'\n')
                                        else:
						with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Replicating a PostgreSQL database backup to another data center storage Unsuccessfully '+'\n')
					if set('zbx').issubset(socket.gethostname())==0: subprocess.call(['cp', dir1+'wal_'+bdarch, dir2])
                                        search()
                                        break
                                else:
					with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' PostgreSQL database backup storage is'+test+'mounted successfully'+'\n')
                                        #Creating a backup copy in the backup storage, since there is no copy in the main storage
                                    backup()
                        elif exit_code != 0:
                                #Creating a backup copy to the backup storage because the main storage is unavailable
                                exit()
                        elif 'bdarch' in locals() and os.path.exists(dir1+bdarch)==1:
                                        #Replication (copying of the created backup) to the backup storage
				exit_code = subprocess.call(['cp', dir1+bdarch, dir2])
				if exit_code==0:
					with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Replicating a PostgreSQL database backup to another data center storage Successfully'+'\n')
                            	else:
					with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Replicating a PostgreSQL database backup to another data center storage Unsuccessfully'+'\n')
				if set('zbx').issubset(socket.gethostname())==0: subprocess.call(['cp', dir1+'wal_'+bdarch, dir2])
                                search()
                                break
                        else:
                             #Creating a backup copy in the backup storage, since there is no copy in the main storage
                             backup()
