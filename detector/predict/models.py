from django.db import models

def upload_to_predictions(instance, filename):
    # store uploads under MEDIA_ROOT/uploads/YYYY/MM/DD/filename
    from datetime import datetime
    now = datetime.now()
    return f"uploads/{now.year}/{now.month:02d}/{now.day:02d}/{filename}"

class Prediction(models.Model):
    # ImageField stores filename relative to MEDIA_ROOT
    image = models.ImageField(upload_to=upload_to_predictions)
    label = models.CharField(max_length=32)
    probability = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.label} ({self.probability}) @ {self.created_at}"