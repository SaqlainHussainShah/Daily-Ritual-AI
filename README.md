# Daily Ritual AI — Docker quick start

Build the Docker image:
```bash
docker build -t daily-ritual-ai .
```

Run the Docker image (this is the command to run the Docker image; it maps container port 8000 to host port 8000):
```bash
docker run --rm -p 8000:8000 daily-ritual-ai
```

Notes:
- Add `-d` to run the container in the background: `docker run -d --name daily-ritual-ai -p 8000:8000 daily-ritual-ai`
- `--rm` removes the container when it exits.
