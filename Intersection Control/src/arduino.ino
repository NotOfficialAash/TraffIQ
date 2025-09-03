/*
================================================================================
Project: Smart Traffic and Accident Monitoring System
File: traffic_lights.ino
Author(s):
    - Aashrith Srinivasa.
License: See LICENSE file in the repository for full terms.
Description:
    Arduino sketch for controlling traffic signal LEDs. Accepts commands 
    over serial in the format "<SIGNAL>_<COLOR>_<STATUS>", where:
        - SIGNAL: A, B, or C (identifies the signal unit)
        - COLOR : R, Y, or G (Red, Yellow, Green)
        - STATUS: ON or OFF
    Based on the received command, the corresponding LED pin is set HIGH or LOW.
    A confirmation message with the affected pin and status is sent back 
    over the serial connection.
================================================================================
*/



// Define LED PINS as a reference. WILL NOT BE USED IN THE PROGRAM
/*
  const int A_R_LED_PIN = 2;
  const int A_Y_LED_PIN = 3;
  const int A_G_LED_PIN = 4;

  const int B_R_LED_PIN = 6;
  const int B_Y_LED_PIN = 7;
  const int B_G_LED_PIN = 8;

  const int C_R_LED_PIN = 10;
  const int C_Y_LED_PIN = 11;
  const int C_G_LED_PIN = 12;
*/


// A 2D array has been defined to manage the pin numbers. The ROWS represent different SIGNAL UNITS. The COLUMNS represent RED, YELLOW and GREEN respectively.
const int LED_PINS[3][3] = {
  {2,  3,  4},  // Signal A ; Unit Number = 0
  {6,  7,  8},  // Signal B ; Unit Number = 1
  {10, 11, 12}  // Signal C ; Unit Number = 2
};

void setup() {
  Serial.begin(9600);
  
  // A for loop to set all the required pins to OUTPUT mode
  for (int i = 0; i < 3; i++) {
    for (int j = 0; j < 3; j++) {
      pinMode(LED_PINS[i][j], OUTPUT);
    }
  }
}


void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n'); // Read incoming string until newline
    command.trim(); // Remove any leading/trailing whitespace

    // Get the required characters to identify the signal unit and color from the command
    char signal_char = command.charAt(0);
    char color_char = command.charAt(2);

    int signal_ident = signal_char - 'A';  // Sets the Signal Unit Number
    int color_ident;
    bool status_ident;

    // Sets the Color Number
    switch (color_char) {
      case 'R': color_ident = 0; break;
      case 'Y': color_ident = 1; break;
      case 'G': color_ident = 2; break;
      default: Serial.println("Invalid Color. USE 'R', 'Y' or 'G' to assign color"); return;
    }

    // Sets the ON / OFF status
    if (command.endsWith("ON")) {
      status_ident = HIGH;
    }
    else {
      status_ident = LOW;
    }

    String confirm_msg = "PIN " + String(LED_PINS[signal_ident][color_ident]) + " set to " + String(status_ident);

    digitalWrite(LED_PINS[signal_ident][color_ident], status_ident);
    Serial.println(confirm_msg);    
  }
}