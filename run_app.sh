# 1. Login to Quay (if repo is private)
docker login quay.io
# 2. Pull the image
docker pull quay.io/<your-quay-username>/repo-analyzer:latest
# 3. Run the container
# Replace /path/to/... with actual paths on your VM
docker run -d \
  --name repo-analyzer \
  --restart always \
  -p 443:443 \
  -e ENV=prod \
  -e VERTEX_PROJECT_ID="your-gcp-project-id" \
  -e VERTEX_LOCATION="us-central1" \
  -e CERT_PATH="/etc/certs/cert.pem" \
  -e KEY_PATH="/etc/certs/key.pem" \
  -e SSH_KEY_PATH="/etc/ssh/id_rsa" \
  -v /path/to/real/cert.pem:/etc/certs/cert.pem:ro \
  -v /path/to/real/key.pem:/etc/certs/key.pem:ro \
  -v /home/user/.ssh/id_rsa:/etc/ssh/id_rsa:ro \
  quay.io/<your-quay-username>/repo-analyzer:latest
