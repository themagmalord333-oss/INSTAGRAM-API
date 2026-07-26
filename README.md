
<div align="center">

<img src="https://i.ibb.co/996jnZtr/x.jpg" width="100%" alt="Anysnap Banner" style="border-radius: 10px; box-shadow: 0px 0px 20px rgba(0,0,0,0.5);">

# 🔥 INSTAGRAM-API — ANYSNAP CORE 🔥

> *You can only see my project, not my efforts.*

<p align="center">
  <a href="https://t.me/MAGMAxRICH"><img src="https://img.shields.io/badge/Telegram-Group-blue?style=for-the-badge&logo=telegram" alt="Telegram GC"></a>
  <a href="https://t.me/MagmaProjects"><img src="https://img.shields.io/badge/Telegram-Channel-red?style=for-the-badge&logo=telegram" alt="Telegram Channel"></a>
  <img src="https://img.shields.io/badge/Python-3.12+-yellow.svg?style=for-the-badge&logo=python" alt="Python Version">
  <img src="https://img.shields.io/badge/FastAPI-High%20Performance-005571?style=for-the-badge&logo=fastapi" alt="FastAPI">
</p>

</div>

---

## ⚡ Overview
**INSTAGRAM-API (Anysnap Engine)** is a high-performance, asynchronous FastAPI backend engineered to bypass standard rate limits and fetch deep Instagram profile data seamlessly. Built with robust fallback mechanisms and strict JSON object formatting, it delivers reliable data directly to your applications.

---

## 🚀 Key Features
* **Asynchronous Architecture:** Powered by `httpx` with HTTP/2 support for lightning-fast requests.
* **Smart Fallback System:** Automatically switches between Direct and Fallback API layers if blocked.
* **Strict JSON Formatting:** Integrated with MongoDB BSON `json_util` to prevent serialization crashes and error 500s.
* **Production Ready:** Pre-configured with Redis, MongoDB, Docker, Sentry tracking, and Prometheus instrumentation.

---

## 🛠️ Quick Setup & Installation

Clone the repository and spin up the environment in seconds:

```bash
# 1. Clone the repository
git clone [https://github.com/themagmalord333-oss/INSTAGRAM-API.git](https://github.com/themagmalord333-oss/INSTAGRAM-API.git) INSTAAPI
cd INSTAAPI

# 2. Setup Virtual Environment
python3 -m venv venv
source venv/bin/activate

# 3. Install Dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Start Databases (Docker)
docker compose up -d

# 5. Run the Server
uvicorn app.main:app --host 0.0.0.0 --port 8000

```
## 📡 API Endpoint Example
**Request:**
```http
GET /api/v1/profile?username=zuck

```
**Response Output (Strict JSON):**
```json
{
  "success": true,
  "data": {
    "username": "zuck",
    "full_name": "Mark Zuckerberg",
    "biography": "",
    "profile_picture": "https://...",
    "followers": 142000000,
    "following": 119,
    "posts": 79,
    "is_verified": true,
    "is_private": false,
    "source": "Anysnap_Direct_API"
  },
  "meta": {
    "source": "Anysnap_Direct_API",
    "cached": false
  }
}

```
## 👥 Connect & Community
Stay updated with upcoming projects and high-end tools:
 * **Discussion Group:** Join Telegram GC
 * **Official Channel:** Join Magma Projects
<div align="center">
<p><b>Developed with 💻 & ⚡ by MAGMAxRICH</b></p>
</div>
