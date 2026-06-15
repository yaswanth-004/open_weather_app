# 🌦️ OpenWeather App

A full-stack weather web application built with **Flask** that lets registered users search for real-time weather conditions and 5-day forecasts for any city worldwide. The app integrates the **OpenWeatherMap API** for weather data and **Nominatim (OpenStreetMap)** for geocoding, with a built-in user authentication system, search history tracking, rate limiting, and an admin dashboard.

---

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
  - [Running the App](#running-the-app)
- [Application Pages & Routes](#application-pages--routes)
- [Database Models](#database-models)
- [Rate Limiting](#rate-limiting)
- [Weather Analysis Logic](#weather-analysis-logic)
- [Role-Based Access](#role-based-access)
- [Contributing](#contributing)
- [License](#license)

---

## ✨ Features

- **User Authentication** — Register, login, and logout with hashed passwords (Flask-Bcrypt)
- **Real-Time Weather** — Fetch current weather data including temperature, humidity, wind speed, pressure, visibility, sunrise/sunset, and cloud cover
- **5-Day Forecast** — Grouped daily forecast with midday readings, precipitation probability, and weather icons
- **Smart Weather Advice** — Context-aware tips generated from live weather data (e.g., umbrella reminders, heat warnings)
- **Geocoding** — City + country + optional zip code resolved to lat/lon via Nominatim
- **Search History** — Last 20 searches stored per user, viewable on the profile page
- **Rate Limiting** — Each user gets 20 free API calls per day; excess requests are blocked
- **User Profile** — Update username, email, phone, or password; delete account
- **Role-Based Access** — `user` and `admin` roles with protected admin routes
- **API Documentation Page** — Built-in docs page for the app's API endpoints
- **Blog Section** — Home feed with posts (admin-creatable)

---

## 🛠️ Tech Stack

| Layer       | Technology                                      |
|-------------|-------------------------------------------------|
| Backend     | Python 3, Flask 3.0                             |
| ORM         | Flask-SQLAlchemy                                |
| Auth        | Flask-Bcrypt, Flask sessions                    |
| Weather API | OpenWeatherMap (current weather + forecast)     |
| Geocoding   | Nominatim (OpenStreetMap)                       |
| Frontend    | Jinja2 templates, HTML/CSS                      |
| Database    | SQLite (dev) / any SQLAlchemy-compatible DB     |
| HTTP Client | Requests                                        |

---

## 📁 Project Structure

```
open_weather_app/
│
├── run.py                    # Entry point — creates and runs the Flask app
├── config.py                 # App configuration (DB URI, secret key, session settings)
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (not committed)
│
└── app/
    ├── __init__.py           # Application factory (create_app)
    │
    ├── database/
    │   └── db.py             # SQLAlchemy models: User, Post, WeatherSearch, RateLimit
    │
    ├── auth/
    │   ├── __init__.py
    │   └── route.py          # /register, /login, /logout
    │
    ├── weather/
    │   ├── __init__.py
    │   ├── route.py          # /weather/, /weather/today, /weather/forecast, /weather/rate-limit
    │   └── service.py        # Geocoding, weather fetching, forecast parsing, weather analysis
    │
    ├── profile/
    │   └── route.py          # /profile/, /profile/update, /profile/delete
    │
    ├── Blog/
    │   ├── __init__.py
    │   └── route.py          # /home, /admin
    │
    ├── api_docs/
    │   ├── __init__.py
    │   └── route.py          # /api_docs/
    │
    ├── util/
    │   └── helper.py         # Decorators: login_required, admin_required, rate_limit_required
    │
    ├── templates/
    │   ├── base.html
    │   ├── home.html
    │   ├── weather.html
    │   ├── login.html
    │   ├── register.html
    │   ├── profile.html
    │   ├── api_docs.html
    │   └── rate_limit.html
    │
    └── static/
        └── style.css
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- pip
- An [OpenWeatherMap API key](https://openweathermap.org/api) (free tier works)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yaswanth-004/open_weather_app.git
cd open_weather_app

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the root directory:

```env
# OpenWeatherMap API key
openweatherapi=your_openweathermap_api_key_here

# Flask secret key (use a long random string)
SECRET_KEY=your_secret_key_here

# Database URL (SQLite for development)
DATABASE_URL=sqlite:///weather.db
```

> **Note:** Never commit your `.env` file. It's included in `.gitignore`.

### Running the App

```bash
python run.py
```

The app will be available at `http://127.0.0.1:5000`. On first run, all database tables are automatically created.

---

## 🗺️ Application Pages & Routes

| Route                   | Method      | Description                                      | Auth Required |
|-------------------------|-------------|--------------------------------------------------|---------------|
| `/`                     | GET         | Redirects to login                               | No            |
| `/register`             | GET, POST   | Create a new account                             | No            |
| `/login`                | GET, POST   | Login with email & password                      | No            |
| `/logout`               | GET         | Clear session and logout                         | Yes           |
| `/home`                 | GET         | Blog home / dashboard                            | Yes           |
| `/weather/`             | GET, POST   | Weather search form                              | Yes           |
| `/weather/today`        | POST        | Fetch and display current weather                | Yes           |
| `/weather/forecast`     | POST        | Fetch and display 5-day forecast                 | Yes           |
| `/weather/rate-limit`   | GET         | Rate limit exceeded page                         | Yes           |
| `/profile/`             | GET         | View profile and search history                  | Yes           |
| `/profile/update`       | POST        | Update profile details or password               | Yes           |
| `/profile/delete`       | POST        | Permanently delete account                       | Yes           |
| `/api_docs/`            | GET         | API documentation page                           | No            |
| `/admin`                | GET         | Admin dashboard                                  | Admin only    |

---

## 🗄️ Database Models

### `User`
Stores registered users.

| Field        | Type     | Description                        |
|--------------|----------|------------------------------------|
| `ID`         | Integer  | Primary key                        |
| `username`   | String   | Unique username                    |
| `email`      | String   | Unique email address               |
| `phone`      | String   | Phone number                       |
| `password`   | String   | Bcrypt-hashed password             |
| `role`       | String   | `user` or `admin`                  |
| `created_at` | DateTime | Account creation timestamp         |

### `WeatherSearch`
Logs every weather query made by a user.

| Field          | Type     | Description                            |
|----------------|----------|----------------------------------------|
| `city`         | String   | Searched city name                     |
| `country`      | String   | Country code/name                      |
| `zip_code`     | String   | Optional zip code                      |
| `latitude`     | Float    | Resolved coordinates                   |
| `longitude`    | Float    | Resolved coordinates                   |
| `weather_json` | Text     | Full JSON for today's weather          |
| `forecast_json`| Text     | Full JSON for 5-day forecast           |
| `search_type`  | String   | `'today'` or `'forecast'`              |
| `searched_at`  | DateTime | Timestamp of the search                |

### `RateLimit`
Tracks API call counts per user per day.

| Field        | Type    | Description                     |
|--------------|---------|---------------------------------|
| `user_id`    | Integer | FK to User                      |
| `date`       | Date    | The calendar date               |
| `call_count` | Integer | Number of API calls made today  |

### `Post`
Blog posts (admin-created).

| Field       | Type     | Description            |
|-------------|----------|------------------------|
| `title`     | String   | Post title             |
| `content`   | Text     | Post body              |
| `created_at`| DateTime | Creation timestamp     |
| `user_id`   | Integer  | FK to author (User)    |

---

## ⏱️ Rate Limiting

Each user is allowed **20 API calls per day**. This resets at midnight.

- Every `/weather/today` or `/weather/forecast` request counts as one call.
- If the limit is exceeded, the user is redirected to `/weather/rate-limit`.
- The profile page and weather search form display remaining calls.
- Admins are subject to the same limit unless custom logic is added.

The `get_rate_limit_info()` helper also tracks system-wide capacity stress (total users × 20 calls/day).

---

## 🌡️ Weather Analysis Logic

After fetching current weather, the app runs `analyze_weather()` which generates human-readable advice based on conditions:

| Condition           | Advice Example                                  |
|---------------------|-------------------------------------------------|
| `temp < 5°C`        | 🥶 Very cold — wear a heavy coat and gloves     |
| `temp 5–15°C`       | 🧥 Cool weather — a jacket is recommended       |
| `temp 15–25°C`      | 😊 Pleasant temperature — comfortable outdoors  |
| `temp 25–35°C`      | ☀️ Warm day — stay hydrated                     |
| `temp > 35°C`       | 🔥 Very hot — avoid prolonged sun exposure      |
| `humidity > 80%`    | 💧 High humidity — it will feel hotter          |
| `humidity < 30%`    | 🌵 Low humidity — carry a water bottle          |
| `wind > 10 m/s`     | 💨 Strong winds — secure loose items            |
| Rain in description | ☔ Rain expected — carry an umbrella             |
| Snow                | ❄️ Snow — dress warmly and drive carefully      |
| Storm/thunder       | ⛈️ Storm warning — stay indoors if possible     |

---

## 🔐 Role-Based Access

| Role    | Permissions                                                    |
|---------|----------------------------------------------------------------|
| `user`  | Register, login, search weather, view profile, read blog       |
| `admin` | All user permissions + access to `/admin` dashboard           |

When registering as an admin, a secret code (`MYADMIN123` by default) must be entered. This should be moved to the `.env` file for production.

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push to your branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---

<p align="center">Built with ❤️ using Flask & OpenWeatherMap API</p>
