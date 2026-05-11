# GitHub Pages 部署指南

> 本指南详细介绍如何将 **QuarkAudio-Edit Demo Page** 部署到 GitHub Pages，
> 让全世界的审稿人和读者通过 `https://<your-name>.github.io/<repo>/` 访问你的论文项目页。

---

## 📋 目录

- [方案对比](#方案对比)
- [准备工作](#准备工作)
- [方案 A：独立仓库 + 用户页（推荐用于论文发布）](#方案-a独立仓库--用户页推荐用于论文发布)
- [方案 B：子目录部署（保留在论文仓库中）](#方案-b子目录部署保留在论文仓库中)
- [方案 C：GitHub Actions 自动化部署（推荐用于持续更新）](#方案-cgithub-actions-自动化部署推荐用于持续更新)
- [方案 D：匿名部署（双盲评审期间）](#方案-d匿名部署双盲评审期间)
- [自定义域名](#自定义域名)
- [大文件处理：Git LFS 与外链](#大文件处理git-lfs-与外链)
- [常见问题排查](#常见问题排查)
- [部署前检查清单](#部署前检查清单)

---

## 方案对比

| 方案 | 适用场景 | URL 形式 | 难度 |
|------|----------|----------|------|
| A. 独立仓库 + 用户页 | 论文正式发布、长期维护 | `https://<user>.github.io/quarkaudio-edit/` | ⭐ |
| B. 子目录部署 | 和论文仓库绑在一起 | `https://<user>.github.io/<paper-repo>/demo_page/` | ⭐⭐ |
| C. GitHub Actions 自动化 | 频繁更新 demo 内容 | 同 A 或 B | ⭐⭐⭐ |
| D. 匿名部署（双盲评审） | EMNLP/ACL/AAAI 投稿期 | `https://<anon-user>.github.io/<repo>/` | ⭐⭐ |

---

## 准备工作

### 1. 注册 GitHub 账号并安装 Git

```bash
# 检查 Git 是否已安装
git --version
```

Windows 用户若未安装，从 <https://git-scm.com/download/win> 下载安装。

### 2. 配置 Git 用户信息

```bash
git config --global user.name  "Your Name"
git config --global user.email "your.email@example.com"
```

### 3. 生成 SSH Key（推荐，避免每次输密码）

```bash
ssh-keygen -t ed25519 -C "your.email@example.com"
# 一路回车
cat ~/.ssh/id_ed25519.pub
```

将输出的公钥添加到 GitHub：*Settings → SSH and GPG keys → New SSH key*。

---

## 方案 A：独立仓库 + 用户页（推荐用于论文发布）

### 步骤 1：在 GitHub 上创建一个新仓库

- 仓库名建议：`quarkaudio-edit`（与项目同名，URL 简洁）
- **Public**（GitHub Pages 免费版要求公开仓库）
- **不要**勾选 "Initialize with README"（我们会手动推送）

### 步骤 2：把 `demo_page/` 推送到仓库根目录

在 PowerShell 中执行（本地路径已用反引号保留中文路径安全）：

```powershell
# 1. 进入 demo_page 目录
cd "D:\02_Project\05_LLM_Audio\20260211-论文撰写\SAO-Instruct-0425\demo_page"

# 2. 初始化 git 仓库（main 分支）
git init
git branch -M main

# 3. 先创建 .gitignore（内容见下方"步骤 3"），避免把本地脚本、IDE 配置、
#    临时素材误提交。此步骤必须在 `git add` 之前完成，否则这些文件会被加入索引。
#    （可用 VS Code / 记事本 / PowerShell 任意方式创建文件）
New-Item -ItemType File -Path .gitignore -Force | Out-Null

# 4. 同理，创建一个空的 .nojekyll 文件，告诉 GitHub Pages 不要对下划线开头
#    的目录（如未来可能新增的 _assets）执行 Jekyll 过滤，避免资源 404。
New-Item -ItemType File -Path .nojekyll -Force | Out-Null

# 5. 把 .gitignore 内容粘贴进去后再执行 add
git add .
git commit -m "Initial commit: QuarkAudio-Edit demo page"

# 6. 绑定远程仓库（二选一）
#    SSH 方式（推荐，需先配置 SSH key）：
git remote add origin git@github.com:<your-username>/quarkaudio-edit.git
#    HTTPS 方式（无需 SSH key，每次 push 需输入 GitHub token）：
# git remote add origin https://github.com/<your-username>/quarkaudio-edit.git

# 7. 首次推送
git push -u origin main
```

> **为什么需要 `.nojekyll`**：GitHub Pages 默认会用 Jekyll 构建器处理仓库，
> 它会**忽略**所有以下划线 `_` 开头的文件/目录（Jekyll 的内部约定）。
> 如果你的静态资源路径出现 `_assets/`、`_audio/` 等命名，页面就会 404。
> 在根目录放一个空的 `.nojekyll` 文件即可关闭此行为。
> 本项目当前未使用下划线目录，但提前放置是**零成本**的安全保险。

### 步骤 3：推荐的 `.gitignore`

在 `demo_page/` 根目录创建 `.gitignore`：

```gitignore
# Local verification / scratch
_verify.py
*.log
.DS_Store
Thumbs.db

# Editor
.vscode/
.idea/
*.swp
*~

# Node (if you later add tooling)
node_modules/
package-lock.json

# Python
__pycache__/
*.pyc
*.pyo
.venv/
venv/

# Temporary audio / figures staging
_staging/

# Build artifacts (if any)
dist/
build/

# OS / env
.env
.env.local

# Note: do NOT ignore .nojekyll — it must be committed to GitHub so that
# Pages disables Jekyll processing for this site.
```

### 步骤 4：在 GitHub 上启用 Pages

1. 打开仓库 → **Settings** → 左侧 **Pages**
2. **Source** 选择 `Deploy from a branch`
3. **Branch** 选择 `main` / Folder 选择 `/ (root)`
4. 点击 **Save**
5. 等待约 30–90 秒，页面顶部会出现
   `Your site is live at https://<your-username>.github.io/quarkaudio-edit/`

### 步骤 5：验证

用浏览器无痕模式访问该 URL，逐项检查：
- Hero 区域正常渲染（深色渐变 + 渐变标题）
- 四张框架图正常显示
- 音频播放器可以播放（需已上传真实 `.wav` 文件）
- Tab 切换、chip 过滤、BibTeX 复制均正常

---

## 方案 B：子目录部署（保留在论文仓库中）

若你希望把 demo_page 和论文 LaTeX 源码保留在同一个仓库：

### 步骤 1：在论文仓库根目录启用 Pages

假设论文仓库叫 `quarkaudio-edit-paper`，目录结构为：

```
quarkaudio-edit-paper/
├── main.tex
├── sections/
├── figures/
├── demo_page/           ← 我们要发布的子目录
└── ...
```

### 步骤 2：选择部署路径

**选项 B1：在仓库根目录创建重定向首页**（最省事，URL 稍长）

在**论文仓库根目录**（与 `main.tex`、`demo_page/` 同级）创建 `index.html`：

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>QuarkAudio-Edit — redirecting…</title>
  <meta http-equiv="refresh" content="0; url=./demo_page/" />
  <link rel="canonical" href="./demo_page/" />
</head>
<body>
  <p>Redirecting to <a href="./demo_page/">./demo_page/</a>…</p>
</body>
</html>
```

同时在仓库根目录创建空文件 `.nojekyll`（原因见方案 A 步骤 2）。
最终 URL：访问 `https://<user>.github.io/<paper-repo>/` 会自动跳到
`https://<user>.github.io/<paper-repo>/demo_page/`。

**选项 B2：用 `publish_dir` 指定子目录为站点根**（URL 更短，推荐）

方案 B 的子目录部署本身无法通过 Pages UI 选中子目录作为根，
官方的正确做法是**用 GitHub Actions 把 `demo_page/` 作为 artifact 上传**
（即方案 C 的做法）。如果你希望 URL 不带 `/demo_page/` 前缀，
**请直接跳到方案 C**，它能精确控制发布目录。

### 步骤 3：启用 Pages

在仓库 **Settings → Pages**：
- **Source**: `Deploy from a branch`
- **Branch**: `main`
- **Folder**: `/ (root)`（因为 B1 的重定向页就在根目录）
- 点击 **Save**

最终 URL（采用 B1）：`https://<user>.github.io/<paper-repo>/`
（自动重定向到 `/demo_page/`）

---

## 方案 C：GitHub Actions 自动化部署（推荐用于持续更新）

这是最优雅的方案：论文仓库保持干净，每次 push 后自动把 `demo_page/` 发布到 Pages。

### 步骤 1：在论文仓库根目录创建 workflow 文件

路径：`.github/workflows/deploy-demo.yml`

```yaml
name: Deploy Demo Page to GitHub Pages

on:
  push:
    branches: [ main ]
    paths:
      - 'demo_page/**'
      - '.github/workflows/deploy-demo.yml'
  workflow_dispatch:     # 允许手动触发

# 只保留一个并发运行，避免多次 push 互相抢占
concurrency:
  group: "pages"
  cancel-in-progress: true

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          lfs: true                 # 若音频/图片使用 Git LFS，必须开启

      - name: Setup Pages
        uses: actions/configure-pages@v5

      - name: Upload artifact (demo_page only)
        uses: actions/upload-pages-artifact@v3
        with:
          path: ./demo_page         # ← 只发布 demo_page 目录，论文源码不对外

      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

### 步骤 2：启用 Pages 的 Actions 源

仓库 → **Settings → Pages → Source** 选择 **GitHub Actions**（而非 Deploy from a branch）。

### 步骤 3：推送代码触发部署

```bash
git add .github/workflows/deploy-demo.yml
git commit -m "ci: auto-deploy demo page to GitHub Pages"
git push origin main
```

### 步骤 4：监控部署

仓库 → **Actions** 标签可看到 workflow 运行日志。
部署成功后，**Settings → Pages** 会显示最终 URL。

### 方案 C 的三大优点

1. **论文源码与发布解耦**：Pages 上只有 `demo_page/` 的内容，LaTeX 源不对外
2. **零维护**：每次更新 demo 内容 push 即可，无需手动操作
3. **路径可控**：URL 直接是仓库根 `https://<user>.github.io/<repo>/`（不含 `/demo_page/` 前缀）

---

## 方案 D：匿名部署（双盲评审期间）

EMNLP / ACL / AAAI 双盲评审期间，**严禁**在论文仓库中出现任何可识别作者身份的信息。以下给出两条**官方推荐**的匿名发布路径，二选一即可。

### 路径 D1：使用 `anonymous.4open.science`（ACL/EMNLP 社区最推荐）

`anonymous.4open.science` 是 ACL Rolling Review 和大部分 NLP 会议**官方认可**的匿名仓库镜像服务，它会去除作者信息、打乱提交历史，并提供一个匿名 URL。

1. 把本项目 push 到你**已有的** GitHub 仓库（可以是 Private）
2. 访问 <https://anonymous.4open.science/>
3. 粘贴你的仓库 URL → 设置到期时间（审稿期 + 2 个月）→ 生成匿名链接
4. 匿名链接形如 `https://anonymous.4open.science/r/quarkaudio-edit-XXXX/`
5. 把该 URL 放进论文的脚注或 abstract 末尾

**优点**：无需新账号，支持 private repo，自动脱敏，会议组委会认可。
**缺点**：是源码浏览界面，不是渲染后的 demo 页（无法直接播放音频）。

### 路径 D2：新建匿名 GitHub 账号 + GitHub Pages（可交互 demo）

若审稿人需要真正**可交互**的 demo 页面（能在线播放音频、查看图片），
则必须用一个匿名账号把 Pages 跑起来：

#### 步骤 1：创建匿名 GitHub 账号

- 用新邮箱（如 Gmail / ProtonMail 小号）注册 GitHub 账号
- 用户名选择中性词汇（如 `anon-quarkaudio-edit-2026`，避免包含真实姓名/学校首字母）
- **不要**在头像、profile、任何 commit 中填写真实信息
- 配置 Git 时使用匿名身份：
  ```bash
  git config user.name  "Anonymous Author"
  git config user.email "anon@example.com"
  ```
- **建议**：在该账号下只放这一个匿名仓库，不要混入其它项目（防止交叉身份识别）

#### 步骤 2：脱敏检查

部署前用以下命令确认没有泄露：

```powershell
# Windows PowerShell
cd "D:\02_Project\05_LLM_Audio\20260211-论文撰写\SAO-Instruct-0425\demo_page"
Select-String -Path *.html,*.css,*.js,*.md -Pattern "author|affiliation|email|github\.com/(?!anonymous)" | Format-Table Path, LineNumber, Line -AutoSize
```

确认 `index.html` 中：
- `.authors` 为 `Anonymous Authors`
- `.affiliations` 为 `Author information hidden for double-blind review`
- BibTeX `author = {Anonymous Authors}`
- Footer 中没有个人邮箱 / 主页链接

#### 步骤 3：按方案 A 正常部署

审稿期结束后，换回正式作者信息重新部署即可。

#### 步骤 4：投稿时在论文中引用

在论文脚注引用：
```latex
\footnote{Demo page and audio samples: \url{https://anon-quarkaudio-edit-2026.github.io/demo/}}
```

#### 步骤 5：commit 历史脱敏检查（易被忽略）

Git 提交历史里的 `Author:` 字段**不会**在浏览器端暴露，但审稿人可以
`git clone` 你的仓库查看。务必在 push 前执行：

```bash
# 查看所有提交的 author 信息
git log --pretty=format:"%h %an <%ae>" | cat

# 若历史中出现了真实姓名，用下面的命令重写全部历史
git filter-repo --name-callback "return b'Anonymous Author'" \
                --email-callback "return b'anon@example.com'"
git push origin main --force
```

---

## 自定义域名

若你有自己的域名（如 `quarkaudio-edit.com`），可以绑定到 Pages：

### 步骤 1：在 DNS 服务商添加记录

GitHub Pages 官方要求**同时**配置 IPv4 (A) 和 IPv6 (AAAA) 记录，
以及 `www` 子域的 CNAME。完整清单如下（数据来自 GitHub 官方文档）：

**Apex 域（`example.com`）**

| 类型  | 主机 | 值                                   | 说明            |
|-------|------|--------------------------------------|-----------------|
| A     | @    | `185.199.108.153`                    | GitHub Pages IPv4 |
| A     | @    | `185.199.109.153`                    | GitHub Pages IPv4 |
| A     | @    | `185.199.110.153`                    | GitHub Pages IPv4 |
| A     | @    | `185.199.111.153`                    | GitHub Pages IPv4 |
| AAAA  | @    | `2606:50c0:8000::153`                | GitHub Pages IPv6 |
| AAAA  | @    | `2606:50c0:8001::153`                | GitHub Pages IPv6 |
| AAAA  | @    | `2606:50c0:8002::153`                | GitHub Pages IPv6 |
| AAAA  | @    | `2606:50c0:8003::153`                | GitHub Pages IPv6 |

**www 子域（`www.example.com`）**

| 类型  | 主机 | 值                          | 说明                              |
|-------|------|-----------------------------|-----------------------------------|
| CNAME | www  | `<your-username>.github.io` | 指向你的用户页（**不要**加末尾的点） |

> 验证配置是否生效：
> ```bash
> dig quarkaudio-edit.com +noall +answer
> dig AAAA quarkaudio-edit.com +noall +answer
> dig www.quarkaudio-edit.com +noall +answer
> ```
> 若看不到 `185.199.*.*` / `2606:50c0:*` / `<user>.github.io` 即说明解析未就绪，
> 等待 DNS TTL（通常 5 分钟至 1 小时）再试。

### 步骤 2：在仓库根目录创建 `CNAME` 文件

内容**只有一行**，就是你的裸域（无 `https://`、无尾斜杠）：

```
quarkaudio-edit.com
```

提交后 GitHub 会自动检测并把仓库的 Pages 域名切换到该自定义域名。

### 步骤 3：启用 HTTPS

**Settings → Pages → Enforce HTTPS** 打勾。
GitHub 会通过 Let's Encrypt **自动**签发证书，需等待 10–60 分钟
（期间该选项可能是灰色不可点，属正常现象，等证书就绪后变为可点）。

### 步骤 4（可选）：在 Apex 域启用 www 重定向

若希望用户访问 `www.quarkaudio-edit.com` 时自动 301 到 `quarkaudio-edit.com`，
GitHub Pages 在 CNAME 文件只填裸域的情况下会自动启用此重定向，**无需额外配置**。

---

## 大文件处理：Git LFS 与外链

GitHub 对单文件 **100 MB**、仓库总量 **1 GB** 的软限制。大量 `.wav` 很容易超标。

### 策略 1：压缩音频

```bash
# 用 ffmpeg 把 wav 转 128 kbps 的 mp3（体积约 1/10）
ffmpeg -i input.wav -codec:a libmp3lame -b:a 128k output.mp3
```

然后在 `assets/js/data.js` 中把 `.wav` 改为 `.mp3`，HTML 的 `<audio>` 标签兼容。

### 策略 2：启用 Git LFS

```bash
# 安装 LFS
git lfs install

# 跟踪所有 wav
git lfs track "assets/audio/**/*.wav"
git add .gitattributes
git add .
git commit -m "track audio with LFS"
git push
```

⚠️ **注意**：GitHub 免费账户 LFS 每月流量仅 1 GB，访问量大时可能被限流。

### 策略 3：音频托管到外部 CDN（推荐大规模 demo）

把 `.wav` 上传到 Hugging Face Datasets / Google Cloud Storage / Cloudflare R2，
然后修改 `assets/js/data.js` 中的路径：

```javascript
// 原来
src: 'assets/audio/operations/add_01_src.wav',

// 改为
src: 'https://huggingface.co/datasets/<你的数据集>/resolve/main/add_01_src.wav',
```

Hugging Face 是学术项目首选（免费、无限流量、匿名可用）。

---

## 常见问题排查

### Q1：部署成功但页面 404

**检查项**：
- 仓库是否为 **Public**（私有仓库的 Pages 需要付费计划）
- Pages 设置里 Source 是否选择正确（Branch 或 Actions）
- `index.html` 是否在选中的 Source 根目录

### Q2：页面能加载但图片 / 音频 404

**原因**：路径大小写不匹配。Windows 文件系统大小写不敏感，Linux（GitHub Pages 运行在 Linux）**严格区分**大小写。

**解决**：统一文件名为小写，并检查 `index.html`、`data.js` 引用路径完全一致：

```powershell
# 列出所有图片和音频文件，确认大小写
cd "D:\02_Project\05_LLM_Audio\20260211-论文撰写\SAO-Instruct-0425\demo_page"
Get-ChildItem -Recurse -File assets\images,assets\audio | Select-Object Name
```

### Q3：推送被拒 `file exceeds 100MB`

某个音频或图片超过 100 MB。执行：

```bash
# 找出仓库中最大的文件
git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | awk '/^blob/ {print $3, $4}' | sort -n | tail -20
```

用策略 1 / 2 / 3 处理后，**从 git 历史完全移除**该文件：

```bash
git filter-repo --path path/to/huge_file.wav --invert-paths
git push origin main --force
```

（`git filter-repo` 需额外安装：`pip install git-filter-repo`）

### Q4：Workflow 运行失败 `HttpError: Not Found`

**Settings → Actions → General → Workflow permissions** 设为 **Read and write permissions**。

### Q5：CSS 样式不生效 / MathJax 公式不渲染

检查浏览器开发者工具 Console：
- 若提示 `Mixed Content`：页面是 HTTPS 但资源是 HTTP → Pages 已自动 HTTPS，外链 CDN 也应改 HTTPS
- 若提示 `CORS`：`<audio>` 的 `crossorigin` 属性可能缺失，一般保持默认即可

### Q6：部署后首屏白屏几秒

Pages 首次访问需冷启动 CDN 缓存，**属于正常现象**。第二次访问会很快。

---

## 部署前检查清单

在点击 "push" 之前，对照这份清单：

### 🎯 内容完整性
- [ ] 四张图片已放入 `assets/images/`（`Edit.png`、`QuarkAudio_edit.jpg`、`data_pipeline.jpg`、`GRPO_training.png`）
- [ ] 音频样本已放入对应子目录，命名与 `assets/js/data.js` 中的路径一致
- [ ] `index.html` 顶部 4 个按钮的 `href="#"` 已替换为真实 URL（或在双盲期保持 `#`）
- [ ] BibTeX 内容准确

### 🔒 双盲评审合规（若在投稿期）
- [ ] `.authors` 和 `.affiliations` 为 `Anonymous`
- [ ] 没有任何个人邮箱 / 主页链接
- [ ] 部署账号是新建的匿名账号
- [ ] 仓库 URL 中不含作者名字

### ⚡ 性能与体积
- [ ] 单个音频文件 < 10 MB（能用 mp3 就用 mp3）
- [ ] 总仓库体积 < 1 GB
- [ ] 图片已压缩（JPG 质量 85，PNG 用 TinyPNG 再压一次）

### 🌐 跨浏览器测试
- [ ] Chrome / Edge / Firefox / Safari 均正常
- [ ] 手机竖屏（< 600px）排版不破
- [ ] 音频播放器在所有浏览器均能播放

### 📋 SEO & 社交分享（锦上添花）
- [ ] `<title>` 标签准确
- [ ] `<meta name="description">` 填写了论文简介
- [ ] 可选：添加 Open Graph 标签（`og:image` 指向 `Edit.png`）以便推特 / 知乎分享时显示预览图

示例 `og:` 标签（加在 `index.html` 的 `<head>` 内）：

```html
<meta property="og:title" content="QuarkAudio-Edit: CoT-RAG for Audio Editing" />
<meta property="og:description" content="The first unified framework for general audio & speech editing with chain-of-thought reasoning." />
<meta property="og:image" content="https://<user>.github.io/quarkaudio-edit/assets/images/Edit.png" />
<meta property="og:url"   content="https://<user>.github.io/quarkaudio-edit/" />
<meta name="twitter:card" content="summary_large_image" />
```

---

## 🎉 部署后推广建议

1. **在论文 PDF 第一页脚注**加上 demo URL
2. **arXiv 描述**中附上 Project Page 链接
3. **在 Papers With Code、Hugging Face Spaces** 建立条目，互相引流
4. **Twitter/X** 发布 demo 视频 + 页面链接，@ 领域大牛
5. **Reddit r/MachineLearning** 的 `[P]` 或 `[R]` tag 发帖

---

## 📚 参考资源

- 官方文档：<https://docs.github.com/en/pages>
- Actions 部署教程：<https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages>
- Git LFS 文档：<https://git-lfs.com/>
- 双盲合规建议（ACL Rolling Review）：<https://aclrollingreview.org/anonymity>

---

**祝投稿顺利！** 如遇问题，可在本文末尾"常见问题排查"中定位，或检查 GitHub Actions 日志。
