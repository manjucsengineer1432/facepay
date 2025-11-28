from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.http import JsonResponse
from .models import Customer, Transaction
from deepface import DeepFace
import cv2
import numpy as np
import base64
import io
from PIL import Image
from django.contrib import messages
from django.core.files.base import ContentFile
import face_recognition
import re


# Create your views here.
def home(request):
    # This will load a template file called home.html
    return render ( request, 'home.html')





def checkout(request):
    error = ""
    success = ""

    if request.method == "POST":
        mobile = request.POST.get("mobile_number")
        amount = float(request.POST.get("amount"))
        face_data = request.POST.get("face_data")

        try:
            customer = Customer.objects.get(mobile_number=mobile)
        except Customer.DoesNotExist:
            error = "Mobile number not registered."
            return render(request, "checkout.html", {"error": error})

        if not face_data:
            error = "Please capture your face."
            return render(request, "checkout.html", {"error": error})

        # Convert base64 to image
        face_bytes = base64.b64decode(face_data.split(',')[1])
        img = Image.open(io.BytesIO(face_bytes))
        img = np.array(img)

        try:
            # Get embedding of live image
            live_embedding = DeepFace.represent(img, model_name='Facenet')[0]["embedding"]
            live_embedding = np.array(live_embedding, dtype=np.float32)

            # Get saved embedding
            saved_embedding = np.frombuffer(customer.face_embedding, dtype=np.float32)

            # Compare embeddings
            distance = np.linalg.norm(saved_embedding - live_embedding)
            if distance > 0.6:  # Threshold for match
                error = "Face not recognized. Transaction denied."
                return render(request, "checkout.html", {"error": error})

        except Exception as e:
            error = f"Face verification failed: {str(e)}"
            return render(request, "checkout.html", {"error": error})

        # Dummy payment
        if customer.balance >= amount:
            customer.balance -= amount
            customer.save()
            Transaction.objects.create(sender=customer, receiver=customer, amount=amount, status="Success")
            success = f"Payment of {amount} successful! Remaining balance: {customer.balance}"
        else:
            Transaction.objects.create(sender=customer, receiver=customer, amount=amount, status="Failed")
            error = "Insufficient balance."

    return render(request, "checkout.html", {"error": error, "success": success})


#*******************************************************


#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#Updated code

# ---------- SIGNUP ----------

def signup(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        identity_number = request.POST.get("identity_number")   # Aadhaar
        mobile_number = request.POST.get("mobile_number")
        bank_name = request.POST.get("bank_name")
        account_number = request.POST.get("account_number")
        face_image_data = request.POST.get("face_image")

        # decode base64 -> numpy image
        header, img_b64 = face_image_data.split(";base64,")
        decoded = base64.b64decode(img_b64)
        np_img = np.frombuffer(decoded, np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        # extract face encodings
        face_enc = face_recognition.face_encodings(img)
        if not face_enc:
            return JsonResponse({"status": "error", "message": "No face detected"})

        encoding = face_enc[0].tobytes()

        # create customer
        customer = Customer.objects.create(
            first_name=first_name,
            last_name=last_name,
            identity_number=identity_number,
            mobile_number=mobile_number,
            bank_name=bank_name,
            account_number=account_number,
            face_encoding=encoding
        )
        
        return render(request, "signup.html", {"success": True})

    return render(request, "signup.html")



        #return JsonResponse({"status": "success", "message": "Signup successful"})

    #return render(request, "signup.html")
   

    

   


'''def signup(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        identity_proof = request.POST.get("identity_proof")
        identity_number = request.POST.get("identity_number")
        mobile_number = request.POST.get("mobile_number")
        bank_name = request.POST.get("bank_name")
        account_number = request.POST.get("account_number")
        face_image_data = request.POST.get("face_image")

        # ✅ check if face image exists
        if not face_image_data:
            return JsonResponse({"success": False, "reason": "No face image captured"})

        try:
            # decode face image
            header, img_b64 = face_image_data.split(';base64,')
            decoded = base64.b64decode(img_b64)
            img = face_recognition.load_image_file(io.BytesIO(decoded))

            encodings = face_recognition.face_encodings(img)
            if not encodings:
                return JsonResponse({"success": False, "reason": "No face detected"})

            face_encoding = np.array(encodings[0]).tobytes()
        except Exception as e:
            import traceback; traceback.print_exc()
            return JsonResponse({"success": False, "reason": "Face processing failed"})

        # ✅ Save customer
        Customer.objects.create(
            first_name=first_name,
            last_name=last_name,
            identity_proof=identity_proof,
            identity_number=identity_number,
            mobile_number=mobile_number,
            bank_name=bank_name,
            account_number=account_number,
            face_encoding=face_encoding
        )

        return JsonResponse({"success": True, "redirect": "/home/"})

    return render(request, "signup.html")
    '''

# ---------- SIGNIN ----------
def signin(request):
    if request.method == "POST":
        step = request.POST.get("step")
        mobile = request.POST.get("mobile_number")

        # Step 1: check mobile
        if step == "check_mobile":
            try:
                customer = Customer.objects.get(mobile_number=mobile)
                aadhaar = getattr(customer, "identity_number", "")
                masked = "XXXX XXXX " + aadhaar[-4:] if len(aadhaar) >= 4 else "XXXX XXXX"
                return JsonResponse({"exists": True, "aadhaar": masked})
            except Customer.DoesNotExist:
                return JsonResponse({"exists": False})

        # Step 2: validate face
        if step == "validate_face":
            try:
                customer = Customer.objects.get(mobile_number=mobile)
            except Customer.DoesNotExist:
                return JsonResponse({"face_valid": False, "reason": "Customer not found"})

            face_image_data = request.POST.get("face_image")
            if not face_image_data:
                return JsonResponse({"face_valid": False, "reason": "No face image provided"})

            try:
                # decode capture
                header, img_b64 = face_image_data.split(";base64,")
                decoded = base64.b64decode(img_b64)
                np_img = np.frombuffer(decoded, np.uint8)
                img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

                captured_enc = face_recognition.face_encodings(img)
                if not captured_enc:
                    return JsonResponse({"face_valid": False, "reason": "No face detected in capture"})

                if not customer.face_encoding:
                    return JsonResponse({"face_valid": False, "reason": "No stored face data"})

                stored_enc = np.frombuffer(customer.face_encoding, dtype=np.float64)

                match = face_recognition.compare_faces([stored_enc], captured_enc[0], tolerance=0.5)
                if match[0]:
                    return JsonResponse({"face_valid": True})
                else:
                    return JsonResponse({"face_valid": False, "reason": "Face mismatch"})

            except Exception as e:
                import traceback; traceback.print_exc()
                return JsonResponse({"face_valid": False, "reason": "Server error during face check"})

        # Step 3: make payment (dummy)
        if step == "make_payment":
            return JsonResponse({"payment": "success"})

    return render(request, "signin.html")



def success(request):
    return render(request, 'success.html')
