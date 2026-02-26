# Copilot Instructions for NeuroHarmonics Integration

## Project Overview
- Flask backend serves API endpoints and static files
- React dashboard is built and served as static files by Flask
- User login via Flask redirects to React dashboard
- All API calls from React go to Flask endpoints

## Integration Steps
1. Build React app (client) for production
2. Copy React build output to Flask's static directory
3. Update Flask routes to serve React index.html for /dashboard
4. Ensure login redirects to /dashboard (React)
5. React fetches data from Flask API endpoints

## Development Guidelines
- Use '.' as the working directory
- Do not create new folders unless required
- Keep backend and frontend code organized
- Document all integration steps in README.md

## Task Checklist
- [ ] Build React app for production
- [ ] Copy build to Flask static directory
- [ ] Update Flask to serve React dashboard
- [ ] Test login and dashboard integration
- [ ] Update documentation
