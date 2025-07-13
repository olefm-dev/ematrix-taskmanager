# Eisenhower Matrix Task Manager

![Python Tests](https://github.com/olefm-dev/ematrix-tasks/actions/workflows/python-tests.yml/badge.svg)

Human Note:
This is just a wibe coded project, where AI has done most of the work, mainly Grok 4 and Claude 3.7 Sonnet. The IDE I'm using is Windsurf, and this is just meant as a little tool to manage my tasks. I will do a full code review at a later date, and maybe add some functionality depending on my needs and/or requests.

Be warned, as this is mostly AI it does not follow best practices, the code is "dirty" and not optimized. But it works, for now.

AI ReadMe:

🚀 A Fun Vibe Coding AI Project

<img width="1425" height="924" alt="image" src="https://github.com/user-attachments/assets/9edcba1b-b469-44a3-9340-0823e188fe3a" />


This is a playful project built with the help of Grok AI, blending productivity with a chill, exploratory coding vibe. It's a sleek task manager inspired by the Eisenhower Matrix—perfect for organizing your chaos while having fun with Flask and modern web tech!

A beautiful dark mode task manager based on the Eisenhower Matrix, built with Flask and SQLite.
## Features

- **Eisenhower Matrix Organization** 📊: Tasks sorted into four dynamic quadrants:
  - Quadrant 1: Urgent & Important (Do) ⚡
  - Quadrant 2: Important, Not Urgent (Schedule) 📅
  - Quadrant 3: Urgent, Not Important (Delegate) 🤝
  - Quadrant 4: Not Urgent, Not Important (Eliminate) 🗑️
- **Dark Mode Interface** 🌙: Modern, eye-friendly theme with toggle support
- **Task Management** ✅: Create, edit, complete, and delete tasks with ease
- **Due Dates & Descriptions** ⏰: Add deadlines and details for better tracking
- **Completed Tasks View** 🏆: Dedicated page to review your wins
- **Share Links & Requested Tasks** 🔗: Generate public links for others to submit tasks, which you can accept into your matrix
- **Drag-and-Drop** 🖱️: Seamlessly move tasks between quadrants
- **Responsive Design** 📱: Works great on mobile and desktop
- **Admin** 👑: Now with an admin panel for creating multiple users with separate tasks

## Installation

1. **Clone the Repository** 📥:
   ```bash
   git clone <repository-url>
   cd ematrix-tasks
   ```

2. **Create a Virtual Environment** 🛡️:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies** 📦:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment** 🔑:
   - Create a `.env` file in the root directory (use the sample provided or generate a secure SECRET_KEY).
   - Example: `SECRET_KEY=your_secure_random_key_here`

## Run the Application 🚀

1. **For development**:
   ```bash
   python app.py
   ```

2. **For production** (recommended with Gunicorn as a systemd service):

   a. Create a systemd service file:
   ```bash
   sudo nano /etc/systemd/system/ematrix.service
   ```

   b. Add the following configuration:
   ```ini
   [Unit]
   Description=Eisenhower Matrix Task Manager
   After=network.target

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/path/to/ematrix-tasks
   Environment="PATH=/path/to/ematrix-tasks/.venv/bin"
   ExecStart=/path/to/ematrix-tasks/.venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 app:app
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```
   (Adjust paths, user/group, and `-w 4` based on your environment and CPU cores)

   c. Enable and start the service:
   ```bash
   sudo systemctl enable ematrix.service
   sudo systemctl start ematrix.service
   ```

   d. Check service status:
   ```bash
   sudo systemctl status ematrix.service
   ```

3. **Configure Reverse Proxy** (Nginx example):
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

4. **Access the App** 🌐: Open your browser and navigate to your domain or http://127.0.0.1:8000.

## Technologies Used

- **Backend** 🛠️: Flask, SQLAlchemy, Flask-Login, Flask-WTF
- **Database** 💾: SQLite (persistent and lightweight)
- **Frontend** 🎨: HTML, Vanilla JavaScript, Tailwind CSS (via CDN for simplicity)
- **Other** 🔧: Gunicorn for production serving, python-dotenv for env management

## Usage

- **Setup & Login** 🔑: On first run, create an account via the setup page. Log in to access the dashboard.
- **Adding Tasks** ➕: Use the "Add New Task" form—select quadrant, add details, and submit.
- **Editing & Moving Tasks** ✏️: Click "Edit" or drag-drop between quadrants for quick reorganization.
- **Completing/Deleting** ✅🗑️: Mark done or remove tasks with a click.
- **Share Links** 🔗: In Settings, create links to share publicly. Others can submit tasks, which appear in your "Requested Tasks" section for acceptance.
- **Completed View** 🏆: Navigate to "Completed" to see archived tasks.
- **Theme Toggle** 🌗: Switch between light/dark modes in Settings.
- **Admin Panel** 👑: Admin users can access the admin panel to manage users, create new accounts, edit user details, and delete users. The first user created during setup is automatically assigned admin privileges.

## Testing

### Running Tests Locally

To run the test suite locally, make sure you have the required testing packages installed:

```bash
pip install pytest pytest-flask
```

Then run the tests using:

```bash
pytest -v
```

Or use the provided script:

```bash
./run_tests.sh
```

### Continuous Integration

This project uses GitHub Actions for continuous integration testing. The workflow automatically runs tests on multiple Python versions whenever changes are pushed to the repository.

Features of the CI pipeline:
- Runs tests on Python 3.10, 3.11, and 3.12
- Performs code linting with flake8
- Generates code coverage reports
- Caches dependencies for faster builds

You can manually trigger the workflow from the Actions tab in the GitHub repository.

To view the current status of the tests, check the badge at the top of this README.

## License

MIT
