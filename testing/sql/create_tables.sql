/* Create deconz group table */
CREATE TABLE public.deconz_group (
	id text NOT NULL,
	etag text NULL,
	group_name text NULL,
	CONSTRAINT deconz_group_pkey PRIMARY KEY (id)
);

/* Create deconz connection table */
CREATE TABLE public.deconz_connection (
	onerow_id bool NOT NULL DEFAULT true,
	api_key varchar(50) NULL,
	ip_address varchar(50) NULL,
	port varchar(50) NULL,
	CONSTRAINT connection_pkey PRIMARY KEY (onerow_id),
	CONSTRAINT onerow_uni CHECK (onerow_id)
);

/* Create light table */
CREATE TABLE public.light (
	unique_id text NOT NULL,
	etag text NULL,
	has_color bool NULL,
	last_announced timestamptz NULL,
	last_seen timestamptz NULL,
	manufacturer_name text NULL,
	model_id text NULL,
	light_name text NULL,
	product_id text NULL,
	product_name text NULL,
	sw_version text NULL,
	light_type text NULL,
	state_brightness int4 NULL,
	state_on bool NULL,
	state_reachable bool NULL,
	id text NULL,
	CONSTRAINT light_pkey PRIMARY KEY (unique_id),
	CONSTRAINT light_un UNIQUE (id)
);

/* Create group light table */
CREATE TABLE public.group_light (
	group_id text NOT NULL,
	light_id text NOT NULL,
	CONSTRAINT group_light_pkey PRIMARY KEY (group_id, light_id),
	CONSTRAINT group_light_fk FOREIGN KEY (light_id) REFERENCES public.light(id) ON DELETE CASCADE,
	CONSTRAINT group_light_fk_1 FOREIGN KEY (group_id) REFERENCES public.deconz_group(id) ON DELETE CASCADE
);

/* Create light history table */
CREATE TABLE public.light_history (
	id serial4 NOT NULL,
	light_id text NULL,
	state_brightness int4 NULL,
	state_on bool NULL,
	state_reachable bool NULL,
	at_time timestamptz NULL DEFAULT CURRENT_TIMESTAMP,
	snapshot_id int4 NULL,
	CONSTRAINT light_history_pkey PRIMARY KEY (id),
	CONSTRAINT light_history_fk FOREIGN KEY (light_id) REFERENCES public.light(unique_id) ON DELETE CASCADE
);

/* Create group_light_v view */
CREATE OR REPLACE VIEW public.group_light_v
AS SELECT light.light_name,
    deconz_group.group_name,
    light.state_on,
    light.state_brightness,
    light.state_reachable,
    light.last_announced,
    light.last_seen,
    light.light_type,
    light.product_name,
    light.manufacturer_name,
    light.unique_id
   FROM light
     LEFT JOIN group_light ON group_light.light_id = light.id
     LEFT JOIN deconz_group ON group_light.group_id = deconz_group.id;

/* Create light_history_v view */
CREATE OR REPLACE VIEW public.light_history_v
AS SELECT light_history.id,
    group_light_v.light_name,
    light_history.at_time,
    light_history.state_on,
    light_history.state_brightness,
    light_history.state_reachable,
    group_light_v.group_name,
    group_light_v.last_announced,
    group_light_v.last_seen,
    group_light_v.light_type,
    group_light_v.product_name,
    group_light_v.manufacturer_name,
    group_light_v.unique_id,
    light_history.snapshot_id
   FROM light_history
     LEFT JOIN group_light_v ON light_history.light_id = group_light_v.unique_id;	