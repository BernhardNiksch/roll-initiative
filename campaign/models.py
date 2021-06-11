from django.db import models
import uuid


class Campaign(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    story = models.TextField(blank=True)
    # TODO create user table to add owner and players fields

    class Meta:
        db_table = "campaign"
        ordering = ("name", )

    def __str__(self):
        return self.name
