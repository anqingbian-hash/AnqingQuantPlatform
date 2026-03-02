#!/bin/bash

echo "=========================================="
echo "  NTDF Backend Deployment Script"
echo "=========================================="
echo ""

# Server details
SERVER="122.51.142.248"
USER="ubuntu"
REMOTE_DIR="/var/www/ntdf/backend"

echo "📦 Deploying to $SERVER:$REMOTE_DIR"
echo ""

# Check if we can connect
echo "🔍 Checking server connection..."
if ! ping -c 1 $SERVER > /dev/null 2>&1; then
    echo "❌ Server is not reachable"
    echo ""
    echo "Please run these commands manually in Tencent Cloud WebShell:"
    echo ""
    echo "1. Create directory:"
    echo "   mkdir -p $REMOTE_DIR && cd $REMOTE_DIR"
    echo ""
    echo "2. Create main.py file (copy content from simple_main.py)"
    echo ""
    echo "3. Create requirements.txt"
    echo ""
    echo "4. Create and activate virtual environment:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo ""
    echo "5. Install dependencies:"
    echo "   pip install -r requirements.txt"
    echo ""
    echo "6. Start server:"
    echo "   uvicorn simple_main:app --host 0.0.0.0 --port 8000"
    echo ""
    exit 1
fi

echo "✅ Server is reachable"
echo ""

# Create remote directory
echo "📁 Creating remote directory..."
ssh $USER@$SERVER "mkdir -p $REMOTE_DIR && cd $REMOTE_DIR && pwd"

# Copy files
echo "📤 Copying files..."
echo "  - simple_main.py"
echo "  - requirements.txt"
echo "  - start.sh"

scp simple_main.py $USER@$SERVER:$REMOTE_DIR/
scp requirements.txt $USER@$SERVER:$REMOTE_DIR/
scp start.sh $USER@$SERVER:$REMOTE_DIR/

# Setup on remote server
echo ""
echo "⚙️  Setting up remote server..."

ssh $USER@$SERVER << 'ENDSSH'
cd /var/www/ntdf/backend

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Make start.sh executable
chmod +x start.sh

echo ""
echo "✅ Setup complete!"
ENDSSH

echo ""
echo "=========================================="
echo "  Deployment Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. SSH into server:"
echo "   ssh ubuntu@122.51.142.248"
echo ""
echo "2. Navigate to backend directory:"
echo "   cd /var/www/ntdf/backend"
echo ""
echo "3. Start server:"
echo "   ./start.sh"
echo ""
echo "Or start manually:"
echo "   source venv/bin/activate"
echo "   uvicorn simple_main:app --host 0.0.0.0 --port 8000"
echo ""
echo "Server will be available at:"
echo "  - API: http://122.51.142.248:8000"
echo "  - Docs: http://122.51.142.248:8000/docs"
echo "  - Health: http://122.51.142.248:8000/health"
echo ""
echo "=========================================="
