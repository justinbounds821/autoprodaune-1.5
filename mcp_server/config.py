"""Configuration management for FastMCP Server"""

import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

# Determine root directory
ROOT_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = Path(__file__).resolve().parent / ".env"

# Load environment variables
load_dotenv(ENV_PATH)


@dataclass
class Settings:
    """Application settings"""

    # Core
    environment: str = os.getenv("MCP_ENV", "development")
    server_host: str = os.getenv("MCP_SERVER_HOST", "127.0.0.1")
    server_port: int = int(os.getenv("MCP_SERVER_PORT", "8012"))  # Changed to 8012

    # Orchestrator
    orchestrator_url: str = os.getenv("ORCHESTRATOR_URL", "http://127.0.0.1:3030")
    orchestrator_node_path: str = os.getenv("ORCHESTRATOR_NODE_PATH", "node")
    orchestrator_index_path: str = os.getenv(
        "ORCHESTRATOR_INDEX_PATH",
        str(Path.home() / "Desktop" / "autoprodaune-1.5" / "mcp-orchestrator" / "dist" / "index.js"),
    )

    # External integrations (used by orchestrator, but accessible here for reference)
    github_token: str = os.getenv("GITHUB_TOKEN", "")
    github_repo: str = os.getenv("GITHUB_REPO", "")
    github_branch: str = os.getenv("GITHUB_BRANCH", "")

    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")
    supabase_service_key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

    vercel_token: str = os.getenv("VERCEL_TOKEN", "")
    vercel_org_id: str = os.getenv("VERCEL_ORG_ID", "")
    vercel_project_id: str = os.getenv("VERCEL_PROJECT_ID", "")

    railway_token: str = os.getenv("RAILWAY_TOKEN", "")
    railway_project_id: str = os.getenv("RAILWAY_PROJECT_ID", "")

    discord_webhook_url: str = os.getenv("DISCORD_WEBHOOK_URL", "")

    # Linear
    linear_api_key: str = os.getenv("LINEAR_API_KEY", "")
    linear_team_id: str = os.getenv("LINEAR_TEAM_ID", "")

    # OpenAI (for GPT Developer Mode)
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


def get_settings() -> Settings:
    """Get application settings singleton"""
    return Settings()


def repo_root() -> Path:
    """Get repository root directory"""
    return ROOT_DIR
