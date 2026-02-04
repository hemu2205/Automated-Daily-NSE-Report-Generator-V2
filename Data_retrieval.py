import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime as t
import time
import random
import os
import zipfile
import shutil

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("nse_report_downloader.log"),
        logging.StreamHandler()
    ]
)

download_directory = os.path.join(os.getcwd(), "nsefiles")

def init_driver():
    """Initialize and return a new Chrome driver instance."""
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--start-maximized")
        # Add headless if you want to avoid UI popping up, but for debugging visual is good.
        # chrome_options.add_argument("--headless") 
        chrome_options.add_argument("Mozilla/5.0")
        chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        chrome_options.add_experimental_option("prefs", {
            "download.default_directory": download_directory,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        })
        
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        logging.critical(f"Failed to initialize driver: {e}")
        raise e

def retry_operation(func, driver, retries=3, base_delay=5):
    for attempt in range(retries):
        try:
            return func()
        except Exception as e:
            logging.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                delay = random.uniform(base_delay, base_delay + 2)
                logging.info(f"Retrying in {delay:.2f} seconds")
                time.sleep(delay)
            else:
                logging.error("Max retries reached.")
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass
                raise e

def load_nse_reports_page(driver):
    logging.info("Navigating to NSE Reports page...")
    retry_operation(
        lambda: driver.get("https://www.nseindia.com/all-reports"),
        driver,
        retries=3,
        base_delay=5
    )
    retry_operation(
        lambda: WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "cr_equity_daily_Current"))
        ),
        driver,
        retries=3,
        base_delay=5
    )
    logging.info("Page loaded successfully.")


def select_reports(driver):
    try:
        logging.info("Selecting reports...")
        container = retry_operation(
            lambda: WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, "cr_equity_daily_Current"))
            ),
            driver,
            retries=3,
            base_delay=5
        )
        reports = container.find_elements(By.CSS_SELECTOR, ".reportsDownload")
        report_names = []
        flag = False
        
        if not reports:
            logging.warning("No report elements found in container.")
            return False, []

        for report in reports:
            try:
                report_name = report.find_element(By.CLASS_NAME, "reportCardSegment").text
                logging.info(f"Found report: {report_name}")
                report_names.append(report_name)
                
                # Scroll to it
                checkbox = report.find_element(By.XPATH, ".//label[@role='checkbox']")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
                time.sleep(0.2)
                
                # Click it
                driver.execute_script("arguments[0].click();", checkbox)
                logging.info(f"Selected: {report_name}")
                flag = True
            except Exception as e:
                logging.warning(f"Error selecting report item: {e}")
        
        return flag, report_names
    except Exception as e:
        logging.error(f"Error accessing reports container: {e}")
        return False, []


def download_reports(driver, flag):
    if flag:
        try:
            logging.info("Initiating download...")
            multi_download = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.ID, "MultiDwnld"))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", multi_download)
            time.sleep(1) # Small pause before click
            driver.execute_script("arguments[0].click();", multi_download)
            logging.info("Multi Download button clicked.")
        except Exception as e:
            logging.error(f"Failed to click download button: {e}")
    else:
        logging.info("No reports selected to download.")


def wait_for_downloads(filenames, download_dir=download_directory, timeout=60):
    """
    Waits for a zip file to appear in the download directory and extracts it.
    Returns True if successful, False otherwise.
    """
    try:
        if not os.path.exists(download_dir):
            os.makedirs(download_dir, exist_ok=True)

        logging.info("Waiting for zip file download...")
        zip_file_path = None
        end_time = time.time() + timeout
        
        # Poll for zip file
        while time.time() < end_time:
            files = os.listdir(download_dir)
            # Filter for .zip and ignore partial downloads (.crdownload)
            zips = [f for f in files if f.endswith(".zip")]
            if zips:
                # Get the most recent zip if multiple
                latest_zip = max([os.path.join(download_dir, f) for f in zips], key=os.path.getctime)
                # Ensure it's not being written to (size > 0 and accessible)
                try:
                    if os.path.getsize(latest_zip) > 0:
                        zip_file_path = latest_zip
                        break
                except OSError:
                    pass # File locked or busy
            time.sleep(1)
            
        if not zip_file_path:
            logging.error(f"Download timed out after {timeout} seconds. No Zip file found.")
            return False

        logging.info(f"Found zip file: {zip_file_path}")
        logging.info("(data_retrieval) In Extraction Process")
        
        today = t.today().strftime("%d%m%y")
        extraction_dir = os.path.join(download_dir, today)
        logging.info(f"(data_retrieval) Extraction directory path: {extraction_dir}")
        
        if os.path.exists(extraction_dir):
            shutil.rmtree(extraction_dir) # Clean existing for fresh run
        os.makedirs(extraction_dir, exist_ok=True)

        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(extraction_dir)
            extracted_files = set(os.path.basename(f) for f in zip_ref.namelist())

        missing_files = [name for name in filenames if name not in extracted_files]
        if missing_files:
            logging.warning(f"Missing files in zip: {missing_files}")
        else:
            logging.info("All files downloaded and verified successfully.")
        
        # Cleanup zip
        try:
            os.remove(zip_file_path)
        except Exception as e:
            logging.warning(f"Could not delete zip file: {e}")
            
        return True
    
    except Exception as e:
        logging.error(f"Unexpected error during download verification: {e}")
        return False