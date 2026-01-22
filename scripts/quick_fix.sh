#!/bin/bash
#
# Quick Fix Script for Trading Bot Service Startup Issues
# This script diagnoses and attempts to fix common systemd service errors
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BOT_USER="tradingbot"
APP_DIR="/opt/trading-bot"
CONFIG_DIR="/etc/trading-bot"
LOG_DIR="/var/log/trading-bot"
DATA_DIR="/var/lib/trading-bot"
SERVICE_NAME="trading-bot"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Trading Bot - Quick Fix Script${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
    fi
}

# Function to fix issues
fix_issue() {
    echo -e "${YELLOW}⚠ Fixing:${NC} $1"
    eval "$2"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Fixed!${NC}\n"
    else
        echo -e "${RED}✗ Failed to fix${NC}\n"
    fi
}

echo "Step 1: Checking system user..."
if id "$BOT_USER" &>/dev/null; then
    print_status 0 "User $BOT_USER exists"
else
    fix_issue "Creating user $BOT_USER" \
        "sudo useradd -r -s /bin/bash -d $APP_DIR $BOT_USER"
fi

echo -e "\nStep 2: Checking directories..."
for dir in "$APP_DIR" "$CONFIG_DIR" "$LOG_DIR" "$DATA_DIR"; do
    if [ -d "$dir" ]; then
        print_status 0 "Directory $dir exists"
    else
        fix_issue "Creating directory $dir" \
            "sudo mkdir -p $dir && sudo chown $BOT_USER:$BOT_USER $dir"
    fi
done

echo -e "\nStep 3: Checking directory permissions..."
for dir in "$APP_DIR" "$CONFIG_DIR" "$LOG_DIR" "$DATA_DIR"; do
    if [ -d "$dir" ]; then
        owner=$(stat -c '%U' "$dir" 2>/dev/null || stat -f '%Su' "$dir" 2>/dev/null)
        if [ "$owner" = "$BOT_USER" ]; then
            print_status 0 "$dir owned by $BOT_USER"
        else
            fix_issue "Fixing ownership of $dir" \
                "sudo chown -R $BOT_USER:$BOT_USER $dir"
        fi
    fi
done

echo -e "\nStep 4: Checking .env file..."
if [ -f "$CONFIG_DIR/.env" ]; then
    print_status 0 ".env file exists"
    
    # Check if it's readable by the service user
    if sudo -u $BOT_USER test -r "$CONFIG_DIR/.env"; then
        print_status 0 ".env file is readable by $BOT_USER"
    else
        fix_issue "Fixing .env permissions" \
            "sudo chown $BOT_USER:$BOT_USER $CONFIG_DIR/.env && sudo chmod 600 $CONFIG_DIR/.env"
    fi
else
    if [ -f "$APP_DIR/.env.template" ]; then
        fix_issue "Creating .env from template" \
            "sudo cp $APP_DIR/.env.template $CONFIG_DIR/.env && sudo chown $BOT_USER:$BOT_USER $CONFIG_DIR/.env && sudo chmod 600 $CONFIG_DIR/.env"
        echo -e "${YELLOW}⚠ Please edit $CONFIG_DIR/.env with your API keys!${NC}\n"
    else
        echo -e "${RED}✗ No .env.template found. Please create $CONFIG_DIR/.env manually${NC}\n"
    fi
fi

echo -e "\nStep 5: Checking Python virtual environment..."
if [ -f "$APP_DIR/venv/bin/python" ]; then
    print_status 0 "Virtual environment exists"
else
    fix_issue "Creating virtual environment" \
        "cd $APP_DIR && sudo python3 -m venv venv && sudo chown -R $BOT_USER:$BOT_USER venv"
fi

echo -e "\nStep 6: Checking Python dependencies..."
if [ -f "$APP_DIR/requirements.txt" ]; then
    echo -e "${YELLOW}Installing/updating dependencies...${NC}"
    sudo -u $BOT_USER $APP_DIR/venv/bin/pip install --upgrade pip -q
    sudo -u $BOT_USER $APP_DIR/venv/bin/pip install -r $APP_DIR/requirements.txt -q
    print_status $? "Dependencies installed"
else
    print_status 1 "requirements.txt not found"
fi

echo -e "\nStep 7: Checking application files..."
if [ -f "$APP_DIR/src/main.py" ]; then
    print_status 0 "main.py exists"
else
    print_status 1 "main.py not found at $APP_DIR/src/main.py"
    echo -e "${RED}Please copy your application files to $APP_DIR${NC}\n"
fi

echo -e "\nStep 8: Checking systemd service file..."
if [ -f "/etc/systemd/system/$SERVICE_NAME.service" ]; then
    print_status 0 "Service file exists"
    
    # Check if it has the correct paths
    if grep -q "WorkingDirectory=$APP_DIR" "/etc/systemd/system/$SERVICE_NAME.service" && \
       grep -q "EnvironmentFile=$CONFIG_DIR/.env" "/etc/systemd/system/$SERVICE_NAME.service"; then
        print_status 0 "Service file has correct paths"
    else
        echo -e "${YELLOW}⚠ Service file may have incorrect paths${NC}"
        echo -e "${YELLOW}Expected:${NC}"
        echo "  WorkingDirectory=$APP_DIR"
        echo "  EnvironmentFile=$CONFIG_DIR/.env"
        echo "  ExecStart=$APP_DIR/venv/bin/python $APP_DIR/src/main.py"
    fi
else
    print_status 1 "Service file not found"
    echo -e "${YELLOW}Creating service file from template...${NC}"
    if [ -f "$APP_DIR/deployment/systemd/trading-bot.service" ]; then
        sudo cp "$APP_DIR/deployment/systemd/trading-bot.service" "/etc/systemd/system/$SERVICE_NAME.service"
        # Replace placeholders
        sudo sed -i "s|{{APP_DIR}}|$APP_DIR|g" "/etc/systemd/system/$SERVICE_NAME.service"
        sudo sed -i "s|{{CONFIG_DIR}}|$CONFIG_DIR|g" "/etc/systemd/system/$SERVICE_NAME.service"
        sudo sed -i "s|{{LOG_DIR}}|$LOG_DIR|g" "/etc/systemd/system/$SERVICE_NAME.service"
        sudo sed -i "s|{{DATA_DIR}}|$DATA_DIR|g" "/etc/systemd/system/$SERVICE_NAME.service"
        print_status 0 "Service file created"
    fi
fi

echo -e "\nStep 9: Testing manual startup..."
echo -e "${YELLOW}Running a quick test as $BOT_USER...${NC}"
sudo -u $BOT_USER bash -c "cd $APP_DIR && source venv/bin/activate && timeout 5 python src/main.py 2>&1 | head -20" || true

echo -e "\nStep 10: Reloading systemd..."
sudo systemctl daemon-reload
print_status $? "Systemd reloaded"

echo -e "\nStep 11: Checking service status..."
if systemctl is-active --quiet $SERVICE_NAME; then
    echo -e "${YELLOW}Service is currently running. Restarting...${NC}"
    sudo systemctl restart $SERVICE_NAME
else
    echo -e "${YELLOW}Service is not running. Starting...${NC}"
    sudo systemctl start $SERVICE_NAME
fi

sleep 2

if systemctl is-active --quiet $SERVICE_NAME; then
    print_status 0 "Service is running!"
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}SUCCESS! Service is running!${NC}"
    echo -e "${GREEN}========================================${NC}\n"
    
    echo "Service status:"
    sudo systemctl status $SERVICE_NAME --no-pager | head -15
    
    echo -e "\n${BLUE}Recent logs:${NC}"
    sudo journalctl -u $SERVICE_NAME -n 10 --no-pager
    
    echo -e "\n${BLUE}To monitor logs in real-time:${NC}"
    echo "  sudo journalctl -u $SERVICE_NAME -f"
    
    echo -e "\n${BLUE}To view full logs:${NC}"
    echo "  sudo journalctl -u $SERVICE_NAME -n 100 --no-pager"
    
else
    print_status 1 "Service failed to start"
    echo -e "\n${RED}========================================${NC}"
    echo -e "${RED}Service failed to start!${NC}"
    echo -e "${RED}========================================${NC}\n"
    
    echo -e "${YELLOW}Detailed error logs:${NC}"
    sudo journalctl -u $SERVICE_NAME -n 50 --no-pager
    
    echo -e "\n${YELLOW}Common issues to check:${NC}"
    echo "1. Check .env file has valid API keys:"
    echo "   sudo nano $CONFIG_DIR/.env"
    echo ""
    echo "2. Check Python dependencies are installed:"
    echo "   sudo -u $BOT_USER $APP_DIR/venv/bin/pip list"
    echo ""
    echo "3. Test manual startup:"
    echo "   sudo -u $BOT_USER bash"
    echo "   cd $APP_DIR"
    echo "   source venv/bin/activate"
    echo "   python src/main.py"
    echo ""
    echo "4. View detailed troubleshooting guide:"
    echo "   cat $APP_DIR/TROUBLESHOOTING.md"
fi

echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}Quick Fix Script Completed${NC}"
echo -e "${BLUE}========================================${NC}\n"
