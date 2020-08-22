CREATE SEQUENCE checks_id_seq;
CREATE TABLE public.checks
(
    id integer NOT NULL DEFAULT nextval('checks_id_seq'),
    created timestamp without time zone NOT NULL DEFAULT now(),
    url text COLLATE pg_catalog."default" NOT NULL,
    code integer NOT NULL,
    body_check_valid boolean NOT NULL,
    "time" real NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    CONSTRAINT checks_pkey PRIMARY KEY (id)

)
