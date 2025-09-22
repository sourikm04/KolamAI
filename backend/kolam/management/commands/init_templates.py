from django.core.management.base import BaseCommand
from kolam.pattern_library import pattern_library

class Command(BaseCommand):
    help = 'Initialize default kolam templates'

    def handle(self, *args, **options):
        self.stdout.write('Initializing default kolam templates...')
        
        try:
            pattern_library.initialize_default_templates()
            self.stdout.write(
                self.style.SUCCESS('Successfully initialized default templates!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error initializing templates: {str(e)}')
            )

