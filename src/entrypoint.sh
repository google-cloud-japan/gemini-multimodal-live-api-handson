#!/bin/bash

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

# Start proxy with output logging
python /app/proxy/proxy.py 2>&1 | tee /var/log/proxy.log &
PROXY_PID=$!

# Give proxy a moment to start
sleep 1

# Check if proxy is still running
if ! kill -0 $PROXY_PID 2>/dev/null; then
    echo "Proxy failed to start. Last few lines of log:"
    tail -n 5 /var/log/proxy.log
    exit 1
fi

echo "listening on port 8080"
nginx -g "daemon off;"
