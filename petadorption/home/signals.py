from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.core.management import call_command

@receiver(post_migrate)
def run_seed(sender, **kwargs):
    # Only run once for our app
    if sender.name == 'home':
        try:
            print("🚀 Running seed after migrate...")
            call_command('seed')
        except Exception as e:
            print(f"⚠️ Error while running seed: {e}")
