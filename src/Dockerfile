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
RUN apt-get update && apt-get install -y nginx gettext-base procps \
    && rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh
CMD ["/app/entrypoint.sh"]

# Install Python dependencies
RUN pip install --no-cache-dir \
    websockets \
    google-auth \
    certifi \
    requests

# Copy application files
COPY proxy/proxy.py /app/proxy/
COPY proxy/nginx.conf /etc/nginx/
COPY shared /app/shared
ARG SRC_DIR=src/
COPY ${SRC_DIR}index.html /app/
