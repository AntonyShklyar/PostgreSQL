#!/usr/bin/python

'''
For Python 2.7.13

BD clusters:
    	bd1iz01.ac.com
        bd1iz02.ac.com
        bd2iz01.ac.com
        bd2iz02.ac.com
        and
        crsvn01.vp.com
        crsvn02.vp.com
        and
        crsin01.in.com
        crsin02.in.com

        Data centers:
        01 - OCOD
        02 - RCOD

        Domaines:
        ac.com
        vp.com
        in.com
'''

import os
import shutil
import socket
import pwd
import grp
import subprocess
from datetime import datetime
import time
import tarfile
import os.path
import multiprocessing

def main():
    def logs():
	'''Creating a session log and a log with a description of all sessions'''
	#If the size of 1 GB is exceeded, the debugdb.log is deleted and recreated
	if not os.path.exists('/var/log/backupdb.log'): f=open('/var/log/backupdb.log', "w+"); f.close()
	if not os.path.getsize('/var/log/backupdb.log')/(1024*1024*1024)==0: os.system(r' >/var/log/backupdb.log')
	#The function returns 0
    def massive(IP=[]):
	'''Selection of an array of hypervisor IP addresses depending on the contour'''
	#Determining the main storage (the storage located on the same subnet as the database server)
	if socket.gethostname().find('01') >= 0:
        	IPIZ = ['10.111.15.54', '10.111.15.63']
                IPVN = ['10.111.16.54', '10.111.16.63']
                IPIN = ['10.111.17.54', '10.111.17.63']
        else:
        	IPIZ = ['10.111.15.63', '10.111.15.54']
                IPVN = ['10.111.16.63', '10.111.16.54']
                IPIN = ['10.111.17.63', '10.111.17.54']
	#Determination of the domain in which the database server is located
	if socket.gethostname().find('vp.com') >= 0: [IP.append(i) for i in IPVN]
	elif socket.gethostname().find('ac.com') >= 0: [IP.append(i) for i in IPIZ]
	else: [IP.insert(0,i) for i in IPIN] 
	#The output is a list of IP-addresses of the main and backup storage
	return IP
    def cluster(a):
	'''Determining if a given server belongs to a DB cluster'''
	#List of servers included in the database cluster
	IP=['bd1iz01.ac.com', 'bd1iz02.ac.com', 'bd2iz01.ac.com', 'bd2iz02.ac.com', 'crsvn01.vp.com', 'crsvn02.vp.com', 'crsin01.in.com', 'crsin02.in.com']
	b=len(IP)-1
	t=0
	for i in IP:
		if i==a:
			t=1
			return t
		elif IP.index(i)!=b: continue
		else: return t
	'''
	The returned data type is a number.
	Returning a value indicating whether the server with the database belongs to the servers included in the cluster of database servers:
	1 - belongs;
	0 - does not belong.
	'''
    def paths(t, a):
	'''Determining the backup storage mount point'''
	if t==1 and '01' in a:
	    var1='/mnt/dbbackup/OCOD/' + a + '/'
            var2='/mnt/dbbackup/RCOD/' + a + '/'
        elif t==1 and '02' in a:
            var1='/mnt/dbbackup/RCOD/' + a + '/'
            var2='/mnt/dbbackup/OCOD/' + a + '/'
        elif t==0 and '01' in a:
	    var1='/mnt/dbbackup/OCOD/'
            var2='/mnt/dbbackup/RCOD/'
        elif t==0 and '02' in a:
	    var1='/mnt/dbbackup/RCOD/'
            var2='/mnt/dbbackup/OCOD/'
	return var1, var2
	'''
	The returned data type is a string. 
	The mount points of the primary and backup storages are returned.
	If the database server is not a server in the database cluster, the returned string will not contain the FGDN name of the database server.
	'''
    def checkservice(t):
	'''Checking the status of database services'''
	'''
	If the server with a database is a server included in the list of servers with a database cluster, the check is performed for the corosync and pacemaker services. 
	Otherwise, for postgresql.
	'''
	if t==1:
		if os.system('systemctl status corosync > /dev/null 2>&1') == 0 and os.system('systemctl status pacemaker > /dev/null 2>&1') == 0:
			return 0
		else:
			with open("/var/log/backupdb.log","a+") as stdout: 
                            stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+" corosync and pacemaker services are not running+'\n'")
			exit()
	elif os.system('systemctl status postgresql > /dev/null 2>&1') == 0: return 0
	else:
		with open("/var/log/backupdb.log","a+") as stdout: 
                    stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+" postgresql service is not running+'\n'")
		exit()
	'''
	The returned data type is a number.
	If 0 is returned, services are available.
	Otherwise, the program terminates.
	'''
    def replication(*args):
	'''Copying a backup to the backup storage'''
        exit_code = subprocess.call(['cp', path1+copy, path2])
	if exit_code==0:
	    with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Replicating a PostgreSQL database backup to another data center storage Successfully '+'\n')
	#For a server that has '01' in its name, walfiles are not backed up or copied.
	    if socket.gethostname().find('zbx') < 0: 
	        subprocess.call(['cp', copywal, path2])
        else:
		with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Replicating a PostgreSQL database backup to another data center storage Unsuccessfully '+'\n')
                exit()
	'''
        The returned data type is a number.
        If 0 is returned, services are available.
        Otherwise, the program terminates.
        '''
    def backup(path, t):
	'''Backup to the mounted spheres of the OCOD and RCOD'''
	'''
	Delete a copy that was created incorrectly during the previous operation of the program 
	(reasons for creating an incorrect copy: manual shutdown of the program, reboot/shutdown/freeze of the storage server/database server, problems with network availability)
	'''
	if os.path.exists(path + 'temp/' + 'base.tar.gz'): os.remove(path + 'temp/' + 'base.tar.gz')
	if checkservice(t)==0:
		#Counting the time it takes to complete a backup operation.The execution time is stored in a variable "TIME"
		start_time = time.time()
		id = subprocess.check_output("cat /etc/passwd | grep postgres | awk -F ':' '{print $3}'", shell=True).split("\n")[0]
                process=subprocess.Popen(["pg_basebackup", "-D", path + 'temp/', "-Ft", "-z", "-Z", "9", "-P", "--xlog"],stdout=subprocess.PIPE, stderr=subprocess.STDOUT, preexec_fn=lambda: os.setuid(int(id))).wait()
        	TIME='-' + str(round(((time.time() - start_time)/60)+30)).split('.')[0]
        	if process==0:
                        with open("/var/log/backupdb.log","a+") as stdout: 
                		stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+" PostgreSQL Database Backup Successful "+'\n')
            		b=subprocess.Popen('echo backupdb-$(uname -n)-$(date +"%Y%m%d-%H%M%S").tar.gz', shell=True, stdout=subprocess.PIPE); copy = subprocess.check_output(('xargs', 'echo'),stdin=b.stdout).split("\n")[0]; b.wait() 
            		os.rename(path + 'temp/' + 'base.tar.gz', path + 'temp/' + copy)
            		os.rename(path + 'temp/' + copy, path + '/' + copy)
            		if socket.gethostname().find('zbx') < 0:
                		if not os.path.isdir('/var/lib/postgresql/wal_archive/'): 
                    			os.mkdir('/var/lib/postgresql/wal_archive/') 
                    		uid = pwd.getpwnam("postgres").pw_uid 
                    		os.chown('/var/lib/postgresql/wal_archive/', uid, -1)
                		os.system('sleep 15m')
                		shutil.rmtree('/tmp/wal', ignore_errors=True)
                		os.mkdir('/tmp/wal')
				#Search and collection of WAL-files, created during the time specified in the variable "TIME'
				subprocess.call(["find", "/var/lib/postgresql/wal_archive/", "-maxdepth", "1", "-mmin", TIME, "-type", "f", "-exec", "cp", "-pr", "{}", "/tmp/wal", ";"])
                		subprocess.call(["find", "/var/lib/postgresql/9.6/main/pg_xlog/", "-maxdepth", "1", "-mmin", TIME, "-type", "f", "-exec", "cp", "-pr", "{}", "/tmp/wal", ";"])
                		copywal=path + 'wal_' + copy
                		with tarfile.open(copywal, mode='w:gz') as archive:
    					archive.add('/tmp/wal/', recursive=True)
				return copy, copywal
            	        else:
                	        return copy
        	else:
            		with open("/var/log/backupdb.log","a+") as stdout: 
                		stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+" PostgreSQL Database Backup Unsuccessful "+'\n')
			exit()
	else:
	    with open("/var/log/backupdb.log","a+") as stdout: 
                stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+" PostgreSQL DB is not running "+'\n')
                #Deleting an incorrectly created backup due to the disabling during the creation of the backup
                os.remove(path + 'temp/' + 'base.tar.gz')
		test='OCOD' if socket.gethostname().find('01') >= 0 else 'RCOD'
		with open("/var/log/backupdb.log","a+") as stdout: 
                    stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+" An incorrectly created backup copy of the database has been deleted " + '\n')
                #Program termination due to disconnection during backup creation
                exit()
	'''
	Return data types: number, string, string
	Return data types: number, string, string If successful, the program returns 0, the name of the backup archive, the name of the WAL-files archive.
	Otherwise, the program ends
	'''
    def sync(path1, path2, a, b, c, d):
	'''Synchronization of the contents of the mounted ball of the OCOD and RCOD'''
	#If there is 1 copy in the backup storage, copy all copies from the main storage to the backup.
	if d==0:
		for i in a:
			exit_code=subprocess.call(['cp', path1+i, path2])
                        if exit_code == 0: 
			    with open("/var/log/backupdb.log","a+") as stdout: 
                                stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Synchronization of archive '+i+' of the backup copy of the DB PostgreSQL RCOD and OCOD Successfully'+"\n")
			else:
			    with open("/var/log/backupdb.log","a+") as stdout: 
                                stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Synchronization of archive '+i+' of the backup copy of the DB PostgreSQL RCOD and OCOD Unsuccessfully'+'\n')
                return 0
	#Copying backups from a vault with more copies to a vault with fewer copies
        for j in a:
		e=d-1
                for k in b:
			if j != k:
                                if e > b.index(k):
					continue
                                elif e == b.index(k):
					exit_code = subprocess.call(['cp', path1+j, path2])
					if exit_code == 0: 
						with open("/var/log/backupdb.log","a+") as stdout: 
                                                    stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Synchronization of archive '+j+' of the backup copy of the DB PostgreSQL RCOD and OCOD Successfully'+"\n")
					else:
						with open("/var/log/backupdb.log","a+") as stdout: 
                                                    stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Synchronization of archive '+j+' of the backup copy of the DB PostgreSQL RCOD and OCOD Unsuccessfully'+'\n')	
                                        break
                        else:
                            b.remove(k)
                            d-=1
                            if d==0:
                                for i in a:
			            exit_code=subprocess.call(['cp', path1+i, path2])
                                return 0
                            break
        #The function returns None
    def search(path1, path2, i):
	'''Checking 'sync' trigger conditions'''
	def checkcopy(path1, path2, i):
		'''Obtaining lists of backup archives and WAL-archives, counting the number of backup copies and WAL-archives'''
		if i==0:
			temp1="ls -rI wal* "+path1+" | grep tar.gz | tail -n +2"; a = subprocess.check_output(temp1,shell=True).split("\n"); a.remove(''); c=len(a)
			temp2="ls -rI wal* "+path2+" | grep tar.gz | tail -n +2"; b = subprocess.check_output(temp2,shell=True).split("\n"); b.remove(''); d=len(b)
	    	else:
			temp1="ls -t "+path1+" | grep wal | tail -n +2"; a = subprocess.check_output(temp1,shell=True).split("\n"); a.remove(''); c=len(a)
        		temp2="ls -t "+path2+" | grep wal | tail -n +2"; b = subprocess.check_output(temp2,shell=True).split("\n"); b.remove(''); d=len(b)
		return a, b, c, d
	#The cycle will run until the number of backups and VAL archives in the vaults becomes the same
	while True:
	    '''Definition of storage with more and fewer backups and WAL-archives'''
            a, b, c, d = checkcopy(path1, path2, i)
            if c > d:
                    sync(path1,path2,a,b,c,d)
            elif c < d:
                    path1, path2, a, b, c, d = path2, path1, b, a, d, c
                    sync(path1,path2,a,b,c,d)
            elif c==d and i==0 and socket.gethostname().find('zbx') >= 0:
                exit()
            elif c==d and i==0 and socket.gethostname().find('zbx') < 0:
                i=1
                continue
            elif c==d and i==1 and socket.gethostname().find('zbx') < 0:
                exit()
	#The function returns None
    def mounts(var, g, path, test):
	'''Checking if the ball is mounted'''
	#Mounting storages on a server with a database, if not mounted
        #Checking the ability to write to storages mounted on a server with a database
        try:
            ls = subprocess.Popen(("mount"), stdout=subprocess.PIPE); mount = subprocess.check_output(("grep", g), stdin=ls.stdout); ls.wait(); n=5
        except subprocess.CalledProcessError, e:
            n=1
	if n==1:
		b=subprocess.Popen(["mount", "//"+g+"/bkp"+path.replace('/mnt', ''), path, "-o", "vers=3.0,credentials=/opt/creds/CredIZ"+test+".txt,rw,file_mode=0666,dir_mode=0777"]).wait();
                if b!=0 and var==1:
				with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Problems with the operation of the smbd service on the server with the repository of'+test+'\n')
                                return 1
		elif b!=0 and var==2:
				with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Problems with the operation of the smbd service on the server with the repository of'+ test +'\n')
                                exit()
                elif b==0 and var==1:
				with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' PostgreSQL database backup storage is'+test+'mounted successfully'+'\n')
				return 0
		elif b==0 and var==2:
				with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' PostgreSQL database backup storage is'+test+'mounted successfully'+'\n')
				return 0
 	else:
		exit_code = subprocess.call(["touch", path+'test'])
		if exit_code != 0 and var==1:
			with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Problems with the operation of the smbd service on the server with the repository of'+test+'\n')
			return 1
		elif exit_code != 0 and var==2:
                	with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Problems with the operation of the smbd service on the server with the repository of'+test+'\n')
                        exit()
                elif exit_code == 0 and var==1: return 0
		elif exit_code == 0 and var==2: return 0
	'''
	Return data type - number
	If the function returns 0, the storage was mounted successfully
	If the function returns 1, the storage was mounted unsuccessfully
	If all storages are mounted unsuccessfully, the program will close
	'''
    def networkavailable(var, g, test):
	'''Determining the network availability of storage'''
	#Checking the availability of hypervisor servers with ICMP backup storages
	test='OCOD' if (socket.gethostname().find('01') >= 0 and var==1) or (socket.gethostname().find('02') >= 0 and var==2) else 'RCOD'
	ping = subprocess.Popen(("ping", "-c4", g), stdout=subprocess.PIPE); exit_code = subprocess.check_output(("sed", "-n", '1,/^---/d;s/%.*//;s/.*, //g;p;q'), stdin=ping.stdout); ping.wait()
	if int(exit_code.replace("\n","")) == 100:
                if var==1:
			with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Server with storage '+test+' is not available'+'\n')
                        return 1
                else:
                        with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Server with storage '+test+' is not available'+'\n')
                        exit()
        else:
		with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Server with storage '+test+' is available'+'\n')
		return 0
	'''
	Return data type - number
	If the function returns 0 - the server with the backup storage is available
	If the function returns 1 - the server with the backup storage is unavailable
	If all servers with a backup storage are unavailable, the program will close
	'''
    def shareavailable(path1, path2):
	'''Checking network storage availability'''
        var=0
        my_array=massive()
        result=0
        for g in my_array:
            var += 1
	    path=path1 if var==1 else path2
	    test='OCOD' if (socket.gethostname().find('01') >= 0 and var==1) or (socket.gethostname().find('02') >= 0 and var==2) else 'RCOD'
	    if networkavailable(var, g, test) == 0:
		mount=mounts(var, g, path, test)
		if mount == 0 and var==1:
                    result=1
                    continue
                elif mount != 0 and var==1: continue	
		elif mount == 0 and var==2 and result==1:
                    path=path1
                    return 2, path
                elif mount == 0 and var == 2 and result == 0:
                    return 1, path
                elif mount != 0 and var==2 and result == 1: 
                    return 0, path
                elif mount != 0 and var==2:
                    exit()
            elif var==1:
                continur
            else:
                exit()
	'''
	Return data types - number, string
	If function returns 0 and path - primary data center NAS unavailable, backup data center NAS is available
	If function returns 1 and path - primary data center NAS is available, backup data center NAS unavailable
	If function returns 2 and path - primary data center NAS is available, backup data center NAS is available
	If all servers with a backup storage are unavailable or all data centers NAS unavailable, the program will close
	'''
    a=socket.gethostname()
    t=cluster(a)
    logs()
    path1, path2 = paths(t, a)
    share, path=shareavailable(path1, path2)
    if share == 0 or share == 1:
        if socket.gethostname().find('zbx') < 0:
            copy, copywal = backup(path, t)
        else:
            copy = backup(path, t)
    elif share == 2:
        if socket.gethostname().find('zbx') < 0:
            copy, copywal = backup(path, t)
        else:
            copy = backup(path, t)
        if socket.gethostname().find('zbx') < 0:
            replication(path1, path2, copy, copywal)
            def searching(path1, path2):
                for i in range(2): search(path1, path2, i)
	#Parallel execution of file synchronization operations
            pool=multiprocessing.Pool()
            answer=pool.map(searching(path1, path2))
        else:
            replication(path1, path2, copy)
            def searching(path1, path2):
                search(path1, path2, 0)
            pool=multiprocessing.Pool()
            answer=pool.map(searching(path1, path2))
if __name__ == '__main__':
    main()
