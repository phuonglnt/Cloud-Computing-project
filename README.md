# Cloud-Computing-project
# AI Teaching Assistant — Team 2
LLM-based teaching assistant deployed with Docker Compose
Students ask questions and get answers built from the course materials, with the source document cited.

> **Status:** installation and deployment. 
Architecture diagram, NIST analysis and additional services to be added.

## Current architecture

| Component | Role |
| --- | --- |
| Open WebUI | Chat interface, user accounts, knowledge base |
| Google Gemini API | Language model generating the answers |
| Knowledge base | Indexed course materials, stored in a Docker volume |

## Requirements

- Docker with Docker Compose
- UPPA VPN (to reach the school server)
- A Gemini API key, created on `aistudio.google.com/apikey`

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

## Configuration

| Variable | Role |
| --- | --- |
| `OPENAI_API_BASE_URL` | Gemini API endpoint, compatible with the OpenAI format |
| `OPENAI_API_KEY` | API key, read from `.env` |
| `HTTPS_PROXY` / `https_proxy` | University proxy, required to reach the Internet |
| `RAG_EMBEDDING_ENGINE` | Document indexing engine, set to the API instead of a local model |
| `RAG_EMBEDDING_MODEL` | Indexing model used |

Two constraints are specific to the school server. A container does not inherit the proxy configuration of the host, so the `HTTPS_PROXY` variables are mandatory. And Open WebUI normally downloads an embedding model on first start, which the proxy blocks; the `RAG_EMBEDDING_*` variables send that step to the Gemini API instead.

## First use

Open `http://10.3.16.187:3000` with the VPN active, then:

1. Create the administrator account (the first account created is the admin).
2. In **Admin Panel → Settings → Interface**, disable title generation, follow-up suggestions and tags. These features consume several API requests per question.
3. In **Workspace → Knowledge**, create a knowledge base and upload the course materials.
4. In the chat, type `#`, select the knowledge base, then ask a question.


## To be added

