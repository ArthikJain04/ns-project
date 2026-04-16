# 🛡️ Nimbus Security — Web Vulnerability Scanner
### Network Security Course Project | AWS Integrated

A full-stack **Web Vulnerability Scanner** that detects common web security flaws and stores results on the AWS Cloud.

---

## 🔍 Features
- **SQL Injection (SQLi)** detection
- **Cross-Site Scripting (XSS)** detection
- **Security Headers** analysis (CSP, HSTS, X-Frame-Options, etc.)
- **Directory & Sensitive File Exposure** checks
- **Cloud-native**: Scan results are stored in **Amazon RDS** and uploaded to **Amazon S3**
- **Premium UI**: Built with React + Tailwind CSS + Framer Motion

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React (Vite), Tailwind CSS v4, Framer Motion, Axios |
| Backend | Python, Flask, Flask-CORS, SQLAlchemy |
| Scanner | requests, BeautifulSoup4 |
| AWS | EC2, RDS (MySQL), S3, IAM |

---

## 🚀 Local Setup

### 1. Backend
```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\Activate

# macOS/Linux
source venv/bin/activate

pip install flask flask-cors requests beautifulsoup4 flask_sqlalchemy python-dotenv boto3

# Copy and configure environment variables
cp .env.example .env
# Edit backend/.env with your AWS credentials

python app.py
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## ☁️ AWS Deployment (EC2)

See the full deployment guide for step-by-step instructions on deploying to an AWS EC2 Ubuntu server.

**Key AWS services used:**
- **EC2** — Hosts the backend Flask API and frontend React build
- **RDS MySQL** — Stores scan history
- **S3** — Stores downloadable JSON scan reports

---

## ⚠️ Disclaimer

This tool is for **educational purposes only**. Only scan websites and systems you own or have explicit permission to test. Unauthorized scanning is illegal.

---

*Made with ❤️ for Network Security Course*
