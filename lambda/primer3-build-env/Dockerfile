FROM amazonlinux:2.0.20220719.0
LABEL maintainer="Mutation Maker https://github.com/Merck/Mutation_Maker"

# Basic Linux tools
RUN yum update -y && \
    yum -y install yum-utils && \
    yum -y groupinstall development && \
    yum -y install zlib-devel openssl-devel bzip2 bzip2-devel readline-devel && \
    yum -y install vim && \
    yum -y install wget && \
    yum -y install gcc

WORKDIR /build_dir

CMD ["/bin/bash"]
