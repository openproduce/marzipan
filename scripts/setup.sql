CREATE DATABASE register_tape;
CREATE DATABASE inventory;
CREATE USER 'marzipan' IDENTIFIED BY 'testpass';
GRANT ALL PRIVILEGES ON register_tape.* TO marzipan@localhost;
GRANT ALL PRIVILEGES ON inventory.* TO marzipan@localhost;
FLUSH PRIVILEGES;

