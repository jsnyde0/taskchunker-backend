# taskchunker-backend

## Development
### Redis
Pull and run Redis locally:
```
docker run --name taskchunker-redis -p 6379:6379 -d redis
```

To stop it later
```
docker stop taskchunker-redis
```

To start it again
```
docker start taskchunker-redis
```

To remove it completely
```
docker rm taskchunker-redis
```
