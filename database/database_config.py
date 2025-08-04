from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class DatabaseConfig:
    host: str
    port: int
    database: str
    username: str
    password: str
    
    @property
    def conenction_string(self) -> str:
        return f"postgresql://{self.username}:{self.password}{self.host}:{self.port}/{self.database}"
    