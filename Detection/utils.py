def generate_pdf_report(user, image_path, prediction, dob="Not Provided", location="Not Provided"):
    from django.conf import settings
    from reportlab.pdfgen import canvas
    import os

    report_dir = os.path.join(settings.MEDIA_ROOT, 'reports')
    os.makedirs(report_dir, exist_ok=True)

    report_filename = 'report.pdf'
    report_path = os.path.join(report_dir, report_filename)

    c = canvas.Canvas(report_path)
    c.drawString(100, 800, "Skin Lesion Prediction Report")
    c.drawString(100, 780, f"User: {user.username if user.is_authenticated else 'Guest'}")
    c.drawString(100, 760, f"Date of Birth: {dob}")
    c.drawString(100, 740, f"Location: {location}")
    c.drawString(100, 720, f"Prediction: {prediction}")
    c.save()

    # Return the MEDIA_URL path for download link
    return os.path.join(settings.MEDIA_URL, 'reports', report_filename)

