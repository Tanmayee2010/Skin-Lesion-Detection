from django import forms
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import User

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")


class UploadImageForm(forms.Form):
    image = forms.ImageField(
        label='Upload Image',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Your Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Your Email'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Your Message'}))

class RecommendationForm(forms.Form):
    # Ensure these labels match your model's output labels
    SKIN_CONDITION_CHOICES = [
        ('mel', 'Melanoma (mel)'),
        ('bcc', 'Basal Cell Carcinoma (BCC)'),
        ('akiec', 'Actinic Keratosis (AK)'),
        ('df', 'Dermatofibroma (DF)'),
        ('nv', 'Benign Nevi (NV)'),
        ('bkl', 'Benign Keratosis (BKL)'),
        ('vasc', 'Vascular Lesions (VASC)'),
    ]
    skin_condition = forms.ChoiceField(choices=SKIN_CONDITION_CHOICES, label="Select Skin Condition")
