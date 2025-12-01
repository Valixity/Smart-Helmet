const int helmetIRPin = 3;        
const int sleepIRPin  = A1;       
const int alcoholPin  = A0;       
const int alcoholThreshold = 210; 

const int buzzerPin = 8;          
const int motorPin  = 5;          // Motor control pin (D5 chosen)

unsigned long eyesClosedStart = 0;
bool eyesWereClosed = false;
bool sleeping = false;

void setup() {
  Serial.begin(115200);
  pinMode(helmetIRPin, INPUT_PULLUP);
  pinMode(sleepIRPin, INPUT);
  pinMode(buzzerPin, OUTPUT);
  pinMode(motorPin, OUTPUT);
  digitalWrite(buzzerPin, LOW);
  digitalWrite(motorPin, LOW);
  Serial.println("Smart Helmet Streaming Status...");
}

void loop() {
  bool helmetWorn = (digitalRead(helmetIRPin) == LOW);
  bool eyesClosed = (digitalRead(sleepIRPin) == LOW);
  int alcoholReading = analogRead(alcoholPin);
  bool alcoholDetected = (alcoholReading > alcoholThreshold);

  // Eyes closed logic
  if (eyesClosed) {
    if (!eyesWereClosed) {
      eyesClosedStart = millis();
      eyesWereClosed = true;
    } else if (millis() - eyesClosedStart >= 5000) {
      sleeping = true;
    }
  } else {
    eyesWereClosed = false;
    sleeping = false;
  }

  // Engine ON only if helmet worn, not sleeping, no alcohol
  bool engineOn = (helmetWorn && !sleeping && !alcoholDetected);

  // Buzzer logic
  if (sleeping || alcoholDetected) {
    digitalWrite(buzzerPin, HIGH);
  } else {
    digitalWrite(buzzerPin, LOW);
  }

  // Motor logic
  if (engineOn) {
    digitalWrite(motorPin, HIGH); // run motor
  } else {
    digitalWrite(motorPin, LOW);  // stop motor
  }

  // Status print
  Serial.println("===========================");
  Serial.print("Helmet: ");   Serial.println(helmetWorn ? "Worn" : "Not Worn");
  Serial.print("Eyes: ");     Serial.println(eyesClosed ? "Closed" : "Open");
  Serial.print("Sleeping: "); Serial.println(sleeping ? "YES (5s closed)" : "NO");
  Serial.print("Alcohol: ");  Serial.println(alcoholDetected ? "Detected" : "Not Detected");
  Serial.print("Alcohol Value: "); Serial.println(alcoholReading);
  Serial.print("Engine: ");   Serial.println(engineOn ? "ON" : "OFF");
  Serial.print("Motor: ");    Serial.println(digitalRead(motorPin) ? "RUNNING" : "STOPPED");
  Serial.print("Buzzer: ");   Serial.println(digitalRead(buzzerPin) ? "ON" : "OFF");
  Serial.println("===========================");

  delay(100);
}
