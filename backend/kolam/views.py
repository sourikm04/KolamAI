# kolam/views.py

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

# This is your home view from the previous step
def home(request):
    return HttpResponse("<h1>Welcome to the Kolam project!</h1>")

@csrf_exempt
@require_POST
def upload_kolam_image(request):
    if 'image' in request.FILES:
        # Here, the uploaded image is available in request.FILES['image']
        # You will integrate the ML model here in a later step.
        # For now, let's just confirm the image was received.
        
        # Get the uploaded image file object
        uploaded_file = request.FILES['image']
        
        # Return a success message
        return JsonResponse({
            'success': True,
            'message': 'Image received successfully. Ready for ML processing.',
            'filename': uploaded_file.name
        })
    else:
        # Return an error if no image was found in the request
        return JsonResponse({
            'success': False,
            'message': 'No image file found in the request.'
        }, status=400)
