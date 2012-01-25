
from django.contrib.auth.backends import ModelBackend
from django.contrib.admin.models import User
from main.models import PendingHash
   
class HashBackend(ModelBackend):
    def authenticate(self, hashcode):
        try:
            ph = PendingHash.objects.get(hashcode=hashcode)
            user=ph.user
            user.is_active=True
            user.save()
            ph.delete()
              
            return user
        except PendingHash.DoesNotExist:
            return None


