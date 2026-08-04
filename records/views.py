from django.shortcuts import render

def record_view(request):
  return render(request, 'records/home.html')