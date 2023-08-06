# Base Image
FROM python:3.11-slim

# Install dos2unix
RUN apt-get update && apt-get install -y dos2unix

# Create app directory
WORKDIR /root/workspace

# # Copy in .bashrc
# COPY .devcontainer/.bashrc /root/.bashrc
# COPY .devcontainer/.bash_aliases /root/.bash_aliases
# COPY .devcontainer/.bash_functions /root/.bash_functions

# Expose Ports
EXPOSE 3000