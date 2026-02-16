--create database link brehat connect to bgn8016a identified by "gerard" using 'VERS_ETUSEC';
select * from EMPB@brehat;
--drop database link brehat;