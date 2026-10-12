# Modelo de datos — LessonForge AI

**Versión 2.0.** PostgreSQL 16 con la extensión `vector` (pgvector). Todas las claves primarias son
UUID y todas las marcas de tiempo son `timestamptz`.

## 1. Diagrama de relaciones

```
users ─┬─< tutor_students >─┬─ users
       │  (teacher)          │  (student)
       │                     │
       └─< lessons >─────────┘          lessons.teacher_id / lessons.student_id
              │
              ├── documents ── document_blobs (temporal)
              │       └─< document_chunks  (embedding vector)
              │
              └─< activities ─< activity_items ── activity_item_keys
                       │
                       └─< submissions (1 por alumno y actividad)

jobs  (cola: DOCUMENT_INGESTION | ACTIVITY_GENERATION | SUBMISSION_FEEDBACK)
ai_usage (tokens por tutor y día, para cuotas)
```

## 2. Tablas

### `users`
| Columna | Tipo | Notas |
|---|---|---|
| id | UUID PK | |
| email | VARCHAR(255) UNIQUE | Se guarda en minúsculas |
| hashed_password | VARCHAR(255) | Argon2. Nunca aparece en esquemas de respuesta |
| full_name | VARCHAR(255) | Ficticio |
| role | ENUM `teacher`, `student` | |
| is_active | BOOLEAN | |
| created_at | timestamptz | |

### `tutor_students`
| Columna | Tipo | Notas |
|---|---|---|
| teacher_id | UUID FK users | Su rol debe ser `teacher` |
| student_id | UUID FK users | Su rol debe ser `student` |
| created_at | timestamptz | |
| | | PK (`teacher_id`, `student_id`) |

### `lessons`
| Columna | Tipo | Notas |
|---|---|---|
| id | UUID PK | |
| teacher_id | UUID FK users | Propietario |
| student_id | UUID FK users | Debe existir en `tutor_students` con ese tutor (se valida en el servicio) |
| title | VARCHAR(200) | |
| target_language | VARCHAR(5) | Código ISO 639-1 de una lista permitida |
| cefr_level | ENUM `A1`…`C2` | |
| held_at | timestamptz | Fecha de la clase |
| keywords | TEXT[] | 1–20 elementos de hasta 50 caracteres |
| observations | TEXT | Hasta 2000 caracteres. **Solo las ve el tutor** |
| created_at, updated_at | timestamptz | |

### `documents`
| Columna | Tipo | Notas |
|---|---|---|
| id | UUID PK | |
| lesson_id | UUID FK lessons UNIQUE | Un PDF por lección en el MVP |
| original_filename | VARCHAR(255) | Saneado. Solo se muestra, nunca se usa como ruta |
| sha256 | CHAR(64) | Integridad |
| size_bytes | INTEGER | Hasta 10 MB |
| page_count | INTEGER | Hasta 50 |
| status | ENUM `PENDING`, `PROCESSING`, `READY`, `FAILED` | |
| error_code | VARCHAR(50) NULL | Código saneado, por ejemplo `NO_TEXT` o `TOO_MANY_PAGES` |
| created_at, updated_at | timestamptz | |

### `document_blobs` (temporal)
| Columna | Tipo | Notas |
|---|---|---|
| document_id | UUID PK FK documents | |
| content | BYTEA | Se **elimina** cuando la ingesta termina bien (ver ADR-003) |

### `document_chunks`
| Columna | Tipo | Notas |
|---|---|---|
| id | UUID PK | |
| document_id | UUID FK documents | |
| lesson_id | UUID FK lessons | Duplicado a propósito: **filtro obligatorio** en la recuperación |
| chunk_index | INTEGER | |
| page_number | INTEGER | Para citar la fuente |
| content | TEXT | Texto extraído y normalizado |
| token_count | INTEGER | |
| embedding | VECTOR(768) | La dimensión es configurable. Índice HNSW con `vector_cosine_ops` |

### `jobs`
| Columna | Tipo | Notas |
|---|---|---|
| id | UUID PK | |
| job_type | ENUM `DOCUMENT_INGESTION`, `ACTIVITY_GENERATION`, `SUBMISSION_FEEDBACK` | |
| owner_id | UUID FK users | Quien puede consultarlo |
| subject_id | UUID | Documento, actividad o entrega afectada |
| status | ENUM `PENDING`, `PROCESSING`, `COMPLETED`, `FAILED` | |
| attempts | INTEGER DEFAULT 0 | |
| max_attempts | INTEGER DEFAULT 3 | |
| run_after | timestamptz | Espera creciente entre intentos |
| locked_at | timestamptz NULL | Para recuperar bloqueos huérfanos |
| locked_by | VARCHAR(100) NULL | Identificador del worker |
| last_error_code | VARCHAR(50) NULL | Saneado. El detalle técnico solo va a los logs |
| prompt_version | VARCHAR(50) NULL | |
| model_name | VARCHAR(100) NULL | |
| created_at, updated_at, completed_at | timestamptz | |

Índice parcial: `(run_after) WHERE status = 'PENDING'`.

### `activities`
| Columna | Tipo | Notas |
|---|---|---|
| id | UUID PK | |
| lesson_id | UUID FK lessons | El tutor y el alumno se obtienen de la lección |
| activity_type | ENUM `quiz`, `fill_blank` | |
| cefr_level | ENUM | Copia del valor usado en la solicitud |
| item_count | SMALLINT | 1–20 |
| exercise_context | TEXT | Hasta 1000 caracteres |
| keywords | TEXT[] | Copia del valor usado en la solicitud |
| status | ENUM `GENERATING`, `DRAFT`, `PUBLISHED`, `DISCARDED`, `FAILED` | |
| generation_job_id | UUID FK jobs | |
| published_at | timestamptz NULL | |
| created_at | timestamptz | |

### `activity_items`
| Columna | Tipo | Notas |
|---|---|---|
| id | UUID PK | |
| activity_id | UUID FK activities | |
| position | SMALLINT | |
| prompt | TEXT | Enunciado. En `fill_blank` contiene exactamente un `___` |
| options | JSONB NULL | Solo en `quiz`: lista de 3–4 opciones `{id, text}` |
| source_chunk_ids | UUID[] | Citas del RAG |

### `activity_item_keys` (respuestas correctas, en una tabla aparte)
| Columna | Tipo | Notas |
|---|---|---|
| item_id | UUID PK FK activity_items | |
| correct_option_id | VARCHAR(10) NULL | `quiz` |
| accepted_answers | TEXT[] NULL | `fill_blank`: 1–3 variantes aceptadas |
| explanation | TEXT | Se muestra **después** de entregar |

Separar las claves en su propia tabla hace que ninguna consulta de la vista del alumno las cargue
por accidente.

### `submissions`
| Columna | Tipo | Notas |
|---|---|---|
| id | UUID PK | |
| activity_id | UUID FK activities | |
| student_id | UUID FK users | |
| answers | JSONB | `{item_id: respuesta}`. Se valida contra los ítems |
| score | NUMERIC(5,2) | 0–100. Determinista |
| breakdown | JSONB | `[{item_id, is_correct, given, expected}]` |
| feedback_status | ENUM `PENDING`, `READY`, `FAILED` | `FAILED`: el tutor puede volver a encolar el trabajo |
| feedback | JSONB NULL | `{summary, improvements: [{item_id, tip}]}` |
| submitted_at | timestamptz | Inmutable |
| | | **UNIQUE (`activity_id`, `student_id`)**: un solo intento |

### `ai_usage`
| Columna | Tipo | Notas |
|---|---|---|
| teacher_id | UUID FK users | |
| usage_date | DATE | |
| input_tokens, output_tokens | INTEGER | |
| | | PK (`teacher_id`, `usage_date`). Se usa para la cuota diaria (LLM10) |
