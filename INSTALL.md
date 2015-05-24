# Preliminary install notes:

* Install SQL Alchemy (the copy of it in this tree will eventually be
  removed).  The most recent version is 1.0.4  

        sudo pip install SqlAlchemy

* Get the source code:

        git clone git@github.com:OpenTechStrategies/marzipan-prep.git

* Set up the databases and database users:

        $ mysql -u root -p
        mysql> CREATE DATABASE register-tape;  
        mysql> CREATE DATABASE inventory;
        mysql> CREATE USER "marzipan" IDENTIFIED BY "testpass";  
        mysql> GRANT ALL ON "register-tape" TO "marzipan"@"localhost";  
        mysql> GRANT ALL ON "inventory" TO "marzipan"@"localhost";
        mysql> quit
        Bye
        $ 

* Load data (THIS IS REAL DATA!)

        $ mysql -u marzipan -p testpass;  
        mysql> use register-tape;  
        mysql> source sample-data/op-register_tape-20150316.sql.bz2;  
        mysql> source sample-data/op-inventory-20150316.sql.bz2;
        mysql> quit
        Bye
        $ 

* Run the cash register interface.  Do this in a terminal that can
  respond to terminal control codes, such as an xterm (e.g., don't use
  an Emacs shell buffer or other pseudo-terminal, because it won't
  work in there):

        cd marzipan-prep
        python staff/register/ui.py

