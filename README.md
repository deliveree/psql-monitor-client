## Client:

This app run every 5 seconds to retrieve these figures:
- PostgreSQL’s Sync delay time
- PostgreSQL’s amount of concurrent queries
- RAM (used/free)
- CPU usage (pecentage)
- Load Average (last 1 minute only)

Then it pushes them to a central server.

## Getting Started:

## Development:
```
pytest --disable-warnings
```
