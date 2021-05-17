#include <WiFi.h>
#include <Servo_ESP32.h>

const char* ssid = "606swifi";
const char* password = "op454125";

// Variable to store the HTTP request
WiFiServer server(80);

String header;
static const int servoPin = 12;
//may be change to 90

Servo_ESP32 myServo;

void setup() {
  Serial.begin(115200);
  myServo.attach(servoPin);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected.");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  server.begin();
}


void loop() {

  WiFiClient client = server.available();

  if (client) { // If a new client connects,
    Serial.println("New Client."); // print a message out in the serial port
    String currentLine = ""; // make a String to hold incoming data from the client
    while (client.connected()) { // loop while the client's connected
      if (client.available()) { // if there's bytes to read from the client,
        char c = client.read(); // read a byte, then
        Serial.write(c); // print it out the serial monitor
        header += c;
        if (c == '\n') { // if the byte is a newline character
          // if the current line is blank, you got two newline characters in a row.
          // that's the end of the client HTTP request, so send a response:
          if (currentLine.length() == 0) {
            // HTTP headers always start with a response code (e.g. HTTP/1.1 200 OK)
            // and a content-type so the client knows what's coming, then a blank line:
            client.println("HTTP/1.1 200 OK");
            client.println("Content-type:text/html");
            client.println("Connection: close");
            client.println();
          }


          if (header.indexOf("GET /12/on") >= 0) {

            for (int posDegrees = 90; posDegrees >= 0; posDegrees--) {
              myServo.write(posDegrees);
              Serial.println(posDegrees);
              delay(20);
            }

            delay(2000);
            for (int posDegrees = 0; posDegrees <= 90; posDegrees++) {
              myServo.write(posDegrees);
              Serial.println(posDegrees);
              delay(20);
            }
          }


          // Display the HTML web page
          client.println("<!DOCTYPE html><html>");
          client.println("<head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">");
          client.println("<link rel=\"icon\" href=\"data:,\">");
          // CSS to style the on/off buttons
          // Feel free to change the background-color and font-size attributes to fit your preferences
          client.println("<style>html { font-family: Helvetica; display: inline-block; margin: 0px auto; text-align: center;}");
          client.println(".button { background-color: #4CAF50; border: none; color: white; padding: 16px 40px;");
          client.println("text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}");
          client.println(".button2 {background-color: #555555;}</style></head>");

          client.println("<p>GATE</p>");
          client.println("<p><a href=\"/12/on\"><button class=\"button\" name=\"seron\">ON</button></a></p>");

          client.println("</body></html>");
          break;
        } else if (c != '\r') {
          currentLine += c;
        }
      }
    }
    // Clear the header variable
    header = "";

    client.stop();
    Serial.println("Client disconnected.");
  }
}
