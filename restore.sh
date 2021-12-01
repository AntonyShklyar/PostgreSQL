#!/bin/bash
OCOD=/mnt/dbbackup/OCOD
RCOD=/mnt/dbbackup/RCOD
massive - select an array of hypervisor IP addresses depending on the contour
restore - restoring a database from a database backup
checkcopy - checking the existence of the entered date/time, when the backup was created
massive()
{
        local -n IP=$1
	IPIZ=(10.111.13.178 10.111.15.178)
        IPVN=(10.111.23.101 10.149.25.101)
        IPIN=(10.111.33.66 10.111.35.162)
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
checkcopy()
{
		if [ $var = 1 ]
        	then
                	path='/mnt/dbbackup/OCOD/'
        	elif [ $var = 2 ]
        	then
                	path='/mnt/dbbackup/RCOD/'
        	fi
		echo Backup list
		ls -l $path
                echo Enter the date and time of the PostgreSQL database backup in the format $(date +"%Y%m%d-%H%M%S")
                read bddate
                if [[ -f $(ls $path$bddate) ]]
                then
                        echo Backup exists
                        break
                else
                        echo No copy exists. Choose another one? y/n
                        read bd
                        case "$bd" in
                                [y]     ) checkcopy;;
                                [n]     ) exit;;
                                *       ) echo Invalid value entered. Try again; checkcopy
                        esac
                fi
}
restore()
{
	if [ $var = 1 ]
        then
                path='/mnt/dbbackup/OCOD/'
        elif [ $var = 2 ]
        then
                path='/mnt/dbbackup/RCOD/'
        fi
	checkcopy
	systemctl stop postgresql
        sudo su - postgres -c "rm -rf /var/lib/postgresql/9.6/main/*"
        ls $path
        tar -C /var/lib/postgresql/9.6/main/ -xvf $path$(uname -n)-$bddate.tar.gz
        systemctl start postgresql
}
input()
{
        echo The checks were successful. Start the procedure for restoring the database? y,n
        read bd
        case "$bd" in
                [y]     ) restore $var;;
                [n]     ) exit;;
                *       ) echo Invalid value entered. Try again; input
        esac
}
var=0
massive my_array
for g in ${my_array[@]};
do
        var=$(($var+1))
        cc=$(ping -c4 $g | sed -n '1,/^---/d;s/%.*//;s/.*, //g;p;q')
        if [[ $cc -eq 100 ]]
        then
                if [ $var = 1 ]
                then
                        echo $(date +"%Y%m%d-%H%M%S")     Server with storage of OCOD is not available   >> /var/log/backupdb.log
                        continue
                elif [[ $var = 2 ]]; then
                        echo $(date +"%Y%m%d-%H%M%S")     Server with storage of RCOD is not available   >> /var/log/backupdb.log
			break
                fi
        else
 		echo $(date +"%Y%m%d-%H%M%S")   $( if [ $var = 1 ]; then echo Server with storage of OCOD is available; elif [ $var = 2 ]; then echo  Server with storage of RCOD is available; fi) >> /var/log/backupdb.log
                if [ $var = 1 ]
                then
                        touch $OCOD/test
                        CRESULT=$?
                        if [[ $(mount | grep "//$g/bkp2/dbbackup/") && $? -eq 1 ]]
                        then
                                mount -a
                                MRESULT=$?
                                if [ $MRESULT != 0 ]
                                then
                                        echo $(date +"%Y%m%d-%H%M%S")   Problems with the operation of the smbd service on the server with the repository of OCOD    >> /var/log/backupdb.log
                                        continue
                                else
                                        echo $(date +"%y%m%d-%h%m%s")   PostgreSQL database backup storage is OCOD mounted successfully >> /var/log/backupdb.log
                                        input
					break
                                fi
                        elif [[ ($(mount | grep "//$g/bkp2/dbbackup/") && $? -eq 0) && $CRESULT -eq 1 ]]; then
                                echo $(date +"%Y%m%d-%H%M%S")   Problems with the operation of the smbd service on the server with the repository of OCOD    >> /var/log/backupdb.log
                                continue
                        elif [[ ($(mount | grep "//$g/bkp2/dbbackup/") && $? -eq 0) && $CRESULT -eq 0 ]]; then
                                input
				break
                        fi

                fi
		if [ $var = 2 ]
                then
                        touch $RCOD/test
                        CRESULT=$?
                        if [[ $(mount | grep "//$g/bkp2/dbbackup/") && $? -eq 1 ]]
                        then
                                mount -a
                                MRESULT=$?
                                if [ $MRESULT != 0 ]
                                then
                                        echo $(date +"%Y%m%d-%H%M%S")   Problems with the operation of the smbd service on the server with the repository of RCOD    >> /var/log/backupdb.log
					echo Problems with the operation of the smbd service on the hypervisors of the OCOD and RCOD. Completion of work
                                        break
                                else
					echo $(date +"%y%m%d-%h%m%s")    PostgreSQL database backup storage is RCOD mounted successfully >> /var/log/backupdb.log
					input
                                fi
                        elif [[ ($(mount | grep "//$g/bkp2/dbbackup/") && $? -eq 0) && $CRESULT -eq 1 ]]; then
                                echo $(date +"%Y%m%d-%H%M%S")   Problems with the operation of the smbd service on the server with the repository of RCOD    >> /var/log/backupdb.log
                                break
                        elif [[ ($(mount | grep "//$g/bkp2/dbbackup/") && $? -eq 0) && $CRESULT -eq 0 ]]; then
                                input
                                break
                        fi
                fi
         fi
done

