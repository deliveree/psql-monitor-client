## Client:

This app run every 3 seconds to retrieve these figures:
- PostgreSQL’s Sync delay time
- PostgreSQL’s amount of concurrent queries
- RAM (used/free)
- CPU usage (pecentage)
- Load Average (last 1 minute only)

Then it pushes them to a central server.

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


### 3. Run Client
```
python main.py
```

## Development

The test in this project requires a running local server, which is socket_server.py
Make sure server's and client's credentials (server.crt, server.key, client_certs.crt) are in **test/**

Make sure common name for server when creating certicate is **localhost**

1. Run server. In **test/**:
```
python socket_server.py
```

2. Run tests. In **test/**:
```
pytest --disable-warnings
```