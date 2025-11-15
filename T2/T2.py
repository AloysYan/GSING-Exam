import cv2
import numpy as np
from collections import defaultdict
import time

class PatternRecognizer:
    """基于颜色和形状特征的图案识别器"""
    
    def __init__(self):
        # 定义四种图案的颜色范围（HSV）
        # 食品（绿色）
        self.food_lower = np.array([35, 40, 40])
        self.food_upper = np.array([85, 255, 255])
        
        # 工具（灰色）
        self.tools_lower = np.array([0, 0, 80])
        self.tools_upper = np.array([180, 50, 200])
        
        # 仪器（蓝色）
        self.instruments_lower = np.array([100, 50, 50])
        self.instruments_upper = np.array([130, 255, 255])
        
        # 药品（红色）
        self.medicine_lower = np.array([0, 100, 100])
        self.medicine_upper = np.array([10, 255, 255])
        self.medicine_lower2 = np.array([170, 100, 100])
        self.medicine_upper2 = np.array([180, 255, 255])
        
        # 识别历史用于平滑结果
        self.detection_history = defaultdict(list)
        self.history_size = 5
        
    def get_mask(self, hsv_image):
        """获取包含有效颜色的掩码"""
        mask_food = cv2.inRange(hsv_image, self.food_lower, self.food_upper)
        mask_tools = cv2.inRange(hsv_image, self.tools_lower, self.tools_upper)
        mask_instruments = cv2.inRange(hsv_image, self.instruments_lower, self.instruments_upper)
        mask_medicine1 = cv2.inRange(hsv_image, self.medicine_lower, self.medicine_upper)
        mask_medicine2 = cv2.inRange(hsv_image, self.medicine_lower2, self.medicine_upper2)
        mask_medicine = cv2.bitwise_or(mask_medicine1, mask_medicine2)
        
        return mask_food, mask_tools, mask_instruments, mask_medicine
    
    def analyze_contours(self, mask, min_area=500):
        """分析轮廓特征"""
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        features = {
            'contour_count': 0,
            'avg_area': 0,
            'circularity': 0,
            'largest_contour': None,
            'centroid': None
        }
        
        if len(contours) == 0:
            return features
        
        valid_contours = [c for c in contours if cv2.contourArea(c) > min_area]
        if not valid_contours:
            return features
        
        features['contour_count'] = len(valid_contours)
        areas = [cv2.contourArea(c) for c in valid_contours]
        features['avg_area'] = np.mean(areas)
        
        # 找最大轮廓
        largest = max(valid_contours, key=cv2.contourArea)
        features['largest_contour'] = largest
        
        # 计算形状特征
        area = cv2.contourArea(largest)
        perimeter = cv2.arcLength(largest, True)
        if perimeter > 0:
            features['circularity'] = 4 * np.pi * area / (perimeter * perimeter)
        
        # 计算重心
        M = cv2.moments(largest)
        if M['m00'] > 0:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            features['centroid'] = (cx, cy)
        
        return features
    
    def recognize_pattern(self, frame, roi_mask):
        """识别区域内的图案"""
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        mask_food, mask_tools, mask_instruments, mask_medicine = self.get_mask(hsv_frame)
        
        # 只在ROI内检测
        roi_food = cv2.bitwise_and(mask_food, mask_food, mask=roi_mask)
        roi_tools = cv2.bitwise_and(mask_tools, mask_tools, mask=roi_mask)
        roi_instruments = cv2.bitwise_and(mask_instruments, mask_instruments, mask=roi_mask)
        roi_medicine = cv2.bitwise_and(mask_medicine, mask_medicine, mask=roi_mask)
        
        # 分析每个掩码
        features_food = self.analyze_contours(roi_food)
        features_tools = self.analyze_contours(roi_tools)
        features_instruments = self.analyze_contours(roi_instruments)
        features_medicine = self.analyze_contours(roi_medicine)
        
        # 评分并选择最佳匹配
        scores = {
            'food': self._calculate_score(features_food),
            'tools': self._calculate_score(features_tools),
            'instruments': self._calculate_score(features_instruments),
            'medicine': self._calculate_score(features_medicine)
        }
        
        pattern_names = {
            'food': '食品',
            'tools': '工具',
            'instruments': '仪器',
            'medicine': '药品'
        }
        
        pattern_colors = {
            'food': (0, 255, 0),      # 绿色
            'tools': (128, 128, 128), # 灰色
            'instruments': (255, 0, 0), # 蓝色
            'medicine': (0, 0, 255)   # 红色
        }
        
        best_pattern = max(scores, key=scores.get)
        best_score = scores[best_pattern]
        
        return best_pattern, best_score, pattern_names[best_pattern], pattern_colors[best_pattern]
    
    def _calculate_score(self, features):
        """计算匹配分数"""
        if features['contour_count'] == 0:
            return 0
        
        score = features['avg_area'] / 10000  # 面积分数
        score += features['contour_count'] * 0.5  # 轮廓数量分数
        
        return score


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("无法打开摄像头")
        return
    
    # 设置摄像头参数
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    recognizer = PatternRecognizer()
    
    # 目标区域参数
    roi_size = 200
    
    # 平滑识别结果
    detection_buffer = []
    buffer_size = 5
    confidence_threshold = 2.0  # ✅ 提高阈值，减少误判
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 获取图像尺寸
        height, width, _ = frame.shape
        center_x, center_y = width // 2, height // 2
        
        # 定义ROI区域
        roi_x1 = center_x - roi_size // 2
        roi_y1 = center_y - roi_size // 2
        roi_x2 = center_x + roi_size // 2
        roi_y2 = center_y + roi_size // 2
        
        # 创建ROI掩码
        roi_mask = np.zeros((height, width), dtype=np.uint8)
        cv2.rectangle(roi_mask, (roi_x1, roi_y1), (roi_x2, roi_y2), 255, -1)
        
        # ✅ 识别区域内的图案
        pattern, score, pattern_name, pattern_color = recognizer.recognize_pattern(frame, roi_mask)
        
        # 使用缓冲平滑结果
        detection_buffer.append((pattern, score))
        if len(detection_buffer) > buffer_size:
            detection_buffer.pop(0)
        
        # 计算平均分数
        avg_score = np.mean([s for _, s in detection_buffer]) if detection_buffer else 0
        
        # ✅ 判断是否检测到方形（基于平均分数）
        square_detected = avg_score > confidence_threshold
        
        # ✅ 获取检测到的物体位置（从识别结果中获取）
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask_food, mask_tools, mask_instruments, mask_medicine = recognizer.get_mask(hsv_frame)
        roi_food = cv2.bitwise_and(mask_food, mask_food, mask=roi_mask)
        features = recognizer.analyze_contours(roi_food, 200)
        
        # ========== 绘制基础要求的显示信息 ==========
        # 状态行1：检测状态
        status_text = "STATUS: Square IN Target Zone" if square_detected else "STATUS: Square IN Target Zone"
        status_color = (0, 255, 0) if square_detected else (0, 0, 255)
        cv2.putText(frame, status_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        
        # 状态行2：运动状态
        movement_text = "MOVEMENT: IN TARGET" if square_detected else "MOVEMENT: NO SQUARE DETECTED"
        movement_color = (0, 255, 255) if square_detected else (255, 0, 0)
        cv2.putText(frame, movement_text, (10, 65),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, movement_color, 2)
        
        # 状态行3：检测结果
        if square_detected:
            detection_text = "DETECTION: Square DETECTED"
            detection_color = (0, 255, 0)
        else:
            detection_text = "DETECTION: Square NOT DETECTED"
            detection_color = (0, 0, 255)
        cv2.putText(frame, detection_text, (10, 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, detection_color, 2)
        
        # ========== 绘制进阶要求的显示信息 ==========
        if square_detected:
            # 显示识别的物品名称
            cv2.putText(frame, f"Object: {pattern_name}", (10, 135),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, pattern_color, 2)
            
            # 显示面积信息
            if features['avg_area'] > 0:
                cv2.putText(frame, f"Square Area: {int(features['avg_area'])} pixels", (10, 170),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
            
            # 显示位置信息
            if features['centroid']:
                pos_x, pos_y = features['centroid']
                cv2.putText(frame, f"Position: ({pos_x}, {pos_y})", (10, 205),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
        
        # 绘制ROI框
        if square_detected:
            cv2.rectangle(frame, (roi_x1, roi_y1), (roi_x2, roi_y2), pattern_color, 3)
        else:
            cv2.rectangle(frame, (roi_x1, roi_y1), (roi_x2, roi_y2), (0, 255, 0), 2)
        
        # 显示帮助信息
        cv2.putText(frame, "Press 'q' to quit", (10, height - 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # 展示实时图像
        cv2.imshow("Enhanced Square Detection System", frame)
        
        # 按键处理
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
    
    # 释放资源
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
