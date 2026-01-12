@echo off
echo Building Docker image...
docker build -t xiaomusic-netease .

echo Cleaning up old container...
docker stop xiaomusic-custom
docker rm xiaomusic-custom

echo Starting new container...
docker run -d ^
  --name xiaomusic-custom ^
  --restart unless-stopped ^
  -p 8080:8080 ^
  -e XIAOMUSIC_PORT=8080 ^
  -v "%cd%/music:/app/music" ^
  -v "%cd%/conf:/app/conf" ^
  xiaomusic-netease

echo Deployment complete!
echo Service is running at: http://localhost:8080
pause
