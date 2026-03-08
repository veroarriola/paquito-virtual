#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/joy.hpp"
#include <iostream>
#include <vector>

#include <geometry_msgs/msg/twist.hpp>
#include <std_msgs/msg/string.hpp>

//#include "paquito.hpp"

#define PS2
/// Control PS2
#if defined(PS2)
const unsigned int X_AXIS = 1;
const unsigned int Y_AXIS = 0;
const unsigned int Z_AXIS = 3;  // ?

const unsigned int STOP = 3;
const unsigned int SPEAK = 2;
/// Control ZhiXu
#elif defined(ZHI_XU)
const unsigned int X_AXIS = 1;      // Joy izquierdo
const unsigned int Y_AXIS = 0;
const unsigned int Z_AXIS = 2;      // Joy derecho horizontal

const unsigned int STOP = 9;        // Atrás inferior derecha
const unsigned int SPEAK = 4;    // X (Botón superior)
#endif

// Generado con ayuda de Gemini 2.5 Pro y adaptado
using std::placeholders::_1;

// La clase hereda de rclcpp::Node, la estructura base de un nodo en ROS 2
class JoySubscriber : public rclcpp::Node
{
public:
    // Constructor
    JoySubscriber() : Node("ps_controller_reader")
    {
        // Creamos la suscripción.
        // El tipo de mensaje es sensor_msgs::msg::Joy.
        // El '10' es la profundidad de la cola (Quality of Service).
        // El callback se enlaza usando std::bind.
        _joy_subscriber = this->create_subscription<sensor_msgs::msg::Joy>(
            "joy",
            10,
            std::bind(&JoySubscriber::joy_callback, this, _1)
        );

        // Publica comandos tipo cadena
        _string_command_publisher = this->create_publisher<std_msgs::msg::String>(
            "command_for_paquito",
            10
        );

        // Publicará las velocidades solicitadas según el uso del control PS2
        _vel_command_publisher = this->create_publisher<geometry_msgs::msg::Twist>(
            "cmd_vel",
            10
        );


        RCLCPP_INFO(this->get_logger(), "Nodo de control de PlayStation iniciado. Esperando mensajes en /joy...  Publicando en /cmd_vel...");
    }

private:
    void log_state(const sensor_msgs::msg::Joy::SharedPtr msg)
    {
        std::stringstream ss;

        // Imprime el estado de botones, ejes y variables de interés
        // msg->axes es un vector de floats, generalmente entre -1.0 y 1.0
        RCLCPP_INFO(this->get_logger(), "Botones:");
        ss << " Eje x " << X_AXIS << ": " << msg->axes[X_AXIS] << std::endl;
        ss << " Eje y " << Y_AXIS << ": " << msg->axes[Y_AXIS] << std::endl;
        ss << " Eje z (giro) " << Z_AXIS << ": " << msg->axes[Z_AXIS] << std::endl;

        ss << " Botón habla " << SPEAK << ": " << (msg->buttons[SPEAK] ? "Presionado" : "Suelto") << std::endl;
        ss << " Botón alto " << STOP << ": " << (msg->buttons[STOP] ? "Presionado" : "Suelto") << std::endl;

        RCLCPP_INFO(this->get_logger(), "%s", ss.str().c_str());
    }

    // Función de callback que se ejecuta al recibir un mensaje
    void joy_callback(const sensor_msgs::msg::Joy::SharedPtr msg)
    {

        if (msg->axes[7] == 1.0)
        {
            std_msgs::msg::String msg_str;
            RCLCPP_INFO(this->get_logger(), "FL");
            msg_str.data = "FL";
            _string_command_publisher->publish(msg_str);
        }
        else if (msg->axes[6] == -1.0)
        {
            std_msgs::msg::String msg_str;
            RCLCPP_INFO(this->get_logger(), "FR");
            msg_str.data = "FR";
            _string_command_publisher->publish(msg_str);
        }
        else if (msg->axes[7] == -1.0)
        {
            std_msgs::msg::String msg_str;
            RCLCPP_INFO(this->get_logger(), "RR");
            msg_str.data = "RR";
            _string_command_publisher->publish(msg_str);
        }
        else if (msg->axes[6] == 1.0)
        {
            std_msgs::msg::String msg_str;
            RCLCPP_INFO(this->get_logger(), "RL");
            msg_str.data = "RL";
            _string_command_publisher->publish(msg_str);
        }
        else if(msg->buttons[SPEAK])
        {
            std_msgs::msg::String msg_str;
            RCLCPP_INFO(this->get_logger(), "speak");
            msg_str.data = "speak";
            _string_command_publisher->publish(msg_str);
        }
        else if(msg->buttons[STOP])
        {
            std_msgs::msg::String msg_str;
            RCLCPP_INFO(this->get_logger(), "stop");
            msg_str.data = "stop";
            _string_command_publisher->publish(msg_str);
        }
        else {
            geometry_msgs::msg::Twist twist;

            twist.linear.x = msg->axes[X_AXIS] * MAX_LINE_SPEED;
            twist.linear.y = msg->axes[Y_AXIS] * MAX_LINE_SPEED;
            twist.angular.z = msg->axes[Z_AXIS] * MAX_ANGLE_SPEED;

            _vel_command_publisher->publish(twist);
        }
    }

    rclcpp::Subscription<sensor_msgs::msg::Joy>::SharedPtr _joy_subscriber;
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr _vel_command_publisher;
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr _string_command_publisher;
    const double MAX_LINE_SPEED = 0.5;        // m/s
    const double MAX_ANGLE_SPEED = 3.1416/2;  // rad/s
};

int main(int argc, char * argv[])
{
    // Inicializa ROS 2
    rclcpp::init(argc, argv);

    // Crea una instancia del nodo y lo mantiene vivo hasta que se detenga (Ctrl+C)
    rclcpp::spin(std::make_shared<JoySubscriber>());

    // Libera los recursos de ROS 2
    rclcpp::shutdown();
    return 0;
}
