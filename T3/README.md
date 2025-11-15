### 请务必看使用说明！

## T3文件夹目录统计

| 类型 | 数量 | 说明 |
|------|------|------|
| Python 文件 | 1 | T3.py |
| Markdown 文件 | 2 | README.md, 技术文档.md |
| 输入图像 | 3 | image1.png, image2.png, image3.png |
| 输出文件 | 2 | Out_image.png, Out_json.json |
| 文档图片 | 5 | 技术文档中的示例图片 |
| 依赖库 | 1 | cv2.pyd |
| 缓存文件 | 1+ | __pycache__ 中的字节码文件 |

## 文件关系

```
T3.py
  ├─ 读取 → Input/*.png
  ├─ 输出 → Output/Out_image.png
  ├─ 输出 → Output/Out_json.json
  └─ 参考 → 技术文档/技术文档.md
```

## 使用说明

1. 准备输入：将待检测图像放入 `Input/` 目录
2. 运行程序：执行 `T3.py`（修改第6行的 `image_path` 变量）
3. 查看结果：
   - 图像结果：`Output/Out_image.png`
   - 数据结果：`Output/Out_json.json`
   - 窗口显示：程序运行时会弹出窗口