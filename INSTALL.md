# Installing the register point-of-sale application:

* PACKAGES  
  - sudo apt-get install git  
  - sudo apt-get install mysql-client  
  - sudo apt-get install mysql-server  
  - sudo apt-get install python-pip  
  - sudo apt-get install python-dev  
  - sudo apt-get install python-mysqldb  
  - sudo apt-get install libcurl4-openssl-dev  
  - sudo pip install pycurl  
  - sudo apt-get install texlive  


* Install SQL Alchemy (the copy of it in this tree will eventually be
  removed).  The most recent version is 1.0.4.

        $ sudo pip install SqlAlchemy

* Get the source code:

        $ git clone git@github.com:OpenTechStrategies/marzipan-prep.git

* Set up the databases and database users.  Note that as currently written this script will drop an existing database, so do not run it if your database exists and has data you want to keep!  If your databases don't exist yet this will create them.

        $ mysql -u root -p < scripts/setup.sql

* Unzip sample data files:

        $ bunzip2 -k sample-data/op-register_tape-20150316.sql.bz2
        $ bunzip2 -k sample-data/op-inventory-20150316.sql.bz2

* Load data (THIS IS REAL DATA!)

        $ mysql -u marzipan -p
        mysql> use register_tape
        mysql> source sample-data/op-register_tape-20150316.sql
        mysql> use inventory
        mysql> source sample-data/op-inventory-20150316.sql
        mysql> quit
        Bye
        $ 

* Copy register/config.py.tmpl to register/config.py and, in register/config.py, change the secrets (in all caps) to their values for your application.

* Run the cash register interface.  Do this in a terminal that can
  respond to terminal control codes, such as an xterm (e.g., don't use
  an Emacs shell buffer or other pseudo-terminal, because it won't
  work in there):

        $ cd marzipan-prep
        $ python register/ui.py

* Make the computer boot directly into text mode, if desired.  Edit
  /etc/default/grub and change the line that reads
  
        GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"

        to

        GRUB_CMDLINE_LINUX_DEFAULT="quiet splash text"

        Then run 'update-grub' and reboot.
 
        $ sudo vi /etc/default/grub
        $ sudo update-grub

        You can then reboot, or wait until you complete the next step.

* Make the computer's TTY1, 2, and 3 run the POS instead of prompting for
  login:  Edit /etc/init/tty1.conf and replace the line

        exec /sbin/getty -8 -38400 tty1

        with

        exec /sbin/getty -8 -n -l /home/openproduce/marzipan-prep/register/launch.sh 38400 tty1

  Now do the same for tty2 and tty3 if desired.

  Next reboot.  You should find ALT-F1 through ALT-F3 run concurrent copies of
  the register, and ALT-F4 etc are available for administrative login.

# Installing the web tools:

  These instructions should work on Ubuntu or Debian GNU/Linux.

* Make sure you have Python 2.7.x installed.
  (It probably is by default, but check with `python --version`.)

* Install other needed packages:

        $ sudo apt-get update
        $ sudo apt-get install apache2
        $ sudo apt-get install apache2-utils
        $ sudo apt-get install mysql-common
        $ sudo apt-get install mysql-server
        $ sudo apt-get install libmysqlclient-dev
        $ sudo apt-get install git
        $ sudo apt-get install python-dev
        $ sudo apt-get install python-pip
        $ sudo pip install SQLAlchemy
        $ sudo pip install MySQL-python

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
        $ bunzip2 -k sample-data/op-register_tape-20150316.sql.bz2
        $ bunzip2 -k sample-data/op-inventory-20150316.sql.bz2

* Load data (THIS IS REAL DATA!)

        $ mysql -u marzipan -p
        mysql> use register_tape
        mysql> source sample-data/op-register_tape-20150316.sql
        mysql> use inventory
        mysql> source sample-data/op-inventory-20150316.sql
        mysql> quit
        Bye
        $ 


* Create the marzipan web root:

        $ cd /var/www
        $ git clone git@github.com:OpenTechStrategies/marzipan-prep.git
        $ mv marzipan-prep marzipan
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

* Test the site by visiting http://YOUR.SITE/ !
