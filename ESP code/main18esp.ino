#include "I2Cdev.h"
#include "MPU6050_6Axis_MotionApps20.h"
#include "Wire.h"
#include "HardwareSerial.h"
#include <WiFi.h>
#include <WebServer.h>

#define lidarTx 17
#define lidarRx 16
#define surveyButton 12
#define connectButton 14
#define lidarPin 4

bool dataFlag = false;


const char* ssid = "Esp32_module";
const char* password = "12345678";

WebServer server(80);

HardwareSerial TF_Luna_Serial(1);

MPU6050 mpu;
uint8_t fifoBuffer[45]; 

struct Angles{
 float yaw;
 float pitch;
 float roll;
} ;
struct Point{
   float coords[3];
};

struct Vector_2d{
   float coords[2];
};

Angles ang;
Vector_2d vec;

void setup() {
  Serial.begin(9600);
  pinMode(surveyButton,INPUT_PULLUP);
  WiFi.mode(WIFI_AP);
  WiFi.softAP(ssid, password);
  Serial.println("SoftAP configured");
  Serial.print("IP address: ");
  Serial.println(WiFi.softAPIP());

  server.on("/get_vector", []() {
    //Serial.print("get contact");
    if (dataFlag){
      String response = "";
      for(int i = 0; i<2; i++){
        response += String(vec.coords[i]);//
        response += ",";
      }
      response += "";
      server.send(200, "text/plain", response);
      dataFlag = false;
    }
    else{
      String response = "No data yet";
      server.send(204, "text/plain", response);//проверить код ответа
    }

  });
  server.on("/get_numbers", []() {
    String response = "[";
    for (int i = 0; i < 10; i++) {
      response += (String)random(10) + ", ";
    }
    response.remove(response.length() - 2);  // Remove the last comma and space
    response += "]";
    server.send(200, "text/plain", response);
  });

  server.begin();
  Serial.println("HTTP server started");
  // Инициализация MPU
  Wire.begin();
  //Wire.setClock(1000000UL);   // разгоняем шину на максимум
  // инициализация DMP
  mpu.initialize();
  mpu.dmpInitialize();
  mpu.setDMPEnabled(true);
  Serial.println("MPU");
  TF_Luna_Serial.begin(115200, SERIAL_8N1, 17, 16);  // Инициализация последовательной связи с TF-Luna

}

void loop() {
      if (digitalRead(surveyButton)){//
        int dist=get_distance();
        //Serial.println(dist);
        //Serial.println(dist);
        //int dist=10;
        //Serial.print(dist);
        //Serial.print(',');
        ang = get_angles();
        vec = calc_point_vec(ang,dist);
        dataFlag = true;
        //Serial.println(vec.coords[1]);
        //Serial.print(vec.coords[0]);
        //Serial.print(",");
        //Serial.println(vec.coords[1]);


        Serial.print(ang.roll); // вокруг оси Z
        Serial.print(',');
        Serial.print(ang.pitch); // вокруг оси Y
        Serial.print(',');
        Serial.print(ang.yaw); // вокруг оси X
        Serial.print(',');
        Serial.println(dist);
      
      }
      else{
        dataFlag = false;
      }
      server.handleClient();
      //delay(200);
}


struct Vector_2d calc_point_vec(struct Angles ang, int dist) {
    struct Vector_2d result_vec;
    //Serial.print("pitch: ");
    //Serial.println(ang.pitch);
    //Serial.print("roll: ");
    //Serial.println(ang.roll);
    //Serial.println(2*2);
    //float corrected_dist = sqrt(pow(dist,2)-pow(sqrt(pow(dist*sin(ang.pitch),2)-pow(cos(ang.roll)*sin(ang.pitch)*dist,2)),2));//dist*cos(ang.pitch)*cos(ang.roll);
//    Serial.println(corrected_dist);
    float x = dist * sin(ang.yaw);
    float y = dist * cos(ang.yaw);
    //delay(100);
    result_vec.coords[0] = x;
    result_vec.coords[1] = y;

    return result_vec;
}

/*struct point calc_point_vec(struct angles ang, int dist) {
    struct point result_vec;
    float x = dist * cos(ang.pitch) * sin(ang.yaw);
    float y = dist * sin(ang.pitch);
    float z = dist *cos(ang.pitch) * cos(ang.yaw);

    result_vec.coords[0] = x;
    result_vec.coords[1] = y;
    result_vec.coords[2] = z;

    return result_vec;
}*/

struct Angles get_angles(){//получаем углы ориентации с mpu
  static uint32_t tmr;
  if (millis() - tmr >= 11) {  // таймер на 11 мс (на всякий случай)
 if (mpu.dmpGetCurrentFIFOPacket(fifoBuffer)) {
      // переменные для расчёта (ypr можно вынести в глобал)
      Quaternion q;
      VectorFloat gravity;
      float ypr[3];
      // расчёты
      mpu.dmpGetQuaternion(&q, fifoBuffer);
      mpu.dmpGetGravity(&gravity, &q);
      mpu.dmpGetYawPitchRoll(ypr, &q, &gravity);
      // выводим результат в радианах (-3.14, 3.14)
      // для градусов можно использовать degrees()
      Angles ang = {ypr[0],ypr[1],ypr[2]};
      //ang.roll=ypr[2]*57.3;
      //ang.pitch=ypr[1]*57.3;
      //ang.yaw=ypr[0]*57.3;
      // выводим результат в радианах (-3.14, 3.14)
      // для градусов можно использовать degrees()
      return ang;
      }      tmr = millis();  // сброс таймера
    }
        
      }






/*struct point calc_point(struct angles ang,struct point view_point,int dist){//расчитываем точку
  float res_vector[3]={0,0,0};

  float roll=ang.roll;
  float pitch=ang.pitch;
  float yaw=ang.yaw;

  //Serial.print(roll); // вокруг оси X
  //Serial.print(',');
  //Serial.print(pitch); // вокруг Y
  //Serial.print(',');
  //Serial.print(yaw); // вокруг оси Z
  //Serial.println();

  float rotation_matrix[3][3] = {
        {(cos(roll) * cos(pitch)),  (cos(roll) * sin(pitch) * sin(yaw) - sin(roll) * cos(yaw)),     (cos(roll) * sin(pitch) * cos(yaw) + sin(roll) * sin(yaw))},
        {(sin(roll) * cos(pitch)),  (sin(roll) * sin(pitch) * sin(yaw) + cos(roll) * cos(yaw)),   (sin(roll) * sin(pitch) * cos(yaw) - cos(roll) * sin(yaw))},
        {(-sin(pitch)) ,cos(pitch) * sin(yaw),cos(pitch) * cos(yaw)}
    };//матрица поворота
  //dist=134;
  int base_vector[3]={0,0,0};
  base_vector[0]=dist;
  int i;
    int j;
    for (i = 0; i < 3; i++) {
        for (j = 0; j < 3; j++) {
            res_vector[i] = res_vector[i]+ base_vector[j] * rotation_matrix[i][j];
        }
    }
  point point_meas;
  for (i = 0; i < 3; i++){
    point_meas.coords[i]=view_point.coords[i]+res_vector[i];
  }
  delay(100);
  //Serial.print("точка:");
  //Serial.print(point_meas.coords[0]);
  //Serial.print(',');
  //Serial.print(point_meas.coords[1]);
  //Serial.print(',');
  //Serial.print(point_meas.coords[2]);
  //Serial.print("расстояне:");
  //Serial.print(dist);
  //Serial.println();
  return point_meas;

}*/

int get_distance(){
  if (TF_Luna_Serial.available() >= 9) {
    uint8_t buf[9];
    uint8_t sum = 0;
    TF_Luna_Serial.readBytes(buf, 9);

    for (int i = 0; i < 8; i++) {
      sum += buf[i];
    }

    if (sum == buf[8]) {
      int distance = (buf[2] | (buf[3] << 8));   // Конвертация данных в расстояние в сантиметрах
      //int distance = (buf[2]);
      return distance;
    }
  }

}