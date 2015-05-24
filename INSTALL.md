# Preliminary install notes:

* Install SQL Alchemy (the copy of it in this tree will be removed).  The most
  recent version is 1.0.4  
   `sudo pip install SqlAlchemy pycurl`

* git clone  
  `git clone git@github.com:OpenTechStrategies/marzipan-prep.git`

* To test the register:
  ` cd marzipan-prep`
  ` python staff/register/ui.py`

* Create databases  
  `CREATE DATABASE register-tape;  
   CREATE DATABASE inventory;` 
* Create a user named "marzipan" and grant access to those databases  
  `CREATE USER "marzipan" IDENTIFIED BY "testpass";  
   GRANT ALL ON "register-tape" TO "marzipan"@"localhost";  
   GRANT ALL ON "inventory" TO "marzipan"@"localhost";`  

* Load data (THIS IS REAL DATA!)  
  `mysql -u marzipan -p testpass;  
  use register-tape;  
  source sample-data/op-register_tape-20150316.sql.bz2;  
  source sample-data/op-inventory-20150316.sql.bz2;`

* To test the register:  
  ` cd marzipan-prep`  
  ` python staff/register/ui.py`  
