FROM amazonlinux:2023
LABEL maintainer="Mutation Maker https://github.com/Merck/Mutation_Maker"

# Basic Linux tools and Python 3.9
RUN yum update -y && \
    yum -y install yum-utils && \
    yum -y groupinstall development && \
    yum -y install zlib-devel openssl-devel bzip2 bzip2-devel readline-devel sqlite-devel && \
    yum -y install vim && \
    yum -y install wget && \
    yum -y install gcc && \
    yum -y install python3 python3-pip python3-devel

# Set locale
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Create symbolic link for python
RUN ln -sf /usr/bin/python3 /usr/bin/python

# Upgrade pip to avoid packaging conflicts with system packages
RUN python3 -m pip install --upgrade pip setuptools wheel

# Install Python dependencies
COPY requirements.txt /var/tmp/
RUN python3 -m pip install -r /var/tmp/requirements.txt

RUN mkdir -p /lambda

COPY . /lambda

WORKDIR /lambda

EXPOSE 3001

CMD /bin/bash
