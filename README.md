# Restaurant App - Setup Instructions

## 1. Prerequisites
* **MySQL Server** (Version 8.0 or higher is recommended)

## 2. Database Setup
1.  Open your MySQL management tool (e.g., MySQL Workbench).
2.  Run the provided SQL script located at: `dist/export.sql`
    * *This will create the `restaurant` database along with all necessary tables, triggers, and views.*

## 3. Configuration
1.  Navigate to the configuration folder: `dist/configuration_files/`
2.  Open the `config.ini` file in a text editor.
3.  Update the values to match your local MySQL server credentials:
    ```ini
    [mysql]
    host = YOUR_HOST_ADDRESS  ; Enter your server address here (e.g., localhost)
    database = restaurant     ; Do NOT change this value
    user = YOUR_USERNAME
    password = YOUR_PASSWORD
    ```
    * *The app uses these settings to establish the database connection.*

## 4. Running the Application
* Launch the application by running: `dist/App.exe`
