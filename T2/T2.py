import cv2
import numpy as np

# 设置摄像头
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 获取图像的中心，定义目标区域
    height, width, _ = frame.shape
    center_x, center_y = width // 2, height // 2
    size = 200  # 正方形的边长

    # 绘制中心的正方形区域
    cv2.rectangle(frame, (center_x - size // 2, center_y - size // 2), 
                  (center_x + size // 2, center_y + size // 2), (0, 255, 0), 2)

    # 在图像中识别特定图案的算法（可以改为实际的图案识别逻辑）
    # 例如，识别到某个颜色的正方形，您可以在此处添加 OpenCV 的颜色过滤或轮廓检测等方法

    # 展示实时图像
    cv2.imshow("Frame", frame)

    # 按下 'q' 键退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放资源
cap.release()
cv2.destroyAllWindows()
