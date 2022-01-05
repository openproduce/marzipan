# Installing the register point-of-sale application:

* PACKAGES  
  - sudo apt-get install git  
  - sudo apt-get install mysql-client  
  - sudo apt-get install mysql-server
  - sudo apt-get install python-dev-is-python3  
  - sudo apt-get install python3-pip  
  - sudo apt-get install libmysqlclient-dev
  - sudo apt-get install texlive
  - sudo apt-get install libcurl4-openssl-dev
  - pip3 install mysqlclient
  - pip3 install pycurl
  - pip3 install sqlalchemy
  - pip3 install lxml
  - pip3 install suds-jurko

* Get the source code:

        $ git clone https://github.com/openproduce/marzipan.git

* Set the mysql root password via "sudo mysql", if it isn't already set

* Set up the databases and database users.  Note that as currently written this script will drop an existing database, so do not run it if your database exists and has data you want to keep!  If your databases don't exist yet this will create them.

        $ mysql -u root -p < scripts/setup.sql

* Unzip sample data files:

        $ bunzip2 -k sample-data/op-register_tape-sample.sql.bz2
        $ bunzip2 -k sample-data/op-inventory-sample.sql.bz2

* Load data (real inventory data, fake customer data)

        $ mysql -u marzipan -p
        mysql> use register_tape
        mysql> source sample-data/op-register_tape-sample.sql
        mysql> use inventory
        mysql> source sample-data/op-inventory-sample.sql
        mysql> quit
        Bye
        $ 

* Copy register/config.py.tmpl to register/config.py and, in register/config.py, change the secrets (in all caps) to their values for your application.

* Set up your receipt printer (strongly recommended) and label printer (optional).  You'll want to set the name of the queue in the "receipt-printer" section of register/config.py

  For the popular Star Micronics TSP100 and other SM receipt printers, instructions are here:

  http://www.starmicronics.com/absolutefm/absolutefm/attachments/168/application%20note%20-%20installing%20star%20printers%20on%20ubuntu-kubuntu%2010%2004%20%20ethernet%20%20usb.pdf

  http://wiki.koha-community.org/wiki/TSP100_thermal_receipt_printers_on_Ubuntu_12.04

* Run the cash register interface.  Do this in a terminal that can
  respond to terminal control codes, such as an xterm (e.g., don't use
  an Emacs shell buffer or other pseudo-terminal, because it won't
  work in there):

        $ cd marzipan
        $ python3 register/ui.py 2> error.log

* Make the computer boot directly into text mode, if desired.  Edit
  /etc/default/grub:

    - disable GRUB_CMDLINE_LINUX_DEFAULT="quiet splash" by adding # at the beginning.
    - set GRUB_CMDLINE_LINUX="" to GRUB_CMDLINE_LINUX="quiet splash text"
    - remove # from the line GRUB_TERMINAL="console" to disable graphical terminal.


        Then run 'update-grub', set system target, and reboot.
 
        $ sudo vi /etc/default/grub
        $ sudo update-grub
	$ sudo systemctl set-default multi-user.target


        You can then reboot, or wait until you complete the next step.

* Make the computer's TTY1, 2, and 3 run the POS instead of prompting for
  login:  Edit /etc/init/tty1.conf and replace the line

        exec /sbin/getty -8 -34800 tty1

        with

        exec /sbin/getty -8 -n -l /home/openproduce/marzipan/register/launch.sh 38400 tty1

* Or, for later versions of ubuntu:
  sudo systemctl edit getty@tty1
  and enter the following:
    [Service]
    ExecStart=  
    ExecStart=-/sbin/agetty --autologin openproduce --noclear %I 38400 linux

  And add the launch script to your shell .profile:

    if [[ -z "$DISPLAY" ]] && [[ $(tty) == /dev/tty1 ]]; then
      exec /path/to/marzipan/register/launch.sh
    fi

  Now do the same for tty2 and tty3 if desired.

  Now reboot.  You should find ALT-F1 through ALT-F3 run separate copies of
  the POS, and ALT-F4 etc are available for administrative login.

# Installing the web tools:

  These instructions should work on Ubuntu or Debian GNU/Linux.

* Make sure you have Python 3 installed
  (It probably is by default, but check with `python --version`.)

* Install other needed packages:

        $ sudo apt-get update
        $ sudo apt-get install apache2
        $ sudo apt-get install apache2-utils
        $ sudo apt-get install mysql-common
        $ sudo apt-get install mysql-server
        $ sudo apt-get install libmysqlclient-dev
        $ sudo apt-get install git
        $ sudo apt-get install python-dev-is-python3
        $ sudo apt-get install python3-pip python3-wheel
        $ sudo pip3 install SQLAlchemy
        $ sudo pip install mysqlclient
	$ sudo apt-get install libdbi-perl
	$ sudo apt-get install libdbd-mysql-perl

* Set up MySQL root credentials:
https://dev.mysql.com/doc/mysql-installation-excerpt/5.7/en/default-privileges.html

* Install Database:

        $ mysql -u root -p
        mysql> CREATE DATABASE register_tape;
        mysql> CREATE DATABASE inventory;
        mysql> CREATE USER 'marzipan' IDENTIFIED BY 'YOUR.STAFF.PASSWORD';
        mysql> GRANT ALL PRIVILEGES ON register_tape.* TO marzipan@localhost;
        mysql> GRANT ALL PRIVILEGES ON inventory.* TO marzipan@localhost;
        mysql> FLUSH PRIVILEGES;
        mysql> quit
        Bye
        $ 

* Unzip sample data files:
        $ bunzip2 -k sample-data/op-register_tape-sample.sql.bz2
        $ bunzip2 -k sample-data/op-inventory-sample.sql.bz2

* Load data 
        $ mysql -u marzipan -p
        mysql> use register_tape
        mysql> source sample-data/op-register_tape-sample.sql
        mysql> use inventory
        mysql> source sample-data/op-inventory-sample.sql
        mysql> quit
        Bye
        $

* Configure db for grouping
  	$ mysql -u marzipan -p
	mysql> SET GLOBAL sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));

* Update DB config with new DB credentials:

 * Staff op_tools:
  * Update web/staff/op_tools/db_config.py with correct database credentials
  * Update web/staff/dash.pl with correct database credentials
  * Update web/staff/dash_booze.pl with correct database credentials


* Create the marzipan web root:

        $ cd /var/www
        $ git clone git@github.com:openproduce/marzipan.git
        $ chown www-data.www-data marzipan

* Create a `.htpasswd` file for staff web authorization:

        $ htpasswd -c /var/www/marzipan/web/staff/.htpasswd YOUR.STAFF.USERNAME

* Configure and restart Apache HTTP:

        $ cp /var/www/marzipan/sample-config/apache-config-example.conf \
             /etc/apache2/sites-available/marzipan.conf

  Edit `/etc/apache2/sites-available/marzipan.conf` in the obvious way
  -- search for "YOUR." as a prefix for things you'll want to change.
  Then run:

        $ sudo a2enmod cgi
        $ sudo a2ensite marzipan
        $ sudo service apache2 restart
	
If you are planning to connect to a database over a network connection, and you are using a laptop, you will need to turn off wifi powersave in order to avoid lag:

	$ sudo nano /etc/NetworkManager/conf.d/default-wifi-powersave-on.conf

Change `wifi.powersave = 3` to `wifi.powersave = 2`

# SETTING UP MYSQL REPLICATION IN THE CLOUD

 * setup master
  * server-id
  * bin-logs

 * get a cloud version of your database
 * ssh tunnel

 * set up slave server-id with different value than master or other slaves

 * setting up replication:
  * on master terminal 1:
        `FLUSH TABLES WITH READ LOCK`
        stops any new commits so we can find our place in replication
  * on master terminal 2:
        `SHOW MASTER STATUS` 
        This will show us the file and position in the binlog to pick up replication

  * Create mysqldump to transfer master state to slave in preparation on replication
      master cmdline: mysqldump -u root inventory --master-data > dump_file
  * Load mysqldump on slave
    * scp dump to slave:
    * mysql inventory < dump_file

  * Use `CHANGE MASTER TO` syntax (https://dev.mysql.com/doc/refman/5.0/en/change-master-to.html)  to set pertinent configuration values for slave. 
  * slave terminal:
`CHANGE MASTER TO MASTER_HOST='xxxxx', MASTER_USER='xxxxxx', MASTER_PASSWORD='xxxxx', MASTER_PORT=12345, MASTER_LOG_FILE='xxxxx', MASTER_LOG_POS=12345`

  * slave terminal:
        START SLAVE

  * MAGIC!

 # moving regsister-tape

 on existing POSmachine:
    * enable bin-logs
           edit my.cnf with:
           

    * lock mysql tables
        `FLUSH TABLES WITH READ LOCK`
        stops any new commits so we can find our place in replication
  * on master terminal 2:
        `SHOW MASTER STATUS` 
        This will show us the file and position in the binlog to pick up replication



* Test the site by visiting http://YOUR.SITE/ !
