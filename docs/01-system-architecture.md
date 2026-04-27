# 01 - System Architecture

## DaveAI Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DAVEAI - AGENTIC 3D PRINT FACTORY                    │
├─────────────────────────────────────────────────────────────────────────┤
│  🤖 Mini-Agent Core  →  Memory, Skills, Tool Execution                │
│  🔌 MiniMax-MCP      →  Vision, Image, Voice, Media Tools              │
│  🔧 Custom MCPs     →  ComfyUI, Moonraker, Blender                    │
│  🖨️ 11-Printer Fleet →  Klipper/Moonraker Controlled                 │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## High-Level System Overview

```mermaid
flowchart TB
    subgraph Input["📥 INPUT LAYER"]
        Photo["📷 Reference Photos"]
        Batch["📁 Batch Folder"]
        API["🔌 REST API"]
        Voice["🎤 Voice Command"]
    end

    subgraph Agent["🤖 DAVEAI AGENT (Mini-Agent)"]
        Core["Agent Core<br/>(Memory, Skills, Tools)"]
        MiniMaxMCP["🔌 MiniMax-MCP<br/>(vision, image, video)"]
        Skills["📋 Skills<br/>(workflow, router, monitor)"]
    end

    subgraph MCPs["🔌 CUSTOM MCPS"]
        ComfyUI["🎨 ComfyUI MCP<br/>(3D Generation)"]
        Moonraker["🌙 Moonraker MCP<br/>(Fleet Control)"]
        Blender["🔧 Blender MCP<br/>(Mesh Processing)"]
    end

    subgraph Hardware["🖥️ HARDWARE"]
        GPU["RTX 3090 Ti<br/>(AI Inference)"]
        Fleet["11 Printer Fleet<br/>(Klipper)"]
    end

    Input --> Agent
    Agent --> MCPs
    MCPs --> Hardware
    Agent --> Skills

    style Agent fill:#1a1a2e,color:#fff
    style MCPs fill:#16213e,color:#fff
```

---

## DaveAI Agent Stack

```mermaid
flowchart TB
    subgraph User["👤 USER"]
        Chat["💬 Chat"]
        Photo["📷 Photo Upload"]
        Voice["🎤 Voice"]
    end

    subgraph MiniAgent["🤖 MINI-AGENT CORE"]
        Loop["Agent Loop<br/>(50+ steps)"]
        Memory["Session Memory<br/>(persistent)"]
        Context["Context Manager<br/>(80K token limit)"]
    end

    subgraph MCPs["🔌 CONNECTED MCPS"]
        MiniMax["MiniMax-MCP<br/>images_understand<br/>gen_images<br/>tts"]
        ComfyUI["ComfyUI MCP<br/>queue_prompt<br/>get_history"]
        Moonraker["Moonraker MCP<br/>get_fleet_status<br/>start_print"]
        Blender["Blender MCP<br/>repair_mesh<br/>export_stl"]
    end

    subgraph Tools["🛠️ TOOLS"]
        File["📁 File Tools<br/>(Read, Write, Edit)"]
        Bash["💻 Bash/Shell<br/>Commands"]
        Skills["📋 Skills Loader<br/>Custom Workflows"]
    end

    User --> MiniAgent
    MiniAgent --> MCPs
    MiniAgent --> Tools
    Tools --> File
    Tools --> Bash
    Tools --> Skills
```

---

## Data Flow Architecture

```mermaid
flowchart LR
    subgraph Input
        P["📷 Photo"]
        S["📄 STL File"]
        B["📁 Batch"]
    end

    subgraph MiniAgent["🤖 MINI-AGENT"]
        Analyze["Analyze Request"]
        Decide["Decide Action"]
        Execute["Execute Tools"]
    end

    subgraph MCPs["🔌 MCPS"]
        Vision["MiniMax Vision"]
        Generate["ComfyUI 3D"]
        Process["Blender Mesh"]
        Print["Moonraker Fleet"]
    end

    subgraph Output
        STL["💾 STL Ready"]
        Print["🖨️ Printing"]
        Status["📊 Status Update"]
    end

    Input --> MiniAgent
    MiniAgent --> MCPs
    MCPs --> Output
```

---

## Component Integration

```mermaid
flowchart TB
    subgraph MiniAgent_Core["🤖 Mini-AgentCore"]
        Agent["Agent.py<br/>(main loop)"]
        LLM["LLM Client<br/>(MiniMax API)"]
        Memory["Session Notes<br/>(persistent)"]
    end

    subgraph MCP_Connection["🔌 MCP TOOLS"]
        MiniMaxTools["MiniMax-MCP<br/>• images_understand<br/>• gen_images<br/>• tts, stt"]
        ComfyUITools["ComfyUI MCP<br/>• queue_prompt<br/>• get_history<br/>• get_output"]
        MoonrakerTools["Moonraker MCP<br/>• fleet_status<br/>• start_print<br/>• get_progress"]
        BlenderTools["Blender MCP<br/>• repair_mesh<br/>• solidify<br/>• export_stl"]
    end

    subgraph External["🌐 EXTERNAL SERVICES"]
        ComfyUIServer["ComfyUI Server<br/>localhost:8188"]
        MoonrakerServer["Moonraker API<br/>mainsail.local:7125"]
        BlenderCLI["Blender CLI<br/>(headless)"]
    end

    subgraph Hardware["🖥️ PRINTERS"]
        Deltas["FLSUN Deltas x5"]
        Cartesians["Cartesian x6"]
    end

    MiniAgent_Core --> MCP_Connection
    ComfyUITools --> ComfyUIServer
    MoonrakerTools --> MoonrakerServer
    BlenderTools --> BlenderCLI
    MoonrakerServer --> Hardware
```

---

## Network Architecture

```mermaid
flowchart TB
    subgraph Internet["🌐 INTERNET"]
        Mobile["📱 Mobile"]
        Remote["💻 Remote PC"]
    end

    subgraph Cloud["☁️ HOSTINGER VPS"]
        Tailscale["Tailscale Exit"]
        Caddy["Caddy Proxy"]
    end

    subgraph Local["🏠 LOCAL NETWORK"]
        subgraph CorePC["🖥️ CORE PC (RTX 3090 Ti)"]
            DaveAI["DaveAI Agent<br/>(Mini-Agent)"]
            ComfyUI["ComfyUI<br/>:8188"]
            MiniMaxAPI["MiniMax API"]
        end

        subgraph PiHost["🍓 RASPBERRY PI / HOST"]
            Moonraker["Moonraker API<br/>:7125"]
            Mainsail["Mainsail<br/>:80"]
        end
    end

    subgraph Printers["🖨️ PRINTERS"]
        V400["FLSUN V400"]
        T1x2["FLSUN T1 x2"]
        Deltas["S1, SuperRacer, QQSP"]
        Cartesians["CR-10S, CR-6, D01, X5SA, MK3S, SV01"]
    end

    Mobile --> Internet
    Remote --> Internet
    Internet --> Cloud
    Cloud --> Local
    Local --> Printers
```

---

## Communication Flow

```mermaid
sequenceDiagram
    participant User
    participant Agent
    participant MiniMaxMCP
    participant ComfyUI
    participant Blender
    participant Moonraker
    participant Printer

    User->>Agent: "Print this photo"
    Agent->>MiniMaxMCP: images_understand(photo)
    MiniMaxMCP-->>Agent: Object analysis

    Agent->>ComfyUI: queue_prompt(workflow)
    ComfyUI-->>Agent: prompt_id
    loop Poll until complete
        Agent->>ComfyUI: get_history(prompt_id)
    end
    ComfyUI-->>Agent: obj_path

    Agent->>Blender: repair_mesh(obj_path)
    Blender-->>Agent: repaired_path
    Agent->>Blender: solidify(repaired_path, 2.5mm)
    Blender-->>Agent: solidified_path
    Agent->>Blender: export_stl(solidified_path)
    Blender-->>Agent: stl_path

    Agent->>Moonraker: get_fleet_status()
    Moonraker-->>Agent: available printers
    Agent->>Moonraker: upload_file(stl_path)
    Agent->>Moonraker: start_print(filename)
    Moonraker->>Printer: Execute print

    loop Monitor
        Printer-->>Moonraker: progress
        Moonraker-->>Agent: 50% complete
    end
    Printer-->>Moonraker: Done
    Moonraker-->>Agent: Complete
    Agent-->>User: Print finished!
```

---

## File Structure

```
3d-printer-daveai/
├── Mini-Agent/                    # Agent framework (git submodule)
│   ├── mini_agent/
│   │   ├── agent.py             # Core agent loop
│   │   ├── llm/                  # LLM clients (MiniMax, OpenAI, Anthropic)
│   │   ├── tools/               # Base tools, MCP loader
│   │   └── skills/              # Skills loader
│   └── examples/                 # Example usage
│
├── config/
│   ├── config.yaml               # Mini-Agent configuration
│   ├── mcp.json                  # MCP server connections
│   └── system_prompt.md         # DaveAI personality
│
├── mcp/                          # Custom MCP servers
│   ├── comfyui-mcp/              # ComfyUI integration
│   ├── moonraker-mcp/           # Printer fleet control
│   └── blender-mcp/             # Mesh processing
│
├── skills/                       # DaveAI skills
│   ├── 3d-print-workflow/       # Main print pipeline
│   ├── printer-router/           # Fleet routing
│   ├── fleet-monitor/           # Status monitoring
│   └── batch-processor/         # Queue management
│
├── scripts/
│   ├── blender/                  # Standalone Blender scripts
│   └── klipper/                  # Moonraker helpers
│
├── workflows/                    # ComfyUI workflows
│   ├── hunyuan3d-workflow.json
│   └── trellis2-workflow.json
│
├── docs/                         # Documentation
│   ├── 01-system-architecture.md
│   ├── 02-hardware-inventory.md
│   ├── 03-end-to-end-workflow.md
│   ├── 04-fleet-routing.md
│   ├── 05-agentic-system.md
│   ├── 06-blender-automation.md
│   ├── 07-firmware-setup.md
│   ├── 08-mcp-servers.md
│   └── 09-skills.md
│
└── output/                       # Generated files
    ├── comfyui/                  # ComfyUI outputs
    └── blender/                  # Processed STL files
```

---

## MCP Tool Reference

### MiniMax-MCP (Installed via npm)

| Tool | Description | Use Case |
|------|-------------|----------|
| `images_understand` | Analyze images with vision | Photo analysis |
| `gen_images` | Generate images | Reference creation |
| `tts` | Text to speech | Voice notifications |
| `stt` | Speech to text | Voice commands |

### ComfyUI MCP (Custom)

| Tool | Description | Use Case |
|------|-------------|----------|
| `comfyui_queue_prompt` | Queue workflow execution | 3D generation |
| `comfyui_get_history` | Get execution status | Track progress |
| `comfyui_get_output` | Download generated file | Get OBJ/GLB |

### Moonraker MCP (Custom)

| Tool | Description | Use Case |
|------|-------------|----------|
| `moonraker_get_fleet_status` | All printer statuses | Fleet overview |
| `moonraker_upload_file` | Upload to printer | Send STL |
| `moonraker_start_print` | Start print job | Execute print |
| `moonraker_get_print_stats` | Print progress | Monitor status |

### Blender MCP (Custom)

| Tool | Description | Use Case |
|------|-------------|----------|
| `blender_repair_mesh` | Fix mesh issues | Pre-print prep |
| `blender_solidify` | Add wall thickness | Make watertight |
| `blender_export_stl` | Export final STL | Ready to slice |
| `blender_check_printable` | Validate mesh | Pre-flight check |

---

## Setup Checklist

- [ ] Install Mini-Agent dependencies (`uv sync`)
- [ ] Configure `config/config.yaml` with MiniMax API key
- [ ] Configure `config/mcp.json` with all MCP servers
- [ ] Install MiniMax-MCP (`npx -y @minimax-ai/mcp-server`)
- [ ] Install Blender and verify CLI works
- [ ] Configure Moonraker API access
- [ ] Load and test skills
- [ ] Run full pipeline test
