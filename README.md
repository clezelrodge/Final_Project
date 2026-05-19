# FileTrack - Document Management System

A Flask-based web application for tracking and managing physical documents using RFID technology. Features role-based access control for admins and users.

![FileTrack](https://img.shields.io/badge/Flask-2.3.3-blue)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- **Role-Based Authentication**: Separate dashboards for Admin and User roles
- **RFID Document Tracking**: Scan RFID tags to check out and return documents
- **Document Search**: Real-time search functionality for users
- **Activity Logs**: Track all document access and returns
- **Storage Location Management**: Organize documents by rows and columns
- **Responsive Design**: Mobile-friendly interface with collapsible sidebar

## Project Structure

```
FileTrack/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── database_setup.sql        # MySQL database schema
├── setup_db.py              # Database setup script
├── .gitignore               # Git ignore file
├── README.md                # This file
├── static/
│   ├── css/
│   │   └── style.css        # Application styles
│   ├── js/
│   │   └── script.js        # Frontend scripts
│   └── img/
│       ├── img2.png         # Landing page image
│       ├── img3.png         # About section image
│       └── img4.png         # Features image
└── templates/
    ├── index.html           # Landing page
    ├── login.html           # Role-based login
    ├── admin_dashboard.html # Admin dashboard
    └── user_dashboard.html  # User dashboard
```

## Prerequisites

- Python 3.8+
- MySQL Server 8.0+
- pip (Python package manager)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/filetrack.git
   cd filetrack
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure MySQL Database**
   
   Update database credentials in `app.py` if needed:
   ```python
   host="localhost"
   user="root"
   password="your_password"
   database="FileTrackDB"
   ```

5. **Setup Database**
   
   Run the database setup script:
   ```bash
   python setup_db.py
   ```

   Or manually import the SQL file in MySQL Workbench.

## Usage

1. **Start the Flask server**
   ```bash
   python app.py
   ```

2. **Access the application**
   Open your browser and navigate to: `http://127.0.0.1:5000`

3. **Login Credentials**

   | Role | Username | Password |
   |------|----------|----------|
   | Admin | `admin` | `12345` |
   | User | `user` | `123` |

## Admin Dashboard

- View total documents, storage slots, active users, and retrieval logs
- RFID scanner simulation for check-out and return operations
- Document status tracking (Available, Borrowed, Missing)
- Activity log history

## User Dashboard

- Search documents by title or RFID tag
- View personal document history
- Check document availability and storage location
- Track assigned records and pending requests

## Database Schema

### Users Table
- `user_id`, `username`, `password`, `full_name`, `email`, `role`

### Documents Table
- `doc_id`, `title`, `rfid_tag`, `row_id`, `column_id`, `status`

### AccessLogs Table
- `log_id`, `doc_id`, `requested_by_user_id`, `processed_by_admin_id`, `action`, `action_timestamp`

### LocationRows & Columns Tables
- Storage location management with row and column labels

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Landing page |
| `/login` | GET/POST | User authentication |
| `/logout` | GET | Logout |
| `/admin/dashboard` | GET | Admin dashboard |
| `/user/dashboard` | GET | User dashboard |
| `/simulate_scan` | POST | RFID scan simulation |
| `/search` | GET | Search documents |

## Screenshots

*Add your screenshots here*

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Flask web framework
- MySQL database
- Font Awesome icons
- Google Fonts

## Contact

Your Name - [@yourtwitter](https://twitter.com/yourtwitter) - email@example.com

Project Link: [https://github.com/yourusername/filetrack](https://github.com/yourusername/filetrack)
