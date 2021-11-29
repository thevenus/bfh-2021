// ============= Includes ===============
#include <TinyGPSPlus.h>
#include <DHT.h>
#include <Arduino.h>
#include <WiFi.h>
#include <WiFiMulti.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>


// ============= Defines ================
#define DHTPIN 4
#define DHTTYPE DHT22
#define RXPin 16
#define TXPin 17
#define GPSBaud 9600

// Initializations
DHT dht(DHTPIN, DHTTYPE);
TinyGPSPlus gps;

// wifi connection delay
unsigned long lastTime = 0;
unsigned long timerDelay = 5000;

// http request server
const char* serverName = "http://revofood.pythonanywhere.com/api/hardwareDataPost/";

const char* ssid = "SSID";
const char* password = "PASS";

// gps NMEA code example stream for demonstration in case if there is no connection with satallites
const char *gpsStream =
        "$GPGSV,3,3,10,29,52,298,34,31,20,307,*74\r\n"
        "$GPGLL,4024.00632,N,04958.74309,E,204457.00,A,A*65\r\n"
        "$GPRMC,204458.00,A,4024.00616,N,04958.74308,E,0.128,,271121,,,A*79\r\n"
        "$GPVTG,,T,,M,0.128,N,0.237,K,A*2E\r\n"
        "$GPGGA,204458.00,4024.00616,N,04958.74308,E,1,06,2.26,52.9,M,-15.7,M,,*48\r\n"
        "$GPGSA,A,3,25,02,29,20,12,06,,,,,,,3.62,2.26,2.82*02\r\n"
        "$GPGSV,3,1,10,02,50,048,29,05,,,25,06,06,045,27,11,42,049,09*4E\r\n"
        "$GPGSV,3,2,10,12,62,139,26,18,12,223,,20,44,096,25,25,78,284,32*75\r\n"
        "$GPGSV,3,3,10,29,52,298,33,31,20,307,*73\r\n"
        "$GPGLL,4024.00616,N,04958.74308,E,204458.00,A,A*6D\r\n"
        "$GPRMC,204459.00,A,4024.00602,N,04958.74299,E,0.092,,271121,,,A*74\r\n"
        "$GPVTG,,T,,M,0.092,N,0.171,K,A*2F\r\n"
        "$GPGGA,204459.00,4024.00602,N,04958.74299,E,1,06,2.26,52.6,M,-15.7,M,,*4A\r\n"
        "$GPGSA,A,3,25,02,29,20,12,06,,,,,,,3.62,2.26,2.82*02\r\n"
        "$GPGSV,3,1,10,02,50,048,29,05,,,25,06,06,045,27,11,42,049,09*4E\r\n"
        "$GPGSV,3,2,10,12,62,139,26,18,12,223,,20,44,096,25,25,79,282,32*72\r\n"
        "$GPGSV,3,3,10,29,52,298,33,31,20,307,*73\r\n"
        "$GPGLL,4024.00602,N,04958.74299,E,204459.00,A,A*60\r\n"
        "$GPRMC,204500.00,A,4024.00587,N,04958.74294,E,0.108,,271121,,,A*78\r\n"
        "$GPVTG,,T,,M,0.108,N,0.200,K,A*28\r\n"
        "$GPGGA,204500.00,4024.00587,N,04958.74294,E,1,06,2.26,52.5,M,-15.7,M,,*47\r\n"
        "$GPGSA,A,3,25,02,29,20,12,06,,,,,,,3.62,2.26,2.82*02\r\n"
        "$GPGSV,3,1,10,02,50,048,29,05,,,25,06,06,045,27,11,42,049,08*4F\r\n"
        "$GPGSV,3,2,10,12,62,139,27,18,12,223,,20,44,096,25,25,79,282,32*73\r\n"
        "$GPGSV,3,3,10,29,52,298,33,31,20,307,*73\r\n"
        "$GPGLL,4024.00587,N,04958.74294,E,204500.00,A,A*6E\r\n"
        "$GPRMC,204501.00,A,4024.00569,N,04958.74293,E,0.052,,271121,,,A*70\r\n"
        "$GPVTG,,T,,M,0.052,N,0.096,K,A*2B\r\n"
        "$GPGGA,204501.00,4024.00569,N,04958.74293,E,1,06,2.26,52.2,M,-15.7,M,,*46\r\n"
        "$GPGSA,A,3,25,02,29,20,12,06,,,,,,,3.62,2.26,2.82*02\r\n"
        "$GPGSV,3,1,10,02,50,048,29,05,,,26,06,06,045,27,11,42,049,08*4C\r\n"
        "$GPGSV,3,2,10,12,62,139,27,18,12,223,,20,44,096,25,25,79,282,32*73\r\n"
        "$GPGSV,3,3,10,29,52,298,33,31,20,307,*73\r\n"
        "$GPGLL,4024.00569,N,04958.74293,E,204501.00,A,A*68\r\n"
        "$GPRMC,204502.00,A,4024.00549,N,04958.74290,E,0.081,,271121,,,A*7C\r\n";


void setup() {
        // start communication with serial monitor
        Serial.begin(9600);

        // start communication with GPS module
        // Serial2.begin(GPSBaud, SERIAL_8N1, RXPin, TXPin);

        // start communication with dht sensor
        dht.begin();
        
        WiFi.begin(ssid, password);
        Serial.println("Connecting");
        while(WiFi.status() != WL_CONNECTED) {
                delay(500);
                Serial.print(".");
        }
        Serial.println("");
        Serial.print("Connected to WiFi network with IP Address: ");
        Serial.println(WiFi.localIP());
        
        delay(2000);   
}

void loop() {
        
        // get temperature and humidity readings
        // compute heat index based on temp and humidity
        float temp = dht.readTemperature();
        float humidity = dht.readHumidity();
        float hic = dht.computeHeatIndex(temp, humidity, false);

//        float lat = 0, lng = 0, alt = 0;
//        int mon = 0, day = 0, year = 0;
//        int hour = 0, minute = 0, second = 0;
//        while (Serial2.available() > 0) {
//                if (gps.encode(Serial2.read())) {
//                        lat = gps.location.lat();
//                        lng = gps.location.lng();
//                        alt = gps.altitude.meters();
//                        day = gps.date.day();
//                        mon = gps.date.month();
//                        year = gps.date.year();   
//                        hour = gps.time.hour();
//                        minute = gps.time.minute();
//                        second = gps.time.second();
//                }
//        }
//
//        char ttime[9], date[11];
//        sprintf(ttime, "%02d:%02d:%02d UTC", hour, minute, second);
//        sprintf(date, "%02d.%02d.%02d", day, mon, year);
//
//        Serial.print(date);
//        Serial.print(" ");
//        Serial.println(ttime);
//        Serial.print(lat, 6);
//        Serial.print(",");
//        Serial.print(lng, 6);
//        Serial.print(" ");
//        Serial.print(alt);
//        Serial.println(" meters");
        
        float lat = 0, lng = 0, alt = 0;
        int mon = 0, day = 0, year = 0;
        int hour = 0, minute = 0, second = 0;

        int counter = 0;
        
        while (gpsStream[counter]) {
                if (gps.encode(gpsStream[counter])) {
                        lat = gps.location.lat();
                        lng = gps.location.lng();
                        alt = gps.altitude.meters();
                        day = gps.date.day();
                        mon = gps.date.month();
                        year = gps.date.year();   
                        hour = gps.time.hour();
                        minute = gps.time.minute();
                        second = gps.time.second();
                }
                counter++;
        }
        
        char ttime[9], date[11];
        sprintf(ttime, "%02d:%02d:%02d UTC", hour, minute, second);
        sprintf(date, "%02d.%02d.%02d", day, mon, year);
        
//        Serial.print(date);
//        Serial.print(" ");
//        Serial.println(ttime);
//        Serial.print(lat, 6);
//        Serial.print(",");
//        Serial.print(lng, 6);
//        Serial.print(" ");
//        Serial.print(alt);
//        Serial.println(" meters");
//        
//
//        // printint for testing
//        Serial.print(F("Humidity: "));
//        Serial.print(humidity);
//        Serial.print(F("%  Temperature: "));
//        Serial.print(temp);
//        Serial.print(F("°C   Heat Index:"));
//        Serial.print(hic);
//        Serial.println(F("°C "));

        if ((millis() - lastTime) > timerDelay) {
                //Check WiFi connection status
                if(WiFi.status()== WL_CONNECTED){
                        WiFiClient client;
                        HTTPClient http;
                        
                        // Your Domain name with URL path or IP address with path
                        http.begin(client, serverName);

                        // Send HTTP POST request
                        DynamicJsonDocument requestDataJSON(1024);
                        DynamicJsonDocument sent_data(512);
                        
                        String requestData;
                        String sent_data_string;       
                        
                        sent_data["temp"] = temp;
                        sent_data["humidity"] = humidity;
                        sent_data["lat"] = lat;
                        sent_data["lng"] = lng;
                        sent_data["alt"] = alt;
                        sent_data["time"] = ttime;
                        sent_data["date"] = date;

                        serializeJson(sent_data, sent_data_string);
                        
                        requestDataJSON["user_id"] = 49;
                        requestDataJSON["sent_data"] = sent_data_string;
                        requestDataJSON["email"] = "qeybulla@istechlal.com";
                        serializeJson(requestDataJSON, requestData);         
                        Serial.println(requestData);         

                        http.addHeader("Content-Type", "application/json");
                        int httpResponseCode = http.POST(requestData);
                        
                        Serial.print("HTTP Response code: ");
                        Serial.println(httpResponseCode);
                        
                        // Free resources
                        http.end();
                }
                else {
                        Serial.println("WiFi Disconnected");
                }
                lastTime = millis();
        }
        
        delay (2000);
}
