#!/bin/bash
# Verify API server connectivity from different perspectives
# Usage: ./verify_api_connectivity.sh [PORT]

PORT=${1:-3000}
SERVER_IP="43.162.90.39"

echo "🔍 API Connectivity Test - Port: $PORT"
echo "========================================"

# 1. Check if API process is running
echo "\n1. Checking API server process..."
if ps aux | grep -v grep | grep -q "api-server"; then
    echo "✅ API server process is running"
else
    echo "❌ API server process NOT found"
fi

# 2. Check listening ports
echo "\n2. Checking listening ports..."
if netstat -tlnp 2>/dev/null | grep -q ":$PORT"; then
    echo "✅ Port $PORT is being listened on"
    netstat -tlnp | grep ":$PORT"
else
    echo "❌ Port $PORT is NOT being listened on"
fi

# 3. Test local connectivity
echo "\n3. Testing local connectivity (localhost:$PORT)..."
if curl -s -o /dev/null -w "%{http_code}" "http://localhost:$PORT" | grep -q "200\|301\|302"; then
    echo "✅ Local connection successful"
else
    echo "❌ Local connection failed"
fi

# 4. Test public connectivity
echo "\n4. Testing public connectivity ($SERVER_IP:$PORT)..."
if curl -s -o /dev/null -w "%{http_code}" "http://$SERVER_IP:$PORT" --connect-timeout 5 | grep -q "200\|301\|302"; then
    echo "✅ Public connection successful"
else
    echo "❌ Public connection failed"
    echo "   This usually means:"
    echo "   a) API server is not listening on 0.0.0.0"
    echo "   b) Cloud provider security group blocks port $PORT"
    echo "   c) Firewall rules block the port"
fi

# 5. Test API endpoint
echo "\n5. Testing API endpoint ($SERVER_IP:$PORT/api/v1/schools)..."
API_RESPONSE=$(curl -s "http://$SERVER_IP:$PORT/api/v1/schools" --connect-timeout 5 | head -c 100)
if [ -n "$API_RESPONSE" ]; then
    echo "✅ API endpoint accessible"
    echo "   Response preview: ${API_RESPONSE}"
else
    echo "❌ API endpoint not accessible"
fi

echo "\n========================================"
echo "📋 Summary:"
echo "- If local works but public fails: Check API server binding (should be 0.0.0.0)"
echo "- If both fail: Check API server process and port binding"
echo "- If process exists but port not listening: Check API server configuration"
echo "- If all tests fail but process exists: Check for errors in API server logs"