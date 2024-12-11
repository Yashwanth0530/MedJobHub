# MedJobHub

MedJobHub is a responsive web portal designed to connect medical professionals with job opportunities. The platform provides features for users to sign up, log in securely with OTP verification, browse job opportunities, and generate resumes dynamically. It also offers functionality for administrators to manage job postings and user profiles.

## Features

### User Features:
- **Secure Login**: Users log in with a username and password. OTP verification is sent to the email registered during signup.
- **Responsive Design**: Accessible on all devices, ensuring usability for diverse users.
- **Resume Generation**: Users can create and download professional resumes based on the information provided in their profiles.
- **Browse Jobs**: Explore job listings for various medical fields, including nursing, paramedics, pharmaceuticals, and more.

### Admin Features:
- **Manage Job Listings**: Add, update, or remove job postings across multiple medical specialties.
- **View User Profiles**: Access user details to assist with job matching and management.

## Directory Structure

### Templates
The `templates` folder contains HTML files for various pages:
- **Job Categories**:
  - `nurse.html`
  - `paramed.html`
  - `pharma.html`
  - `physio.html`
  - `radio.html`
- **User Authentication**:
  - `signin.html`
  - `signup1.html`
  - `verify_otp.html`
- **User and Admin Pages**:
  - `profile.html`
  - `admin.html`
- **Static Pages**:
  - `about.html`
  - `contact.html`
  - `home.html`

### Static Files
The `static` folder contains:

#### CSS Files:
- `styles.css`
- `about.css`
- `homecss.css`
- `jobs.css`
- `profile.css`
- `signin.css`
- `signup.css`

#### Images:
- Backgrounds and logos: `background-image.jpg`, `headerlogo.jpg`, `footerlogo.jpg`
- Icons and avatars: `avatar.jpg`, `avatar1.jpeg`, `avatar2.jpeg`, ...

## Technologies Used

### Frontend:
- **HTML, CSS, JavaScript**: For building responsive and interactive pages.

### Backend:
- **Flask**: Python-based web framework for server-side logic.

### Database:
- **MongoDB**: For storing user data, job listings, and other application data.

### Additional Tools:
- **SMTP**: For sending OTP emails during login.
- **Jinja2**: For templating and dynamic content rendering.

## How to Run the Project



### Installation:
1. Clone the repository.
2. Install dependencies using:
   ```bash
   pip install -r requirements.txt
