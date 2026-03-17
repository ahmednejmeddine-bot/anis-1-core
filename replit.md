# ANIS-1 – Autonomous Neural Intelligence System

## Overview
ANIS-1 is the AI operations, strategy, and automation platform for Abdeljelil Group. This is a static web frontend served by a lightweight Node.js HTTP server.

## Project Structure
- `index.html` – Main landing page
- `style.css` – Styles for the landing page
- `server.js` – Minimal Node.js HTTP server serving static files on port 5000

## Running the App
The application runs via the "Start application" workflow which executes `node server.js`. It listens on `0.0.0.0:5000`.

## Tech Stack
- **Frontend:** Plain HTML + CSS (no framework)
- **Server:** Node.js built-in `http` module (no dependencies)
- **Port:** 5000

## Deployment
Configured as a static deployment. The `publicDir` is the root directory (`.`).
