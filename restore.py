#!/usr/bin/python

#Added the ability to restore from a backup of any cluster server
'''
For Python 2.7.13

	Data centers:
	01 - OCOD
	02 - RCOD

	Domaines:
	ac.com
	vp.com
	in.com
'''       

import os
import tarfile
import socket
import subprocess
from datetime import datetime

def main():
    def logs():
        '''Creating a session log and a log with a description of all sessions'''
        #If the size of 1 GB is exceeded, the debugdb.log is deleted and recreated
        if not os.path.exists('/var/log/backupdb.log'): f=open('/var/log/backupdb.log', "w+"); f.close()
        if not os.path.getsize('/var/log/backupdb.log')/(1024*1024*1024)==0: os.system(r' >/var/log/backupdb.log')
        #The function returns 0
    def massive(ocod, domvn, domiz, IP=[]):
        '''Selection of an array of hypervisor IP addresses depending on the contour'''
        #Determining the main storage (the storage located on the same subnet as the database server)
        if socket.gethostname().find(ocod) >= 0:
                IPIZ = ['10.111.15.54', '10.111.15.63']
                IPVN = ['10.111.16.54', '10.111.16.63']
                IPIN = ['10.111.17.54', '10.111.17.63']
        else:
                IPIZ = ['10.111.15.63', '10.111.15.54']
                IPVN = ['10.111.16.63', '10.111.16.54']
                IPIN = ['10.111.17.63', '10.111.17.54']
        #Determination of the domain in which the database server is located
        if socket.gethostname().find(domvn) >= 0: [IP.append(i) for i in IPVN]
        elif socket.gethostname().find(domiz) >= 0: [IP.append(i) for i in IPIZ]
        else: [IP.insert(0,i) for i in IPIN]
        #The output is a list of IP-addresses of the main and backup storage
        return IP
    def paths(a, ocod, domvn, domiz, codlist):
        '''Determining the backup storage mount point'''
        path=[]
        for k,j in enumerate(codlist, 1):
            try:
		temp=subprocess.check_output("ls -d /mnt/dbbackup/"+j+"/*/", shell=True).split("\n"); temp.remove('')
	    except subprocess.CalledProcessError:
                print
                print(' '.join(['Problems with the operation of the smbd service on the server with the repository of ',j]))
                print
                with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Problems with the operation of the smbd service on the server with the repository of'+j+'\n')
                if k < len(codlist):
                    continue
                elif len(path)==0:
                    exit()
            path.append(temp)
	IP=massive(ocod, domvn, domiz)
        d={}
        for x in path:
            for y in x:
		if "OCOD" in y:
        		d[y] = IP[0]
    		else:
        		d[y] = IP[1]
	return d, len(path)
        '''
        The returned data type is a dictionary (Storage mount point: IP-address of the storage) and count of storage mount point
        '''
    def mounts(var, g, path, test):
        '''Checking if the ball is mounted'''
        #Mounting storages on a server with a database, if not mounted
        #Checking the ability to write to storages mounted on a server with a database
        try:
		ls = subprocess.Popen(("mount"), stdout=subprocess.PIPE); mount = subprocess.check_output(("grep", g), stdin=ls.stdout); ls.wait(); n=5
        except subprocess.CalledProcessError, a:
                n=1
        c=[]
	e=[]
        for k,v in path.items():
            if v == g:
                c.append(k)
        s=len(c)
	for l, j in enumerate(c, 1):
        	if n==1:
                	b=subprocess.Popen(["mount", "//"+g+"/bkp"+j.replace('/mnt', ''), j, "-o", "vers=3.0,credentials=/opt/creds/CredIZ"+test+".txt,rw,file_mode=0666,dir_mode=0777"]).wait();
                	if b!=0 and var==1:
                            print(' '.join(['Problems with the operation of the smbd service on the server with the repository of ',test]))
                            with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Problems with the operation of the smbd service on the server with the repository of'+test+'\n')
                            if l < s:
			        continue
			    else:
			        return 1
                	elif b!=0 and var==2:
                            print(' '.join(['Problems with the operation of the smbd service on the server with the repository of ',test]))
                            with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Problems with the operation of the smbd service on the server with the repository of'+ test +'\n')
                            if l < s:
                                continue
                            else:
                                exit()
                	elif b==0 and var==1:
                            print(' '.join(['PostgreSQL database backup storage is ',test,' mounted successfully']))
                            with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' PostgreSQL database backup storage is '+test+' mounted successfully'+'\n')
                            if l < s:
                 	        e.append(j)
                                continue
                            else:
                 	        e.append(j)
                                return e
                	elif b==0 and var==2:
                            print(' '.join(['PostgreSQL database backup storage is ',test,' mounted successfully']))
                            with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' PostgreSQL database backup storage is'+test+'mounted successfully'+'\n')
                            if l < s:
                 	        e.append(j)
                                continue
                            else:
                 	        e.append(j)
                                return e
            	else:
                	exit_code = subprocess.call(["touch", j+'test'])
                	if exit_code != 0 and var==1:
                            print(' '.join(['Problems with the operation of the smbd service on the server with the repository of ',test]))
                            with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Problems with the operation of the smbd service on the server with the repository of'+test+'\n')
                            if l < s:
                                continue
                            else:
                                return 1
                	elif exit_code != 0 and var==2:
                            print(' '.join(['Problems with the operation of the smbd service on the server with the repository of ',test]))
                            with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Problems with the operation of the smbd service on the server with the repository of'+test+'\n')
                            if l < s:
                                continue
                            else:
                                exit()
                	elif exit_code == 0 and var==1:
			    if l < s:
                 	        e.append(j)
                                continue
                            else:
                 	        e.append(j)
                                return e
                	elif exit_code == 0 and var==2:
			    if l < s:
                 	        e.append(j)
                                continue
                            else:
                 	        e.append(j)
                                return e
        '''
        Return data type - massive/number
        If the function returns e (path to storage mount point), the storage is available
        If the function returns 1, the storage is not available
        If all storages are mounted unsuccessfully, the program will close
        '''
    def networkavailable(var, g, test, ocod, rcod):
        '''Determining the network availability of storage'''
        #Checking the availability of hypervisor servers with ICMP backup storages
        test='OCOD' if (socket.gethostname().find(ocod) >= 0 and var==1) or (socket.gethostname().find(rcod) >= 0 and var==2) else 'RCOD'
        ping = subprocess.Popen(("ping", "-c4", g), stdout=subprocess.PIPE); exit_code = subprocess.check_output(("sed", "-n", '1,/^---/d;s/%.*//;s/.*, //g;p;q'), stdin=ping.stdout); ping.wait()
        if int(exit_code.replace("\n","")) == 100:
                if var==1:
			print(' '.join(['Server with storage ',test,' is not available']))
                        print
                        with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Server with storage '+test+' is not available'+'\n')
                        return 1
                else:
			print(' '.join(['Server with storage ',test,' is not available']))
                        print
                        with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Server with storage '+test+' is not available'+'\n')
                        exit()
        else:
		print(' '.join(['Server with storage ',test,' is available']))
                print
                with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Server with storage '+test+' is available'+'\n')
                return 0
        '''
        Return data type - number
        If the function returns 0 - the server with the backup storage is available
        If the function returns 1 - the server with the backup storage is unavailable
        If all servers with a backup storage are unavailable, the program will close
        '''
    def shareavailable(path, n, ocod, rcod, domvn, domiz):
        '''Checking network storage availability'''
        result=0
        IP=[]
	array=[]
        for k,v in path.items():
            IP.append(v)
        for var,g in enumerate(IP, 1):
            test=ocod if (socket.gethostname().find(ocod) >= 0 and var==1) or (socket.gethostname().find(rcod) >= 0 and var==2) else rcod
            if networkavailable(var, g, test, ocod, rcod) == 0:
                e=mounts(var, g, path, test)
                if e==1:
                    continue
                else:
                    for i in e:
		        array.append(i)
                    if var==2:
                        return array
	    else:
		continue
        return array
        '''
        Return data types - massive
        If function returns array - data center NAS available
        If all servers with a backup storage are unavailable or all data centers NAS unavailable, the program will close
        '''
    def restore(array):
	'''Restoring from a backup'''
	#View backups in available locations
	for i in range(len(array)):
         	print(' '.join(['Backup list', array[i]]))
                print
                try:
                    ls = subprocess.Popen(("ls", "-rI","wal*", array[i]), stdout=subprocess.PIPE); a = subprocess.check_output(('grep', 'tar.gz'), stdin=ls.stdout); a=a.split("\n"); a.remove('')
                    for j in a:
                        print(j)
                except subprocess.CalledProcessError:
			print('No copy in NAS ', array[i])
                        print
                        if len(array)==1:
                            print('There are no copies. Completion of the program.')
			    exit()
			continue 
 	print(' '.join(['Enter the date and time of the PostgreSQL database backup in the format', array[0] + a[0]])); bddata = raw_input()
        print
        #Selecting the desired backup by the user
	if os.path.exists(bddata):
                print('Backup exists')
        else:
                bd = raw_input('No copy exists. Choose another one? y/n ')
                d = {'y': restore, 'n': exit}
		try:
			d[bd](array)
		except KeyError:
            		print('Invalid value entered. Try again'); restore(array)
	#Commands of recovery from reserve copy
	os.system('systemctl stop postgresql')
        os.system('sudo su - postgres -c "rm -rf /var/lib/postgresql/9.6/main/*"')
        subprocess.call(["tar", "-C", "/var/lib/postgresql/9.6/main/", "-xvf", bddata])
        os.system('systemctl start postgresql')
	'''
        Return data types - None
        '''
    def input(array):
	'''Consent/refuse to restore from a backup'''
        bd = raw_input('The checks were successful. Start the procedure for restoring the database? y,n ')
        d = {'y': restore, 'n': exit}
        try:
        	d[bd](array)
        except KeyError:
            print('Invalid value entered. Try again'); input(array)
            print
	'''
        Return data types - None
        '''
    a=socket.gethostname()
    ocod='01'
    rcod='02'
    domvn='vp.com'
    domiz='ac.com'
    codlist=['OCOD', 'RCOD']
    logs()
    path,n = paths(a, ocod, domvn, domiz, codlist)
    array=shareavailable(path, n, ocod, rcod, domvn, domiz)
    input(array)
if __name__ == '__main__':
    main()
