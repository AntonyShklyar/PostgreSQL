#!/bin/bash

#massive - selection of an array of hypervisor IP addresses depending on the contour
#backup - backup to the mounted spheres of the OCOD and RCOD
#sync - synchronization of the contents of the mounted ball of the OCOD and RCOD
#search - checking 'sync' trigger conditions

#Creating a log file for long-term storage of script events
if [[ ! -f /var/log/debugdb.log ]]; then touch /var/log/debugdb.log; chmod 666 /var/log/debugdb.log; fi
#If the size of 1 GB is exceeded, the debug.log is deleted and recreated
if [[ $(find /var/log/ -name debugdb.log -size +1G) ]]; then rm -f /var/log/debugdb.log; fi 
cp /var/log/backupdb.log /var/log/debugdb.log
#Creating a log file to store the events of one script launch
rm -f /var/log/backupdb.log
touch /var/log/backupdb.log
chmod 666 /var/log/backupdb.log
#Selection of the main and backup storages depending on the data center in which the server with the database is located 
if [[ $(hostname | grep 01) ]]
then
	dir1=/mnt/dbbackup/OCOD
	dir2=/mnt/dbbackup/RCOD
elif [[ $(hostname | grep 02) ]]
then	
	dir1=/mnt/dbbackup/RCOD
	dir2=/mnt/dbbackup/OCOD
fi
massive()
{
	#Selecting IP-addresses of the main and backup storages
	local -n IP=$1
	if [[ $(hostname | grep 01) ]]
	then	
        	IPIZ=(10.111.13.178 10.111.15.178)
        	IPVN=(10.111.23.101 10.149.25.101)
        	IPIN=(10.111.33.66 10.111.35.162)
	elif [[ $(hostname | grep 02) ]]
	then
		IPIZ=(10.111.15.178 10.111.13.178)
       		IPVN=(10.149.25.101 10.111.23.101)
      		IPIN=(10.111.35.162 10.111.33.66)
	fi
        IP=()
        if [[ $(hostname | grep vn) ]]
        then
                for t in ${IPVN[@]}; do
                        IP+=($t)
                done
        elif [[ $(hostname | grep iz) ]]; then
                for t in ${IPIZ[@]}; do
                        IP+=($t)
                done
        else
                for t in ${IPIN[@]}; do
                        IP+=($t)
                done
        fi
}
backup()
{
	var=$1
	if [[ ! -d /var/lib/postgresql/wal_archive/ ]]; then mkdir /var/lib/postgresql/wal_archive/ && chown postgres /var/lib/postgresql/wal_archive/; fi
	if [[ ($var = 1) && $(hostname | grep 01) ]]
	then
		#Defining a directory for temporary storage of backups
		path='/mnt/dbbackup/OCOD/temp'
		#Deleting backups that were created incorrectly during the previous operation of the script due to the shutdown/freezing of the server from the database
		rm -f $path/base.tar.gz
	elif [[ ($var = 1) && $(hostname | grep 02) ]]
	then
		path='/mnt/dbbackup/RCOD/temp'
		rm -f $path/base.tar.gz
	elif [[ ($var = 2) && $(hostname | grep 01) ]]
	then
		path='/mnt/dbbackup/RCOD/temp'
		rm -f $path/base.tar.gz
	elif [[ ($var = 2) && $(hostname | grep 02) ]]
	then
		path='/mnt/dbbackup/OCOD/temp'
		rm -f $path/base.tar.gz
	fi
	#Determining an array of IP-addresses of servers with database clusters
	IP=(s39bd1iz01.iz.com s39bd1iz02.iz.com s39bd2iz01.iz.com s39bd2iz02.iz.com s39crsvn01.vn.com s39crsvn02.vn.com s39crsin01.in.com s39crsin02.in.com)
	a=$(uname -n)
	m=0
	for i in ${IP[@]}
	do
		if [ "$a" == "$i" ]
		then
			m=1
			if [[ ($(sudo systemctl status corosync) && ($? -eq 0)) && ($(sudo systemctl status pacemaker) && ($? -eq 0)) ]]; then
				#Creating a backup archive on a server with database clusters
				TIME=$($(time sudo su - postgres -c "pg_basebackup -D $path -Ft -z -Z 9 -P --xlog && echo $(date +"%Y%m%d-%H%M%S")     PostgreSQL Database Backup Successful >> /var/log/backupdb.log || echo $(date +"%Y%m%d-%H%M%S")     PostgreSQL DB backup Unsuccessful >> /var/log/backupdb.log") 2>&1 > /dev/null | grep real | awk '{print $2}' | sed 's/m.*//g')
				if [[ ($(sudo systemctl status corosync) && ($? -ne 0)) && ($(sudo systemctl status pacemaker) && ($? -ne 0)) ]];
                        	then
                        		echo $(date +"%Y%m%d-%H%M%S") PostgreSQL DB is not running >> /var/log/backupdb.log
					#Deleting an incorrectly created backup due to the disabling of corosync and pacemaker services during the creation of the backup
                                	rm -f $path/* && echo $(date +"%Y%m%d-%H%M%S")     An incorrectly created backup copy of the database has been deleted $( if [[ ($var = 1) && $(hostname | grep 01) ]]; then echo OCOD; elif [[ ($var = 1) && $(hostname | grep 02) ]]; then echo RCOD; elif [[ ($var = 2) && $(hostname | grep 01) ]]; then echo OCOD; elif [[ ($var = 2) && $(hostname | grep 02) ]]; then echo RCOD; fi) >> /var/log/backupdb.log
					#Program termination due to disconnection of corosync and pacemaker services during backup creation
                                	exit
                        	else
                                	bdarch=$(uname -n)-$(date +"%Y%m%d-%H%M%S").tar.gz
                                	mv $path/base.tar.gz $path/$bdarch
                                	mv $path/* $(echo $path | cut -c 1-19)
					#Creating a backup copy of WAL files
                                        sleep 15m
                                        WAL='/tmp/wal'
                                        rm -rf $WAL
                                        mkdir $WAL
                                        find /var/lib/postgresql/wal_archive/ -maxdepth 1 -mmin -$(expr $TIME + 30) -type f -exec cp -pr {} $WAL \;
                                        find /var/lib/postgresql/9.6/main/pg_xlog/ -maxdepth 1 -mmin -$(expr $TIME + 30) -type f -exec cp -pr {} $WAL \;
                                        cd $WAR ; tar -cpzf $(echo $path | cut -c 1-18)/wal_$bdarch *
					break
				fi
			elif [[ ($(sudo systemctl status corosync) && ($? -ne 0)) && ($(sudo systemctl status pacemaker) && ($? -ne 0)) ]]; then
				echo $(date +"%Y%m%d-%H%M%S") PostgreSQL DB is not running >> /var/log/backupdb.log
				#Program termination due to inoperability of corosync and pacemaker services
				exit
			fi
		fi
	done 
	if [[ $(systemctl status postgresql) && ($? -eq 0) ]]
	then
		#Creating a backup archive on a server with a database (not a cluster)
		TIME=$($(time sudo su - postgres -c "pg_basebackup -D $path -Ft -z -Z 9 -P --xlog && echo $(date +"%Y%m%d-%H%M%S")     PostgreSQL Database Backup Successful >> /var/log/backupdb.log || echo $(date +"%Y%m%d-%H%M%S")     PostgreSQL DB backup Unsuccessful >> /var/log/backupdb.log") 2>&1 > /dev/null | grep real | awk '{print $2}' | sed 's/m.*//g')
		if [[ $(systemctl status postgresql) && ($? -ne 0) ]]
		then
			echo $(date +"%Y%m%d-%H%M%S") PostgreSQL database service postgresql.service is not running >> /var/log/backupdb.log
			#Deleting an incorrect backup because the postgresql service was disabled while the backup was being created
			rm -f $path/* && echo $(date +"%Y%m%d-%H%M%S")     An incorrectly created backup copy of the database has been deleted $( if [[ ($var = 1) && $(hostname | grep 01) ]]; then echo OCOD; elif [[ ($var = 1) && $(hostname | grep 02) ]]; then echo RCOD; elif [[ ($var = 2) && $(hostname | grep 01) ]]; then echo OCOD; elif [[ ($var = 2) && $(hostname | grep 02) ]]; then echo RCOD; fi) >> /var/log/backupdb.log
			#Program termination due to shutdown of postgresql service during backup
			exit
		else
			bdarch=$(uname -n)-$(date +"%Y%m%d-%H%M%S").tar.gz
			mv $path/base.tar.gz $path/$bdarch
        		mv $path/* $(echo $path | cut -c 1-19) 
			#Creating a backup copy of WAL files
			if [[ ! $(hostname | grep zbx) ]]
			then
				sleep 15m
				WAL='/tmp/wal'
				rm -rf $WAL
				mkdir $WAL
				find /var/lib/postgresql/wal_archive/ -maxdepth 1 -mmin -$(expr $TIME + 30) -type f -exec cp -pr {} $WAL \;
				find /var/lib/postgresql/9.6/main/pg_xlog/ -maxdepth 1 -mmin -$(expr $TIME + 30) -type f -exec cp -pr {} $WAL \;
				cd $WAR ; tar -cpzf $(echo $path | cut -c 1-18)/wal_$bdarch *
				break
			fi
			break
		fi
	elif [ $m = 0 ]; then
		echo echo $(date +"%Y%m%d-%H%M%S") PostgreSQL database service postgresql.service is not running >> /var/log/backupdb.log
		#Termination of the program due to the inoperability of the postgresql service
		exit
	fi
}
sync()
{
		#Synchronization of contents of storages /mnt/dbbackup/OCOD and /mnt/dbbackup/RCOD in Active-Active mode 
                if [ $1 = 0 ]
                then
                        var1=/mnt/dbbackup/OCOD/
                        var2=/mnt/dbbackup/RCOD/
                        if [ $2 = 0 ]
                        then
                                a=($(ls -rI "wal*" $var2 | grep tar.gz))
                                b=($(ls -rI "wal*" $var1 | grep tar.gz))
                                c=$(ls -I "wal*" $var1 | grep tar.gz | wc -l)
                                d=$(ls -I "wal*" $var2 | grep tar.gz | wc -l)
                        else
                                a=($(ls -t $var2 | grep wal))
                                b=($(ls -t $var1 | grep wal))
                                c=$(ls -t $var1 | grep wal | wc -l)
                                d=$(ls -t $var2 | grep wal | wc -l)
                        fi
                else
                        var1=/mnt/dbbackup/RCOD/
                        var2=/mnt/dbbackup/OCOD/
                        if [ $2 = 0 ]
                        then
                                a=($(ls -rI "wal*" $var2 | grep tar.gz))
                                b=($(ls -rI "wal*" $var1 | grep tar.gz))
                                c=$(ls -I "wal*" $var1 | grep tar.gz | wc -l)
                                d=$(ls -I "wal*" $var2 | grep tar.gz | wc -l)
                        else
                                a=($(ls -t $var2 | grep wal))
                                b=($(ls -t $var1 | grep wal))
                                c=$(ls -t $var1 | grep wal | wc -l)
                                d=$(ls -t $var2 | grep wal | wc -l)
                        fi
                fi
                if [[ $c = 0 ]]
                then
                        for j in ${a[@]}
                        do
                                cp $var2$j $var1;
                        done
                fi
                for j in ${a[@]}
                do
                        e=0
                        for k in ${b[@]}
                        do
                                        if [[ $j != $k ]]
                                        then
                                                        e=$(($e+1))
                                                        if [[ $e -lt ${#b[@]} ]]; then continue
                                                        elif [[ $e -eq ${#b[@]} ]]
                                                        then
                                                                cp $var2$j $var1 && echo $(date +"%Y%m%d-%H%M%S")     Synchronization of archive $(echo $j) of the backup copy of the DB PostgreSQL RCOD and OCOD Successfully >> /var/log/backupdb.log || echo $(date +"%Y%m%d-%H%M%S")     Synchronization of archive $(echo $j) of the backup copy of the DB PostgreSQL RCOD and OCOD Unsuccessfully >> /var/log/backupdb.log
                                                        fi
                                        else
                                                if [[ ! $(diff $var2$j $var1$k) ]]; then
                                                        if [[  ${#b[@]} = 1 ]]; then echo j - $j; echo Yes; break; fi
                                                        delete=($k)
                                                                for target in "${delete[@]}"; do
                                                                        for n in "${!b[@]}"; do
                                                                               if [[ ${b[n]} = "${delete[0]}" ]]; then
                                                                                        unset 'b[n]'
                                                                                fi
                                                                        done
                                                                done
                                                        break
                                                else
                                                        cp $var2$j $var1 && echo $(date +"%Y%m%d-%H%M%S")     Synchronization of archive $(echo $j) of the backup copy of the DB PostgreSQL RCOD and OCOD Successfully >> /var/log/backupdb.log || echo $(date +"%Y%m%d-%H%M%S")     Synchronization of archive $(echo $j) of the backup copy of the DB PostgreSQL RCOD and OCOD Unsuccessfully >> /var/log/backupdb.log
                                                        if [[  ${#b[@]} = 1 ]]; then echo Yes2; break; fi
                                                        delete=($k)
                                                                for target in "${delete[@]}"; do
                                                                        for n in "${!b[@]}"; do
                                                                                if [[ ${b[n]} = "${delete[0]}" ]]; then
                                                                                        unset 'b[n]'
                                                                                fi
                                                                       done
                                                                done
                                                        break
                                                fi
                                        fi
                        done
                done
if [ $1 = 0 ]
then
                        if [ $2 = 0 ]
                        then
                                b=($(ls -rI "wal*" $var1 | grep tar.gz))
                                c=$(ls -I "wal*" $var1 | grep tar.gz | wc -l)
                        else
                                b=($(ls -t $var1 | grep wal))
                                c=$(ls -t $var1 | grep wal | wc -l)
                        fi
                else
                        if [ $2 = 0 ]
                        then
                                b=($(ls -rI "wal*" $var1 | grep tar.gz))
                                c=$(ls -I "wal*" $var1 | grep tar.gz | wc -l)
                        else
                                b=($(ls -t $var1 | grep wal))
                                c=$(ls -t $var1 | grep wal | wc -l)
                        fi
                fi
if [[ $c -gt $d ]]
then
        for j in ${b[@]}
        do
        e=0
                for k in ${a[@]}
                do
                        if [[ $j != $k ]]
                        then
                                e=$(($e+1))
                                if [[ $e -lt $d ]]; then continue
                                elif [[ $e -eq $d ]]
                                then
                                        cp $var1$j $var2 && echo $(date +"%Y%m%d-%H%M%S")     Synchronization of archive $(echo $j) of the backup copy of the DB PostgreSQL RCOD and OCOD Successfully >> /var/log/backupdb.log || echo $(date +"%Y%m%d-%H%M%S")     Synchronization of archive $(echo $j) of the backup copy of the DB PostgreSQL RCOD and OCOD Unsuccessfully >> /var/log/backupdb.log
                                        break
                                fi
                        fi
               done
       done
fi
}
search()
{
	#Checking sync trigger conditions
	for (( i = 0; i < 2; i++))
	do
		if [[ ($i = 1) && $(hostname | grep zbx) ]]; then break; fi
        	if [ $i = 0 ]
        	then
                	if [[ $(ls -I "wal*" /mnt/dbbackup/RCOD/ | grep tar.gz | wc -l) -eq $(ls -I "wal*" /mnt/dbbackup/OCOD/ | grep tar.gz | wc -l) ]]
                	then
                        	continue
                	elif [[ $(ls -I "wal*" /mnt/dbbackup/RCOD/ | grep tar.gz | wc -l) -gt $(ls -I "wal*" /mnt/dbbackup/OCOD/ | grep tar.gz | wc -l) ]]
                	then
                        	sync 0 0
                        	continue
                	elif [[ $(ls -I "wal*" /mnt/dbbackup/RCOD/ | grep tar.gz | wc -l) -lt $(ls -I "wal*" /mnt/dbbackup/OCOD/ | grep tar.gz | wc -l) ]]
                	then
                        	sync 1 0
                        	continue
			fi
        	elif [ $i = 1 ]
        	then
                	if [[ $(ls /mnt/dbbackup/RCOD/ | grep wal | wc -l) -eq $(ls /mnt/dbbackup/OCOD/ | grep wal | wc -l) ]]
                	then
                		break
                	elif [[ $(ls /mnt/dbbackup/RCOD/ | grep wal | wc -l) -gt $(ls /mnt/dbbackup/OCOD/ | grep wal | wc -l) ]]
                	then
                        	sync 0 1
                	elif [[ $(ls /mnt/dbbackup/RCOD/ | grep wal | wc -l) -lt $(ls /mnt/dbbackup/OCOD/ | grep wal | wc -l) ]]
                	then
                        	sync 1 1
			fi
                fi
	done
}
var=0
massive my_array
for g in ${my_array[@]};
do
	var=$(($var+1))
	#Checking the availability of hypervisor servers with ICMP backup storages
      	cc=$(ping -c4 $g | sed -n '1,/^---/d;s/%.*//;s/.*, //g;p;q')
        if [[ $cc -eq 100 ]]
        then
                if [ $var = 1 ]
                then
			echo $(date +"%Y%m%d-%H%M%S")     Server with storage $(if [[ $(hostname | grep 01) ]]; then echo OCOD; elif [[ $(hostname | grep 02) ]]; then echo RCOD; fi) is not available	>> /var/log/backupdb.log 
                        continue
                elif [[ $var = 2 ]]; then
			echo $(date +"%Y%m%d-%H%M%S")     Server with storage $(if [[ $(hostname | grep 01) ]]; then echo OCOD; elif [[ $(hostname | grep 02) ]]; then echo RCOD; fi) is not available	>> /var/log/backupdb.log 
                        break
                fi
        else
		echo $(date +"%Y%m%d-%H%M%S")	$( if [[ ($var = 1) && $(hostname | grep 01) ]]; then echo Server with storage of OCOD is available; elif [[ ($var = 1) && $(hostname | grep 02) ]]; then echo Server with storage of RCOD is available; elif [[ ($var = 2) && $(hostname | grep 01) ]]; then echo Server with storage of OCOD is available; elif [[ ($var = 2) && $(hostname | grep 02) ]]; then echo Server with storage of RCOD is available; fi)	>> /var/log/backupdb.log
                if [ $var = 1 ]
                then
			#Mounting storages on a server with a database, if not mounted
			#Checking the ability to write to storages mounted on a server with a database 
                        touch $dir1/test
                        CRESULT=$?
			if [[ ! $(mount | grep "//$g/bkp2/dbbackup/") ]]
                        then
				mount -a
				MRESULT=$?
				if [ $MRESULT != 0 ]
				then
					echo $(date +"%Y%m%d-%H%M%S")	Problems with the operation of the smbd service on the server with the repository of $(if [[ $(hostname | grep 01) ]]; then echo OCOD; elif [[ $(hostname | grep 02) ]]; then echo RCOD; fi)	>> /var/log/backupdb.log
					continue
				else 
					echo $(date +"%y%m%d-%h%m%s")	PostgreSQL database backup storage is $(if [[ $(hostname | grep 01) ]]; then echo OCOD; elif [[ $(hostname | grep 02) ]]; then echo RCDO; fi) mounted successfully	>> /var/log/backupdb.log
					backup $var $bdarch
				fi
			elif [[ $(mount | grep "//$g/bkp2/dbbackup/") && $CRESULT -eq 1 ]]; then
				echo $(date +"%Y%m%d-%H%M%S")	Problems with the operation of the smbd service on the server with the repository of $(if [[ $(hostname | grep 01) ]]; then echo OCOD; elif [[ $(hostname | grep 02) ]]; then echo RCOD; fi) >> /var/log/backupdb.log
				continue
			elif [[ $(mount | grep "//$g/bkp2/dbbackup/") && $CRESULT -eq 0 ]]; then
				backup $var $bdarch
                        fi

                fi
                if [ $var = 2 ]
                then
			#Mounting storages on a server with a database, if not mounted
			#Checking the ability to write to storages mounted on a server with a database
                        touch $dir2/test
                        CRESULT=$?
                        if [[ ! $(mount | grep "//$g/bkp2/dbbackup/") ]]
                        then
				mount -a
				MRESULT=$?
				if [ $MRESULT != 0 ]
				then
					echo $(date +"%Y%m%d-%H%M%S")	Problems with the operation of the smbd service on the server with the repository of $(if [[ $(hostname | grep 01) ]]; then echo RCOD; elif [[ $(hostname | grep 02) ]]; then echo OCOD; fi)	>> /var/log/backupdb.log
					exit
				elif [[ $(mount | grep "//${my_array[0]}/bkp2/dbbackup/") && $CRESULT -eq 1 ]]; then
					#Creating a backup copy to the backup storage because the main storage is unavailable
					backup $var
					exit
				elif [[ -e $dir1/$bdarch ]]; then
					#Replication (copying of the created backup) to the backup storage
					cp $dir1/$bdarch $dir2/ && echo $(date +"%Y%m%d-%H%M%S")	Replicating a PostgreSQL database backup to another data center storage Successfully 	>> /var/log/backupdb.log || echo $(date +"%Y%m%d-%H%M%S")        Replicating a PostgreSQL database backup to another data center storage Unsuccessfully       >> /var/log/backupdb.log
					if [[ ! $(hostname | grep zbx) ]]; then cp $dir1/wal_$bdarch $dir2; fi
					search	
					break
				else
					echo $(date +"%y%m%d-%h%m%s")	PostgreSQL database backup storage is $(if [[ $(hostname | grep 01) ]]; then echo RCOD; elif [[ $(hostname | grep 02) ]]; then echo OCOD; fi) mounted successfully	>> /var/log/backupdb.log
					#Creating a backup copy in the backup storage, since there is no copy in the main storage
					backup $var
				fi
			elif [[ $(mount | grep "//${my_array[0]}/bkp2/dbbackup/") && $CRESULT -eq 1 ]]; then
				#Creating a backup copy to the backup storage because the main storage is unavailable
				backup $var
				exit
			elif [[ $(mount | grep "//$g/bkp2/dbbackup/") && $CRESULT -eq 0 ]]; then
				if [[ -e $dir1/$bdarch ]]
				then
					#Replication (copying of the created backup) to the backup storage
					cp $dir1/$bdarch $dir2 && echo $(date +"%Y%m%d-%H%M%S")	Replicating a PostgreSQL database backup to another data center storage Successfully 	>> /var/log/backupdb.log || echo $(date +"%Y%m%d-%H%M%S")        Replicating a PostgreSQL database backup to another data center storage Unsuccessfully       >> /var/log/backupdb.log
					if [[ ! $(hostname | grep zbx) ]]; then cp $dir1/wal_$bdarch $dir2; fi
					search
					break
				else
					#Creating a backup copy in the backup storage, since there is no copy in the main storage
					backup $var
				fi
                        fi
                fi
        fi
done
