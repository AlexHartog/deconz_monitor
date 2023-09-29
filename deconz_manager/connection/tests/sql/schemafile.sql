/* Create Deconz connection table */
CREATE TABLE "connection" (
	onerow_id bool NOT NULL DEFAULT true,
	api_key varchar(50) NULL,
	ip_address varchar(50) NULL,
	port varchar(50) NULL,
	CONSTRAINT connection_pkey PRIMARY KEY (onerow_id),
	CONSTRAINT onerow_uni CHECK (onerow_id)
);

CREATE TABLE public.deconz_group (
	id text NOT NULL,
	etag text NULL,
	group_name text NULL,
	CONSTRAINT deconz_group_pkey PRIMARY KEY (id)
);