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
from multiprocessing import Pool
from contextlib import closing
from operator import itemgetter
import math

def main():
    def logs():
	'''Creating a session log and a log with a description of all sessions'''
	#If the size of 1 GB is exceeded, the debugdb.log is deleted and recreated
	if not os.path.exists('/var/log/backupdb.log'): f=open('/var/log/backupdb.log', "w+"); f.close()
	if not os.path.getsize('/var/log/backupdb.log')/(1024*1024*1024)==0: os.system(r' >/var/log/backupdb.log')
	#The function returns 0
    def cluster(vipcluster, a):
	'''Determining if a given server belongs to a DB cluster'''
        for i, j in vipcluster.items():
            for k in j:
                if a in k:
                    IP=i
                    return IP
                else:
                    return 1
        '''
	Return data type is a list(server name)/number.
	Returning a value indicating whether the server with the database belongs to the servers included in the cluster of database servers:
	list - belongs;
	1 - does not belong.
	'''
    def paths(a, domain, codname, codid):
	'''Determining the backup storage mount point'''
	d={}
	for x, y in domain.items():
		if x in a:
		    d[x]=y
	s=networkavailable(d,codname) 
        dic={}
        for k,(i,j) in enumerate(s.items(), 1):
            try:
		temp=subprocess.check_output("ls -d /mnt/dbbackup/"+i+"/*/ | grep $(uname -n)", shell=True).split("\n"); temp.remove('')
	    except subprocess.CalledProcessError:
                with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Problems with the operation of the smbd service on the server with the repository of'+i+'\n')
                if k < len(s):
                    continue
                elif len(dic)==0:
                    exit()
		elif k==len(s) and len(dic)!=0:
			break
            dic[i]=temp
        e=mounts(s, dic)	
	return e, len(e)
        '''
        The returned data type is a list (Storage mount point) and count of storage mount point
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
        for k,i in enumerate(path, 1):
            if k==1:
                continue
            exit_code = subprocess.call(['cp', path[0]+copy, i])
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
		with open("/var/log/backupdb.log","a+") as stdout: 
                    stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+" An incorrectly created backup copy of the database has been deleted " + '\n')
                #Program termination due to disconnection during backup creation
                exit()
	'''
	Return data types: number, string, string
	Return data types: number, string, string If successful, the program returns 0, the name of the backup archive, the name of the WAL-files archive.
	Otherwise, the program ends
	'''
    def sync(path1, path2, a, b, c, d, processors=2):
	'''Synchronization of the contents of the mounted ball of the OCOD and RCOD'''
	#If there is 1 copy in the backup storage, copy all copies from the main storage to the backup.
        def copy(path1, path2, a):
            for i in a:
		exit_code=subprocess.call(['cp', path1+i, path2])
        def submassive(a, processors):
    		if len(a)%processors == 0:
        		n = int(math.ceil(len(a)/processors))
    		else:
        		n = int(math.ceil(len(a)/processors)) + 1
    		for x in range(0, len(a), n):
        		each_chunk = a[x: n+x]
        		yield each_chunk
	def syncronize(path1, path2, m):
		with closing(Pool(processors)) as pool:
                    for i in m:
        		pool.map(copy(path1, path2, i), iterable=[(path1, path1, i)])
        	    pool.terminate()
        if d==0:
	    m=list((submassive(a, processors)))
            syncronize(path1, path2, a)
            return 0
        #Copying backups from a vault with more copies to a vault with fewer copies
        w=len(b)
        z=len(a)
        temp=[]
        for k in b:
            temp.append(k)
        s=[]
        for n, k in enumerate(b, 1):
            if k not in a:
                s.append(k)
                if n==w and len(s)!=0:
		    m=list((submassive(a, processors)))
                    syncronize(path1, path2, m)
                    a=s
                    path1, path2 = path2, path1
		    m=list((submassive(a, processors)))
                    syncronize(path1, path2, m)
                    return 0
            else:
                temp.remove(k)
                a.remove(k)
                d-=1
                if d==0:
 		    m=list((submassive(a, processors)))
                    syncronize(path1, path2, m)
                    return 0
                elif n==w:
                    m=list((submassive(a, processors)))
                    syncronize(path1, path2, m)
                    a=s
                    path1, path2 = path2, path1
                    m=list((submassive(a, processors)))
                    syncronize(path1, path2, m)
                    return 0
                continue
        #The function returns None
    def search(path, i):
	'''Checking 'sync' trigger conditions'''
	def checkcopy(path, i):
                copy={}
		count={}
                for j in path:
		    '''Obtaining lists of backup archives and WAL-archives, counting the number of backup copies and WAL-archives'''
		    if i==0:
			try:
				temp1="ls -rI wal* "+j+" | grep tar.gz"; a = subprocess.check_output(temp1,shell=True).split("\n"); a.remove(''); b=len(a)
                        except subprocess.CalledProcessError:
				a=[]
				b=0
			copy.setdefault(j, a)
			count[j]=b
	    	    else:
			try:
				temp1="ls -t "+j+" | grep wal"; a = subprocess.check_output(temp1,shell=True).split("\n"); a.remove(''); b=len(a)
                        except subprocess.CalledProcessError:
                                a=[]
                                b=0
			copy.setdefault(j, a)
			count[j]=b
		return copy, count
	#The cycle will run until the number of backups and WAL-archives in the vaults becomes the same
	for n in range(2):
	    '''Definition of storage with more and fewer backups and WAL-archives'''
	    copy, count = checkcopy(path, i)
            if n==1:
                s=max(count.iteritems(), key=itemgetter(1))[1]
                if s>m:
                    m=s
                else:
                    exit()
            else:
	        m=max(count.iteritems(), key=itemgetter(1))[1]
            for x, y in count.items():
                if y==m:
                    pm=x
            for k, (x, y) in enumerate(count.items(), 1):
		    if m > y:
                        print('n', n, 'm', m)
                        sync(pm, x, copy.get(pm), copy.get(x), m, y)
                    elif k==len(count) and n==0:
                        break
                    elif k==len(count) and n==1:
			exit()
                    else:
                        continue
        #The function returns None
    def mounts(s, dic):
	'''Checking if the ball is mounted'''
	#Mounting storages on a server with a database, if not mounted
        #Checking the ability to write to storages mounted on a server with a database
        e=[]
        for p,(i, j) in enumerate(s.items(), 1):
            for l in j:
                for z, (x, y) in enumerate(dic.items(), 1):
                    for k, t in enumerate(y, 1):
                        if i==x:
                            try:
		                ls = subprocess.Popen(("mount"), stdout=subprocess.PIPE); mount = subprocess.check_output(("grep", l), stdin=ls.stdout); ls.wait(); n=5
                            except subprocess.CalledProcessError:
                                n=1
        	            if n==1:
                	        b=subprocess.Popen(["mount", "//"+l+"/bkp"+t.replace('/mnt', ''), t, "-o", "vers=3.0,credentials=/opt/creds/CredIZ"+i+".txt,rw,file_mode=0666,dir_mode=0777"]).wait();
                	        if b!=0:
                                    with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Problems with the operation of the smbd service on the server with the repository of'+i+'\n')
                                    if k < len(y):
                                        continue
                                    elif z<len(dic):
                                        break
                                    elif z==len(dic) and len(e)==0:
                                        exit()                	        
                                else:
                                    with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' PostgreSQL database backup storage is '+i+' mounted successfully'+'\n')
                                    if p!=len(s):
                                        e.append(t)
                                    else:
                                        e.append(t)
                                        return e                            
                            else:
                	        exit_code = subprocess.call(["touch", t+'test'])
                	        if exit_code != 0:
                                    with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Problems with the operation of the smbd service on the server with the repository of'+i+'\n')
                                    if k < len(y):
                                        continue
                                    elif z<len(dic):
                                        break
                                    elif z==len(dic) and len(e)==0:
                                        exit()
                                else:
                                    if p!=len(s):
                                        e.append(t)
                                    else:
                                        e.append(t)
                                        return e
        '''
        Return data type - massive
        If the function returns e (path to storage mount point), the storage is available
        '''
    def networkavailable(d, codname):
	'''Determining the network availability of storage'''
	#Checking the availability of hypervisor servers with ICMP backup storages
        l={}
        for x, y in d.items():
            for i, j in codname.items():
                for z in y:
                    for k in j:
                        if z in k:
                            l.setdefault(i, [])
                            l[i].append(k)
        s={}
        for i, j in l.items():
            for x in j:
                ping = subprocess.Popen(("ping", "-c4", x), stdout=subprocess.PIPE); exit_code = subprocess.check_output(("sed", "-n", '1,/^---/d;s/%.*//;s/.*, //g;p;q'), stdin=ping.stdout); ping.wait()
                if int(exit_code.replace("\n","")) == 100:
		    print(' '.join(['Server with storage ',i,' is not available']))
                    print
                    with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Server with storage '+i+' is not available'+'\n')
                else:
		    print(' '.join(['Server with storage ',i,' is available']))
                    print
                    with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Server with storage '+i+' is available'+'\n')
                    s.setdefault(i, [])
                    s[i].append(x)
        if len(s)==0:
            print(' '.join(['Servers with storage is not available']))
            print
            with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Servers with storage is not available'+'\n')
            exit()
        return s
        '''
        Return data type - dictionary
        Data - ta center name and array of IP-addresses of each data center.
        If all servers with a backup storage are unavailable, the program will close
        '''
        '''
    Editable parameters:
    --codd
    The data type is a dictionary.
    Data - Data Center ID: Data Center Name
    --codname
    The data type is a dictionary.
    Data - data center name: list of IP addresses of data center storages    
    --domain
    The data type is a dictionary.
    Data - domain: list of IP addresses of domain stores
    --vipcluster
    The data type is a dictionary.
    Data - virtual IP address of the cluster master node: list of servers included in the cluster    
    '''
    codid={'01':'OCOD', '02':'RCOD', '03':'GCOD'}
    codname={'OCOD':['10.111.15.54', '10.111.16.54', '10.111.17.54'], 'RCOD':['10.111.15.63', '10.111.16.63', '10.111.17.63'], 'GCOD':['10.111.15.75', '10.111.16.75', '10.111.17.75']}
    domain={'auc':['10.111.15.54', '10.111.15.63', '10.111.15.75'],'vp.com':['10.111.16.54', '10.111.16.63', '10.111.16.75'],'in.com':['10.111.17.54', '10.111.17.63', '10.111.17.75']}
    vipcluster={'10.111.15.80':['bd1iz01.ac.com', 'bd1iz02.ac.com', 'bd2iz01.ac.com', 'bd2iz02.ac.com'], '10.111.16.80':['crsvn01.vp.com', 'crsvn02.vp.com'], '10.111.17.80':['crsin01.in.com', 'crsin02.in.com']}
    a=socket.gethostname()
    logs()
    path,n = paths(a, domain, codname, codid)
    IP=cluster(vipcluster, a)
    t=0 if IP==1 else 1
    if len(path)==1:
        if socket.gethostname().find('zbx') < 0:
            copy, copywal = backup(path[0], t)
            exit()
        else:
            copy = backup(path[0], t)
            exit()
    else:
        if socket.gethostname().find('zbx') < 0:
            copy, copywal = backup(path[0], t)
            replication(path, copy, copywal)
            for i in range(2): search(path, i)
        else:
            search(path, 0)
if __name__ == '__main__':
    main()
