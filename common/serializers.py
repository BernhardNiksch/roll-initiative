from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class FilteringSerializer(serializers.Serializer):
    """Dynamically create a choice list field for each filterable field"""

    def __init__(self, *args, filter_options=None, **kwargs):
        super().__init__(*args, **kwargs)
        if filter_options:
            for field, options in filter_options.items():
                choices = [option["id"] for option in options]
                self.fields[field] = serializers.ListField(
                    child=serializers.ChoiceField(choices=choices, allow_null=True),
                    required=False,
                    allow_null=True,
                )


class SortingSerializer(serializers.Serializer):
    """Dynamically create Boolean fields for each sortable field"""

    def __init__(self, *args, sort_fields=None, **kwargs):
        super().__init__(*args, **kwargs)
        if sort_fields:
            for field in sort_fields:
                self.fields[field] = serializers.BooleanField(required=False)

    def validate(self, data):
        if len(data) > 1:
            raise ValidationError("Cannot sort by more than one field.")
        return data


class ManagedListSerializer(serializers.Serializer):
    search = serializers.CharField(required=False)

    def __init__(self, *args, filter_options=None, sort_fields=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["filter"] = FilteringSerializer(
            filter_options=filter_options, required=False
        )
        self.fields["sort"] = SortingSerializer(sort_fields=sort_fields, required=False)
