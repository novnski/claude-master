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

pip3 install --user --quiet textual pyyaml watchdog

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dependencies installed successfully${NC}"
else
    echo -e "${RED}✗ Failed to install dependencies${NC}"
    exit 1
fi
echo ""

# Create command wrapper
echo -e "${YELLOW}Creating command alias...${NC}"
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"

cat > "$BIN_DIR/claude-dashboard" << EOF
#!/bin/bash
cd "$INSTALL_DIR" && python3 -m claude_dashboard "\$@"
EOF

chmod +x "$BIN_DIR/claude-dashboard"
echo -e "${GREEN}✓ Command created: $BIN_DIR/claude-dashboard${NC}"
echo ""

# Detect shell and configure PATH automatically
echo -e "${YELLOW}Configuring PATH for your shell...${NC}"

# Detect current shell
SHELL_NAME="$(basename "$SHELL")"
CONFIG_FILE=""
CONFIG_LINE=""
PATH_EXPORT="export PATH=\"\$HOME/.local/bin:\$PATH\""
PATH_ADDED=false

case "$SHELL_NAME" in
    zsh)
        CONFIG_FILE="$HOME/.zshrc"
        CONFIG_LINE="# Claude Master Dashboard"
        ;;
    bash)
        # Check for .bashrc or .bash_profile
        if [ -f "$HOME/.bashrc" ]; then
            CONFIG_FILE="$HOME/.bashrc"
        elif [ -f "$HOME/.bash_profile" ]; then
            CONFIG_FILE="$HOME/.bash_profile"
        else
            # Create .bashrc if it doesn't exist
            CONFIG_FILE="$HOME/.bashrc"
            touch "$CONFIG_FILE"
        fi
        CONFIG_LINE="# Claude Master Dashboard"
        ;;
    fish)
        CONFIG_FILE="$HOME/.config/fish/config.fish"
        mkdir -p "$(dirname "$CONFIG_FILE")"
        CONFIG_LINE="# Claude Master Dashboard"
        PATH_EXPORT="set -gx PATH \$HOME/.local/bin \$PATH"
        if [ ! -f "$CONFIG_FILE" ]; then
            touch "$CONFIG_FILE"
        fi
        ;;
    *)
        echo -e "${YELLOW}⚠ Unknown shell: $SHELL_NAME${NC}"
        echo -e "${YELLOW}  Adding to ~/.profile (fallback)${NC}"
        CONFIG_FILE="$HOME/.profile"
        CONFIG_LINE="# Claude Master Dashboard"
        ;;
esac

# Check if PATH already contains ~/.local/bin
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    # Add to shell config
    if [ -n "$CONFIG_FILE" ]; then
        # Check if our marker already exists
        if ! grep -q "$CONFIG_LINE" "$CONFIG_FILE" 2>/dev/null; then
            {
                echo ""
                echo "$CONFIG_LINE"
                echo "$PATH_EXPORT"
            } >> "$CONFIG_FILE"
            echo -e "${GREEN}✓ Added PATH to $CONFIG_FILE${NC}"
            PATH_ADDED=true
        else
            echo -e "${YELLOW}⚠ PATH already configured in $CONFIG_FILE${NC}"
        fi
    fi

    # Also add to ~/.profile for all shells
    if [ "$CONFIG_FILE" != "$HOME/.profile" ] && [ -f "$HOME/.profile" ]; then
        if ! grep -q "$CONFIG_LINE" "$HOME/.profile" 2>/dev/null; then
            {
                echo ""
                echo "$CONFIG_LINE"
                echo "$PATH_EXPORT"
            } >> "$HOME/.profile"
            echo -e "${GREEN}✓ Also added to ~/.profile${NC}"
        fi
    fi
else
    echo -e "${GREEN}✓ PATH already configured${NC}"
fi
echo ""

# Source the config to make it work immediately
if [ "$PATH_ADDED" = true ] && [ -f "$CONFIG_FILE" ]; then
    echo -e "${YELLOW}Sourcing configuration...${NC}"
    # Source in a way that works for both bash and zsh
    if [ "$SHELL_NAME" = "zsh" ]; then
        source "$CONFIG_FILE" 2>/dev/null || true
    elif [ "$SHELL_NAME" = "bash" ]; then
        source "$CONFIG_FILE" 2>/dev/null || true
    fi
    echo -e "${GREEN}✓ Configuration loaded${NC}"
    echo ""
fi

# Verify installation
echo -e "${YELLOW}Verifying installation...${NC}"
if command -v claude-dashboard &> /dev/null; then
    echo -e "${GREEN}✓ 'claude-dashboard' command is available${NC}"
else
    echo -e "${YELLOW}⚠ Command not found in current session${NC}"
    echo -e "${YELLOW}  It will be available in new terminal sessions${NC}"
fi
echo ""

# Done!
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    Installation Complete!                    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Quick Start:${NC}"
echo ""
echo -e "  ${GREEN}➜  Open a new terminal window (or restart your shell)${NC}"
echo -e "  ${GREEN}➜  Run:${NC} ${BLUE}claude-dashboard${NC}"
echo ""
echo -e "Or run directly from this directory:"
echo -e "  ${BLUE}cd $INSTALL_DIR && python3 -m claude_dashboard${NC}"
echo ""
echo -e "${YELLOW}Note: Your shell config was updated automatically.${NC}"
echo -e "${YELLOW}      The command will work in new terminal sessions.${NC}"
echo ""
