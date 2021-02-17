FROM amazonlinux:2018.03.0.20200318.1
LABEL maintainer="Mutation Maker https://github.com/Merck/Mutation_Maker"

# Basic Linux tools
RUN yum update -y && \
    yum -y install yum-utils && \
    yum -y groupinstall development && \
    yum -y install zlib-devel openssl-devel bzip2 bzip2-devel readline-devel sqlite3-dev && \
    yum -y install vim && \
    yum -y install wget && \
    yum -y install gcc && \
    yum -y install python36

# Set locale
ENV LC_ALL=en_US.utf8
ENV LANG=en_US.utf8

# Install Pyenv
RUN git clone https://github.com/yyuu/pyenv.git /root/.pyenv && \
    echo 'export PATH="/root/.pyenv/bin:$PATH"' >> /root/.bashrc && \
    echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> /root/.bashrc && \
    echo 'eval "$(pyenv init -)"' >> /root/.bashrc

# Install Python 3.6 using Pyenv
RUN source /root/.bashrc && \
    pyenv install 3.6.1 && \
    pyenv global 3.6.1

# Install Python dependencies
COPY requirements.txt /var/tmp/
RUN python3 -m pip install -r /var/tmp/requirements.txt

RUN mkdir -p /lambda

COPY . /lambda

WORKDIR /lambda

EXPOSE 3001

CMD /bin/bash
