FROM ubuntu

ENV TZ=Asia/Tokyo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && \
  apt-get install -y \
  python3-opencv \
  libopencv-dev \
  ghostscript \
  libsm-dev \
  python3 \
  python3-pip

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN python3 -m pip install -r requirements.txt

COPY ./ /app

WORKDIR /app/src

CMD ["python3", "main.py"]
