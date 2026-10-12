# Modelo de Datos - LessonForge AI

## 1. Entidades Principales y Relaciones

### 1.1 `users`
- `id`: UUID (PK)
- `email`: VARCHAR(255) UNIQUE
- `hashed_password`: VARCHAR(255)
- `full_name`: VARCHAR(255)
- `role`: ENUM ('teacher', 'student')
- `created_at`: TIMESTAMP

### 1.2 `classrooms`
- `id`: UUID (PK)
- `name`: VARCHAR(255)
- `teacher_id`: UUID (FK -> users.id) - Propietario de la clase
- `created_at`: TIMESTAMP

### 1.3 `classroom_members` (Tabla intermedia)
- `classroom_id`: UUID (FK -> classrooms.id)
- `student_id`: UUID (FK -> users.id)
- `joined_at`: TIMESTAMP

### 1.4 `documents`
- `id`: UUID (PK)
- `owner_id`: UUID (FK -> users.id)
- `classroom_id`: UUID (FK -> classrooms.id, Opcional)
- `title`: VARCHAR(255)
- `file_path`: VARCHAR(512) - Ubicación del PDF en almacenamiento
- `file_hash`: VARCHAR(64) - Hash SHA-256 para integridad
- `processing_status`: ENUM ('PENDING', 'PROCESSED', 'FAILED')
- `created_at`: TIMESTAMP

### 1.5 `document_chunks`
- `id`: UUID (PK)
- `document_id`: UUID (FK -> documents.id)
- `chunk_index`: INTEGER
- `content`: TEXT - Texto extraído y sanitizado
- `token_count`: INTEGER
- `created_at`: TIMESTAMP

### 1.6 `generation_jobs` (Trazabilidad y Resiliencia)
- `id`: UUID (PK)
- `teacher_id`: UUID (FK -> users.id)
- `document_id`: UUID (FK -> documents.id)
- `activity_type`: ENUM ('multiple_choice', 'fill_blank')
- `status`: ENUM ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')
- `retry_count`: INTEGER DEFAULT 0
- `max_retries`: INTEGER DEFAULT 3
- `error_message`: TEXT (Nullable)
- `prompt_version`: VARCHAR(50)
- `model_name`: VARCHAR(100)
- `created_at`: TIMESTAMP
- `updated_at`: TIMESTAMP

### 1.7 `activities`
- `id`: UUID (PK)
- `classroom_id`: UUID (FK -> classrooms.id)
- `generation_job_id`: UUID (FK -> generation_jobs.id, Nullable)
- `title`: VARCHAR(255)
- `activity_type`: ENUM ('multiple_choice', 'fill_blank')
- `content_payload`: JSONB - Estructura de preguntas, opciones y claves correctas
- `created_at`: TIMESTAMP

### 1.8 `submissions` (Intentos y Evaluaciones)
- `id`: UUID (PK)
- `activity_id`: UUID (FK -> activities.id)
- `student_id`: UUID (FK -> users.id)
- `answers_payload`: JSONB - Respuestas enviadas por el alumno
- `grade_score`: NUMERIC(5,2) - Calificación determinista calculada
- `grade_breakdown`: JSONB - Detalle de aciertos y fallos deterministas
- `pedagogical_feedback`: TEXT - Observaciones y recomendaciones de la IA
- `submitted_at`: TIMESTAMP
