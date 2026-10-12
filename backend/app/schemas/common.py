from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Esquema de respuesta para el endpoint de comprobación de salud."""

    status: str = Field(default="ok", description="Estado operativo del servicio")
    app_name: str = Field(..., description="Nombre del servicio")
    environment: str = Field(..., description="Entorno de ejecución")
