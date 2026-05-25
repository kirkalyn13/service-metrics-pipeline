from datetime import datetime
from pydantic import BaseModel

class SpeedTestResult(BaseModel):
    timestamp: datetime = None
    isp: str
    ip: str
    location: str
    download_speed: float
    upload_speed: float
    idle_latency: int
    download_latency: int
    upload_latency: int