# Cloud-Computing-project
# Assistant pédagogique IA — Team 2
Assistant pédagogique basé sur un LLM, déployé avec Docker Compose
Les étudiants posent leurs questions et reçoivent une réponse construite à partir des supports de cours, avec citation de la source.

> **État :** installation et déploiement.
Schéma d'architecture, analyse NIST et services complémentaires restent à ajouter.

## Architecture actuelle

| Composant | Rôle |
| --- | --- |
| Open WebUI | Interface de chat, comptes utilisateurs, base de connaissances |
| API Google Gemini | Modèle de langage qui génère les réponses |
| Base de connaissances | Supports de cours indexés, stockés dans un volume Docker |

## Prérequis

- Docker avec Docker Compose
- VPN UPPA (pour joindre le serveur de l'école)
- Une clé d'API Gemini, créée sur `aistudio.google.com/apikey`

## Installation

```bash
mkdir -p ~/CodeCloud && cd ~/CodeCloud
```
Créer le fichier `.env` avec votre propre clé :

```
OPENAI_API_KEY=votre_cle_ici
```
Créer le fichier `docker-compose.yml` :

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

Démarrer les services :

```bash
docker compose up -d
docker compose ps
```

## Exploitation

```bash
docker compose down                     # arrêter en conservant les données
docker compose up -d --force-recreate   # appliquer les changements du fichier YAML
```

**Ne jamais utiliser `docker compose down -v`** : l'option `-v` supprime le volume, donc les comptes, les conversations et la base de connaissances.

Le premier démarrage prend quelques minutes. Suivre la progression avec :

```bash
docker compose logs -f --tail 20
```

## Configuration

| Variable | Rôle |
| --- | --- |
| `OPENAI_API_BASE_URL` | Point d'entrée de l'API Gemini, compatible avec le format OpenAI |
| `OPENAI_API_KEY` | Clé d'API, lue depuis `.env` |
| `HTTPS_PROXY` / `https_proxy` | Proxy de l'université, obligatoire pour sortir sur Internet |
| `RAG_EMBEDDING_ENGINE` | Moteur d'indexation des documents, réglé sur l'API plutôt qu'en local |
| `RAG_EMBEDDING_MODEL` | Modèle d'indexation utilisé |

Deux contraintes sont propres au serveur de l'école. Un conteneur n'hérite pas de la configuration proxy de l'hôte, les variables `HTTPS_PROXY` sont donc obligatoires. Et Open WebUI télécharge normalement un modèle d'indexation au premier démarrage, ce que le proxy bloque ; les variables `RAG_EMBEDDING_*` déportent cette étape vers l'API Gemini.

## Première utilisation

Ouvrir `http://10.3.16.187:3000` avec le VPN actif, puis :

1. Créer le compte administrateur (le premier compte créé est administrateur).
2. Dans **Admin Panel → Settings → Interface**, désactiver la génération de titre, les suggestions de suite et les tags. Ces fonctions consomment plusieurs requêtes API par question.
3. Dans **Workspace → Knowledge**, créer une base de connaissances et y déposer les supports de cours.
4. Dans le chat, taper `#`, sélectionner la base de connaissances, puis poser la question.


## À compléter
