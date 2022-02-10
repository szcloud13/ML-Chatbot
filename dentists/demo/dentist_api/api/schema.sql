CREATE TABLE dentists ( 
id integer primary key autoincrement,
name varchar2(30) NOT NULL,
location varchar2(50) NOT NULL,
specialization  varchar2(100) NOT NULL
);

INSERT INTO dentists VALUES (null,'Chang Low Ying', 'Chatswood', 'Oral Surgery');
INSERT INTO dentists VALUES (null,'Asman Nematallah', 'Bankstown', 'Orthodontics');
INSERT INTO dentists VALUES (null,'John Smith', 'Randwick', 'Paediatric Dentistry');
