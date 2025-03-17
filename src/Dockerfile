# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM python:3.12-slim

WORKDIR /app

# Install required system packages
RUN apt-get update && apt-get install -y nginx gettext-base procps tini \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
ARG SRC_DIR=src/
COPY ${SRC_DIR}index.html /app/
COPY proxy/proxy.py /app/proxy/
COPY shared /app/shared

# Install Python dependencies
RUN pip install --no-cache-dir \
    websockets \
    google-auth \
    certifi \
    requests

# Configure nginx
RUN echo 'events { worker_connections 1024; } http { include /etc/nginx/mime.types; map $http_upgrade $connection_upgrade { default upgrade; "" close; } server { listen 8080; location / { root /app; try_files $uri $uri/ =404; } location /ws { proxy_pass http://localhost:8081; proxy_http_version 1.1; proxy_set_header Upgrade $http_upgrade; proxy_set_header Connection "upgrade"; proxy_set_header Host $host; } } }' > /etc/nginx/nginx.conf

COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

EXPOSE 8080

CMD ["/usr/bin/tini", "--", "/app/entrypoint.sh"]
