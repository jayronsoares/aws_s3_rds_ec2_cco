## Cloud Metrics Dashboard

The Cloud Metrics Dashboard is a Flask web application that allows users to monitor and visualize metrics from Amazon Web Services (AWS) resources. It fetches data from AWS CloudWatch for Amazon S3, Amazon RDS, and Amazon EC2 services, and displays the metrics in a tabular format.

## Features

- Displays metrics from Amazon S3, Amazon RDS, and Amazon EC2 services.
- Metrics include S3 bucket usage, RDS instance performance, and EC2 instance utilization.
- Metrics are fetched from AWS CloudWatch using the Boto3 library.
- Fetched data is stored in a PostgreSQL database for historical analysis.

## Prerequisites

- Python 3.x installed.
- AWS account with appropriate permissions for CloudWatch access.
- PostgreSQL database to store fetched metrics.
- Environment variables set in a `.env` file for AWS credentials and database connection.

## Installation

1. Clone or download the project repository from GitHub.

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install flask boto3 psycopg2-binary python-dotenv
   ```

4. Create a `.env` file in the project directory and add your AWS credentials, database URL, and resource IDs:
   ```
   AWS_ACCESS_KEY_ID=your-aws-access-key-id
   AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
   DB_URL=your-postgresql-database-url
   S3_BUCKET_NAME=your-s3-bucket-name
   RDS_INSTANCE_ID=your-rds-instance-id
   EC2_INSTANCE_ID=your-ec2-instance-id
   ```

5. Run the Flask app:
   ```bash
   python app.py
   ```

6. Access the dashboard in your web browser by navigating to `http://127.0.0.1:5000/`.

## Usage

- The dashboard provides a visual representation of metrics from Amazon S3, RDS, and EC2.
- Metrics are fetched from AWS CloudWatch and displayed in tables.
- Data is stored in a PostgreSQL database for historical tracking and analysis.

## Conclusion

The Cloud Metrics Dashboard provides a convenient way to monitor and visualize metrics from AWS resources. By fetching and storing data, users can gain insights into resource utilization and historical trends for better resource management and optimization.
