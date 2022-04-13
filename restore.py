#!/usr/bin/python

#Added the ability to restore from a backup of any cluster server
'''
Tested on Python versions 2.7.13 and 3.5.3
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
                temp=subprocess.check_output("ls -d /mnt/dbbackup/"+i+"/*/", shell=True).decode("utf-8")
                temp=temp.split("\n"); temp.remove('')
            except subprocess.CalledProcessError:
                print
                print(' '.join(['Problems with the operation of the smbd service on the server with the repository of ',i]))
                print
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
    def mounts(s, dic):
        '''Checking if the ball is mounted'''
        #Mounting storages on a server with a database, if not mounted
        #Checking the ability to write to storages mounted on a server with a database
        e=[]
        for i, j in s.items():
            for z, (x, y) in enumerate(dic.items(), 1):
                for p, l in enumerate(j, 1):
                    for k, t in enumerate(y, 1):
                        if i==x:
                            try:
                                ls = subprocess.Popen(("mount"), stdout=subprocess.PIPE); mount = subprocess.check_output(("grep", l), stdin=ls.stdout); ls.wait(); n=5
                            except subprocess.CalledProcessError:
                                n=1
                            if n==1:
                                b=subprocess.Popen(["mount", "//"+l+"/bkp"+t.replace('/mnt', ''), t, "-o", "vers=3.0,credentials=/opt/creds/CredIZ"+i+".txt,rw,file_mode=0666,dir_mode=0777"]).wait();
                                if b!=0:
                                    print(' '.join(['Problems with the operation of the smbd service on the server with the repository of ',i]))
                                    with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Problems with the operation of the smbd service on the server with the repository of'+i+'\n')
                                    if k < len(y):
                                        continue
                                    elif z<len(dic):
                                        break
                                    elif z==len(dic):
                                        return 1                	        
                                else:
                                    print(' '.join(['PostgreSQL database backup storage is ',i,' mounted successfully']))
                                    with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' PostgreSQL database backup storage is '+i+' mounted successfully'+'\n')
                                    if k < len(y):
                                        e.append(t)
                                    elif z<len(dic):
                                        e.append(t)
                                        break
                                    elif z==len(dic):
                                        e.append(t)
                                        return e
                            else:
                                exit_code = subprocess.call(["touch", t+'test'])
                                if exit_code != 0:
                                    print(' '.join(['Problems with the operation of the smbd service on the server with the repository of ',i]))
                                    with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Problems with the operation of the smbd service on the server with the repository of'+i+'\n')
                                    if k < len(y):
                                        continue
                                    elif z<len(dic):
                                        break
                                    elif z==len(dic):
                                        return 1
                                else:
                                    if k < len(y):
                                        e.append(t)
                                        continue
                                    elif z<len(dic):
                                        e.append(t)
                                        break
                                    elif z==len(dic):
                                        e.append(t)
                                        return e
        '''
        Return data type - massive/number
        If the function returns e (path to storage mount point), the storage is available
        If the function returns 1, the storage is not available
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
                ping = subprocess.Popen(("ping", "-c4", x), stdout=subprocess.PIPE); exit_code = subprocess.check_output(("sed", "-n", '1,/^---/d;s/%.*//;s/.*, //g;p;q'), stdin=ping.stdout).decode("utf-8"); ping.wait()
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
    def cluster(vipcluster, a):
        for i, j in vipcluster.items():
            for k in j:
                if a in k:
                    IP=i
                    return IP
                else:
                    return 1
    def restore(path, t, IP):
        '''Restoring from a backup'''
        if t==1:
            postgre = subprocess.check_output("ps aux | grep '/bin/postgre' | grep -v 'grep /bin/postgre' | awk '{print $11}'", shell=True).decode("utf-8")
            postgre=postgre.split("\n"); postgre.remove(''); 
            if len(postgre) != 0 and os.system('systemctl status corosync > /dev/null 2>&1') == 0 and os.system('systemctl status pacemaker > /dev/null 2>&1') == 0:
                subprocess.call(['rm', '-rf', '/var/lib/postgresql/9.6/main'])
                process=subprocess.Popen(['pg_basebackup', '-h', IP, '-p', '5432', '-U', 'postgres', '-D', '/var/lib/postgresql/9.6/main/', '-P', '--xlog'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                if process==0:
                    print(' '.join(['Cluster master-node ', IP, ' is available']))
                    with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Cluster master-node '+IP+' is available'+'\n')
                    subprocess.call(['rm', '/var/lib/pgsql/tmp/PGSQL.lock'])
                    subprocess.call(['chmod', '0700', '/var/lib/postgresql/9.6/main', '-R'])
                    subprocess.call(['chown', 'postgres:postgres', '/var/lib/postgresql/9.6/main', '-R'])
                    subprocess.call(['pcs', 'cluster', 'start'])
                    exit()
                else:
                    print(' '.join(['Cluster master-node ', IP, ' is not available. Cluster needs to be restored manually']))
                    with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Cluster master-node '+IP+' is available. Cluster needs to be restored manually'+'\n')
                    exit()
            else:
                print(' '.join(['Cluster needs to be restored manually']))
                with open("/var/log/backupdb.log","a+") as stdout: stdout.write(str(datetime.now().strftime("%Y%m%d-%H%M%S"))+' Cluster needs to be restored manually'+'\n')
                exit()
	#View backups in available locations
        for i in range(len(path)):
            print(' '.join(['Backup list', path[i]]))
            print
            try:
                ls = subprocess.Popen(("ls", "-rI","wal*", path[i]), stdout=subprocess.PIPE); a = subprocess.check_output(('grep', 'tar.gz'), stdin=ls.stdout).decode("utf-8"); a=a.split("\n"); a.remove('')
                for j in a:
                    print(j)
            except subprocess.CalledProcessError:
                print('No copy in NAS ', path[i])
                print
                if len(path)==1:
                    print('There are no copies. Completion of the program.')
                    exit()
                continue 
        print(' '.join(['Enter the date and time of the PostgreSQL database backup in the format', path[0] + a[0]]))
        bd = input()
        '''
        For Python2:
        bd = raw_input()
        '''
        print
        #Selecting the desired backup by the user
        if os.path.exists(bd):
            print('Backup exists')
        else:
            '''
            For Python2:
            bd = raw_input('No copy exists. Choose another one? y/n ')
            '''
            bd = input('No copy exists. Choose another one? y/n ')
            d = {'y': restore, 'n': exit}
            try:
                d[bd](path, t) if bd=='y' else d[bd]()
            except KeyError:
                print('Invalid value entered. Try again'); restore(path, t)
	#Commands of recovery from reserve copy
        os.system('systemctl stop postgresql')
        os.system('sudo su - postgres -c "rm -rf /var/lib/postgresql/9.6/main/*"')
        subprocess.call(["tar", "-C", "/var/lib/postgresql/9.6/main/", "-xvf", bddata])
        os.system('systemctl start postgresql')
        '''
        Return data types - None
        '''
    def inputdata(path, t, IP):
        '''Consent/refuse to restore from a backup'''
        '''
        For Python2:
        bd = raw_input('The checks were successful. Start the procedure for restoring the database? y,n ')
        '''
        bd = input('The checks were successful. Start the procedure for restoring the database? y,n ')
        d = {'y': restore, 'n': exit}
        try:
            d[bd](path, t, IP) if bd=='y' else d[bd]()
        except KeyError:
            print('Invalid value entered. Try again'); inputdata(path, t, IP)
            print
        '''
        Return data types - None
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
    domain={'ac.com':['10.111.15.54', '10.111.15.63', '10.111.15.54'],'vp.com':['10.111.16.54', '10.111.16.63', '10.111.16.75'],'in.com':['10.111.17.54', '10.111.17.63', '10.111.17.75']}
    vipcluster={'10.111.15.80':['bd1iz01.ac.com', 'bd1iz02.ac.com', 'bd2iz01.ac.com', 'bd2iz02.ac.com'], '10.111.16.80':['crsvn01.vp.com', 'crsvn02.vp.com'], '10.111.17.80':['crsin01.in.com', 'crsin02.in.com']}
    logs()
    a=socket.gethostname()
    path,n = paths(a, domain, codname, codid)
    IP=cluster(vipcluster, a)
    t=0 if IP==1 else 1
    inputdata(path, t, IP)
if __name__ == '__main__':
    main()
