# 🚀 Zero-Cost Serverless Setup Guide

Your application has been successfully migrated to a "Serverless" architecture.

- **Frontend**: React (deploy to Vercel)
- **Backend/Scraper**: Python (runs on GitHub Actions)
- **Database**: Firebase Firestore (Free Tier)

all code is pushed to: `https://github.com/bunnyankitraj/ALGO_TRADE`

## Step 1: Firebase Setup

1.  Go to [Firebase Console](https://console.firebase.google.com/) and create a new project.
2.  **Enable Firestore Database**: Go to "Build" -> "Firestore Database" -> "Create Database".
3.  **Get Web Config**:
    - Go to Project Settings -> General -> "Add app" (Web </>).
    - Copy the `firebaseConfig` keys (apiKey, authDomain, etc.).
    - You will need these for the **Frontend**.
4.  **Get Service Account (for Backend)**:
    - Go to Project Settings -> Service Accounts.
    - Click "Generate new private key".
    - Download the JSON file. Content of this file is your `FIREBASE_CREDENTIALS`.

## Step 2: GitHub Actions (Backend)

1.  Go to your GitHub Repo -> **Settings** -> **Secrets and variables** -> **Actions**.
2.  Add the following Repository Secrets:
    - `FIREBASE_CREDENTIALS`: Paste the **entire content** of the JSON file you downloaded.
    - `GROQ_API_KEY`: Your Groq API Key.
    - `OPENAI_API_KEY`: Your OpenAI API Key.

## Step 3: Frontend Deployment

1.  Go to [Vercel](https://vercel.com) and "Add New Project".
2.  Import your `ALGO_TRADE` repository.
3.  **Root Directory**: Click "Edit" and select `frontend`.
4.  **Environment Variables**: Add the keys from Step 1 (Web Config):
    - `VITE_FIREBASE_API_KEY`
    - `VITE_FIREBASE_AUTH_DOMAIN`
    - `VITE_FIREBASE_PROJECT_ID`
    - etc. (See `frontend/.env.example`).
5.  Click **Deploy**.

## Testing

- **Backend**: Go to "Actions" tab in GitHub and manually run the "Daily Market Scan" workflow to populate data.
- **Frontend**: Open your Vercel URL to see the dashboard!
