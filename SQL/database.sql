create table users (
	id_user SERIAL primary key,
	username VARCHAR(20) not null unique,
	pass VARCHAR(20) not null,
	auth_level int not null,
	fullname VARCHAR(100) not null,
	is_blocked BOOLEAN not null default False
);

create table logs(
	id_log SERIAL primary key,
	log_date timestamptz not null,
	commentary VARCHAR(500) not null,
	id_user int
);

alter table logs add constraint FK_logs_users foreign key (id_user) references users(id_user);

CREATE OR REPLACE FUNCTION addLog() RETURNS TRIGGER AS $fechas$
DECLARE
BEGIN
	new.log_date := now();
	RETURN new;
END;
$fechas$ LANGUAGE 'plpgsql';

CREATE TRIGGER AD_Log
BEFORE INSERT ON public.logs
FOR EACH ROW
EXECUTE PROCEDURE addLog();

insert into users (id_user, username,pass,auth_level,fullname) values (0,'Anon','None',4,'Anonymous');