## Deconz Manager

This project will create overviews of the states of deconz devices.

### Lights

### Sensors

### Switches


temp password:
deconzm

## Testing

### Postgres Testing Instance

The postgres testing instance can be run using docker-compose.
Run `docker-compose up -d` to get it started.

It will read initial setup from testing/sql/create_tables.sql. It will only do this on the first start up. If data in the sql file is changed and needs to be loaded, `docker-compose down --rmi all --volumes` will make sure that all the volumes are removed and on next start up the new sql files is loaded.