# Windows Installation & Setup Guide

Complete step-by-step guide for installing and running the Brand Visibility Intelligence project on Windows using PowerShell in VS Code.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Project Structure Overview](#project-structure-overview)
3. [Installation Steps](#installation-steps)
4. [Running the Project](#running-the-project)
5. [Detailed Explanations](#detailed-explanations)
6. [Troubleshooting](#troubleshooting)
7. [Using the Dashboard](#using-the-dashboard)

---

## Prerequisites

### 1. **Python Installation**

You need Python 3.10 or higher. Windows doesn't come with Python pre-installed.

**Steps:**

1. Visit [python.org](https://www.python.org/downloads/)
2. Download Python 3.12 (or 3.10+)
3. Run the installer
4. **IMPORTANT**: Check the box that says "Add Python to PATH" ✓
5. Click "Install Now"
6. After installation completes, click "Disable path length limit" when prompted

**Verify Installation:**

Open PowerShell and run:

```powershell
python --version
pip --version
```

You should see something like:
```
Python 3.12.x
pip 24.x
```

### 2. **Visual Studio Code**

1. Download from [code.visualstudio.com](https://code.visualstudio.com/)
2. Run the installer
3. During installation, check:
   - ✓ "Add to PATH"
   - ✓ "Open with Code"
4. Install the **Python Extension** (Ctrl+Shift+X → search "Python" → install Microsoft's Python extension)

### 3. **Git** (Optional but recommended)

1. Download from [git-scm.com](https://git-scm.com/download/win)
2. Run installer with default settings

---

## Project Structure Overview

Understanding the project layout helps you know where things are:

```
Brand/
├── src/brand_visibility/           # Main source code
│   ├── pipeline.py                 # Data processing pipeline
│   ├── config.py                   # Configuration settings
│   ├── dashboard/app.py            # Streamlit dashboard
│   ├── analytics/eda.py            # Data analysis
│   └── data/                       # Data processing modules
├── data/                           # Data storage
│   ├── raw/                        # Original data
│   ├── processed/                  # Cleaned data
│   └── database/                   # SQLite database
├── tests/                          # Test files
├── scripts/                        # Utility scripts
├── pyproject.toml                  # Project dependencies and config
├── Makefile                        # Commands for Unix/Mac (not used on Windows)
└── requirements.txt                # Python packages needed
```

**Key Files You'll Work With:**

- `pyproject.toml` - Lists all dependencies
- `src/brand_visibility/pipeline.py` - Main ETL process
- `src/brand_visibility/dashboard/app.py` - Streamlit web dashboard

---

## Installation Steps

### Step 1: Clone or Extract the Project

**Option A: Using Git (if installed)**

Open PowerShell and navigate to where you want the project:

```powershell
# Navigate to your projects folder
cd C:\Users\YourUsername\Documents

# Clone the repository
git clone https://github.com/YourUsername/Brand.git
cd Brand
```

**Option B: Extract ZIP file**

1. Download the project as ZIP
2. Right-click → Extract All
3. Open PowerShell and navigate to that folder:

```powershell
cd C:\path\to\Brand
```

### Step 2: Open Project in VS Code

```powershell
code .
```

This opens VS Code in the current folder (Brand/).

### Step 3: Create and Activate Virtual Environment

A **virtual environment** is an isolated Python space for this project only. It prevents conflicts with other Python projects.

**Create the virtual environment:**

```powershell
python -m venv .venv
```

**What this does:**
- Creates a `.venv` folder with a separate Python installation
- Takes ~30 seconds
- Look for a `.venv` folder appearing in your file explorer

**Activate the virtual environment:**

```powershell
.venv\Scripts\Activate.ps1
```

**Success indicators:**
- Your PowerShell prompt changes to show `(.venv)`
- Example: `(.venv) C:\Users\YourUsername\Brand>`

If you see an error like "cannot be loaded because running scripts is disabled", run this **once** in PowerShell as Administrator:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activating again.

### Step 4: Install Project Dependencies

With the virtual environment activated (you should see `(.venv)` in your prompt), run:

```powershell
pip install -e ".[dev]"
```

**What this does:**
- `-e` = "editable" mode (project updates apply instantly)
- `.[dev]` = install package + development tools (pytest, ruff)
- Downloads ~50-100 MB
- Takes 2-5 minutes depending on internet speed

**What gets installed:**
- `streamlit` - web dashboard framework
- `pandas` - data manipulation
- `numpy` - numerical computing
- `plotly` - interactive charts
- `pytest` - testing framework
- `ruff` - code quality checker

**Verify installation:**

```powershell
python -c "import streamlit; print(streamlit.__version__)"
```

Should print a version number like `1.38.0`.

---

## Running the Project

**Always remember:** Activate the virtual environment first!

```powershell
.venv\Scripts\Activate.ps1
```

### Option 1: Run the Full Pipeline (Process Data)

Processes data from raw → cleaned → analysis-ready:

```powershell
python -m brand_visibility.pipeline
```

**What happens:**
1. Loads data from `data/raw/`
2. Cleans and validates data
3. Handles missing values
4. Exports to `data/processed/`
5. Creates SQLite database
6. Takes 10-30 seconds
7. Watch the progress in PowerShell

**Demo mode (no CSV needed):**

If no CSV is provided, it creates synthetic test data. Perfect for first run!

**With your own CSV:**

```powershell
python -m brand_visibility.pipeline --csv C:\path\to\your\file.csv
```

### Option 2: Start the Dashboard

Launches the interactive web dashboard at `http://localhost:8501`:

```powershell
streamlit run src\brand_visibility\dashboard\app.py
```

**What happens:**
1. PowerShell shows: "You can now view your Streamlit app in your browser..."
2. Browser automatically opens (or copy the URL)
3. See 6 tabs of charts and analysis
4. Press `Ctrl+C` in PowerShell to stop

**Dashboard tabs:**
- Overview - Key metrics
- Inventory - Product listings
- Rankings - Position analysis
- Ratings - Quality scores
- Prices - Price distribution
- Cleaning Report - Data quality details

### Option 3: Run Data Analysis (EDA)

Generates 30 exploratory data analysis questions and answers:

```powershell
python scripts\export_eda.py
```

**Output:** `reports/eda_answers.md` (read in any text editor)

### Option 4: Run Tests

Validates that code works correctly:

```powershell
pytest -q
```

**What this does:**
- Runs all tests in `tests/` folder
- Shows `.` for each passed test
- Shows `F` for failures
- Takes 5-10 seconds

### Option 5: Check Code Quality

Finds formatting and style issues:

```powershell
ruff check src tests scripts
```

---

## Detailed Explanations

### Understanding the Pipeline

The **pipeline** is the heart of the project. It has 3 stages:

**1. Extract**
- Reads data from CSV files or APIs
- Fetches brand visibility data from SerpAPI
- Location: `src/brand_visibility/data/extract.py`

**2. Transform**
- Cleans messy data
- Fixes missing values using medians
- Normalizes text and numbers
- Removes duplicates
- Handles outliers
- Location: `src/brand_visibility/data/transform.py`

**3. Load**
- Saves cleaned data to CSV
- Stores in SQLite database for fast queries
- Creates report of cleaning actions
- Location: `src/brand_visibility/data/database.py`

**Run it with:**
```powershell
python -m brand_visibility.pipeline
```

### Understanding Virtual Environments

**Why do we need it?**

Imagine you have two projects:
- Project A needs `pandas 1.5`
- Project B needs `pandas 2.0`

Without virtual environments, they'd conflict. Virtual environments isolate each project.

**Your virtual environment:**
- Location: `.venv/` folder
- Only active in current PowerShell window
- Each project gets its own `.venv`
- Always activate before working: `.venv\Scripts\Activate.ps1`

### Understanding pyproject.toml

This file defines:
- Project name, version, description
- Required packages and versions
- Python version requirement
- Development dependencies
- Tool configurations (pytest, ruff)

**Example:**
```toml
[project]
requires-python = ">=3.10"
dependencies = ["streamlit>=1.38", "pandas>=2.1"]
```

Means: Python 3.10+ with streamlit 1.38+ and pandas 2.1+

### Understanding Makefile vs Windows PowerShell

The `Makefile` has shortcuts for Unix/Mac:
- `make install` → our `pip install -e ".[dev]"`
- `make pipeline` → our `python -m brand_visibility.pipeline`
- `make dashboard` → our `streamlit run ...`

**Windows can't use Makefile**, so we run the longer commands directly.

---

## Troubleshooting

### Error: "Python not found"

**Problem:** `python: The term 'python' is not recognized`

**Solution:**
1. Verify Python installed: `python --version`
2. If not found, reinstall Python and **CHECK "Add Python to PATH"**
3. Restart PowerShell after reinstalling Python
4. Try: `py --version` (sometimes `py` works when `python` doesn't)

---

### Error: "Cannot run activation script"

**Problem:** `.venv\Scripts\Activate.ps1 cannot be loaded...`

**Solution:**

Run **once** in PowerShell (as Administrator):

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate again:
```powershell
.venv\Scripts\Activate.ps1
```

---

### Error: "ModuleNotFoundError: No module named 'streamlit'"

**Problem:** Packages not installed or virtual environment not activated.

**Solution:**
1. Verify virtual environment is activated (look for `(.venv)` in prompt)
2. Reinstall: `pip install -e ".[dev]"`
3. Verify: `pip list` (should show streamlit, pandas, etc.)

---

### Error: "Port 8501 is already in use"

**Problem:** Another Streamlit app is running on the same port.

**Solution:**
1. Find and close the other PowerShell window running Streamlit
2. Or run on different port:
   ```powershell
   streamlit run src\brand_visibility\dashboard\app.py --server.port 8502
   ```

---

### Slow Installation (pip install takes forever)

**Problem:** Downloading packages is slow.

**Solution:**
1. Check internet connection
2. Use a faster pip mirror:
   ```powershell
   pip install -i https://mirrors.aliyun.com/pypi/simple/ -e ".[dev]"
   ```
3. Be patient (first install is slowest)

---

### Error: "No CSV file found"

**Problem:** Pipeline runs but creates only test data.

**Solution:**
1. Prepare your CSV file with columns:
   - `keyword`, `title`, `platform`, `price`, `rating`, `position`
2. Run with full path in quotes:
   ```powershell
   python -m brand_visibility.pipeline --csv "C:\Users\YourUsername\Downloads\your_data.csv"
   ```

---

### Virtual environment not deactivating properly

**To deactivate:**
```powershell
deactivate
```

**Or just close PowerShell.** Opening a new PowerShell window won't have `.venv` active.

---

## Using the Dashboard

### First Launch

1. Ensure pipeline has run at least once:
   ```powershell
   python -m brand_visibility.pipeline
   ```

2. Start dashboard:
   ```powershell
   streamlit run src\brand_visibility\dashboard\app.py
   ```

3. Wait for: `You can now view your Streamlit app in your browser at http://localhost:8501`

4. Click the link or paste in browser

### Dashboard Features

**Overview Tab:**
- Total products, brands, keywords
- Average price, rating, position

**Inventory Tab:**
- Complete product list with all attributes
- Search and filter by keyword/brand

**Rankings Tab:**
- Position analysis
- Visibility scores (higher = more visible)
- Best and worst ranking products

**Ratings Tab:**
- Star rating distribution
- Quality metrics by brand

**Prices Tab:**
- Price range analysis
- Average prices by category
- Outlier detection

**Cleaning Report Tab:**
- Summary of data quality
- What was fixed
- Missing value strategies

### Interacting with the Dashboard

- **Sidebar controls** - Filter by keyword, brand, platform
- **Hover on charts** - See exact values
- **Click legend items** - Toggle series on/off
- **Full-screen button** - Expand any chart
- **Refresh button** - Reload data

---

## Quick Reference

### Everyday Commands

**Activate virtual environment:**
```powershell
.venv\Scripts\Activate.ps1
```

**Run pipeline (process data):**
```powershell
python -m brand_visibility.pipeline
```

**Start dashboard (web UI):**
```powershell
streamlit run src\brand_visibility\dashboard\app.py
```

**Run tests:**
```powershell
pytest -q
```

**Check code quality:**
```powershell
ruff check src tests scripts
```

**Deactivate virtual environment:**
```powershell
deactivate
```

---

## Getting Help

### If something goes wrong:

1. **Read the error message carefully** - First line usually tells you the problem
2. **Check prerequisites** - Verify Python and VS Code installed
3. **Verify virtual environment** - See `(.venv)` in prompt?
4. **Review logs** - PowerShell shows what failed and why
5. **Try again from scratch:**
   ```powershell
   deactivate
   Remove-Item -Recurse .venv
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -e ".[dev]"
   ```

### Useful Resources

- Python: [python.org/docs](https://docs.python.org/3/)
- Streamlit: [streamlit.io/docs](https://docs.streamlit.io/)
- Pandas: [pandas.pydata.org](https://pandas.pydata.org/)
- VS Code: [code.visualstudio.com/docs](https://code.visualstudio.com/docs)

---

## Summary

**In 5 steps:**

1. Install Python 3.10+
2. `python -m venv .venv` - Create virtual environment
3. `.venv\Scripts\Activate.ps1` - Activate it
4. `pip install -e ".[dev]"` - Install packages
5. `streamlit run src\brand_visibility\dashboard\app.py` - Run dashboard

**That's it!** You now have a fully functional data pipeline and analytics dashboard.

---

## Next Steps

- **Learn more**: Read `docs/architecture.md` for technical details
- **Add your data**: Use `--csv` flag with your own datasets
- **Customize**: Modify `src/brand_visibility/config.py` to change settings
- **Develop**: Edit Python files and dashboard reloads automatically

Happy analyzing! 🎉
