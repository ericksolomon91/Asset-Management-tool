# Project Title
Asset Management Tool

## Description
This project is an Asset Management Tool built using Flask. It allows users to manage spare parts, create delivery receipts, and track recently added parts.

## Using Docker
Docker is a platform that allows you to automate the deployment of applications inside lightweight, portable containers. Containers package your application and its dependencies together, ensuring that it runs consistently across different environments.


### How to Use Docker with This Application
1. **Build the Docker Image**: Run the following command in the terminal:
   ```bash
   docker-compose build
   ```
   This command reads the `Dockerfile` and installs the necessary dependencies listed in `requirements.txt`.

2. **Run the Application**: Start the application and the PostgreSQL database with:
   ```bash
   docker-compose up
   ```
   This command will run your Flask application in a Docker container, making it accessible at `http://localhost:5001`.

3. **Stopping the Application**: To stop the application, you can use:
   ```bash
   docker-compose down
   ```

## Installation Instructions (Non-Docker Approach)
To run this project without Docker, you will need to install the following tools and plugins:

- **Python**: Make sure you have Python installed on your machine.
- **Create a Virtual Environment**:
  ```bash
  sudo apt-get install python3-venv
  python3 -m venv venv
  source venv/bin/activate
  ```
- **Flask**: Install Flask using pip:
  ```bash
  pip install Flask
  ```
- **Flask-SQLAlchemy**: Install Flask-SQLAlchemy using pip:
  ```bash
  pip install Flask-SQLAlchemy
  ```
- **Flask-WTF**: Install Flask-WTF using pip:
  ```bash
  pip install Flask-WTF
  ```
- **PostgreSQL**: Ensure you have PostgreSQL installed and running.

## Running the Application Automatically
To ensure that your Flask application runs automatically after being installed on an Ubuntu server VM, you can create a systemd service. This service will start the application on boot and allow you to control it easily.

### Steps to Create a Systemd Service
1. In `/etc/systemd/system/` create a service file named `myflaskapp.service`  with the following content:
   ```ini
   [Unit]
   Description=My Flask App
   After=network.target

   [Service]
   User=yourusername
   Group=www-data
   WorkingDirectory=/path/to/your/app
   Environment="PATH=/path/to/your/venv/bin"
   ExecStart=/usr/local/bin/docker-compose up

   [Install]
   WantedBy=multi-user.target
   ```

2. Reload the systemd daemon:
   ```bash
   sudo systemctl daemon-reload
   ```

3. Enable the service to start on boot:
   ```bash
   sudo systemctl enable myflaskapp
   ```

4. Start the service:
   ```bash
   sudo systemctl start myflaskapp
   ```

5. Check the status of the service:
   ```bash
   sudo systemctl status myflaskapp
   ```

## Usage
The application will be available at `http://localhost:5001` once it is running.

## Contributing
If you would like to contribute to this project, please fork the repository and submit a pull request.

## License
This project is licensed under the MIT License.
