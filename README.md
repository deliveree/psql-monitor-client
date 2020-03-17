## Client:

This app triggers every second to retrieve these figures and pushes them to a central server separately:
- PostgreSQL’s Sync delay time
- PostgreSQL’s amount of concurrent queries
- RAM (used/free)
- CPU usage (pecentage)
- Load Average (last 1 minute only)


## Example of data stored in redis:
```
{
    "server_1": {
        "cpu_usage": 10000,
        "cpu_usage_updated_at": "2020-01-30 00:00:00",
        "delay": 100,
        "delay_updated_at": "2020-01-30 00:00:00",
    },
    "server_2": {...}
}
```

## Getting Started:

### 1. Authentication Setup:

1. Make sure we already have SSL certificates and key for server and client (**Required**):
```
openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 -keyout server.key -out server.crt
openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 -keyout client.key -out client.crt
```

**Note**: Common name for server must be your server hostname (ex: example.com)

2. Put **client.crt** and **client.key** in /src
3. Make sure client's certificate (**client.crt**) has been added to the file that server uses to authenticate. The format for the file is:

```
-----BEGIN CERTIFICATE-----
client 1's certificate
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
client 2's certificate
-----END CERTIFICATE-----
```

### 2. Add credentials for daemon connection and psql access:
Fill credentials in file **src/sample_creds.conf** and change its name to **creds.conf**

- **psql**: the target postgres database whose stats will be sent to daemon.
- **daemon**: the target server that figures will be sent to.


### 3. Run App
```
python main.py
```

## Options:
### Config log path
The default log is **src/main.log**
You can change path to log in **conf/log.conf**

## Development

Each resource is retrieved and pushed to central server within a thread. The time waiting for each thread is 0.05s.

### Test
The test in this project run a server and client in different processes.

Make sure server's and client's credentials (server.crt, server.key, client_certs.crt) are in **test/**.

Make sure common name for server when creating certicate is **localhost**.

Run tests. In **test/**:
```
pytest --disable-warnings
```