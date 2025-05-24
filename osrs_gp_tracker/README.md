# OSRS GP/Hour Tracker

A locally hosted web application for tracking Old School RuneScape (OSRS) GP/hour rates across different activities. Built with Flask (backend) and React (frontend), featuring real-time Grand Exchange price integration and Firebase user configuration storage.

## Features

- **Real-time GP/hour calculations** for multiple OSRS activities:
  - 🌿 Herb Farming (Torstol, etc.)
  - 🏠 Birdhouse Runs
  - 🔮 Guardians of the Rift (GOTR)
  - ⚔️ Slayer tasks
- **Live Grand Exchange prices** from OSRS Wiki API
- **User configuration management** with Firebase Firestore
- **Interactive charts** for data visualization
- **Responsive design** with OSRS-themed UI
- **Anonymous authentication** for user sessions

## Project Structure

```
osrs_gp_tracker/
├── backend/                 # Flask API server
│   ├── app.py              # Main Flask application
│   ├── requirements.txt    # Python dependencies
│   └── utils/
│       ├── ge_api.py       # Grand Exchange API integration
│       └── calculations.py # GP/hour calculation logic
├── frontend/               # React web application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API and Firebase services
│   │   ├── context/        # React Context providers
│   │   └── App.jsx         # Main application component
│   ├── package.json        # Node.js dependencies
│   └── vite.config.js      # Vite configuration
└── environment-template.txt # Environment variables template
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 16+
- Firebase project (optional, for user data persistence)

### 1. Clone and Setup

```bash
cd osrs_gp_tracker
```

### 2. Backend Setup

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Copy environment template and configure
cp ../environment-template.txt ../.env
# Edit .env with your Firebase credentials (optional)

# Run the Flask server
python app.py
```

The backend will start on `http://localhost:5000`

### 3. Frontend Setup

```bash
cd frontend

# Install Node.js dependencies
npm install

# Start the development server
npm run dev
```

The frontend will start on `http://localhost:3000`

### 4. Firebase Configuration (Optional)

If you want to persist user configurations:

1. Create a Firebase project at https://console.firebase.google.com
2. Enable Firestore Database
3. Generate a service account key
4. Update the `.env` file with your Firebase credentials
5. For frontend config, add your Firebase web app config to `.env`

## API Endpoints

### Backend (Flask)

- `GET /api/health` - Health check and Firebase status
- `GET /api/ge_price/<item_id>` - Get Grand Exchange price for item
- `POST /api/calculate_gp_hr` - Calculate GP/hour for activity
- `GET /api/user_config/<user_id>` - Get user configuration
- `POST /api/user_config/<user_id>` - Save user configuration
- `GET /api/default_config` - Get default configuration

### Example API Usage

```javascript
// Calculate farming GP/hour
const response = await fetch('http://localhost:5000/api/calculate_gp_hr', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    activity_type: 'farming',
    params: {
      num_patches: 9,
      avg_yield_per_patch: 8,
      growth_time_minutes: 80
    },
    user_id: 'user123'
  })
});
```

## Configuration

### Activity Parameters

Each activity type supports different configuration parameters:

#### Farming
- `num_patches`: Number of herb patches (1-15)
- `avg_yield_per_patch`: Average herbs per patch (1-20)
- `growth_time_minutes`: Growth time in minutes (1-300)
- `seed_id`, `herb_id`, `compost_id`: Item IDs (auto-configured)

#### Birdhouse
- `avg_nests_per_run`: Average bird nests per run (1-50)
- `avg_value_per_nest`: Average GP value per nest (100-50000)
- `run_time_minutes`: Active time per run (1-30)
- `cycle_time_minutes`: Total cycle time (30-120)

#### GOTR
- `games_per_hour`: Games completed per hour (1-10)
- `essence_per_game`: Pure essence used per game (50-500)
- `avg_rune_value_per_game`: Average rune value per game (1000-100000)
- `avg_pearl_value_per_game`: Average pearl value per game (1000-50000)

#### Slayer
- `monster_name`: Monster being killed
- `kills_per_hour`: Kills per hour (1-1000)
- `avg_loot_value_per_kill`: Average loot value per kill (100-1000000)
- `avg_supply_cost_per_hour`: Supply costs per hour (0-1000000)

## Development

### Adding New Activities

1. Add calculation function to `backend/utils/calculations.py`
2. Update `CALCULATION_FUNCTIONS` dictionary
3. Add default config to `DEFAULT_USER_CONFIG` in `app.py`
4. Add UI components in `frontend/src/components/ActivityCard.jsx`
5. Update navigation in `frontend/src/components/Navbar.jsx`

### Technology Stack

**Backend:**
- Flask - Web framework
- Requests - HTTP client for OSRS Wiki API
- Firebase Admin SDK - Firestore integration
- CacheTools - Price caching

**Frontend:**
- React 18 - UI framework
- Vite - Build tool and dev server
- Tailwind CSS - Styling
- Chart.js - Data visualization
- Firebase SDK - Authentication and Firestore
- Axios - HTTP client

## Troubleshooting

### Common Issues

1. **Backend not starting**: Check Python dependencies and port 5000 availability
2. **Frontend API errors**: Ensure backend is running on port 5000
3. **Firebase errors**: Verify credentials in `.env` file
4. **Price fetching fails**: Check internet connection and OSRS Wiki API status

### Logs

- Backend logs appear in the terminal running `python app.py`
- Frontend logs appear in browser developer console
- Check Network tab for API request/response details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational and personal use. OSRS is a trademark of Jagex Ltd.

## Acknowledgments

- OSRS Wiki for providing the Grand Exchange API
- Jagex for Old School RuneScape
- React and Flask communities for excellent documentation 