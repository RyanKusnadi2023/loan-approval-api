from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    database: str = "db_loan"
    username: str = "bdpit4"
    password: str = "Bcabca01"
    
    @property
    def conenction_string(self) -> str:
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self