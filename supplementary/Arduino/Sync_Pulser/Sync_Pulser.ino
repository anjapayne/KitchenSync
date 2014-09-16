//Pulses pin 13 at a pattern, "on" and "off" counting up in bianary, for syncing data collection equiptment
#define DELAY 60 //60 MS delay between pulses
#define SIGNAL_PIN 13
#define ANALOG_PIN A3

void setup() {
    Serial.begin(9600);
    pinMode(SIGNAL_PIN, OUTPUT);
        pinMode(ANALOG_PIN, OUTPUT);
}

int Q = 1;
void loop() {
  pulse(Q);
  Q += 1;
  delay(1000);
  digitalWrite(SIGNAL_PIN, HIGH);
  tone(ANALOG_PIN, 294);
  delay(1000);
  digitalWrite(SIGNAL_PIN, LOW);
  noTone(ANALOG_PIN);
}

//returns bin string with leading zeros, 16 bit unsigned
String int_to_bin_str(unsigned int n) {
 String sans_zeros = String(n,BIN);
 int zero_count = 16 - sans_zeros.length();
 String leading_zeros = "";
 for(unsigned int i=0; i < zero_count; i++) {
   leading_zeros += "0";
 }
 return leading_zeros + sans_zeros;
}

void pulse(unsigned int n) {
  String bin_string = int_to_bin_str(n);
  
  for(int i = 0; i < bin_string.length(); i++) {
    boolean pin_state = (bin_string[i] == '1');
    digitalWrite(SIGNAL_PIN, pin_state);
    toggle_tone(pin_state);
    delay(DELAY);
      
  }
  digitalWrite(SIGNAL_PIN, LOW);
  noTone(ANALOG_PIN);
}

void toggle_tone(boolean state) {
  if(state) {
    int Hz = random(200,300);
    tone(ANALOG_PIN, Hz);
  }
  else {
    noTone(ANALOG_PIN);
  }
}

  
