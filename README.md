# procounsel-scraper

This repository contains a Python scraper that pulls data from a website. The setup is designed to make it easy for both macOS/Linux and Windows users to get started with **one command**.

---

## 1. Prerequisites

* **Python 3.9+** installed
* **Git** installed (for cloning the repo)

Check Python version:

```bash
python3 --version    # macOS/Linux
python --version     # Windows
```

---

## 2. Clone the Repository

```bash
git clone https://github.com/your-username/procounsel-scraper.git
cd procounsel-scraper
```

---

## 3. Setup Virtual Environment and Install Dependencies

### macOS/Linux

1. Make the shell script executable (first time only):

```bash
chmod +x run.sh
```

2. Run the setup script **using `source`**:

```bash
source run.sh
```

> ⚠️ Important: On macOS/Linux, you must use `source` to keep the virtual environment active in your terminal. Using `./run.sh` will not keep it activated.

* This script will:

  * Create a virtual environment (`scrape/`) if it doesn’t exist
  * Activate the virtual environment
  * Upgrade `pip` and install all dependencies from `requirements.txt`

3. Verify activation:

```bash
which python   # Should point to scrape/bin/python
pip list       # Should show installed packages
```

---

### Windows (Command Prompt)

1. Run the batch script:

```cmd
run.bat
```

* This will:

  * Create a virtual environment (`scrape\`) if it doesn’t exist
  * Activate the virtual environment
  * Upgrade `pip` and install dependencies from `requirements.txt`

2. After the script runs, the environment is active in that terminal session.

3. Verify activation:

```cmd
where python   # Should point to scrape\Scripts\python.exe
pip list       # Should show installed packages
```

---

## 4. Running the Scraper

Once the virtual environment is activated:

```bash
python scraper/your_scraper_file.py
```

Replace `your_scraper_file.py` with the actual script name.

---

## 5. Notes

* The **virtual environment** is stored in the `scrape/` directory
* To **reactivate** the environment in a new terminal:

**macOS/Linux:**

```bash
source scrape/bin/activate
```

**Windows (cmd):**

```cmd
scrape\Scripts\activate.bat
```

**Windows (PowerShell):**

```powershell
scrape\Scripts\Activate.ps1
```

* To **deactivate** the environment:

```bash
deactivate
```

---

## 6. Updating Dependencies

If you add new packages:

```bash
pip install new_package
pip freeze > requirements.txt
```

Then others can install the new packages via:

```bash
source run.sh      # macOS/Linux
run.bat            # Windows
```

---

This README ensures **macOS/Linux and Windows users can easily set up and activate the environment**, and explains why macOS/Linux requires `source` for proper activation.
