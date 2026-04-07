# 🚀 Production Deployment Guide

This guide will walk you through making your **Multi-Persona AI Assistant** live on the internet! 

## 1. Prerequisites
- A [GitHub](https://github.com/) account.
- A [Google Gemini API Key](https://aistudio.google.com/app/apikey) (Free).
- A [Render](https://render.com/) or [Railway](https://railway.app/) account.

---

## 2. Prepare for GitHub
1. Create a new **Private** or **Public** repository on GitHub.
2. Open your terminal in the project folder and run:
   ```bash
   git init
   git add .
   git commit -m "feat: Prepare for production deployment"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```

---

## 3. Deploy on Render (Recommended & Free)
1. Log in to [Render](https://dashboard.render.com/).
2. Click **New +** > **Web Service**.
3. Connect your GitHub repository.
4. Set the following configurations:
   - **Name**: `multipersona-ai-assistant`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.app:app`
5. **Environment Variables**:
   Click **Advanced** > **Add Environment Variable**:
   - `GEMINI_API_KEY`: `(Your Actual API Key)`
   - `PYTHON_VERSION`: `3.10.0` (or your current version)
6. Click **Create Web Service**. 

Wait 2-3 minutes, and Render will provide you with a public URL like `https://multipersona-ai-assistant.onrender.com`.

---

## 4. Environment Variables Setup
Ensure you never share your `GEMINI_API_KEY` publicly. Only set it in the deployment platform's settings or a local `.env` file (which is hidden by `.gitignore`).

---

## 5. Local Running (Production Mode)
To test the production setup locally:
1. Create a `.env` file and add `GEMINI_API_KEY=your_key_here`.
2. Run:
   ```bash
   python -m uvicorn backend.app:app --reload
   ```

---

## ✅ Deployment Checklist
- [x] API set to Google Gemini.
- [x] Memory/History integrated.
- [x] Production server (Gunicorn) configured.
- [x] Footer branding updated to "Developed by Reyansh Babu".
- [x] Precaution & Medical Disclaimer enforced.
- [x] Responsive Design for all devices.
