# 📈 Automated Daily NSE Report Generator (NSE Bot)

![Status](https://img.shields.io/badge/Status-Operational-success?style=for-the-badge&logo=statuspage)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B?style=for-the-badge&logo=streamlit)
![Selenium](https://img.shields.io/badge/Selenium-4.10%2B-43B02A?style=for-the-badge&logo=selenium)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

## 📖 Abstract

The **Automated Daily NSE Report Generator** is a robust robotic process automation (RPA) tool designed to streamline the acquisition and distribution of financial data from the National Stock Exchange (NSE) of India. By leveraging Selenium for headless browser automation and Streamlit for a modern, responsive user interface, this application autonomously fetches critical equity reports (including CM-Bhavcopy and F&O data), performs data validation, and dispatches them via a secure SMTP relay to stakeholders. This project mitigates manual data retrieval errors and ensures timely access to market data.

---

## 📑 Table of Contents

- [Abstract](#-abstract)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Technology Stack](#-technology-stack)
- [Installation & Setup](#-installation--setup)
- [Configuration](#-configuration)
- [Usage Guide](#-usage-guide)
- [Project Structure](#-project-structure)
- [Future Enhancements](#-future-enhancements)
- [License](#-license)

---

## 🚀 Key Features

*   **Autonomous Data Extraction**: Navigates the dynamic NSE portal to identify, select, and download daily reports without human intervention.
*   **Intelligent Retry Mechanism**: Implements exponential backoff and retry logic to handle network instability and portal timeouts effectively.
*   **Secure Email Dispatch**: Integrated SMTP client with TLS encryption to securely deliver reports and execution logs to configured recipients.
*   **Cron-based Scheduling**: Built-in `APScheduler` integration allows for precise, automated daily execution at user-defined intervals.
*   **Real-time Monitoring Dashboard**: A comprehensive "Deep Fintech Dark" themed UI provides live execution logs, system status, and manual control overrides.
*   **Data Integrity Checks**: Validates downloaded files to ensure completeness before distribution.

---

## 🏗 System Architecture

The application is built on a modular architecture:

1.  **Frontend Layer**: Built with **Streamlit**, providing a reactive interface for configuration, monitoring, and manual control.
2.  **Automation Engine**: **Selenium WebDriver** acts as the core engine, simulating user interactions to bypass basic bot detection and handle dynamic content.
3.  **Orchestration Layer**: Managing the workflow state, error handling, and linking the automation engine with the notification system.
4.  **Notification Service**: A dedicated module using Python's `smtplib` to handle attachment encoding and secure email transmission.

---

## 💻 Technology Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Language** | Python 3.10+ | Core logic and scripting. |
| **Frontend** | Streamlit | Rapid application development for the dashboard. |
| **Automation** | Selenium | Web scraping and browser automation. |
| **Scheduling** | APScheduler | Advanced background job scheduling. |
| **Data Handling** | Pandas | CSV processing and validation. |
| **UI Components** | Streamlit Option Menu | Enhanced sidebar navigation. |

---

## � Installation & Setup

### Prerequisites
- Windows 10/11, macOS, or Linux.
- Python 3.10 or higher installed.
- Google Chrome browser installed.

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/nse-report-generator.git
cd nse-report-generator
```

### Step 2: Create a Virtual Environment (Recommended)
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

---

## ⚙ Configuration

1.  **Launch the Application**:
    ```bash
    streamlit run Streamlit.py
    ```

2.  **Email Configuration**:
    - Navigate to the **Email Setup** tab in the dashboard.
    - Enter your **Sender Email** and **App Password** (Required for Gmail).
    - *Note: Ensure 2-Factor Authentication is enabled on your Google Account to generate an App Password.*

3.  **Local Storage**:
    - The application automatically creates a directory at `C:\NSE\nsefiles` for storing downloaded reports. Ensure your user account has write permissions for this path.

---

## ▶ Usage Guide

### Manual Execution
For ad-hoc report retrieval:
1.  Open the dashboard (`http://localhost:8501`).
2.  Navigate to **NSE Downloader**.
3.  Click **START PROCESS**.
4.  Monitor the **System Logs** tab for real-time progress.

### Automated Scheduling
To set up daily runs:
1.  Navigate to the **Schedule** tab.
2.  Select the desired **Date** and **Time**.
3.  Click **Add to Queue**.
4.  *Requirement: The host machine must remain powered on, and the application terminal must be open.*

---

## 📂 Project Structure

```text
nse-report-generator/
├── Streamlit.py            # Main application entry point & UI
├── main.py                 # Core workflow orchestrator
├── Data_retrieval.py       # Selenium automation logic
├── notification.py         # Email notification service
├── mail_setup.py           # Email configuration & OTP utilities
├── Scheduling.py           # Job scheduler management
├── requirements.txt        # Project dependencies
└── README.md               # Project documentation


## 🔮 Future Enhancements

- [ ] **Cloud Deployment**: Containerize with Docker for deployment on AWS/Azure.
- [ ] **Database Integration**: Store historical data in PostgreSQL/MySQL for trend analysis.
- [ ] **Data Visualization**: Add charts to the dashboard to visualize market trends from downloaded reports.
- [ ] **API Support**: Expose a REST API for triggering downloads externally.



## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

