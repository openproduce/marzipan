DROP DATABASE IF EXISTS register_tape;
CREATE DATABASE register_tape;
DROP DATABASE IF EXISTS inventory;
CREATE DATABASE inventory;
DROP USER IF EXISTS 'marzipan'@'localhost';
FLUSH PRIVILEGES;
CREATE USER 'marzipan'@'localhost' IDENTIFIED BY 'testpass';
GRANT ALL PRIVILEGES ON register_tape.* TO marzipan@localhost;
GRANT ALL PRIVILEGES ON inventory.* TO marzipan@localhost;
FLUSH PRIVILEGES;

