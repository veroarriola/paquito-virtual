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
