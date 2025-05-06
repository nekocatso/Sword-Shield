FROM python:3.13.2-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


COPY ./ /opt/Sword_Shield
WORKDIR /opt/Sword_Shield

RUN echo "deb http://mirrors.ustc.edu.cn/debian bullseye main\ndeb http://mirrors.ustc.edu.cn/debian bullseye-updates main" > /etc/apt/sources.list \
 && apt-get update && apt-get install -y curl build-essential \
 && curl https://sh.rustup.rs -sSf | sh -s -- -y \
 && . "$HOME/.cargo/env" \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.cargo/bin:${PATH}"

RUN python -m pip install --upgrade pip -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com \
 && python -m pip install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

RUN apt-get update &&   apt-get -y install libnss3 xvfb gconf-service libasound2 libatk1.0-0 libc6 libcairo2 libcups2   libdbus-1-3 libexpat1 libfontconfig1 libgbm1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0   libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1   libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1   libxtst6 ca-certificates fonts-liberation libnss3 lsb-release xdg-utils wget vim libgomp1 \
 && apt-get clean && rm -rf /var/lib/apt/lists/*