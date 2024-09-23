import sys
import os  # Import os for environment variables
import requests
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie


class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.is_celsius = True  # State tracking for temperature unit

        # Initialize UI elements
        self.city_label = QLabel("Enter City Name:", self)
        self.city_input = QLineEdit(self)
        self.get_weather_button = QPushButton("Get Weather", self)
        self.temperature_label = QLabel(self)
        self.emoji_label = QLabel(self)
        self.description_label = QLabel(self)
        self.unit_switch_button = QPushButton("Switch to °F", self)
        self.loading_label = QLabel(self)

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Weather App")
        self.setFixedSize(400, 600)  # Set a fixed window size

        # Main vertical layout
        vbox = QVBoxLayout()

        # Add widgets to the layout
        vbox.addWidget(self.city_label)
        vbox.addWidget(self.city_input)
        vbox.addWidget(self.get_weather_button)
        vbox.addWidget(self.temperature_label)
        vbox.addWidget(self.emoji_label)
        vbox.addWidget(self.description_label)
        vbox.addWidget(self.unit_switch_button)
        vbox.addWidget(self.loading_label)

        self.setLayout(vbox)

        # Alignments for other labels, except the button (fix for the issue)
        self.city_label.setAlignment(Qt.AlignCenter)
        self.city_input.setAlignment(Qt.AlignCenter)
        self.temperature_label.setAlignment(Qt.AlignCenter)
        self.emoji_label.setAlignment(Qt.AlignCenter)
        self.description_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setAlignment(Qt.AlignCenter)

        # Set object names for styling
        self.city_label.setObjectName("city_label")
        self.city_input.setObjectName("city_input")
        self.get_weather_button.setObjectName("get_weather_button")
        self.temperature_label.setObjectName("temperature_label")
        self.emoji_label.setObjectName("emoji_label")
        self.description_label.setObjectName("description_label")
        self.unit_switch_button.setObjectName("unit_switch_button")
        self.loading_label.setObjectName("loading_label")

        # Set size policy to ensure emojis fit properly
        self.emoji_label.setSizePolicy(self.sizePolicy().Preferred, self.sizePolicy().Expanding)
        self.emoji_label.setAlignment(Qt.AlignCenter)  # Center the emoji
        self.emoji_label.setStyleSheet("font-size: 128px;")  # Increase the font size for emoji display

        # StyleSheet for UI enhancements
        self.setStyleSheet(""" 
        QWidget {
            background-color: #f0f8ff;
            padding: 20px;
        }
        QLabel, QPushButton, QLineEdit {
            font-family: Calibri;
            margin: 10px;
        }
        QLabel#city_label {
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
        }
        QLineEdit#city_input {
            font-size: 20px;
            border-radius: 10px;
            padding: 5px;
            border: 2px solid #3498db;
        }
        QPushButton#get_weather_button, QPushButton#unit_switch_button {
            font-size: 18px;
            font-weight: bold;
            background-color: #3498db;
            color: white;
            border-radius: 10px;
            padding: 10px;
        }
        QPushButton#get_weather_button:disabled {
            background-color: #95a5a6;
        }
        QLabel#temperature_label {
            font-size: 48px;
            color: #e74c3c;
        }
        QLabel#emoji_label {
            font-size: 128px;
        }
        QLabel#description_label {
            font-size: 24px;
            color: #2980b9;
        }
        QLabel#loading_label {
            font-size: 18px;
            color: #2c3e50;
        }
        """)

        # Connect buttons to their respective functions
        self.get_weather_button.clicked.connect(self.get_weather)
        self.unit_switch_button.clicked.connect(self.toggle_temperature_unit)

        # Initialize loading indicator (hidden by default)
        self.loading_movie = QMovie("loading_spinner.gif")  # Ensure you have a loading_spinner.gif in your project directory
        self.loading_label.setMovie(self.loading_movie)
        self.loading_label.hide()

    def get_weather(self):
        api_key = os.getenv("WEATHER_API_KEY")  # Use the environment variable
        if not api_key:
            self.display_error("API Key not found.\nSet the WEATHER_API_KEY environment variable.")
            return

        city = self.city_input.text().strip()
        if not city:
            self.display_error("Please enter a city name.")
            return

        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"

        # Show loading indicator and disable buttons to prevent multiple clicks
        self.loading_label.show()
        self.loading_movie.start()
        self.get_weather_button.setDisabled(True)
        self.unit_switch_button.setDisabled(True)

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("cod") == 200:
                self.display_weather(data)
            else:
                message = data.get("message", "Error fetching weather data.")
                self.display_error(message.capitalize())

        except requests.exceptions.HTTPError as http_error:
            status_code = response.status_code
            if 400 <= status_code < 500:
                if status_code == 401:
                    self.display_error("Unauthorized:\nInvalid API Key.")
                elif status_code == 404:
                    self.display_error("City not found.")
                else:
                    self.display_error(f"Client Error {status_code}:\n{http_error}")
            elif 500 <= status_code < 600:
                self.display_error(f"Server Error {status_code}:\nPlease try again later.")
            else:
                self.display_error(f"HTTP error occurred:\n{http_error}")

        except requests.exceptions.ConnectionError:
            self.display_error("Connection Error:\nCheck your internet connection.")
        except requests.exceptions.Timeout:
            self.display_error("Timeout Error:\nThe request timed out.")
        except requests.exceptions.TooManyRedirects:
            self.display_error("Too many Redirects:\nCheck the URL.")
        except requests.exceptions.RequestException as req_error:
            self.display_error(f"Request Error:\n{req_error}")

        finally:
            # Hide loading indicator and enable buttons
            self.loading_movie.stop()
            self.loading_label.hide()
            self.get_weather_button.setDisabled(False)
            self.unit_switch_button.setDisabled(False)

    def display_error(self, message):
        self.temperature_label.setStyleSheet("font-size: 24px; color: #e74c3c;")
        self.temperature_label.setText(message)
        self.emoji_label.clear()
        self.description_label.clear()

    def display_weather(self, data):
        temperature_k = data["main"]["temp"]
        weather_description = data["weather"][0]["description"]
        weather_id = data["weather"][0]["id"]

        # Convert temperature based on the current unit
        if self.is_celsius:
            temperature = temperature_k - 273.15
            unit = "°C"
        else:
            temperature = (temperature_k * 9/5) - 459.67
            unit = "°F"

        self.temperature_label.setStyleSheet("font-size: 48px; color: #e74c3c;")
        self.temperature_label.setText(f"{temperature:.1f}{unit}")
        self.emoji_label.setText(self.get_weather_emoji(weather_id))
        self.description_label.setText(weather_description.capitalize())

    @staticmethod
    def get_weather_emoji(weather_id):
        if 200 <= weather_id <= 232:
            return "⛈️"
        elif 300 <= weather_id <= 321:
            return "🌦️"
        elif 500 <= weather_id <= 531:
            return "🌧️"
        elif 600 <= weather_id <= 622:
            return "❄️"
        elif 701 <= weather_id <= 781:
            return "🌫️"
        elif weather_id == 800:
            return "☀️"
        elif 801 <= weather_id <= 804:
            return "☁️"
        else:
            return "❓"

    def toggle_temperature_unit(self):
        self.is_celsius = not self.is_celsius
        unit = "°F" if self.is_celsius else "°C"
        self.unit_switch_button.setText(f"Switch to {'°C' if self.is_celsius else '°F'}")

        # If temperature is already displayed, update it without making another API call
        temp_text = self.temperature_label.text()
        if temp_text and (temp_text.endswith("°C") or temp_text.endswith("°F")):
            try:
                temp_value = float(temp_text[:-2])
                if self.is_celsius:
                    temperature = (temp_value - 32) * 5/9
                    unit_symbol = "°C"
                else:
                    temperature = (temp_value * 9/5) + 32
                    unit_symbol = "°F"
                self.temperature_label.setText(f"{temperature:.1f}{unit_symbol}")
            except ValueError:
                pass  # In case of parsing issues, do nothing

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WeatherApp()
    window.show()
    sys.exit(app.exec_())
