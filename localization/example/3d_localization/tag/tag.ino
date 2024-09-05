#include <DW1000Ng.hpp>
#include <DW1000NgUtils.hpp>
#include <DW1000NgRanging.hpp>
#include <DW1000NgRTLS.hpp>

const uint8_t PIN_RST = 15; // reset pin
const uint8_t PIN_IRQ = 17; // irq pin
const uint8_t PIN_SS = 4; // spi select pin
const uint8_t PIN_SCK = 18;
const uint8_t PIN_MOSI = 23;
const uint8_t PIN_MISO = 19;

byte tag_shortAddress[] = {0x05, 0x02};
uint16_t next_anchor = 2;
const char EUI[] = "AA:BB:CC:DD:EE:FF:00:03";

double range_A = 0;
double range_B = 0;
double range_C = 0;



boolean received_A = false;
boolean received_B = false;
boolean received_C = false;

device_configuration_t DEFAULT_CONFIG = {
    false,
    true,
    true,
    true,
    false,
    SFDMode::STANDARD_SFD,
    Channel::CHANNEL_5,
    DataRate::RATE_850KBPS,
    PulseFrequency::FREQ_16MHZ,
    PreambleLength::LEN_256,
    PreambleCode::CODE_3
};

frame_filtering_configuration_t ANCHOR_FRAME_FILTER_CONFIG = {
    false,
    false,
    true,
    false,
    false,
    false,
    false,
    true /* This allows blink frames */
};

void setup() {
    // DEBUG monitoring
    Serial.begin(115200);
    Serial.println(F("### DW1000Ng-arduino-ranging-anchorMain ###"));
    // initialize the driver
    #if defined(ESP8266)
    DW1000Ng::initializeNoInterrupt(PIN_SS);
    #else
    DW1000Ng::initializeNoInterrupt(PIN_SS, PIN_RST);
    #endif
    Serial.println(F("DW1000Ng initialized ..."));
    // general configuration
    DW1000Ng::applyConfiguration(DEFAULT_CONFIG);
    DW1000Ng::enableFrameFiltering(ANCHOR_FRAME_FILTER_CONFIG);
    
    DW1000Ng::setEUI(EUI);

    DW1000Ng::setPreambleDetectionTimeout(64);
    DW1000Ng::setSfdDetectionTimeout(273);
    DW1000Ng::setReceiveFrameWaitTimeoutPeriod(5000);

    DW1000Ng::setNetworkId(RTLS_APP_ID);
    DW1000Ng::setDeviceAddress(1);
	
    DW1000Ng::setAntennaDelay(16436);
    
    Serial.println(F("Committed configuration ..."));
    // DEBUG chip info and registers pretty printed
    char msg[128];
    DW1000Ng::getPrintableDeviceIdentifier(msg);
    Serial.print("Device ID: "); Serial.println(msg);
    DW1000Ng::getPrintableExtendedUniqueIdentifier(msg);
    Serial.print("Unique ID: "); Serial.println(msg);
    DW1000Ng::getPrintableNetworkIdAndShortAddress(msg);
    Serial.print("Network ID & Device Address: "); Serial.println(msg);
    DW1000Ng::getPrintableDeviceMode(msg);
    Serial.print("Device mode: "); Serial.println(msg);    
}

void loop() {
  // put your main code here, to run repeatedly:
  if(DW1000NgRTLS::receiveFrame()){
        size_t recv_len = DW1000Ng::getReceivedDataLength();
        byte recv_data[recv_len];
        DW1000Ng::getReceivedData(recv_data, recv_len);

        Serial.print("Received data in HEX: ");

        for (size_t i = 0; i < recv_len; i++) {
            if (recv_data[i] < 0x10) Serial.print("0"); // 한 자리 숫자의 경우 앞에 0 추가
            Serial.print(recv_data[i], HEX);
            Serial.print(" ");
        }
        Serial.println();
        if(recv_data[0] == BLINK){
          if (recv_data[2] == 0){
            received_A = true;
            
            DW1000NgRTLS::transmitRangingInitiation(&recv_data[2], tag_shortAddress);
            DW1000NgRTLS::waitForTransmission();

            RangeAcceptResult result = DW1000NgRTLS::anchorRangeAccept(NextActivity::RANGING_CONFIRM, next_anchor);
            if(!result.success) return;
            range_A=result.range;
          }else if (recv_data[2] == 1){
            received_B = true;
            
            DW1000NgRTLS::transmitRangingInitiation(&recv_data[2], tag_shortAddress);
            DW1000NgRTLS::waitForTransmission();

            RangeAcceptResult result = DW1000NgRTLS::anchorRangeAccept(NextActivity::RANGING_CONFIRM, next_anchor);
            if(!result.success) return;
            range_B=result.range;
          }else if (recv_data[2] == 2){
            received_C = true;
            
            DW1000NgRTLS::transmitRangingInitiation(&recv_data[2], tag_shortAddress);
            DW1000NgRTLS::waitForTransmission();

            RangeAcceptResult result = DW1000NgRTLS::anchorRangeAccept(NextActivity::RANGING_CONFIRM, next_anchor);
            if(!result.success) return;
            range_C =result.range;
          }
        }

        if(received_A && received_B && received_C ){
          received_A = false;
          received_B = false;
          received_B = false;
          
          Serial.print("Range A: "); Serial.println(range_A);
          Serial.print("Range B: "); Serial.println(range_B);
          Serial.print("Range C: "); Serial.println(range_C);
        }
}}
