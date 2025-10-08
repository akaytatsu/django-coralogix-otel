from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('health/', views.health_check, name='health_check'),
    path('api/data/', views.api_data, name='api_data'),
    path('api/error/', views.api_error, name='api_error'),
    path('slow/', views.slow_endpoint, name='slow_endpoint'),
    path('hybrid/', views.hybrid_instrumentation_view, name='hybrid_instrumentation'),
    path('manual-trace/', views.manual_tracing_view, name='manual_tracing'),
    path('database/', views.database_view, name='database_view'),
    path('external-api/', views.external_api_view, name='external_api_view'),
    path('logging-test/', views.logging_test_view, name='logging_test'),
]