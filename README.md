# Smart Waste Management System

A smart city monitoring dashboard that tracks waste bin fill levels across multiple cities and helps optimize waste collection routes.

## Features

- Monitor smart garbage bins across multiple cities
- Real-time bin fill level monitoring
- Critical alerts for bins above 80%
- Route optimizer for waste collection planning
- Add / edit / delete smart bins
- Sensor simulation for testing IoT data
- City-based filtering and analytics

## Technologies Used

Frontend
- React
- Axios
- CSS Dashboard UI

Backend
- FastAPI
- SQLAlchemy
- SQLite

## Project Architecture

Frontend (React Dashboard)
↓
API Calls
↓
Backend (FastAPI)
↓
Database (SQLite)

## How to Run the Project

### Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8002