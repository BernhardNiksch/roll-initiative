from django.core.paginator import Paginator
from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from .serializers import ManagedListSerializer


class ManagedListView(GenericAPIView):
    """
    Base class for list views.
    Allows sorting, filtering, searching, and paginating lists.

    filter_options: Field and options key-value pairs where options is a list of dictionaries
    containing an identifier, 'id', and display name, 'name'.
    ordering: Default sorting order. Should end on a unique field to ensure stable order.

    """

    search_fields = None
    sort_fields = None
    field_map = None
    filter_options = None
    ordering = ["id"]
    queryset = None
    serializer_class = None
    page_size = 25

    @extend_schema(request=ManagedListSerializer)
    def post(self, request: Request):
        managed_serializer = ManagedListSerializer(
            data=request.data,
            filter_options=self.filter_options,
            sort_fields=self.sort_fields,
        )
        managed_serializer.is_valid(raise_exception=True)

        filter_query = self.filter_query(managed_serializer.validated_data.get("filter"))
        search_query = self.search_query(managed_serializer.validated_data.get("search"))
        queryset = self.get_queryset().filter(filter_query & search_query)
        queryset = self.sort_queryset(managed_serializer.validated_data.get("sort"), queryset)

        serializer_class = self.get_serializer_class()
        serializer = serializer_class(queryset, many=True)
        paginated_response = self.paginate_response(request, serializer.data)

        if self.filter_options:
            paginated_response["filter_options"] = self.filter_options
        return Response(paginated_response)

    def paginate_response(self, request, data):
        page_size = self.page_size
        page_size_param = request.query_params.get("page_size")
        if page_size_param:
            try:
                page_size = int(page_size_param)
            except ValueError:
                pass

        page_number = 1
        page_param = request.query_params.get("page")
        if page_param:
            try:
                page_number = int(page_param)
            except ValueError:
                pass

        p = Paginator(data, page_size)
        page = p.page(page_number)
        pagination = {
            "count": p.count,
            "results": page.object_list,
        }
        if page.has_next():
            pagination["next"] = f"?page={page.next_page_number()}&page_size={page_size}"
        if page.has_previous():
            pagination["previous"] = f"?page={page.previous_page_number()}&page_size={page_size}"
        return pagination

    def filter_query(self, filters: dict):
        filter_query = Q()
        if filters:
            for field, values in filters.items():
                field_query = Q()
                for v in values:
                    field_query |= Q(**{field: v})
                filter_query &= field_query
        return filter_query

    def search_query(self, search: str):
        search_query = Q()
        if search:
            search = search.strip()
        if search:
            # strip() could return empty string
            for field in self.search_fields:
                search_query |= Q(**{f"{field}__icontains": search})
        return search_query

    def sort_queryset(self, sorting, queryset):
        order = self.ordering.copy()
        if sorting:
            for field, ascending in sorting.items():
                if self.field_map:
                    field = self.field_map.get(field, field)
                direction = "" if ascending else "-"
                order.insert(0, f"{direction}{field}")
        return queryset.order_by(*order)
