FROM vault.habana.ai/gaudi-docker/1.24.1/ubuntu24.04/habanalabs/pytorch-installer-2.11.0:latest

LABEL maintainer="Gaudi Training Base"
LABEL description="Gaudi2 8-Card Multimodal LLM Training Environment (Synapse 1.24.1, PyTorch 2.11.0)"

WORKDIR /workspace

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    wget \
    curl \
    vim \
    tmux \
    htop \
    && rm -rf /var/lib/apt/lists/*

# 锁定依赖版本
RUN pip install --no-cache-dir \
    optimum-habana==1.21.1 \
    transformers==4.55.0 \
    peft==0.11.1 \
    accelerate==1.10.1 \
    tensorboard \
    pillow \
    einops

# 安装Habana DeepSpeed分支
RUN pip install --no-cache-dir \
    git+https://github.com/HabanaAI/DeepSpeed.git@1.21.0

# 设置工作目录
WORKDIR /workspace/gaudi-training-base

CMD ["/bin/bash"]
