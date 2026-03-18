# 🐾 **PetRescue Pro**

### *Bringing lost companions back home, one report at a time.*

---

## 📌 **Project Overview**


**PetRescue Pro** aims to develop an interactive web platform that bridges the gap between individuals who find lost pets and their owners.

The website will provide functionalities for users to raise requests regarding found pets, while admins can view and manage these requests to facilitate reunions.

The platform will also allow users to check whether their lost pets have been reported on the website, thereby enhancing the chances of a reunion.

The intuitive interface and structured data management will ensure a seamless experience for both users and admins.

## ✨ **Key Features**

### 👤 **For Users**

* 📝 **Detailed Reporting**
  Submit *Lost* or *Found* reports including pet name, breed, color, description, and images.

* 📊 **Intuitive Dashboard**
  Manage your reports and view the latest community updates in one place.

* 🔔 **Smart Matching Alerts**
  Get notified when a report matches your lost pet’s description or breed.

* 🔍 **Advanced Search**
  Filter reports based on:

  * Animal type
  * Breed
  * Color
  * Location

* 🔐 **Secure Authentication**
  Personal accounts ensure privacy and secure access to your data.

---

### 🛠️ **For Administrators**

* 🧑‍💼 **Branded Admin Portal**
  Clean and structured dashboard for efficient management.

* 🔄 **Status Management**
  Update report status easily:
  `Pending → Accepted → Closed/Reunited`

* 🚫 **Moderation Tools**
  Reject invalid, duplicate, or suspicious reports.

* 👥 **User Oversight**
  Track report submissions and communicate effectively with users.

---

## 🛠️ **Technology Stack**

| Layer        | Technology Used                        |
| ------------ | -------------------------------------- |
| **Backend**  | Python, Django 6.0                     |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript        |
| **Styling**  | Custom CSS (Glassmorphism & Modern UI) |
| **Database** | PostgreSQL                             |
| **Icons**    | FontAwesome 6+                         |

---
## 🚀 Setup Instructions

### 📌 Prerequisites

* Python 3.10+
* PostgreSQL
* Git

---

### 1. 📥 Clone the Repository

```bash
git clone https://github.com/AnnMariya2005/Pet_Adoption_and_Rescue.git
cd Pet_Adoption_and_Rescue
```

---

### 2. 🐍 Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

---

### 3. 📦 Install Dependencies

```bash
pip install django djangorestframework psycopg2-binary
```

---

### 4. ⚙️ Configure Database

Create a PostgreSQL database named:

```
pet_rescue_db
```

(Optional: If using `.env`, you can add:)

```
DB_NAME=pet_rescue_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

---

### 5. 🗄️ Run Migrations

```bash
python manage.py migrate
```

---

### 6. 👤 Create Superuser

```bash
python manage.py createsuperuser
```

---

### 7. ▶️ Run the Server

```bash
python manage.py runserver
```

---

### 🌐 Access the Application

* Frontend: http://127.0.0.1:8000/
* Admin Panel: http://127.0.0.1:8000/admin/

---

## 📊 **Project Stats**

* 📌 **Total Reports Filed**
  Tracks all active lost & found cases.

* 🎉 **Happy Reunions**
  Managed through the **"Closed"** report status.

---

## 💡 **Future Enhancements**

* 📍 Real-time location tracking
* 🤖 AI-based pet image matching
* 📱 Mobile app integration
* 📢 SMS/Email alert system

---

## 🤝 **Contributing**

Contributions are welcome!
Feel free to fork the repository and submit pull requests.

---

## 📜 **License**

This project is open-source and available under the **MIT License**.

---

### ❤️ *Helping pets find their way back home, one report at a time.*
