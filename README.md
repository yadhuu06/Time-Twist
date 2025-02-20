# Time Twist - E-commerce Platform

Time Twist is a feature-rich e-commerce website built using **Django, HTML, CSS, Bootstrap, PostgreSQL, and Django ORM**. This platform is designed to provide a seamless online shopping experience for watch enthusiasts with secure authentication, payment integration, and advanced product management features.

## Features

### 🔒 Authentication & User Management
- Google login and OTP verification for secure authentication.
- Password reset functionality via email link.
- User profile management with address book support.

### 🛒 E-commerce Functionalities
- Product listing with detailed descriptions, images, and pricing.
- Sorting and filtering by **brand, category, price, and featured items**.
- Wishlist functionality for saving favorite products.
- Recently viewed product tracking.

### 💳 Payments & Order Management
- Integrated **Razorpay** payment gateway for secure transactions.
- Cash on Delivery (COD) option for orders below ₹10,000.
- Real-time order tracking and status updates.
- 7-day return policy with refund processing.
- Wallet system for storing refunded amounts.

### 📊 Admin Dashboard
- Manage products, categories, and brands.
- Apply individual product offers, discount coupons, and seasonal deals.
- Generate **weekly, monthly, and yearly sales reports**.
- View and manage user accounts, including blocking/unblocking users.

### 🛠️ Tech Stack
- **Backend:** Django, Django ORM, PostgreSQL
- **Frontend:** HTML, CSS, Bootstrap
- **Authentication:** Google OAuth, OTP-based verification, JWT
- **Payments:** Razorpay Integration
- **Deployment:** hosted in AWS

## Installation & Setup

### 1️⃣ Clone the Repository
```bash
 git clone https://github.com/yadhuu06/Time-Twist.git
 cd Time-Twist
```

### 2️⃣ Create & Activate Virtual Environment
```bash
 python -m venv venv
 source venv/bin/activate  # On macOS/Linux
 venv\Scripts\activate  # On Windows
```

### 3️⃣ Install Dependencies
```bash
 pip install -r requirements.txt
```

### 4️⃣ Apply Migrations & Create Superuser
```bash
 python manage.py migrate
 python manage.py createsuperuser
```

### 5️⃣ Run the Development Server
```bash
 python manage.py runserver
```

The project will be available at **http://127.0.0.1:8000/**
hosted in AWS :  **https://timetwist.shop/**

## Future Enhancements
- AI-powered recommendations based on user preferences.
- Integration of MongoDB alongside PostgreSQL for better data handling.
- Progressive Web App (PWA) support for mobile-friendly experience.

## 📬 Contact
For any queries or contributions, reach out via:
- **GitHub:** [yadhuu06](https://github.com/yadhuu06)
- **LinkedIn:** [Yadhu Krishnan PS](https://www.linkedin.com/in/yadhu-krishnan-s/)
