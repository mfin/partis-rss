NOTE: A work in progress

# partis-rss
Partis.si RSS feed generator

## Run it with Docker
```
docker build -t partis-rss .
docker run -d -p 5000:5000 -e PARTIS_USERNAME='your_username' -e PARTIS_PASSWORD='your_password' partis-rss
```

Point your torrent client/web browser to http://127.0.0.1:5000 to get the feed.