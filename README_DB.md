# Run with postgres
- Create rtb.env from rtb.env.sample

```
# POSTGRES
POSTGRES_USER=rtb
POSTGRES_PASSWORD=XHb6&oUUQy973
POSTGRES_DB=rootthebox
PGADMIN_DEFAULT_EMAIL=info@acme.org
PGADMIN_DEFAULT_PASSWORD=U4AOm9588^MP
PGADMIN_LISTEN_PORT=80
```

- docker-compose -f docker-compose__postgres up -d
- Available link:
  - RootTheBox: at port 8888
  - pgadmin: at port 15432

Sample `files/roothebox.cfg` file:

```
# [ Database ]
sql_dialect = "postgres"
sql_database = "rootthebox"
sql_host = "postgres"
sql_port = 5432
sql_user = "rtb"
sql_sslca = ""
sql_password = "XHb6&oUUQy973"
log_sql = False
```

## Issues
- user _locked filed is boolean and filtering with =0 is not valid => resolved
- garbage field in box model is binary and encoded lenght is > 32 char

# Run with mariadb
- Create rtb.env from rtb.env.sample

```
# MYSQL
MYSQL_DATABASE=rootthebox
MYSQL_ROOT_PASSWORD=XHb6&oUUQy973
MYSQL_USER=rtb
MYSQL_PASSWORD=XHb6&oUUQy973
```

- docker-compose -f docker-compose__postgres up -d
- Available link:
  - RootTheBox: at port 8888
  
Sample `files/roothebox.cfg` file:
```
# [ Database ]
sql_dialect = "mysql"
sql_database = "rootthebox"
sql_host = "mariadb"
sql_port = 3306
sql_user = "rtb"
sql_sslca = ""
sql_password = "XHb6&oUUQy973"
log_sql = False
```

# GraphQl wip access
With both postgres and mariadb doker-compose files add -profile graphql to expose graphql access on port 7007