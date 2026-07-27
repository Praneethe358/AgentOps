from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AgentOps Orchestrator"
    POSTGRES_URI: str = "postgresql://postgres:postgrespassword@localhost:5432/agentops_db?sslmode=disable"
    
    class Config:
        env_file = ".env"

settings = Settings()
