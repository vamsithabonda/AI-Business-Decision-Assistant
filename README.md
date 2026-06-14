# AI Business Decision Assistant

## Overview

AI Business Decision Assistant is a Flask-based business analytics dashboard that helps organizations analyze sales performance, customer trends, product performance, and business insights using AI.

The system uses MySQL as the database backend and integrates AI-powered recommendations for better business decision-making.

---

## Features

* User Login & Authentication
* Interactive Business Dashboard
* Sales Analytics
* Region-wise Sales Analysis
* Top Products Analysis
* Top Customers Analysis
* AI-Powered Business Insights
* Data Explorer with Search & Filters
* PDF Business Report Generation
* Excel Data Export
* Dark Mode Support
* Dynamic Data Updates from MySQL

---

## Technologies Used

### Backend

* Python
* Flask
* Pandas
* MySQL

### Frontend

* HTML
* CSS
* JavaScript

### AI Integration

* Groq API
* Llama 3.3 70B Versatile

### Reporting

* ReportLab
* OpenPyXL

### Visualization

* Matplotlib

---

## Database

Database: MySQL

Table: train

The dashboard dynamically reads business data directly from MySQL and updates all analytics automatically.

---

## Installation

### Clone Repository

```bash
git clone <repository-link>
cd project-folder
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure MySQL

Create a database:

```sql
CREATE DATABASE businessdb;
```

Import the train dataset into the train table.

### Run Application

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

---

## Project Modules

### Dashboard

Displays KPIs including:

* Total Sales
* Total Customers
* Total Orders
* Total Profit
* Sales Growth

### Analytics

Provides:

* Region Sales Chart
* Category Distribution
* Product Performance Trends

### AI Insights

Generates business recommendations using AI.

### Data Explorer

Provides:

* Search functionality
* Region filters
* Category filters
* Date filters

### Reports

* PDF Report Download
* Excel Data Export

---

## Future Enhancements

* Predictive Sales Forecasting
* Advanced AI Analytics
* Real-Time Dashboards
* Role-Based Access Control
* Cloud Deployment

---

## Author

Developed as an AI-Powered Business Analytics Project using Flask, MySQL, and Generative AI.
