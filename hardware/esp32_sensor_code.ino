/*
 * esp32_sensor_code.ino
 * AI-AC-Health-Monitor — ESP32 DS18B20 Temperature Sensor
 *
 * Hardware:
 *   - ESP32 development board (ESP32-WROOM-32D)
 *   - DS18B20 digital temperature probe (1-Wire)
 *   - 4.7 kΩ pull-up resistor on DATA line
 *
 * Wiring:
 *   DS18B20 VCC  → ESP32 3.3V
 *   DS18B20 GND  → ESP32 GND
 *   DS18B20 DATA → ESP32 GPIO 4 (with 4.7kΩ pull-up to 3.3V)
 *
 * Libraries required (install via Arduino Library Manager):
 *   - OneWire by Paul Stoffregen
 *   - DallasTemperature by Miles Burton
 *
 * Serial output format (115200 baud):
 *   TEMP:<temperature_celsius>
 *
 * This format is parsed by the Python serial reader in future versions.
 */

#include <OneWire.h>
#include <DallasTemperature.h>

// GPIO pin connected to DS18B20 DATA line
#define ONE_WIRE_BUS 4

// Sampling interval (milliseconds)
#define SAMPLE_INTERVAL_MS 1000

// Setup OneWire and DallasTemperature
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// Timing
unsigned long lastSampleTime = 0;

void setup() {
  Serial.begin(115200);
  sensors.begin();

  // Print startup info
  Serial.println("=== AI-AC-Health-Monitor ESP32 Node ===");
  Serial.print("Sensor count: ");
  Serial.println(sensors.getDeviceCount());

  if (sensors.getDeviceCount() == 0) {
    Serial.println("ERROR: No DS18B20 sensor detected. Check wiring.");
  } else {
    Serial.println("DS18B20 ready. Starting telemetry...");
    sensors.setResolution(12);  // 12-bit resolution (0.0625°C)
  }
}

void loop() {
  unsigned long now = millis();

  if (now - lastSampleTime >= SAMPLE_INTERVAL_MS) {
    lastSampleTime = now;

    sensors.requestTemperatures();
    float tempC = sensors.getTempCByIndex(0);

    if (tempC == DEVICE_DISCONNECTED_C) {
      Serial.println("ERROR: Sensor disconnected");
    } else {
      // Output in machine-readable format for Python serial reader
      Serial.print("TEMP:");
      Serial.println(tempC, 4);  // 4 decimal places (DS18B20 resolution)
    }
  }
}

