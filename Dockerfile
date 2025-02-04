# Use an official Python image as the base
FROM python:3.12-slim

# Install Poetry without root privileges
RUN pip install --user poetry

# Set the working directory to /src
WORKDIR /src

# Copy the current directory contents into the container at /src
COPY . /src

# Install dependencies using Poetry
RUN poetry install --no-interaction

# Expose the port that the application will use
EXPOSE 8501

# Set the entrypoint to run the Streamlit application
ENTRYPOINT ["poetry", "run", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]