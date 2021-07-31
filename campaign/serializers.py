from rest_framework import serializers

from .models import Campaign


class CampaignNameSerializer(serializers.ModelSerializer):
    """
    Serialize the campaign's id and name.
    """

    class Meta:
        model = Campaign
        fields = ['id', 'name']
