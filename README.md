# Restaurant Backend (FastAPI + Async SQLAlchemy + JWT + RBAC + WebSockets)

Backend asíncrono para gestionar un restaurante:
- FastAPI (async), SQLAlchemy Async, JWT, RBAC por permisos.
- WebSockets en tiempo real para pedidos y menú.
- Documentación (`/docs`, `/openapi.json`) protegible por Basic Auth o token.

**Stack**
- Framework: `fastapi`
- Server: `uvicorn`
- DB: `sqlalchemy` async (`aiomysql`/`asyncmy`)
- Auth: `python-jose`, `passlib[bcrypt]`
- WebSockets: FastAPI WS
- Env: `python-dotenv`

**Carpetas clave**
- `app/main.py`: inicialización, routers, protección de docs, OpenAPI.
- `app/core/security.py`: JWT, OAuth2 y helpers de seguridad.
- `app/db/base.py`: `create_async_engine`, `AsyncSessionLocal` y pool de conexiones.
- `app/routers/`: endpoints REST y WebSockets:
  - `auth`, `user`, `menu`, `tables`, `orders`, `reservations`, `category`, `sub_category`, `ws_orders`, `ws_menu`
- `app/models/`, `app/schemas/`: modelos SQLAlchemy y esquemas Pydantic.
- `app/requirements.txt`: dependencias.

---

## Requisitos

- Python 3.11+
- MySQL 8.x (o compatible)
- Windows (comandos y rutas mostrados para Windows)

---

## Instalación

1) Crear entorno virtual (si no usas el `env` ya presente):

```bash
python -m venv env
```

2) Activar entorno virtual:

```bash
env\Scripts\activate
```

3) Instalar dependencias:

```bash
pip install -r app\requirements.txt
```

---

## Configuración (.env)

Crea o edita `app\.env` con:

- Base de datos:
  - `DATABASE_URL` (default `mysql+aiomysql://user:password@localhost:3306/restaurant_db`)
- Pool de conexiones:
  - `DB_POOL_SIZE` (default `10`)
  - `DB_MAX_OVERFLOW` (default `20`)
  - `DB_POOL_RECYCLE` (default `1800`)
  - `DB_POOL_TIMEOUT` (default `30`)
  - `DB_POOL_PRE_PING` (`true`/`false`, default `true`)
- JWT:
  - `JWT_SECRET` (default `secret`)
  - `JWT_ALGORITHM` (default `HS256`)
  - `ACCESS_TOKEN_EXPIRE_MINUTES` (default `60`)
- Protección de documentación:
  - `PROTECT_DOCS` (`true`/`false`)
  - `DOCS_AUTH_MODE` (`basic` o `token`)
  - `DOCS_ROLE_ID` (ID de rol con acceso cuando `DOCS_AUTH_MODE=token`, default `1`)
  - `DOCS_USER`, `DOCS_PASS` (si `DOCS_AUTH_MODE=basic`)

Ejemplo mínimo:

```bash
DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/restaurant_db
JWT_SECRET=supersecret
PROTECT_DOCS=true
DOCS_AUTH_MODE=token
DOCS_ROLE_ID=1
```

---

## Ejecutar

Desde `backend_restaurant\app`:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Health check:

```bash
http://localhost:8000/
```

Nota: `main.py` crea las tablas automáticamente en `startup` con `Base.metadata.create_all`.

---

## Documentación API

- Si `PROTECT_DOCS=false`:
  - `http://localhost:8000/docs`
  - `http://localhost:8000/redoc`
  - `http://localhost:8000/openapi.json`
- Si `PROTECT_DOCS=true`:
  - Modo `basic`: introduce `DOCS_USER` y `DOCS_PASS`.
  - Modo `token`: restringe `/openapi.json` y, por extensión, Swagger UI. Usa un usuario con rol `DOCS_ROLE_ID` (p. ej., admin) y envía el token como Bearer en los requests.

Dentro de Swagger, pulsa “Authorize”:
- Esquema `BearerAuth` (global): pega solo el token (sin prefijo `Bearer`).
- Los endpoints con `OAuth2PasswordBearer` también aceptan el token.

---

## Autenticación

Login:

```bash
curl -Method POST -Uri http://localhost:8000/auth/login -Body (@{dni="12345678";password="secret"} | ConvertTo-Json) -ContentType "application/json"
```

Respuesta:

```json
{"access_token":"<JWT>","token_type":"bearer"}
```

Usa el token:
- Headers: `Authorization: Bearer <JWT>`
- Swagger: botón “Authorize” y pega el token.

---

## Endpoints principales

- Menú:
  - `GET /menu` — lista ítems (permiso `read`).
  - `POST /menu` — crear (permiso `crud`).
  - `PUT /menu/{id}` — actualizar (permiso `crud`).
  - `DELETE /menu/{id}` — eliminar (permiso `crud`).
- Mesas:
  - `GET /tables`, `POST /tables`, `PUT /tables/{id}`, `DELETE /tables/{id}`.
- Reservas:
  - `GET /reservations`, `PUT /reservations/{id}`.
- Pedidos:
  - `GET /orders`, `POST /orders`.
- Usuarios:
  - `GET /user`, `GET /user/{id}`, `PUT /user/{id}` — protegidos por token.
- Categorías y Subcategorías:
  - `GET /category`, `GET /category/{id}`
  - `GET /sub_categories`, `GET /sub_categories/{id}`

Protección por roles:
- Usa `get_current_user` (token) y `permission_required("read"|"crud")` para RBAC según rol.

---

## WebSockets

- Pedidos: `ws://localhost:8000/ws/orders`
- Menú: `ws://localhost:8000/ws/menu` (montado mediante `routers/ws_menu.py` en `main.py`)

Ejemplo navegador:

```bash
# JavaScript (incluirlo en console o tu app)
const ws = new WebSocket("ws://localhost:8000/ws/menu");
ws.onopen = () => console.log("Conectado");
ws.onmessage = (e) => console.log("WS:", e.data);
ws.onclose = () => console.log("Cerrado");
```

Con token opcional por query:

```bash
# JavaScript
const token = "<JWT>";
const ws = new WebSocket(`ws://localhost:8000/ws/menu?token=${encodeURIComponent(token)}`);
```

Broadcast:
- Eventos de menú (`menu_created`, `menu_updated`, `menu_deleted`) se emiten después de `commit` para asegurar estado final.

---

## Pool de Conexiones (DB)

En `app/db/base.py`, el engine async usa pool configurable por `.env`:
- `DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, `DB_POOL_RECYCLE`, `DB_POOL_TIMEOUT`, `DB_POOL_PRE_PING`.
- Ajusta `pool_recycle` bajo el `wait_timeout` de MySQL.
- Define `pool_size`/`max_overflow` según el número de workers y `max_connections`.

---

## Migrations (Opcional)

Alembic está inicializado:
- Edita `app/alembic.ini` con tu `sqlalchemy.url`.
- Usa migraciones si prefieres versionar el esquema.
- El proyecto funciona sin Alembic porque crea tablas al inicio.

---

## Troubleshooting

- `403` al conectar a `ws://.../ws/menu`:
  - Verifica que `app.include_router(ws_menu.router)` esté en `main.py`.
  - Usa `ws://localhost:8000/ws/menu` (no `ws://localhost:8000/menu/ws/menu`).
  - Si pasas `?token`, asegura que el JWT sea válido (tenga `user_id`).
- `401` en endpoints:
  - Token inválido o expirado.
  - El usuario no existe o no tiene permisos requeridos (ver RBAC).
- DB:
  - Revisa credenciales y `DATABASE_URL`.
  - Ajusta parámetros del pool según carga y límites del servidor.

---