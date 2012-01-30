
from django.contrib.auth.backends import ModelBackend
from django.contrib.admin.models import User
from main.models import PendingHash
from django.utils import timezone
   
class HashBackend(ModelBackend):
    def authenticate(self, hashcode):
        try:
            ph = PendingHash.objects.get(hashcode=hashcode)
            user=ph.user
            user.is_active=True
            user.save()
            if ph.party:
                ph.party.active=True
                ph.party.save()
            if pk.one_time_use:
                ph.delete()
              
            return user
        except PendingHash.DoesNotExist:
            return None
        return None

