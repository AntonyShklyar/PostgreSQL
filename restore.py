#!/usr/bin/python

#Added the ability to restore from a backup of any cluster server

:<<end_of_comments
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
end_of_comments

#massive - select an array of hypervisor IP addresses depending on the contour
#restore - restoring a database from a database backup
#checkcopy - checking the existence of the entered date/time, when the backup was created

import os
import tarfile
import socket
import subprocess

def massive(IP=[]):
        if set('01').issubset(socket.gethostname()):
                IPIZ = ['10.111.15.54', '10.111.15.63']
                IPVN = ['10.111.16.54', '10.111.16.63']
                IPIN = ['10.111.17.54', '10.111.17.63']
        elif set('02').issubset(socket.gethostname()):
                IPIZ = ['10.111.15.63', '10.111.15.54']
                IPVN = ['10.111.16.63', '10.111.16.54']
                IPIN = ['10.111.17.63', '10.111.17.54']
        if set('vn').issubset(socket.gethostname()):
                for i in IPVN:
                        IP.append(i)
        elif set('iz').issubset(socket.gethostname()):
                for i in IPIZ:
                        IP.append(i)
        else:
                for i in IPIN:
                        IP.append(i)
        return IP
def checkcopy(*args):
        a=len(args)
        if a==4:
                print
                print(' '.join(['Backup list', args[0]]))
                print('Backup list', args[0])
                ls = subprocess.Popen(("ls", "-rI","wal*", args[0]), stdout=subprocess.PIPE); a = subprocess.check_output(('grep', 'tar.gz'), stdin=ls.stdout); ls.wait(); print(a)
                print
                print(' '.join(['Backup list', args[1]]))
                ls = subprocess.Popen(("ls", "-rI","wal*", args[1]), stdout=subprocess.PIPE); a = subprocess.check_output(('grep', 'tar.gz'), stdin=ls.stdout); ls.wait(); print(a)
                print
                print(' '.join(['Backup list', args[2]]))
                ls = subprocess.Popen(("ls", "-rI","wal*", args[2]), stdout=subprocess.PIPE); a = subprocess.check_output(('grep', 'tar.gz'), stdin=ls.stdout); ls.wait(); print(a)
                echo
                print(' '.join(['Backup list', args[3]]))
                ls = subprocess.Popen(("ls", "-rI","wal*", args[3]), stdout=subprocess.PIPE); a = subprocess.check_output(('grep', 'tar.gz'), stdin=ls.stdout); ls.wait(); print(a)
                echo
        elif a==2:
                print
                print(' '.join(['Backup list', args[0]]))
                ls = subprocess.Popen(("ls", "-rI","wal*", args[0]), stdout=subprocess.PIPE); a = subprocess.check_output(('grep', 'tar.gz'), stdin=ls.stdout); ls.wait(); print(a)
                print
                print(' '.join(['Backup list', args[1]]))
                ls = subprocess.Popen(("ls", "-rI","wal*", args[1]), stdout=subprocess.PIPE); a = subprocess.check_output(('grep', 'tar.gz'), stdin=ls.stdout); ls.wait(); print(a)
                print
        else:
                print
                print(' '.join(['Backup list', args[0]]))
                ls = subprocess.Popen(("ls", "-rI","wal*", args[0]), stdout=subprocess.PIPE); a = subprocess.check_output(('grep', 'tar.gz'), stdin=ls.stdout); ls.wait(); print(a)
                print
        print(' '.join(['Enter the date and time of the PostgreSQL database backup in the format', args[0] + '/' + a])); bddata = raw_input()
        if os.path.exists(bddata):
                print('Backup exists')
        else:
                bd = raw_input('No copy exists. Choose another one? y/n')
                d = {'y': checkcopy(args[0], args[1], args[2], args[3]) if a==4 else checkcopy(args[0], args[1]) if a==2 else checkcopy(args[0]), 'n': exit}
                try:
                        if a==4:
                                d[bd](args[0], args[1], args[2], args[3])
                        elif a==2:
                                d[bd](args[0], args[1])
                        else:
                                d[bd](args[0])
                except KeyError:
                        print('Invalid value entered. Try again')
                        if a==4:
                                d[bd](args[0], args[1], args[2], args[3])
                        elif a==2:
                                d[bd](args[0], args[1])
                        else:
                                d[bd](args[0])
        return bddata
def restore(var, n):
        if socket.gethostname()[0:5]=='s39bd' and n==1:
                path1='/mnt/dbbackup/OCOD/s39bd1iz01.iz.com'
                path2='/mnt/dbbackup/OCOD/s39bd2iz01.iz.com'
                bddata=checkcopy(path1, path2)
        elif socket.gethostname()[0:5]=='s39bd' and n==2:
                path1='/mnt/dbbackup/OCOD/s39bd1iz01.iz.com'
                path2='/mnt/dbbackup/OCOD/s39bd2iz01.iz.com'
                path3='/mnt/dbbackup/RCOD/s39bd1iz02.iz.com'
                path4='/mnt/dbbackup/RCOD/s39bd2iz02.iz.com'
                bddata=checkcopy(path1, path2, path3, path4)
        elif socket.gethostname()[0:5]=='s39bd' and n==3:
                path1='/mnt/dbbackup/RCOD/s39bd1iz02.iz.com'
                path2='/mnt/dbbackup/RCOD/s39bd2iz02.iz.com'
                bddata=checkcopy(path1, path2)
        elif socket.gethostname()[0:8]=='s39crsin' and n==1:
                path1='/mnt/dbbackup/OCOD/s39crsin01.in.com'
                bddata=checkcopy(path1)
        elif socket.gethostname()[0:8]=='s39crsin' and n==2:
                path1='/mnt/dbbackup/OCOD/s39crsin01.in.com'
                path2='/mnt/dbbackup/RCOD/s39crsin02.in.com'
                bddata=checkcopy(path1, path2)
        elif socket.gethostname()[0:8]=='s39crsin' and n==3:
                path1='/mnt/dbbackup/RCOD/s39crsin02.in.com'
                bddata=checkcopy(path1)
        elif socket.gethostname()[0:8]=='s39crsvn' and n==1:
                path1='/mnt/dbbackup/OCOD/s39crsvn01.vn.com'
                bddata=checkcopy(path1)
        elif socket.gethostname()[0:8]=='s39crsvn' and n==2:
                path1='/mnt/dbbackup/OCOD/s39crsvn01.vn.com'
                path2='/mnt/dbbackup/RCOD/s39crsvn02.vn.com'
                bddata=checkcopy(path1, path2)
        elif socket.gethostname()[0:8]=='s39crsvn' and n==3:
                path2='/mnt/dbbackup/RCOD/s39crsvn02.vn.com'
                bddata=checkcopy(path1)
        elif not ((socket.gethostname()[0:6]=='s39crs' or socket.gethostname()[0:5]=='s39bd') and var==1):
                path1='/mnt/dbbackup/OCOD'
                bddata=checkcopy(path1)
        elif not ((socket.gethostname()[0:6]=='s39crs' or socket.gethostname()[0:5]=='s39bd')) and var==2):
                path1='/mnt/dbbackup/RCOD'
                bddata=checkcopy(path1)
        os.system('systemctl stop postgresql')
        os.system('sudo su - postgres -c "rm -rf /var/lib/postgresql/9.6/main/*"')
        subprocess.call(["tar", "-C", "/var/lib/postgresql/9.6/main/", "-xvf", bddata])
        os.system('systemctl start postgresql')
def input(var,n):
        bd = raw_input('The checks were successful. Start the procedure for restoring the database? y,n')
        d = {'y': restore, 'n': exit}
        try:
                if socket.gethostname()[0:6]=='s39crs' or socket.gethostname()[0:5]=='s39bd':
                        d[bd](var, n)
                else:
                        d[bd](var)
        except KeyError:
            print('Invalid value entered. Try again'); input(var, n)
def networkavailable(var, g):
        mount = subprocess.Popen(("ping", "-c4", g), stdout=subprocess.PIPE); exit_code = subprocess.check_output(("sed", "-n", '1,/^---/d;s/%.*//;s/.*, //g;p;q'), stdin=mount.stdout); mount.wait();
        if exit_code==1:
                if var==1:
                        os.system('echo $(date +"%Y%m%d-%H%M%S")     Server with storage OCOD is not available       >> /var/log/backupdb.log')
                        return 1
                else:
                        os.system('echo $(date +"%Y%m%d-%H%M%S")     Server with storage RCOD is not available       >> /var/log/backupdb.log')
                        return 1
        else:
                os.system('echo $(date +"%Y%m%d-%H%M%S")   Server with storage OCOD is available      >> /var/log/backupdb.log')
                return 0
def mountavailable(var, g):
        if socket.gethostname()[0:8]=='s39crsin':
                OCOD='/mnt/dbbackup/OCOD/s39crsin01.in.com'
                RCOD='/mnt/dbbackup/RCOD/s39crsin02.in.com'
        elif socket.gethostname()[0:8]=='s39crsvn':
                OCOD='/mnt/dbbackup/OCOD/s39crsvn01.vn.com'
                RCOD='/mnt/dbbackup/RCOD/s39crsvn02.vn.com'
        elif socket.gethostname()[0:5]=='s39bd':
                OCOD='/mnt/dbbackup/OCOD/s39bd1iz01.iz.com'
                RCOD='/mnt/dbbackup/RCOD/s39bd1iz02.iz.com'
        else:
                OCOD='/mnt/dbbackup/OCOD/'
                RCOD='/mnt/dbbackup/RCOD/'
        if var==1:
                exit_code = subprocess.call(["touch", OCOD+'test'])
                try:
                    ls = subprocess.Popen(("mount"), stdout=subprocess.PIPE); mount = subprocess.check_output(("grep", g), stdin=ls.stdout); ls.wait(); n=5
                except subprocess.CalledProcessError, e:
                    n=1
                if n==1:
                        os.system('mount -a')
                        if n==1:
                                os.system('echo $(date +"%Y%m%d-%H%M%S")   Problems with the operation of the smbd service on the server with the repository of >> /var/log/backupdb.log')
                                return 1
                        else:
                                os.system('echo $(date +"%y%m%d-%h%m%s")   PostgreSQL database backup storage is mounted successfully   >> /var/log/backupdb.log')
                                return 0
                elif exit_code != 0:
                    os.system('echo $(date +"%Y%m%d-%H%M%S")   Problems with the operation of the smbd service on the server with the repository of >> /var/log/backupdb.log')
                    return 1
                else:
                    return 0
        if var==2:
                exit_code = subprocess.call(["touch", RCOD+'test'])
                try:
                    ls = subprocess.Popen(("mount"), stdout=subprocess.PIPE); mount = subprocess.check_output(("grep", g), stdin=ls.stdout); ls.wait(); n=5
                except subprocess.CalledProcessError, e:
                    n=1
                if n==1:
                        os.system('mount -a')
                        if n==1:
                                os.system('echo $(date +"%Y%m%d-%H%M%S")   Problems with the operation of the smbd service on the server with the repository >> /var/log/backupdb.log')
                                return 1
                        else:
                                os.system('echo $(date +"%y%m%d-%h%m%s")   PostgreSQL database backup storage is mounted successfully   >> /var/log/backupdb.log')
                                return 0
                elif exit_code != 0:
                    return 1
                else:
                    return 0
m=0
var=0
a=socket.gethostname()
my_array=massive()
for g in my_array:
        var += 1
        b=networkavailable(var, g)
        if b==0:
                c=mountavailable(var, g)
        elif var != len(my_array):
                continue
        else:
                exit()
        if socket.gethostname()[0:6]=='s39crs' or socket.gethostname()[0:5]=='s39bd':
            if var==1 and (b==0 and c==0):
                m=1
                continue
            elif (var==1 and b==1) or (var==1 and c==1):continue
            elif var==2 and (b==0 and c==0):
                if m==0:
                    input(var, 3)
                else:
                    input(var, 2)
            elif (var==2 and b==1) or (var==2 and c==1):
                if m==0:
                    exit
            else:
                input(var, 1)
        else:
                if var==1 and (b==0 and c==0): input(var, 4)
                elif var==2 and (b==0 and c==0):input(var, 5)
                elif (var==1 and b==1) or (var==1 and c==1): continue
                elif (var==2 and b==1) or (var==2 and c==1): exit
