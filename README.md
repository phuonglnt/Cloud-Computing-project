# Cloud-Computing-project
# AI Teaching Assistant — Team 2
LLM-based teaching assistant deployed with Docker Compose
Students ask questions and get answers built from the course materials, with the source document cited.

> **Status:** installation and deployment. 
Architecture diagram, NIST analysis and additional services to be added.

## Current architecture

| Service | Role | Image |
| --- | --- | --- |
| `open-webui` | Chat interface, user accounts, knowledge base | Existing image |
| `postgres` | Stores accounts, conversations and knowledge metadata | Existing image |
| `quiz-api` | Generates quizzes from the course materials | Built from our own Dockerfile |

External dependency: the Google Gemini API provides the language model.

How a quiz request is processed:

1. A client calls `POST /quiz` on `quiz-api` with a knowledge base id and a topic.
2. `quiz-api` calls Open WebUI on the internal network, passing the knowledge base.
3. Open WebUI retrieves the relevant passages and queries the Gemini API.
4. The generated quiz is returned to the client.


## Requirements

- Docker with Docker Compose
- UPPA VPN (to reach the school server)
- A Gemini API key, created on `aistudio.google.com/apikey`
- An Open WebUI API key

## Installation

```bash
mkdir -p ~/CodeCloud && cd ~/CodeCloud
```
Create the `.env` file with your own key:

```
OPENAI_API_KEY=your_key_here
```
Create `docker-compose.yml`:

```yaml
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    ports:
      - "3000:8080"
    volumes:
      - open-webui:/app/backend/data
    environment:
      - OPENAI_API_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - RAG_EMBEDDING_ENGINE=openai
      - RAG_EMBEDDING_MODEL=models/gemini-embedding-001
      - DATABASE_URL=postgresql://cloudapp:${POSTGRES_PASSWORD}@postgres:5432/cloudapp
    depends_on:
      - postgres
    restart: always

  postgres:
    image: postgres:16
    volumes:
      - postgres-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=cloudapp
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=cloudapp
    restart: always

  quiz-api:
    build: ./quiz-api
    ports:
      - "8000:8000"
    environment:
      - ASSISTANT_URL=http://open-webui:8080
      - ASSISTANT_API_KEY=${ASSISTANT_API_KEY}
      - NO_PROXY=open-webui,postgres,localhost,127.0.0.1
      - no_proxy=open-webui,postgres,localhost,127.0.0.1
    depends_on:
      - open-webui
    restart: always

volumes:
  open-webui:
```

Start the stack:

```bash
docker compose up -d
docker compose ps
```

## Operations

```bash
docker compose down                     # stop, keep the data
docker compose up -d --force-recreate   # apply changes made to the YAML file
```

**Never run `docker compose down -v`**: the `-v` option deletes the volume, and with it the accounts, the conversations and the knowledge base.

The first start takes a few minutes. Follow the progress with:

```bash
docker compose logs -f --tail 20
```

## Services

| Service | Address | Use |
| --- | --- | --- |
| Assistant | http://10.3.16.187:3000 | Chat interface for students and teachers |
| Quiz API | http://10.3.16.187:8000/docs | Interactive API documentation, quiz generation |
| PostgreSQL | internal only | Not published outside the Docker network |

PostgreSQL has no `ports:` entry on purpose: only the services declared in the same compose file can reach it.

## Configuration

| Variable | Service | Role |
| --- | --- | --- |
| `OPENAI_API_BASE_URL` | open-webui | Gemini API endpoint, compatible with the OpenAI format |
| `OPENAI_API_KEY` | open-webui | Gemini key, read from `.env` |
| `HTTPS_PROXY` / `https_proxy` | open-webui | University proxy, required to reach the Internet |
| `RAG_EMBEDDING_ENGINE` | open-webui | Indexing engine, set to the API instead of a local model |
| `RAG_EMBEDDING_MODEL` | open-webui | Indexing model used |
| `DATABASE_URL` | open-webui | PostgreSQL connection, by service name |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | postgres | Created on the first start of the container |
| `ASSISTANT_URL` | quiz-api | Internal address of Open WebUI |
| `ASSISTANT_API_KEY` | quiz-api | Open WebUI key, created in Settings → Account |
| `NO_PROXY` / `no_proxy` | quiz-api | Excludes internal services from the proxy |

Services reach each other by **service name**, not by IP address: `postgres:5432` and `open-webui:8080`.

## First use

Open `http://10.3.16.187:3000` with the VPN active, then:

1. Create the administrator account (the first account created is the admin).
2. In **Admin Panel → Settings → Interface**, disable title generation, follow-up suggestions and tags. These features consume several API requests per question.
3. In **Settings → Account**, create an API key and put it in `.env` as `ASSISTANT_API_KEY`.
4. In **Workspace → Knowledge**, create a knowledge base and upload the course materials.
5. In the chat, type `#`, select the knowledge base, then ask a question.

## Using the Quiz API

Open `http://10.3.16.187:8000/docs`, select `POST /quiz`, click **Try it out** and send:

```json
{
  "knowledge_id": "your_knowledge_base_id",
  "sujet": "histoire du cloud computing",
  "nombre": 3
}
```
The knowledge base id is visible in the URL of the knowledge base in Open WebUI, or through:

```bash
curl -s --noproxy '*' http://127.0.0.1:3000/api/v1/knowledge/ -H "Authorization: Bearer YOUR_KEY"
```

## Known limitations

- The free Gemini tier allows 20 requests per day per model. The quota is counted per model, so several models can be configured to spread the load.
- Retrieval only returns the closest passages. If the requested topic is not covered by the documents, the model still answers, with content that may drift from the course.
- The "custom model" feature of Open WebUI does not pass the knowledge base correctly in this version. Referencing it with `#` in the chat works and gives the same result.