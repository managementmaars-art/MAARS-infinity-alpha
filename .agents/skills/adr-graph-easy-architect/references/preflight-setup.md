# Preflight Setup

Run these checks in order. Each layer depends on the previous.

## Layer 1: Package Manager

```bash
/usr/bin/env bash << 'SETUP_EOF'
# Detect OS and set package manager
case "$(uname -s)" in
  Darwin) PM="brew" ;;
  Linux)  PM="apt" ;;
  *)      echo "ERROR: Unsupported OS (require macOS or Linux)"; exit 1 ;;
esac
command -v $PM &>/dev/null || { echo "ERROR: $PM not installed"; exit 1; }
echo "✓ Package manager: $PM"
SETUP_EOF
```

## Layer 2: Perl + cpanminus (mise-first approach)

```bash
# Prefer mise for unified tool management
if command -v mise &>/dev/null; then
  # Install Perl via mise
  mise which perl &>/dev/null || mise install perl
  # Install cpanminus under mise perl
  mise exec perl -- cpanm --version &>/dev/null 2>&1 || {
    echo "Installing cpanminus under mise perl..."
    mise exec perl -- curl -L https://cpanmin.us | mise exec perl -- perl - App::cpanminus
  }
  echo "✓ cpanminus installed (via mise perl)"
else
  # Fallback: Install cpanminus via system package manager
  command -v cpanm &>/dev/null || {
    echo "Installing cpanminus via $PM..."
    case "$PM" in
      brew) brew install cpanminus ;;
      apt)  sudo apt install -y cpanminus ;;
    esac
  }
  echo "✓ cpanminus installed"
fi
```

## Layer 3: Graph::Easy Perl module

```bash
# Check if Graph::Easy is installed (mise-first)
if command -v mise &>/dev/null; then
  mise exec perl -- perl -MGraph::Easy -e1 2>/dev/null || {
    echo "Installing Graph::Easy via mise perl cpanm..."
    mise exec perl -- cpanm Graph::Easy
  }
  echo "✓ Graph::Easy installed (via mise perl)"
else
  perl -MGraph::Easy -e1 2>/dev/null || {
    echo "Installing Graph::Easy via cpanm..."
    cpanm Graph::Easy
  }
  echo "✓ Graph::Easy installed"
fi
```

## Layer 4: Verify graph-easy is in PATH

```bash
# Verify graph-easy is accessible and functional
command -v graph-easy &>/dev/null || {
  echo "ERROR: graph-easy not found in PATH"
  exit 1
}
# Test actual functionality (--version exits with code 2, unreliable)
echo "[Test] -> [OK]" | graph-easy &>/dev/null && echo "✓ graph-easy ready"
```

## All-in-One Preflight Script

```bash
/usr/bin/env bash << 'PREFLIGHT_EOF'
# Copy-paste this entire block to ensure graph-easy is ready (macOS + Linux)
# Prefers mise for unified cross-platform tool management

# Check for mise first (recommended)
if command -v mise &>/dev/null; then
  echo "Using mise for Perl management..."
  mise which perl &>/dev/null || mise install perl
  mise exec perl -- cpanm --version &>/dev/null 2>&1 || \
    mise exec perl -- curl -L https://cpanmin.us | mise exec perl -- perl - App::cpanminus
  mise exec perl -- perl -MGraph::Easy -e1 2>/dev/null || mise exec perl -- cpanm Graph::Easy
else
  # Fallback: system package manager
  echo "💡 Tip: Install mise for unified tool management: curl https://mise.run | sh"
  case "$(uname -s)" in
    Darwin) PM="brew" ;;
    Linux)  PM="apt" ;;
    *)      echo "ERROR: Unsupported OS"; exit 1 ;;
  esac
  command -v $PM &>/dev/null || { echo "ERROR: $PM not installed"; exit 1; }
  command -v cpanm &>/dev/null || { [ "$PM" = "apt" ] && sudo apt install -y cpanminus || brew install cpanminus; }
  perl -MGraph::Easy -e1 2>/dev/null || cpanm Graph::Easy
fi

# Verify graph-easy is in PATH and functional
command -v graph-easy &>/dev/null || {
  echo "ERROR: graph-easy not in PATH after installation"
  exit 1
}
# Test actual functionality (--version exits with code 2, unreliable)
echo "[Test] -> [OK]" | graph-easy &>/dev/null && echo "✓ graph-easy ready"
PREFLIGHT_EOF
```
