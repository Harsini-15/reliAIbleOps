# ReliAIbleOps
**AI Platform for Reliable Engineering Data & Intelligent Operations**

ReliAIbleOps is a cloud-ready engineering intelligence platform. It collects operational edge data, automatically cleans and validates its reliability, detects anomalies using Machine Learning (Isolation Forest & Z-Score), and visualizes predictive insights through an intuitive, premium React dashboard.

## 🚀 Features
- **Data Reliability Engine**: Scores incoming data based on Completeness, Consistency, and Uniqueness.
- **AI Anomaly Detection**: Built-in Python ML Pipeline utilizing `scikit-learn` (Isolation Forest) and `scipy` statistics.
- **Decision Intelligence**: Automatically generates severity-based alerts and actionable infrastructure recommendations.
- **Premium Visual Analytics**: React + Chart.js glassmorphism dashboard providing real-time system health metrics.

## 🛠 Tech Stack
- **Backend:** Python, Django, Django REST Framework
- **Machine Learning:** Pandas, Scikit-learn, Numpy, Scipy
- **Frontend:** React, Vite, Chart.js, Vanilla CSS
- **Database:** PostgreSQL
- **Infrastructure:** Docker, Docker Compose

## 📦 Setup Instructions (Docker)
The easiest way to run the application is via Docker Compose.

1. **Clone the repository.**
2. **Build and start the containers:**
   ```bash
   docker-compose up --build
   ```
3. **Wait for initialization:**
   The backend entrypoint will automatically wait for PostgreSQL, run migrations, and create a default admin user.
   - Admin Email: `admin@reliableops.io`
   - Admin Password: `admin123`

4. **Access the Application:**
   - **Frontend Dashboard:** [http://localhost:5173](http://localhost:5173)
   - **Backend API Root:** [http://localhost:8000](http://localhost:8000)
   - **Django Admin:** [http://localhost:8000/admin/](http://localhost:8000/admin/)

## 🧪 Running a Demo
1. Open the Frontend Dashboard.
2. Click **"Simulate IoT Stream"** in the top right header.
3. This triggers the complete data pipeline:
   - Ingests 300 engineering data points
   - Validates data and assigns a Reliability Score
   - Runs the AI Anomaly Detection pipeline
   - Generates intelligent alerts
4. Watch the dashboard instantly populate with health gauges, charts, and actionable insights.
5. Alternatively, upload the `datasets/sample_operational_data.csv` file using the **Upload CSV** button.

## 🌐 Cloud Deployment (Hackathon Ready)
This project is configured for **One-Click Zero-Cost Deployment**:

- **Backend (Django + Neon Postgres):** [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Harsini-15/reliAIbleOps)
- **Frontend (React + Vercel):** [![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/import?s=https://github.com/Harsini-15/reliAIbleOps&root-directory=frontend)

## 📁 Project Structure
- `backend/` - Django APIs, Data Reliability Engine, Alerts, and ML Pipeline integration.
- `frontend/` - React SPA with custom styling and Chart.js integration.
- `ml_models/` - Standalone data generation and AnomalyDetector classes for offline training.
- `datasets/` - Sample operational data.

---
**Built for Cloud Infrastructure Intelligence • 2026**
