export type CurrentWeather = {
  temperatureC: number;
  humidityPct: number;
  rainfallMm: number;
  windSpeedKmh: number;
};

// Open-Meteo: free, no API key, safe to call directly from the browser.
export async function fetchCurrentWeather(
  lat: number,
  lon: number
): Promise<CurrentWeather> {
  const params = new URLSearchParams({
    latitude: String(lat),
    longitude: String(lon),
    current: "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
  });

  const response = await fetch(`https://api.open-meteo.com/v1/forecast?${params}`);
  if (!response.ok) {
    throw new Error(`Open-Meteo responded ${response.status}`);
  }

  const data = await response.json();
  const current = data.current;

  return {
    temperatureC: current.temperature_2m,
    humidityPct: current.relative_humidity_2m,
    rainfallMm: current.precipitation,
    windSpeedKmh: current.wind_speed_10m,
  };
}
