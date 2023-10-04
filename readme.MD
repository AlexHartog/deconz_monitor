## Deconz Manager

This project will create overviews of the states of deconz devices.

### Lights
All lights will be requested from deconz and saved into database tables. If an instance is run
with the flag `ENABLE_SCHEDULER=True` in .env, it will refresh this data every minute and store
a snapshot.

### Sensors
Not implemented yet

### Switches
Not implemented yet

### Running in development
You can use the following command 

`flask --app deconz_manager run --host 0.0.0.0 --debug`


A .env file is required with at least the following settings:
```
DB_HOST=
DB_DATABASE=
DB_USER=
DB_PASSWORD=
```

## Testing

Automated testing is implemented through GitHub Actions.

### Postgres Testing Instance

For running tests locally, a postgres testing instance can be run using docker-compose.
To get it started, run: 

`docker-compose up -d` 

It will read initial setup from testing/sql/create_tables.sql. It will only do this on the 
first start up. If data in the sql file is changed and needs to be loaded, we can make sure 
that all the volumes are removed and on next start up the new sql files are loaded by running:

`docker-compose down --rmi all --volumes` 