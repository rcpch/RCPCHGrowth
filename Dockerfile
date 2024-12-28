FROM python:3.12

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Create a virtual environment
RUN python -m venv /app/venv

# Upgrade pip and install the dependencies in the virtual environment
RUN /app/venv/bin/pip install --upgrade pip
RUN /app/venv/bin/pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set the entrypoint to use the virtual environment's Python interpreter
CMD ["python3"]