from django.http import JsonResponse

def custom_404(request, exception):
  return JsonResponse(
    {"message": "API endpoint not found"},
    status=404
  )
