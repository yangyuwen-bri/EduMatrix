import os
from huggingface_hub import snapshot_download

# 下载目录
local_dir = "models/text2vec-base-chinese"

print(f"开始下载模型到本地目录: {local_dir} ...")
print("请确保你的 VPN 已开启 (全局模式最佳)")

snapshot_download(
    repo_id="shibing624/text2vec-base-chinese",
    local_dir=local_dir,
    local_dir_use_symlinks=False,  # 重要：不使用软链接，方便 Docker Copy
    resume_download=True
)

print("\n✅ 模型下载完成！")
print("现在你可以重新执行 docker build 命令了。")
