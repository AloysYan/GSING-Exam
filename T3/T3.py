import cv2
import numpy as np
import json
import os

# 加载图像（使用脚本目录的相对路径，避免工作目录不同导致找不到文件）
script_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(script_dir, "image1.png")
image = cv2.imread(image_path)

if image is None:
    print(f"错误：无法加载图像 '{image_path}'。请确认文件存在并可读取。")
    raise SystemExit(1)

# 转换为灰度图像
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 使用 Canny 边缘检测 + 形态学闭运算以更稳健地提取方块轮廓
blur = cv2.GaussianBlur(gray, (5, 5), 0)
edges = cv2.Canny(blur, 50, 150)
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 定义颜色字典
color_dict = {'red': (0, 0, 255), 'green': (0, 255, 0), 'blue': (255, 0, 0), 'yellow': (0, 255, 255)}
color_count = {'red': 0, 'green': 0, 'blue': 0, 'yellow': 0}

# 检测方块并统计颜色（使用多种过滤以提高鲁棒性）
detections = []
for contour in contours:
    area = cv2.contourArea(contour)
    if area < 500:  # 忽略过小噪声，阈值可根据图像调整
        continue

    # 逼近多边形并筛选四边形
    epsilon = 0.02 * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)
    if len(approx) != 4:
        continue

    # 排除非凸的多边形
    if not cv2.isContourConvex(approx):
        continue

    # 计算中心点（安全处理 m00）
    M = cv2.moments(contour)
    if M['m00'] == 0:
        continue
    cx = int(M['m10'] / M['m00'])
    cy = int(M['m01'] / M['m00'])

    # 使用最小外接矩形计算角度与尺寸
    rect = cv2.minAreaRect(contour)
    (rx, ry), (rw, rh), angle = rect
    size_px = int((rw + rh) / 2)
    angle_deg = float(angle)

    # 使用边界框并在内部采样颜色，避免黑色轮廓干扰
    x, y, w, h = cv2.boundingRect(approx)
    inner_margin = max(1, int(min(w, h) * 0.2))
    sx = x + inner_margin
    sy = y + inner_margin
    sw = w - 2 * inner_margin
    sh = h - 2 * inner_margin
    if sw <= 2 or sh <= 2:
        # 如果内部区域太小，退回到掩码平均
        mask = np.zeros(gray.shape, dtype=np.uint8)
        cv2.drawContours(mask, [contour], -1, 255, -1)
        mean_val = cv2.mean(image, mask=mask)[:3]
    else:
        roi = image[sy:sy+sh, sx:sx+sw]
        if roi.size == 0:
            continue
        mean_val = cv2.mean(roi)[:3]

    # 最接近的颜色匹配
    def nearest_color(bgr):
        b, g, r = bgr
        best = None
        best_dist = None
        for name, col in color_dict.items():
            cb, cg, cr = col
            dist = (float(cb) - b) ** 2 + (float(cg) - g) ** 2 + (float(cr) - r) ** 2
            if best_dist is None or dist < best_dist:
                best_dist = dist
                best = name
        return best

    color = nearest_color(mean_val)
    color_count[color] += 1

    # 绘制检测结果（最小外接矩形以显示旋转）
    box = cv2.boxPoints(rect)
    box = box.astype(int)
    cv2.drawContours(image, [box], 0, color_dict[color], 3)
    cv2.circle(image, (cx, cy), 4, (0, 0, 255), -1)

    # 在方块附近绘制颜色标签（先绘制较粗的白色描边，再绘制黑色文字以增强可读性）
    label = f"{color}"
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7
    thickness = 2
    # 文本位置优先在方块上方，如果空间不足则放到下方
    text_x = x
    text_y = y - 8 if y - 8 > 12 else y + h + 18
    # 描边（白）
    cv2.putText(image, label, (text_x, text_y), font, font_scale, (255, 255, 255), thickness + 2, cv2.LINE_AA)
    # 主体（黑）
    cv2.putText(image, label, (text_x, text_y), font, font_scale, (0, 0, 0), thickness, cv2.LINE_AA)

    detections.append({
        'cx': cx, 'cy': cy, 'size_px': size_px, 'angle_deg': angle_deg, 'color': color
    })

# 保存检测结果为 JSON
out = {
    'filename': os.path.basename(image_path),
    'detections': detections,
    'color_counts': color_count
}
with open("detections.json", "w", encoding="utf-8") as json_file:
    json.dump(out, json_file, ensure_ascii=False, indent=2)

# 保存并根据环境决定是否展示结果图像
out_image_path = os.path.join(script_dir, "detected_image.png")
cv2.imwrite(out_image_path, image)
# 通过环境变量控制是否弹窗显示（设置 SHOW_IMAGE=0 可跳过），默认会显示
show_image = os.environ.get("SHOW_IMAGE", "1") != "0"
if show_image:
    try:
        window_name = "Detected Image"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        # 如果图像过大，按比例缩放到最大边长，以免窗口超出屏幕
        h, w = image.shape[:2]
        max_dim = 1200
        if max(h, w) > max_dim:
            scale = max_dim / max(h, w)
            display = cv2.resize(image, (int(w * scale), int(h * scale)))
        else:
            display = image
        cv2.imshow(window_name, display)
        print("按任意键关闭窗口（若看不到窗口请确保在带 GUI 的环境运行）。")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except Exception:
        # 在无 GUI 环境或无法创建窗口时忽略错误
        pass
else:
    print(f"已保存检测可视化到: {out_image_path}（未弹窗，SHOW_IMAGE=0）")

# 输出颜色统计
print(color_count)
