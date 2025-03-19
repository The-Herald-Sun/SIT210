void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
}

void dot() {
  digitalWrite(LED_BUILTIN, HIGH);  
  delay(300);
  digitalWrite(LED_BUILTIN, LOW);
  delay(300);
}

void dash() {
  digitalWrite(LED_BUILTIN, HIGH);  
  delay(600);
  digitalWrite(LED_BUILTIN, LOW);
  delay(300);
}

void newChar() {
  delay(600);
}

void loop() {
  // S
  dot();
  dot();
  dot();

  newChar();

  // A
  dot();
  dash();

  newChar();

  // M
  dash();
  dash();

  newChar();
  newChar();
}