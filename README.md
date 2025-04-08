# ToDo Manager  

A collaborative task management web app built with Flask. Users can create groups, assign tasks, and manage permissions.  

## Features  
- **User Authentication**: Secure registration/login with bcrypt hashing  
- **Group Management**:  
  - Create/delete groups  
  - Add/remove members  
  - Assign admin privileges (group owner only)  
- **Task System**:  
  - Create/edit tasks with due dates  
  - Sort by name, status, creator, or due date  
  - Role-based permissions (owner/admins can edit/delete any task)  
- **Profile Management**: Update username/password with automatic foreign key updates  

## Technologies  
- **Backend**: Flask, SQLAlchemy, Flask-Login  
- **Frontend**: Bootstrap 5, Jinja2 templates  
- **Database**: SQLite

## Installation  
1. Clone repository:
   ```bash
   git clone https://github.com/yourusername/todo.git
   cd todo
2. Install dependencies:  
   ```bash  
   pip install -r requirements.txt  