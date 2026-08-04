from django.shortcuts import render

def forecast_view(request):
  return render(request, 'forecasting/home.html')
