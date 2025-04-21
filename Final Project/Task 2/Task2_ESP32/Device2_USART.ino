#define TXD1 17
#define RXD1 16
#define USE_API_MODE true  // change to change the mode sending in

uint8_t dest_addr[8] = { 0x00, 0x13, 0xA2, 0x00, 0x41, 0xD0, 0x0C, 0xF1 }; // MAC for sink node

// function to configure and send the API mode, used packet from Zigbee
void send_api_frame(const char* payload) {
  uint8_t frame_type = 0x10; 
  uint8_t frame_id = 0x01;
  uint8_t dest16[2] = { 0xFF, 0xFE };
  uint8_t broadcast_radius = 0x00;
  uint8_t options = 0x00;

  size_t payload_len = strlen(payload);
  size_t frame_data_len = 14 + payload_len;

  uint8_t frame[100]; // large enough for a big frame

  // header information
  frame[0] = 0x7E;
  frame[1] = (frame_data_len >> 8) & 0xFF;
  frame[2] = frame_data_len & 0xFF;

  size_t i = 3;
  frame[i++] = frame_type;
  frame[i++] = frame_id;

  // address information
  for (int j = 0; j < 8; j++) frame[i++] = dest_addr[j];
  frame[i++] = dest16[0];
  frame[i++] = dest16[1];
  frame[i++] = broadcast_radius;
  frame[i++] = options;

  // writes the message to the frame
  for (int j = 0; j < payload_len; j++) frame[i++] = payload[j];

  // help with error control
  uint8_t checksum = 0;
  for (int j = 3; j < i; j++) checksum += frame[j];
  frame[i++] = 0xFF - checksum;

  // writes message
  Serial1.write(frame, i);
}

void send_transparent(const char* message) {
  // sends in transparent mode
  Serial1.println(message); 
}


void setup() {
  // sets up baud rate and serial communication
  Serial1.begin(9600, SERIAL_8N1, RXD1, TXD1); // 1 stop and start bit, 8 data, no parity, set Rx and Tx pins
  delay(1000);
}

// CHANGE MODE AT THE TOP
void loop() {
  if (USE_API_MODE) {
    send_api_frame("2025"); // case for api frame
  } else {
    send_transparent("2025"); // case for transparent mode
  }
  delay(1000); // delay for visability
}


