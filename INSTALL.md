# Installing the register point-of-sale application:

* Install SQL Alchemy (the copy of it in this tree will eventually be
  removed).  The most recent version is 1.0.4.

        $ sudo pip install SqlAlchemy

* Get the source code:

        $ git clone git@github.com:OpenTechStrategies/marzipan-prep.git

* Set up the databases and database users:
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

* Run the cash register interface.  Do this in a terminal that can
  respond to terminal control codes, such as an xterm (e.g., don't use
  an Emacs shell buffer or other pseudo-terminal, because it won't
  work in there):

        $ cd marzipan-prep
        $ python register/ui.py

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
