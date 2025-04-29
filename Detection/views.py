from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from .forms import RecommendationForm, ContactForm, UploadImageForm
from .models import UserProfile
from django.core.files.storage import FileSystemStorage
import tensorflow as tf
import numpy as np
from PIL import Image
import os
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .utils import generate_pdf_report  # Import the utility

# User Signup
def user_signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        dob = request.POST.get("dob")
        location = request.POST.get("location")
        phone = request.POST.get("phone") 

        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists!")
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Email is already in use!")
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                # Store extra user info in session
                request.session["dob"] = dob
                request.session["location"] = location

                messages.success(request, "Account created successfully! Please log in.")
                return redirect("login")
        else:
            messages.error(request, "Passwords do not match!")

    return render(request, "signup.html")


# User Login
def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("index")  # Redirect to home page after login
        else:
            messages.error(request, "Invalid username or password!")

    return render(request, "login.html")

# User Logout
def user_logout(request):
    logout(request)
    return redirect("login")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Adjusted to get the correct path
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'HAM10000_CNN.h5')

if os.path.exists(MODEL_PATH):
    model = tf.keras.models.load_model(MODEL_PATH)
else:
    raise FileNotFoundError(f" Model file NOT found at {MODEL_PATH}")

# Add below HAM10000 model load block
BINARY_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'lesion_classifier.h5')

if os.path.exists(BINARY_MODEL_PATH):
    binary_model = tf.keras.models.load_model(BINARY_MODEL_PATH)
else:
    raise FileNotFoundError(f" Binary model not found at {BINARY_MODEL_PATH}")


# Define class labels with full names
lesion_classes = {
    0: "Actinic Keratoses (AKIEC)",
    1: "Basal Cell Carcinoma (BCC)",
    2: "Benign Keratosis (BKL)",
    3: "Dermatofibroma (DF)",
    4: "Melanoma (MEL)",
    5: "Nevus (NV)",
    6: "Vascular Lesions (VASC)"
}

def index(request):
    return render(request, 'index.html')

def is_skin_lesion(img_path):
    try:
        img = Image.open(img_path).convert("RGB")
        img = img.resize((128, 128))  # Resize for binary model
        img = np.array(img) / 255.0
        img = np.expand_dims(img, axis=0)
        prediction = binary_model.predict(img)
        print("Binary Model Prediction Score:", prediction[0][0])  # Add this
        return prediction[0][0] > 0.5
    except Exception as e:
        print("Error during binary prediction:", e)
        return False

def predict_view(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(image.name, image)
        uploaded_file_url = fs.url(filename)

        return render(request, 'index.html', {
            'uploaded_file_url': uploaded_file_url
        })
    
    return render(request, 'index.html')
    

@login_required
def home(request):
    form = UploadImageForm()
    prediction = None
    uploaded_file_url = None
    img_path = None
    report_url = None

    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(image.name, image)
        uploaded_file_url = fs.url(filename)
        img_path = fs.path(filename)

        try:
            if is_skin_lesion(img_path):
                img = Image.open(img_path).convert("RGB")
                img = img.resize((224, 224))
                img = np.array(img) / 255.0
                img = np.expand_dims(img, axis=0)

                predictions = model.predict(img)
                predicted_class = np.argmax(predictions)
                prediction = lesion_classes.get(predicted_class, "Unknown")
            else:
                prediction = "Non-skin lesion. Please upload a valid skin lesion image."

            # Fetch DOB and location from session
            dob = request.session.get("dob", "Not Provided")
            location = request.session.get("location", "Not Provided")

            # Generate the PDF and get the relative URL
            report_url = generate_pdf_report(request.user, img_path, prediction, dob=dob, location=location)

        except Exception as e:
            prediction = f"Error processing image: {str(e)}"

    return render(request, 'home.html', {
        'form': form,
        'uploaded_file_url': uploaded_file_url,
        'prediction': prediction,
        'report_url': report_url
    })


def about(request):
    return render(request, 'about.html')

def faq(request):
    return render(request, 'faq.html')

def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            message = form.cleaned_data["message"]
            
            subject = f"New Contact Form Submission from {name}"
            body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
            
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                ['yewalesayali9@gmail.com'],
                fail_silently=False,
            )
            return render(request, "thank_you.html")
    else:
        form = ContactForm()

    return render(request, "contact.html", {"form": form})

# Skin care recommendations based on lesion class
recommendations = {
    'mel': (
        "For melanoma(mel):\n"
        "- Consult a dermatologist immediately.\n"
        "- Regularly check your skin for any new or changing moles.\n"
        "- Avoid sun exposure and wear sunscreen with SPF 30+.\n"
        "- Follow your doctor’s instructions for further testing and treatment."
    ),
    'bcc': (
        "For basal cell carcinoma (BCC):\n"
        "- Early detection and removal by a healthcare professional are key.\n"
        "- Avoid sun exposure and use sunscreen daily.\n"
        "- Monitor any skin changes and report them to your doctor."
    ),
    'akiec': (
        "For actinic keratosis (AK):\n"
        "- Consult a dermatologist for treatment options like cryotherapy.\n"
        "- Use sunscreen regularly to protect your skin from UV damage.\n"
        "- Keep an eye on the affected areas for any changes."
    ),
    'df': (
        "For dermatofibroma (DF):\n"
        "- Typically harmless, but if you notice changes, consult a dermatologist.\n"
        "- Avoid scratching or picking at the area to prevent irritation."
    ),
    'nv': (
        "For benign nevi (moles):\n"
        "- Regularly monitor any moles for changes in size, shape, or color.\n"
        "- Avoid excessive sun exposure and use sunscreen to protect your skin."
    ),
    'bkl': (
        "For benign keratosis (BKL):\n"
        "- These are usually harmless but should be checked by a dermatologist.\n"
        "- Apply sunscreen to prevent further skin damage."
    ),
    'vasc': (
        "For vascular lesions (VASC):\n"
        "- Consult a healthcare provider if the lesion is growing or bleeding.\n"
        "- Avoid excessive sun exposure, as UV rays can worsen vascular lesions."
    ),
}



def recommendation(request):
    recommendation_message = ""
    
    if request.method == 'POST':
        form = RecommendationForm(request.POST)
        if form.is_valid():
            skin_condition = form.cleaned_data['skin_condition']
            
            # Based on the selected skin condition (HAM10000 classes), provide a recommendation
            recommendation_message = recommendations.get(skin_condition, "No recommendation available for this condition.")
    
    else:
        form = RecommendationForm()

    return render(request, 'recommendation.html', {'form': form, 'recommendation_message': recommendation_message})