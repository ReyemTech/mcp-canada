"""Constants for the MSC GeoMet weather module."""

BASE_URL = "https://api.weather.gc.ca"
API_NAME = "msc-geomet"
RATE_GROUP = "weather"
RATE_LIMIT = 20.0

# Cache TTLs (seconds)
CACHE_TTL_REALTIME = 300        # 5 min — current conditions, SWOB, AQHI, hydro realtime
CACHE_TTL_FORECAST = 1800       # 30 min — forecasts, AQHI forecasts
CACHE_TTL_ALERTS = 120          # 2 min — weather alerts
CACHE_TTL_CLIMATE = 86400       # 24 hours — climate daily/monthly/normals/trends
CACHE_TTL_STATIONS = 86400      # 24 hours — station lists
CACHE_TTL_COLLECTIONS = 3600    # 1 hour — collection browser

# Province/territory bounding boxes: (lon_min, lat_min, lon_max, lat_max)
PROVINCE_BBOX: dict[str, tuple[float, float, float, float]] = {
    "BC": (-139.06, 48.30, -114.03, 60.00),
    "AB": (-120.00, 49.00, -110.00, 60.00),
    "SK": (-110.00, 49.00, -101.36, 60.00),
    "MB": (-102.05, 49.00, -88.94, 60.00),
    "ON": (-95.16, 41.67, -74.34, 56.86),
    "QC": (-79.76, 45.00, -57.10, 62.58),
    "NB": (-69.06, 44.56, -63.77, 48.07),
    "NS": (-66.32, 43.42, -59.69, 47.03),
    "PE": (-64.43, 45.95, -61.97, 47.06),
    "NL": (-67.80, 46.61, -52.62, 60.37),
    "YT": (-141.00, 60.00, -124.00, 69.65),
    "NT": (-136.46, 60.00, -101.99, 78.77),
    "NU": (-120.00, 60.00, -61.00, 83.11),
}

# OGC Collection ID constants (verified against live MSC GeoMet API)
COLL_CITYPAGE = "citypageweather-realtime"
COLL_SWOB = "swob-realtime"
COLL_ALERTS = "weather-alerts"
COLL_CLIMATE_STATIONS = "climate-stations"
COLL_SWOB_STATIONS = "swob-stations"
COLL_CLIMATE_HOURLY = "climate-hourly"
COLL_CLIMATE_DAILY = "climate-daily"
COLL_CLIMATE_MONTHLY = "climate-monthly"
COLL_CLIMATE_NORMALS = "climate-normals"
COLL_AHCCD_TRENDS = "ahccd-trends"
COLL_LTCE_TEMP = "ltce-temperature"
COLL_LTCE_PRECIP = "ltce-precipitation"
COLL_LTCE_SNOW = "ltce-snowfall"
COLL_CMIP5 = "climate:cmip5:projected:annual:anomaly"
COLL_CMIP6 = "climate:dcs:projected:annual:absolute"
COLL_SPEI_3 = "climate:spei-3:historical"
COLL_AQHI_OBS = "aqhi-observations-realtime"
COLL_AQHI_FORECAST = "aqhi-forecasts-realtime"
COLL_AQHI_STATIONS = "aqhi-stations"
COLL_HYDRO_REALTIME = "hydrometric-realtime"
COLL_HYDRO_DAILY = "hydrometric-daily-mean"
COLL_HYDRO_STATIONS = "hydrometric-stations"
COLL_HYDRO_PEAKS = "hydrometric-annual-peaks"
COLL_MARINE = "marineweather-realtime"
COLL_HURRICANE_TRACK = "hurricanes-track-realtime"
COLL_THUNDERSTORM = "thunderstorm_outlook"
COLL_RADAR = "weather:rdpa:10km:24f"
