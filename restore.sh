#!/bin/bash

#Added the ability to restore from a backup of any cluster server

:<<end_of_comments
BD clusters:
bd1iz01.ac.com
bd1iz02.ac.com
bd2iz01.ac.com
bd2iz02.ac.com
and
s39crsvn01.vp.com
s39crsvn02.vp.com
and
s39crsin01.in.com 
s39crsin02.in.com
end_of_comments

#massive - select an array of hypervisor IP addresses depending on the contour
#restore - restoring a database from a database backup
#checkcopy - checking the existence of the entered date/time, when the backup was created
massive()
{
        local -n IP=$1
	IPAC=(10.111.13.178 10.111.15.178)
        IPVP=(10.111.23.101 10.111.25.101)
        IPIN=(10.111.33.66 10.111.35.162)
        IP=()
        if [[ $(hostname | grep vn) ]]
        then
                for t in ${IPVP[@]}; do
                        IP+=($t)
                done
        elif [[ $(hostname | grep ac) ]]; then
                for t in ${IPAC[@]}; do
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
        if [ $# -eq 5 ]; then
                echo
                echo "Backup list $path1"
                ls -l $path1
                echo
                echo "Backup list $path2"
                ls -l $path2
                echo
                echo "Backup list $path3"
                ls -l $path3
                echo
                echo "Backup list $path4"
                ls -l $path4
                echo
        elif [ $# -eq 3 ]; then
                echo
                echo "Backup list $path1"
                ls -l $path1
                echo
                echo "Backup list $path2"
                ls -l $path2
                echo
        else
                echo
                echo "Backup list $path1"
                ls -l $path1
                echo
        fi
                local -n bddata=$3
		echo "Enter the date and time of the PostgreSQL database backup in the format $path1/$(uname -n)-$(date +"%Y%m%d-%H%M%S").tar.gz"
                read bddata
                if [[ -f $(ls $bddata) ]]
                then
                        echo Copy exists
                else
                        echo No copy exists. Choose another? y/n
                        read bd
                        case "$bd" in
                                [y]     ) if [ $# -eq 4 ]; then checkcopy $1 $2 $3 $4; elif [ $# -eq 2 ]; then checkcopy $1 $2; else checkcopy $1; fi;;
                                [n]     ) exit;;
                                *       ) echo Invalid value entered. Try again; if [ $# -eq 4 ]; then checkcopy $1 $2 $3 $4; elif [ $# -eq 2 ]; then checkcopy $1 $2; else checkcopy $1; fi;;
                        esac
                fi
}
restore()
{
	if [[ ($(uname -n | grep bd) && ($? -eq 0)) && ($2 -eq 1) ]]; then
                path1='/mnt/dbbackup/OCOD/bd1iz01.ac.com'
                path2='/mnt/dbbackup/OCOD/bd2iz01.ac.com'
                checkcopy $path1 $path2 bddata
        elif [[ ($(uname -n | grep bd) && ($? -eq 0)) && ($2 -eq 2) ]]; then
                path1='/mnt/dbbackup/OCOD/bd1iz01.ac.com'
                path2='/mnt/dbbackup/OCOD/bd2iz01.ac.com'
                path3='/mnt/dbbackup/RCOD/bd1iz02.ac.com'
                path4='/mnt/dbbackup/RCOD/bd2iz02.ac.com'
                checkcopy $path1 $path2 $path3 $path4 bddata
        elif [[ ($(uname -n | grep bd) && ($? -eq 0)) && ($2 -eq 3) ]]; then
                path1='/mnt/dbbackup/RCOD/bd1iz02.iz.com'
                path2='/mnt/dbbackup/RCOD/bd2iz02.iz.com'
                checkcopy $path1 $path2 bddata
        elif [[ ($(uname -n | grep crsin) && ($? -eq 0)) && ($2 -eq 1) ]]; then
                path1='/mnt/dbbackup/OCOD/crsin01.in.com'
                checkcopy $path1 bddata
        elif [[ ($(uname -n | grep crsin) && ($? -eq 0)) && ($2 -eq 2) ]]; then
                path1='/mnt/dbbackup/OCOD/crsin01.in.com'
                path2='/mnt/dbbackup/RCOD/crsin02.in.com'
                checkcopy $path1 $path2 bddata
        elif [[ ($(uname -n | grep crsin) && ($? -eq 0)) && ($2 -eq 3) ]]; then
                path1='/mnt/dbbackup/RCOD/crsin02.in.com'
                checkcopy path1 bddata
        elif [[ ($(uname -n | grep crsvn) && ($? -eq 0)) && ($2 -eq 1) ]]; then
                path1='/mnt/dbbackup/OCOD/crsvn01.vp.com'
                checkcopy path1 bddata
        elif [[ ($(uname -n | grep crsvn) && ($? -eq 0)) && ($2 -eq 2) ]]; then
                path1='/mnt/dbbackup/OCOD/crsvn01.vp.com'
                path2='/mnt/dbbackup/RCOD/crsvn02.vp.com'
                checkcopy $path1 $path2 bddata
        elif [[ ($(uname -n | grep crsvn) && ($? -eq 0)) && ($2 -eq 3) ]]; then
                path1='/mnt/dbbackup/RCOD/crsvn02.vp.com'
                checkcopy $path1 bddata
        elif [[ ($(uname -n | grep crs) && ($? -eq 1)) && ($(uname -n | grep bd) && ($? -eq 1)) && ($1 -eq 1) ]]; then
                path1='/mnt/dbbackup/OCOD'
                checkcopy $path1 bddata
        elif [[ ($(uname -n | grep crs) && ($? -eq 1)) && ($(uname -n | grep bd) && ($? -eq 1)) && ($1 -eq 2) ]]; then
                path1='/mnt/dbbackup/RCOD'
                checkcopy $path1 bddata
        fi
	systemctl stop postgresql
        sudo su - postgres -c "rm -rf /var/lib/postgresql/9.6/main/*"
        ls $path
        tar -C /var/lib/postgresql/9.6/main/ -xvf $path$(uname -n)-$bddate.tar.gz
        systemctl start postgresql
}
input()
{
        echo The checks were successful. Start database recovery procedure? y,n
        read bd
        case "$bd" in
                [y]     ) if [[ ($(uname -n | grep crs) && ($? -eq 0)) || ($(uname -n | grep bd) && ($? -eq 0)) ]]; then restore "$1" "$2"; else restore "$1"; fi;;
                [n]     ) exit;;
                *       ) echo Invalid value entered. Try again; if [ $# -eq 2 ]; then input $1 $2; else input $1; fi;;
        esac
}
networkavailable()
{
        cc=$(ping -c4 $2 | sed -n '1,/^---/d;s/%.*//;s/.*, //g;p;q')
        if [ $cc -eq 100 ]; then
                if [ $1 = 1 ]
                then
                        echo $(date +"%Y%m%d-%H%M%S")     The OCOD hypervisor server is unavailable   >> /var/log/backupdb.log
                        return 1
                else
                        echo $(date +"%Y%m%d-%H%M%S")     The RCOD hypervisor server is unavailable   >> /var/log/backupdb.log
                        echo The storage facilities of the OCOD and RCOD are inaccessible via ICMP
                        return 1
                fi
        else
                echo $(date +"%Y%m%d-%H%M%S")   $( if [ $1 = 1 ]; then echo OCOD hypervisor server is available; else echo RCOD hypervisor server is available; fi) >> /var/log/backupdb.log
                return 0
        fi
}
mountavailable()
{
        a=$(uname -n)
        if [[ $a == $(uname -n | grep crsin) ]]; then
                OCOD=/mnt/dbbackup/OCOD/$a
                RCOD=/mnt/dbbackup/RCOD/crsin02.in.com
        elif [[ $a == $(uname -n | grep crsvn) ]]; then
                OCOD=/mnt/dbbackup/OCOD/$a
                RCOD=/mnt/dbbackup/RCOD/crsvn02.vp.com
        elif [[ $a == $(uname -n | grep bd) ]]; then
                OCOD=/mnt/dbbackup/OCOD/$a
                RCOD=/mnt/dbbackup/RCOD/bd1iz02.ac.com
        else
                OCOD=/mnt/dbbackup/OCOD/
                RCOD=/mnt/dbbackup/RCOD/
        fi
        if [ $1 = 1 ]; then
                touch $OCOD/test
                CRESULT=$?
                if [[ $(mount | grep $2) && $? -eq 1 ]]; then
                        mount -a
                        MRESULT=$?
                        if [ $MRESULT != 0 ]
                        then
                                echo $(date +"%Y%m%d-%H%M%S")   Problems with the operation of the smbd service on the OCOD hypervisor    >> /var/log/backupdb.log
                                return 1
                        else
                                echo $(date +"%y%m%d-%h%m%s")   Repository backup DB PostgreSQL OCOD is mounted successfully >> /var/log/backupdb.log
                                return 0
			fi
                elif [[ ($(mount | grep $2) && $? -eq 0) && $CRESULT -eq 1 ]]; then
                        echo $(date +"%Y%m%d-%H%M%S")   Problems with the operation of the smbd service on the OCOD hypervisor    >> /var/log/backupdb.log
                        return 1
                elif [[ ($(mount | grep $2) && $? -eq 0) && $CRESULT -eq 0 ]]; then
                        return 0
                fi
        else
                touch $RCOD/test
                CRESULT=$?
                if [[ $(mount | grep $2) && $? -eq 1 ]]; then
                        mount -a
                        MRESULT=$?
                        if [ $MRESULT != 0 ]; then
                                echo $(date +"%Y%m%d-%H%M%S")   Problems with the operation of the smbd service on the RCOD hypervisor    >> /var/log/backupdb.log
                                echo Problems with the operation of the smbd service on the hypervisors of the OCOD and RCOD.
                                return 1
                        else
                                echo $(date +"%y%m%d-%h%m%s")   Repository backup DB PostgreSQL RCOD is mounted successfully >> /var/log/backupdb.log
                                return 0
                        fi
                elif [[ ($(mount | grep $2) && $? -eq 0) && $CRESULT -eq 1 ]]; then
                        echo $(date +"%Y%m%d-%H%M%S")   Problems with the operation of the smbd service on the RCOD hypervisor    >> /var/log/backupdb.log
                        return 1
                elif [[ ($(mount | grep $2) && $? -eq 0) && $CRESULT -eq 0 ]]; then
                        return 0
                fi
        fi
}
m=0
var=0
massive my_array
a=$(uname -n)
for g in ${my_array[@]};
do
        var=$(($var+1))
        networkavailable "$var" "$g"
        b=$?
        if [ "$b" -eq 0 ]; then
                mountavailable "$var" "$g"
                c=$?
        elif [ "$var" -ne "${#my_array[@]}" ]; then
                continue
        else
                exit
        fi
        if [[ ($a == $(uname -n | grep bd)) || ($a == $(uname -n | grep crs)) ]]; then
                if [[ $var -eq 1 && (($b -eq 0) && ($c -eq 0)) ]]; then m=1; continue
                elif [[ (($var -eq 1) && ($b -eq 1)) || (($var -eq 1) && ($c -eq 1)) ]]; then continue
                elif [[ $var -eq 2 && (($b -eq 0) && ($c -eq 0)) ]]; then
                        if [ "$m" -eq 0 ]; then input "$var" "3"; else input "$var" "2"; fi
                elif [[ (($var -eq 2) && ($b -eq 1)) || (($var -eq 2) && ($c -eq 1)) ]]; then
                        if [ "$m" -eq 0 ]; then exit; else input "$var" "1"; fi
                fi
        else
                if [[ ($var -eq 1) && (($b -eq 0) && ($c -eq 0)) ]]; then input "$var"
                elif [[ ($var -eq 2) && (($b -eq 0) && ($c -eq 0)) ]]; then input "$var"
                elif [[ (($var -eq 1) && ($b -eq 1)) || (($var -eq 1 ) && ($c -eq 1)) ]]; then continue
                elif [[ (($var -eq 2) && ($b -eq 1)) || (($var -eq 2) && ($c -eq 1)) ]]; then exit
                fi
	fi
done
