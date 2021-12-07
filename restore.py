#!/usr/bin/python

#massive - select an array of hypervisor IP addresses depending on the contour
#restore - restoring a database from a database backup
#checkcopy - checking the existence of the entered date/time, when the backup was created

import os
import tarfile
import socket
import subprocess

OCOD='/mnt/dbbackup/OCOD/'
RCOD='/mnt/dbbackup/RCOD/'

def massive(IP=[]):
        if set('01').issubset(socket.gethostname()):
                IPIZ = ['10.111.15.54', '10.111.15.63']
                IPVN = ['10.111.16.54', '10.111.16.63']
                IPIN = ['10.111.17.54', '10.111.17.63']
        elif set('02').issubset(socket.gethostname()):
                IPIZ = ['10.111.15.63', '10.111.15.54']
                IPVN = ['10.111.16.63', '10.111.16.54']
                IPIN = ['10.111.17.63', '10.111.17.54']
        if set('vp').issubset(socket.gethostname()):
                for i in IPVN:
                        IP.append(i)
        elif set('in').issubset(socket.gethostname()):
                for i in IPIZ:
                        IP.append(i)
        else:
                for i in IPIN:
                        IP.append(i)
        return IP
def checkcopy():
	path='/mnt/dbbackup/OCOD/' if var==1 else '/mnt/dbbackup/RCOD/'
	print(path)
	print('Backup list')
	ls = subprocess.Popen(("ls", "-rI","wal*", path), stdout=subprocess.PIPE); a = subprocess.check_output(('grep', 'tar.gz'), stdin=ls.stdout); ls.wait(); print(a)
	os.system('echo Enter the date and time of the PostgreSQL database backup in the format $(date +"%Y%m%d-%H%M%S")'); bddate = raw_input()
        if os.path.exists(path + socket.gethostname() + '-' + bddate + '.tar.gz'):
		print('Backup exists')
	else:
		bd = raw_input('No copy exists. Choose another one? y/n')
		d = {'y': checkcopy, 'n': exit}
    		try:
        		d[bd]()
    		except KeyError:
        		print('Invalid value entered. Try again'); checkcopy
        return bddate
def restore(var):
	path='/mnt/dbbackup/OCOD/' if var==1 else '/mnt/dbbackup/RCOD/'
	bddate=checkcopy()
	os.system('systemctl stop postgresql')
	os.system('sudo su - postgres -c "rm -rf /var/lib/postgresql/9.6/main/*"')
	subprocess.call(["tar", "-C", "/var/lib/postgresql/9.6/main/", "-xvf", path + socket.gethostname() + '-' + bddate + '.tar.gz'])
	os.system('systemctl start postgresql')
def input(var):
	bd = raw_input('The checks were successful. Start the procedure for restoring the database? y,n')
	d = {'y': restore, 'n': exit}
        try:
            d[bd](var)
        except KeyError:
            print('Invalid value entered. Try again'); input
def mounts(g):
	try:
        	ls = subprocess.Popen(("mount"), stdout=subprocess.PIPE); mount = subprocess.check_output(("grep", g), stdin=ls.stdout); ls.wait(); n=5
        except subprocess.CalledProcessError, e:
        	n=1
	return n
my_array=massive()
#print(my_array)
var=0
for g in my_array:
        print(g)
        var += 1
        #Checking the availability of hypervisor servers with ICMP backup storages
	mount = subprocess.Popen(("ping", "-c4", g), stdout=subprocess.PIPE); exit_code = subprocess.check_output(("sed", "-n", '1,/^---/d;s/%.*//;s/.*, //g;p;q'), stdin=mount.stdout); mount.wait();
        if exit_code==1:
                if var==1:
                        os.system('echo $(date +"%Y%m%d-%H%M%S")     Server with storage OCOD is not available       >> /var/log/backupdb.log')
                        continue
                else:
                        os.system('echo $(date +"%Y%m%d-%H%M%S")     Server with storage RCOD is not available       >> /var/log/backupdb.log')
                        break
        else:
                os.system('echo $(date +"%Y%m%d-%H%M%S")   Server with storage is available      >> /var/log/backupdb.log')
                if var==1:
                        #Mounting storages on a server with a database, if not mounted
                        #Checking the ability to write to storages mounted on a server with a database
                        exit_code = subprocess.call(["touch", OCOD+'test'])
                        if mounts(g)==1:
                                os.system('mount -a')
                                if mounts(g)==1:
                                        os.system('echo $(date +"%Y%m%d-%H%M%S")   Problems with the operation of the smbd service on the server with the repository of >> /var/log/backupdb.log')
                                        continue
                                else:
                                        os.system('echo $(date +"%y%m%d-%h%m%s")   PostgreSQL database backup storage is mounted successfully   >> /var/log/backupdb.log')
                                        input(var)
					break
                        elif exit_code != 0:
                                os.system('echo $(date +"%Y%m%d-%H%M%S")   Problems with the operation of the smbd service on the server with the repository of >> /var/log/backupdb.log')
                                continue
                        else:
                                input(var)
				break
	 	if var==2:
                        #Mounting storages on a server with a database, if not mounted
                        #Checking the ability to write to storages mounted on a server with a database
                        exit_code = subprocess.call(["touch", RCOD+'test'])
			if mounts(g)==1:
                                os.system('mount -a')
				if mounts(g)==1:
                                        os.system('echo $(date +"%Y%m%d-%H%M%S")   Problems with the operation of the smbd service on the server with the repository >> /var/log/backupdb.log')
                                        exit()
                                else:
                                    os.system('echo $(date +"%y%m%d-%h%m%s")   PostgreSQL database backup storage is mounted successfully   >> /var/log/backupdb.log')
                                    input(var)
                        elif exit_code != 0:
                                break
                        else:
                             input(var)
