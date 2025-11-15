import cv2
import numpy as np
import json

# 其下输入图片名称 (＾▽＾) 
image_path = "image1.png"   # <-- (＾▽＾) 在此处输入图片名称 
# 其上输入图片名称 (＾▽＾) 

image = cv2.imread("T3/Input/" + image_path)

# 检查图像是否成功加载
if image is None:
    print(f"错误：无法加载图像 '{image_path}'。请确认文件存在并可读取。")
    raise SystemExit(1)

# 基于 HSV 颜色阈值进行检测
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# 定义 HSV 范围
color_ranges = {
    'red1': (np.array([0, 100, 100]), np.array([10, 255, 255])),
    'red2': (np.array([160, 100, 100]), np.array([179, 255, 255])),
    'green': (np.array([40, 60, 60]), np.array([85, 255, 255])),
    'blue': (np.array([90, 60, 60]), np.array([140, 255, 255])),
    'yellow': (np.array([15, 60, 60]), np.array([35, 255, 255]))
}

# 初始化颜色计数器
color_count = {'red': 0, 'green': 0, 'blue': 0, 'yellow': 0}

# 初始化检测结果列表
detections = []

# 对每个目标颜色生成掩码并检测轮廓
for cname in ['red', 'green', 'blue', 'yellow']:
    if cname == 'red':
        mask1 = cv2.inRange(hsv, color_ranges['red1'][0], color_ranges['red1'][1])
        mask2 = cv2.inRange(hsv, color_ranges['red2'][0], color_ranges['red2'][1])
        mask = cv2.bitwise_or(mask1, mask2)
    else:
        low, high = color_ranges[cname]
        mask = cv2.inRange(hsv, low, high)

    # 查找轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 遍历每个轮廓
    for cnt in contours:
        # 计算轮廓面积
        area = cv2.contourArea(cnt)
        if area < 200:  # 更低的阈值以捕获更小方块
            continue

        # 使用最小外接矩形以获得旋转角度和准确的尺寸
        rect = cv2.minAreaRect(cnt)
        (cx_rect, cy_rect), (rw, rh), angle = rect
        cx = int(cx_rect)
        cy = int(cy_rect)
        # 用矩形的较长边作为主要尺寸（更代表方块大小）
        size_px = int(max(rw, rh))
        angle_deg = int(round(angle))  # 取整旋转角度

        color_count[cname] += 1

        # 绘制旋转矩形和中心点
        box = cv2.boxPoints(rect)
        box = box.astype(int)
        
        # 绘制灰色边框
        gray_color = (64, 64, 64)
        cv2.drawContours(image, [box], 0, gray_color, 3)
        cv2.circle(image, (cx, cy), 4, (0, 0, 0), -1)

        # 在矩形左上角附近标注颜色（标签）
        box_points = box.tolist()
        min_y = min(pt[1] for pt in box_points)     # 找到最小 y 坐标（最上方的点） 生成器表达式
        min_x = min(pt[0] for pt in box_points)     # 找到最小 x 坐标（最左侧的点） 生成器表达式
        text_x = max(5, min_x)                      # 确保文本不会太靠近图像左边缘
        text_y = max(15, min_y - 8)                 # 确保文本不会太靠近图像上边缘
        # 绘制黑色主体
        cv2.putText(image, cname, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1, cv2.LINE_AA)

        detections.append({'cx': cx, 'cy': cy, 'size_px': size_px, 'angle_deg': angle_deg, 'color': cname})

# 保存检测结果为 JSON
out = {
    'filename': image_path,
    'detections': detections,
    'color_counts': color_count
}
with open("T3/Output/Out_json.json", "w", encoding="utf-8") as json_file:
    json.dump(out, json_file, ensure_ascii=False, indent=2)

# 保存结果图像
out_image_path = "T3/Output/Out_image.png"
cv2.imwrite(out_image_path, image)

# 显示结果图像窗口
try:
    window_name = "Out_Image"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    # 显示结果图像
    cv2.imshow(window_name, image)
    print("\n按任意键关闭窗口。")
    # 等待按键关闭窗口
    cv2.waitKey(0)
    # 关闭窗口
    cv2.destroyAllWindows(window_name)
except Exception:
    # 在无 GUI 环境或无法创建窗口时忽略错误
    pass
