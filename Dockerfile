# Stage 1: Use Amazon Linux to install dependencies and create ZIP file
FROM amazonlinux:2 as builder

# Install Python, zip utility, gcc, and Python development headers
RUN yum install -y python3-pip zip gcc python3-devel

# Set the working directory
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip3 install -r requirements.txt -t .

# Copy the application files into the container
COPY allowed_food.py database.py main.py models.py pork.py/

# Create a ZIP file of the application and its dependencies
RUN zip -r9 /app.zip .

# Stage 2: Use AWS Lambda Python base image to build the final image
FROM amazon/aws-lambda-python:3.8

# Install the unzip utility
RUN yum install -y unzip

# Set the working directory to the Lambda task root
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy the ZIP file from the builder stage
COPY --from=builder /app.zip .

# Unzip the application files
RUN unzip /app.zip

# Set the command for the Lambda function
CMD ["main.handler"]

# Instructions to build the Docker image and extract the ZIP file
# docker build -t lambda-deployment .
# docker run --rm -v "$PWD:/output" lambda-deployment cp /app.zip /output/
