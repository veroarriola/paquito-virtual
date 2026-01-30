import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image

import cv2
import numpy as np

class CameraViewer(Node):
    def __init__(self):
        super().__init__('camera_viewer_node')
        
        # Nos suscribimos al mismo tópico que creamos en la Raspberry
        self.subscription = self.create_subscription(
            Image,
            '/camera/image',
            self.listener_callback,
            10)
        
        self.get_logger().info('Nodo visualizador iniciado. Esperando imágenes...')

    def listener_callback(self, msg):
        im_arr = np.frombuffer(msg.data, dtype=np.uint8)
        im_arr = im_arr.reshape((msg.height, msg.width, 3))

        self.get_logger().info(f"Img: {im_arr.shape}")
        cv_image = im_arr

        # # 1. Convertir el buffer de bytes del mensaje a un array de NumPy
        # # El tipo de dato es uint8 (unsigned int de 8 bits para colores 0-255)
        # im_arr = np.frombuffer(msg.data, dtype=np.uint8)

        # # Intentamos el reshape usando la información del mensaje
        # try:
        #     # Si hay rayitas, a veces es porque el buffer trae más datos de los calculados
        #     # Tomamos solo los bytes necesarios para (H * W * 3)
        #     expected_size = msg.height * msg.width * 3
            
        #     # 2. Reestructurar el array plano a las dimensiones de la imagen (H, W, Canales)
        #     # Usamos los datos que vienen en el propio mensaje
        #     #im_arr = im_arr.reshape((msg.height, msg.width, 3))
        #     im_arr = im_arr[:expected_size].reshape((msg.height, msg.width, 3))

        #     # 3. Conversión de Color: de RGB (ROS2) a BGR (OpenCV)
        #     # Si no haces esto, los rojos se verán azules y viceversa
        #     cv_image = cv2.cvtColor(im_arr, cv2.COLOR_RGB2BGR)

        #     # 4. Mostrar la imagen en una ventana
        #     cv2.imshow("Stream de la Raspberry Pi", cv_image)
            
        #     # Necesario para que la ventana de OpenCV se refresque
        #     cv2.waitKey(1)
        # except Exception as e:
        #     self.get_logger().error(f'Error reconstruyendo imagen: {e}')
        
        if cv_image is not None:
            small_img = cv2.resize(cv_image, (cv_image.shape[1]//2, cv_image.shape[0]//2))
            cv2.imshow("Stream", small_img)
            cv2.waitKey(1)

    def destroy_node(self):
        cv2.destroyAllWindows()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = CameraViewer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
