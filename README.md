# Prerequisites-
Before you begin, ensure you have the following installed:

Python 3.8 or higher
pip (Python package installer)

# Installation-

Clone the repository

Create and activate a virtual environment:

# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

Install required dependencies:

Windows
pip install -r requirements.txt

# macOS/Linux
pip3 install -r requirements.txt
Creating requirements.txt (For Developers)
If you need to update the requirements.txt file:
bashCopy# Make sure your virtual environment is activated, then:
pip freeze > requirements.txt
Running the Application

Activate the virtual environment (if not already activated):

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate

Start the application:

python main.py
The application will be available at http://localhost:5000 (or whichever port you've configured)
