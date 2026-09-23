FROM vault.habana.ai/gaudi-docker/1.24.1/ubuntu24.04/habanalabs/pytorch-installer-2.11.0:latest

# 训练所需的环境变量
ENV PT_HPU_LAZY_MODE=0
ENV PT_HPU_RECIPE_CACHE_CONFIG=/root/.cache/habana/recipe_cache,true,1024,false
ENV PT_HPU_ENABLE_LAZY_COLLECTIVES=true
ENV OMPI_MCA_btl_vader_single_copy_mechanism=none

# 锁住 Habana 基础镜像自带的包，防止 pip 重装破坏 HPU 支持
RUN printf '%s\n' \
    'torch==2.11.0a0+git009b5f6' \
    'torchvision==0.26.0+cpu' \
    > /tmp/constraints.txt

# 一键安装，pip 自动解析依赖
RUN pip install -c /tmp/constraints.txt \
    transformers==5.8.0 \
    peft==0.18.1 \
    trl==0.22.2 \
    datasets==4.0.0 \
    accelerate==1.7.0 \
    fastapi \
    uvicorn \
    fire \
    gradio \
    hf-transfer \
    matplotlib \
    modelscope \
    omegaconf \
    sse-starlette \
    tiktoken \
    torchdata \
    tyro \
    sentencepiece

# 单独安装 CPU 版 torchaudio（必须从 CPU 源，否则会装到 CUDA 版）
RUN pip install --no-deps torchaudio==2.11.0 \
    --extra-index-url https://download.pytorch.org/whl/cpu

WORKDIR /workspace

# 验证核心依赖
RUN python -c "import transformers; print('transformers:', transformers.__version__)" && \
    python -c "import torchaudio; print('torchaudio:', torchaudio.__version__)" && \
    python -c "import peft, trl, datasets, accelerate, gradio, fastapi; print('training deps OK')"
