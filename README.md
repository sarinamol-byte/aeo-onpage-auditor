# AEO On-Page Auditor

A comprehensive on-page Answer Engine Optimization (AEO) auditor that analyzes web pages for AI search engine optimization.

## 🚀 Quick Start
```bash
# Build and run with Docker
docker-compose up --build

# Access at http://localhost:3000
```

## 📁 Project Structure
```
aeo-onpage-auditor/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── pages/
│   ├── styles/
│   ├── package.json
│   └── Dockerfile
└── docker-compose.yml
```

## ✨ Features

- Schema markup analysis (FAQ, HowTo, Article)
- Question-based heading detection
- Featured snippet optimization scoring
- E-E-A-T signals detection
- Entity extraction
- Content structure analysis
- Actionable recommendations

## 🛠️ Tech Stack

- **Backend**: Python, Flask, BeautifulSoup, TextStat
- **Frontend**: Next.js, React, TailwindCSS
- **Deployment**: Docker, Docker Compose
```

---

## 📋 **COMPLETE FILE CHECKLIST**

Make sure you have created ALL these files:
```
aeo-onpage-auditor/
├── docker-compose.yml ✓
├── README.md ✓ (optional)
├── backend/
│   ├── app.py ✓
│   ├── requirements.txt ✓
│   └── Dockerfile ✓
└── frontend/
    ├── package.json ✓
    ├── next.config.js ✓
    ├── tailwind.config.js ✓
    ├── postcss.config.js ✓
    ├── Dockerfile ✓
    ├── pages/
    │   ├── _app.js ✓
    │   ├── _document.js ✓
    │   └── index.js ✓
    └── styles/
        └── globals.css ✓