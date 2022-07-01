-- query for extracting courses by compre dates 
select * from course where compreSch like '20%';

-- getting prof name for a course
select distinct(profName) from instnames where insID in (select profid from instructors where comcod = (select comcod from course where courseName='BIO F111'));

-- getting prof name for a course and section
select distinct(profName) from instnames where insID in (select profid from instructors where comcod = (select comcod from course where courseName='BIO F111') and section like '%2%');

-- getting number of credits for a course
select credit from course where courseName='BIO F111';

-- getting time of lecture for a course and section
select time from schedule where comcod = (select comcod from course where courseName='BIO F111') and section like 'L2%';

-- getting room for a course and section
select room from schedule where comcod = (select comcod from course where courseName='BIO F111') and section like 'L2%';

-- where is the prof now
select * from schedule where (comcod,section) in (select comcod,section from instructors where profid = 1) and time like 'M%3';

-- what is the class going on right now time and room
select * from course where comcod in (select comcod from schedule where room = 5106 and time like 'M%2');

-- what are the courses under a particular department
select courseTitle from course where Upper(courseName) like Upper('BiO%');


