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

1. Run the setup script **using `source`**:

```bash
source run.sh
```

* This script will:

  * Create a virtual environment (`scrape/`) if it doesn’t exist
  * Activate the virtual environment
  * Upgrade `pip` and install all dependencies from `requirements.txt`

2. Verify activation:

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


2. Verify activation:

```cmd
where python   # Should point to scrape\Scripts\python.exe
pip list       # Should show installed packages
```

---

## 4. Running the Scraper

Once the virtual environment is activated, replace the below code with the one in examples.txt file

```bash
python scraper/your_scraper_file.py
```

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

---

This README ensures **macOS/Linux and Windows users can easily set up and activate the environment**, and explains why macOS/Linux requires `source` for proper activation.
