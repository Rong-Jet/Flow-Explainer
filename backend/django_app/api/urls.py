from django.urls import path
from .views import GenerateDiagramView, HomeView, ProcessJsonView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('generate-diagram/', GenerateDiagramView.as_view(), name='generate_diagram'),
    path('process-json/', ProcessJsonView.as_view(), name='process_json'),
] 