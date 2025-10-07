from django.apps import AppConfig

class RagConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rag'

    def ready(self):
        print("App rag carregado")  # ou inicializar Neo4j
