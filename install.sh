#!/bin/bash

# Claude Master Dashboard Installation Script
# This script installs the Claude Master Dashboard and its dependencies

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       Claude Master Dashboard - Installation Script       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    echo "Please install Python 3.10 or higher from https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}Error: Python $REQUIRED_VERSION or higher is required (found $PYTHON_VERSION)${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"
echo ""

# Check if pip is available
echo -e "${YELLOW}Checking pip availability...${NC}"
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}Error: pip3 is not installed${NC}"
    echo "Please install pip: https://pip.pypa.io/en/stable/installation/"
    exit 1
fi
echo -e "${GREEN}✓ pip3 found${NC}"
echo ""

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
echo "  - textual (TUI framework)"
echo "  - pyyaml (frontmatter parsing)"
echo "  - watchdog (file watching)"

pip3 install --user textual pyyaml watchdog

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dependencies installed successfully${NC}"
else
    echo -e "${RED}✗ Failed to install dependencies${NC}"
    exit 1
fi
echo ""

# Create symlink for easy access (optional)
echo -e "${YELLOW}Creating command alias...${NC}"
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"

cat > "$BIN_DIR/claude-dashboard" << EOF
#!/bin/bash
cd "$INSTALL_DIR" && python3 -m claude_dashboard "\$@"
EOF

chmod +x "$BIN_DIR/claude-dashboard"

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo -e "${YELLOW}⚠ $HOME/.local/bin is not in your PATH${NC}"
    echo ""
    echo "Add the following to your ~/.bashrc or ~/.zshrc:"
    echo -e "${GREEN}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
    echo ""
    echo "Then run: source ~/.bashrc (or source ~/.zshrc)"
else
    echo -e "${GREEN}✓ Command 'claude-dashboard' created in $BIN_DIR${NC}"
fi
echo ""

# Done!
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    Installation Complete!                    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "To run the dashboard:"
echo -e "  ${BLUE}claude-dashboard${NC}"
echo ""
echo "Or directly:"
echo -e "  ${BLUE}cd $INSTALL_DIR && python3 -m claude_dashboard${NC}"
echo ""
echo "For help, run:"
echo -e "  ${BLUE}claude-dashboard --help${NC}"
echo ""
