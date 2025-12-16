# Water Consumption Analysis

A robust Flask-based web application designed to track daily water meter readings, calculate consumption, analyze costs, and detect abnormal usage spikes. This tool helps users monitor their water usage habits and manage expenses effectively.

## Tech Stack

This project is built using the following technologies:

- **Frontend:** HTML, CSS, JavaScript (Jinja2 Templates)
- **Backend:** Python (Flask)
- **Database:** SQLite (SQLAlchemy ORM)
- **Authentication:** Flask-Login for secure user session management

## Features

- **User Authentication:** 
  - Secure registration and login system.
  - Data isolation ensures users only see their own readings.
  
- **Consumption Tracking:** 
  - Easy interface to add daily meter readings.
  - Automatic calculation of daily consumption based on previous readings.
  - History view to manage and delete past records.

- **Smart Dashboard:** 
  - Visual summary of total consumption and average daily usage.
  - Recent activity feed.
  
- **Spike Detection:** 
  - Intelligent logic to flag abnormal usage spikes based on historical averages.
  - Helps in identifying potential leaks or unusual activity.

- **Cost Analysis:** 
  - Configurable tariff system (default value per liter).
  - Monthly cost calculation including estimated wastage costs for spike days.
  - Visual categorization of consumption (Low, Average, High).

## Installation and Setup

Follow these steps to get the project running on your local machine:

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/Aryan1337x/Water-Consumption-Analysis.git
    cd Water
    ```

2.  **Install Dependencies**
    Ensure you have Python installed. It is recommended to use a virtual environment.
    ```bash
    pip install flask flask-sqlalchemy flask-login
    ```

3.  **Run the Application**
    Navigate to the project root and execute the run script:
    ```bash
    python run/run.py
    ```

4.  **Access the App**
    Open your web browser and go to:
    `http://127.0.0.1:5000`

## Everyday Use

1.  **Register/Login:** Start by creating an account.
2.  **Add Readings:** Go to the "Add Reading" section and input the date and the value from your water meter.
3.  **Check Dashboard:** The home page will update with your usage statistics.
4.  **Analyze Costs:** Visit the "Cost Analysis" page to update your water tariff and view detailed cost breakdowns.

## Credits

Made by Aryan  
Instagram: [@aryan.skid](https://www.instagram.com/aryan.skid/)


