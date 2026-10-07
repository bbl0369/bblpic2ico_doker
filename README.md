## Pic2Ico Docker 版（Python）

这是一个与原 `Pic2Ico` 功能类似的 **NAS / Docker 版图片转 ICO 服务**，使用 **Python + FastAPI + Pillow** 实现，通过浏览器上传图片即可生成包含多尺寸的 `.ico` 图标文件。

### 功能说明

- **支持格式**：PNG / JPG / JPEG。
- **多尺寸 ICO 一次生成**：前端页面提供 256、128、96、64、48、32、24、16 这些常见尺寸的勾选，至少选择一个。
- **Web 页面 + API**：
  - 访问根路径 `/`，打开一个简洁的上传页面；
  - 也可以直接调用接口 `POST /convert` 实现自动化。

### 本地运行（无需 Docker）

1. 安装依赖（推荐使用 Python 3.10+）：

```bash
cd bblpic2ico_doker
pip install -r requirements.txt
```

2. 启动服务：

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

3. 在浏览器中访问：

- 打开 `http://127.0.0.1:8000/`，上传图片并选择尺寸，点击「转换」后浏览器会下载生成的 `.ico` 文件。

### 使用 Docker 运行

#### 1. 构建镜像

在 `bblpic2ico_doker` 目录下执行：

```bash
docker build -t pic2ico-docker .
```

#### 2. 运行容器

```bash
docker run -d --name pic2ico-docker -p 8000:8000 pic2ico-docker
```

- 这样就可以在宿主机/NAS 上通过 `http://<NAS_IP>:8000/` 访问 Web 界面。

### 接口说明（适合脚本/自动化）

**POST `/convert`**

- **Content-Type**：`multipart/form-data`
- **参数**：
  - `file`：图片文件（PNG / JPG / JPEG）
  - `sizes`：可以是多个字段，如 `sizes=256&sizes=128&sizes=64`（对应前端的多选框）
- **返回**：`image/x-icon` 文件流，浏览器会直接触发下载。

使用 `curl` 示例：

```bash
curl -X POST "http://127.0.0.1:8000/convert" ^
  -F "file=@C:/path/to/image.png" ^
  -F "sizes=256" -F "sizes=128" -F "sizes=64" ^
  --output icon.ico
```

（Linux/Mac 把 `^` 替换为 `\` 并改成对应的路径即可）

### 与原 C# 项目的关系

- 原仓库中的 `Pic2Ico` 是 **Windows 桌面版**，适合在本地 PC 上直接双击使用；
- `bblpic2ico_doker` 下的这个 Python 版本是 **面向 NAS / 服务器 / Docker 环境** 的 Web 服务版：
  - 不依赖 Windows GUI；
  - 可以让局域网中多台设备通过浏览器共同使用同一个服务。

