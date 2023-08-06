# Base Image
FROM alpine:latest

# Bash setup
RUN apk add --no-cache bash
RUN sed -i 's/\/bin\/ash/\/bin\/bash/g' /etc/passwd

# Node.js Setup
RUN apk add --update nodejs npm

# Create app directory
WORKDIR /root/workspace

# Expose Ports
EXPOSE 3000
RUN 
