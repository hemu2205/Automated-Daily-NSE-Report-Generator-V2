import Data_retrieval as d
import duplicates_handler as dh
import time
import os 
from datetime import date
import logging
from csv_validation import FilePath,run_validations
from segregation import segregate
from notification import send_mail as s

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("nse_report_downloader.log"),
        logging.StreamHandler()
    ]
)

download_directory = "C:\\NSE\\nsefiles"

def main():
    driver = None
    try:
        logging.info("=== STARTING NEW RUN ===")
        status = "Failed"
        num_downloaded = 0 # Default if everything fails
        
        # Initialize Driver Locally
        logging.info("Initializing browser driver...")
        driver = d.init_driver()
        
        d.load_nse_reports_page(driver)
        # time.sleep(2) # Reduced sleep
        
        flag, report_names = d.select_reports(driver)
        logging.info(f"Reports selection status: {flag}, Count: {len(report_names)}")
        
        # time.sleep(2)
        d.download_reports(driver, flag)
        
        download_success = False
        if flag:
            logging.info("Waiting for downloads...")
            # Increased timeout to 120s just in case network is slow
            download_success = d.wait_for_downloads(report_names, download_directory, 120)
            logging.info(f"Download Success Status: {download_success}")
            
            if not download_success:
                logging.error("Downloads not verified. Aborting protocol.")
                return # Exit early
        else:
            logging.warning("No reports selected/found. Aborting protocol.")
            return

        logging.info("Processing downloaded files...")
        today = date.today().strftime("%d%m%y")
        today_folder = os.path.join(download_directory,today)
        
        if not os.path.exists(today_folder):
             logging.error(f"Download folder {today_folder} does not exist.")
             return

        if dh.handle_redundant_files(today_folder):
            logging.info("All file successfully verified for duplicates")
        else:
            # If duplicates handling fails, we might still want to proceed or warn
            logging.warning("Duplicate verification returned False.")
            
        num_downloaded = len(os.listdir(today_folder))
        logging.info(f"Number of files downloaded: {num_downloaded}")
        
        csv_files = segregate(today_folder)
        logging.info(f"Segregation complete. CSV folder: {csv_files}")

        if csv_files and os.path.exists(csv_files):
            for file_name in os.listdir(csv_files):
                file_path = os.path.join(csv_files, file_name)
                if os.path.isfile(file_path):
                    file_obj = FilePath(file_path)
                    if not run_validations(file_obj):
                        logging.warning(f"Validation failed for: {file_name}")
        
        status = "success"
        logging.info("Protocol finished successfully.")
            
    except Exception as e:
        logging.critical(f"(Main) Critical error occurred: {e}", exc_info=True)
    finally:
        logging.info(f"Sending status email: {status}")
        try:
            s(status, num_downloaded, num_downloaded, 0)
        except Exception as mail_error:
            logging.error(f"Error sending mail: {mail_error}")
            
        if driver:
            logging.info("Closing driver...")
            try:
                driver.quit()
            except Exception as e:
                logging.warning(f"Error closing driver: {e}")
        logging.info("=== RUN COMPLETE ===")

if __name__ == "__main__":
    main()