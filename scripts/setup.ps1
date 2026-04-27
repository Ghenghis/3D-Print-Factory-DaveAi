# DaveAI Setup Script
# Run this to set up the complete DaveAI environment

param(
    [string]$MiniMaxApiKey = "",
    [string]$MoonrakerApiKey = ""
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DaveAI - Agentic 3D Print Factory" -ForegroundColor Cyan
Write-Host "  Setup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "[1/7] Checking prerequisites..." -ForegroundColor Yellow

# Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Python not found. Install Python 3.10+ first." -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ Python found: $(python --version)"

# Check uv
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "  Installing uv..."
    powershell -Command "irm https://astral.sh/uv/install.ps1 | iex"
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
}
Write-Host "  ✓ uv found"

# Check Blender
if (-not (Get-Command blender -ErrorAction SilentlyContinue)) {
    Write-Host "  WARNING: Blender not found in PATH" -ForegroundColor Yellow
    Write-Host "  Download from: https://www.blender.org/download/" -ForegroundColor Yellow
} else {
    Write-Host "  ✓ Blender found: $(blender --version | Select-Object -First 1)"
}

# Check Node.js
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "  WARNING: Node.js not found. Install for MiniMax-MCP." -ForegroundColor Yellow
    Write-Host "  Download from: https://nodejs.org/" -ForegroundColor Yellow
} else {
    Write-Host "  ✓ Node.js found: $(node --version)"
}

Write-Host ""

# Initialize git submodules
Write-Host "[2/7] Initializing git submodules..." -ForegroundColor Yellow
if (Test-Path ".gitmodules") {
    git submodule update --init --recursive
    Write-Host "  ✓ Submodules initialized"
} else {
    Write-Host "  ⚠ No submodules configured"
}

Write-Host ""

# Install Python dependencies
Write-Host "[3/7] Installing Python dependencies..." -ForegroundColor Yellow
uv sync
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Dependencies installed"
} else {
    Write-Host "  ERROR: Failed to install dependencies" -ForegroundColor Red
}

Write-Host ""

# Install MiniMax-MCP
Write-Host "[4/7] Installing MiniMax-MCP..." -ForegroundColor Yellow
if (Get-Command npx -ErrorAction SilentlyContinue) {
    npm install -g @minimax-ai/mcp-server
    Write-Host "  ✓ MiniMax-MCP installed"
} else {
    Write-Host "  ⚠ SKIPPED: Node.js required" -ForegroundColor Yellow
}

Write-Host ""

# Create config files
Write-Host "[5/7] Creating configuration files..." -ForegroundColor Yellow

# config.yaml
$configYaml = @"
# DaveAI Configuration
api_key: "${MiniMaxApiKey}"
api_base: "https://api.minimax.io"
model: "MiniMax-M2.5"
provider: "anthropic"

max_steps: 100
workspace_dir: "./workspace"

tools:
  enable_file_tools: true
  enable_bash: true
  enable_skills: true
  skills_dir: "./skills"
  enable_mcp: true
  mcp_config_path: "mcp.json"

daveai:
  comfyui_url: "http://localhost:8188"
  moonraker_url: "http://mainsail.local:7125"
  moonraker_api_key: "${MoonrakerApiKey}"
"@

if (-not (Test-Path "config")) {
    New-Item -ItemType Directory -Path "config" | Out-Null
}
Set-Content -Path "config/config.yaml" -Value $configYaml
Write-Host "  ✓ config/config.yaml created"

# mcp.json
$mcpJson = @"
{
  "mcpServers": {
    "minimax": {
      "command": "npx",
      "args": ["-y", "@minimax-ai/mcp-server"],
      "env": {
        "MINIMAX_API_KEY": "${MiniMaxApiKey}"
      }
    },
    "comfyui": {
      "command": "python",
      "args": ["-m", "mcp.comfyui-mcp"],
      "env": {
        "COMFYUI_HOST": "localhost",
        "COMFYUI_PORT": "8188"
      },
      "execute_timeout": 300
    },
    "moonraker": {
      "type": "streamable_http",
      "url": "http://mainsail.local:7125",
      "headers": {
        "X-Api-Key": "${MoonrakerApiKey}"
      }
    },
    "blender": {
      "command": "blender",
      "args": ["--background", "--python", "./mcp/blender-mcp/__init__.py"]
    }
  }
}
"@

Set-Content -Path "config/mcp.json" -Value $mcpJson
Write-Host "  ✓ config/mcp.json created"

Write-Host ""

# Create directories
Write-Host "[6/7] Creating directory structure..." -ForegroundColor Yellow
$dirs = @("output/comfyui", "output/blender", "input/photos", "input/stl", "workspace")
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Host "  ✓ Directories created"

Write-Host ""

# Final instructions
Write-Host "[7/7] Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Next Steps" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Edit config files with your API keys:" -ForegroundColor White
Write-Host "   - config/config.yaml" -ForegroundColor Gray
Write-Host "   - config/mcp.json" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Start ComfyUI if not running:" -ForegroundColor White
Write-Host "   python ComfyUI/main.py" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Run DaveAI:" -ForegroundColor White
Write-Host "   uv run python -m mini_agent.cli --config config/config.yaml" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Or with custom system prompt:" -ForegroundColor White
Write-Host "   uv run python -m mini_agent.cli --config config/config.yaml --system-prompt config/system_prompt.md" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
