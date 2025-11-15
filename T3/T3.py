import cv2
import numpy as np
import json

# 加载图像
image = cv2.imread("image.png")

# 转换为灰度图像
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 使用边缘检测找到方块轮廓
_, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 定义颜色字典
color_dict = {'red': (0, 0, 255), 'green': (0, 255, 0), 'blue': (255, 0, 0), 'yellow': (0, 255, 255)}
color_count = {'red': 0, 'green': 0, 'blue': 0, 'yellow': 0}

# 检测方块并统计颜色
detections = []
for contour in contours:
    # 逼近多边形
    epsilon = 0.04 * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)
    
    # 判断是否为四边形（方块）
    if len(approx) == 4:
        # 获取中心点
        M = cv2.moments(contour)
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])

        # 计算方块的边长（假设是正方形）
        size_px = cv2.norm(approx[0] - approx[1])

        # 计算旋转角度（角度假设为 ±30°）
        angle_deg = 0  # 示例代码，可以使用更复杂的角度计算方法

        # 假设通过颜色检测识别方块颜色（这里只是示例）
        color = 'red'  # 可以使用颜色分割或颜色识别算法来识别实际颜色
        color_count[color] += 1

        # 绘制方块
        cv2.drawContours(image, [approx], -1, color_dict[color], 3)
        cv2.circle(image, (cx, cy), 5, (0, 0, 255), -1)
        
        # 记录检测到的方块信息
        detections.append({
            'cx': cx, 'cy': cy, 'size_px': size_px, 'angle_deg': angle_deg, 'color': color
        })

# 保存检测结果为 JSON
with open("detections.json", "w") as json_file:
    json.dump({'filename': 'image.png', 'detections': detections}, json_file)

# 展示结果图像
cv2.imshow("Detected Image", image)
cv2.waitKey(0)
cv2.destroyAllWindows()

# 输出颜色统计
print(color_count)
