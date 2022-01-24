from rest_framework import filters


class RecipeFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        tags = request.query_params.getlist('tags')
        if len(tags) != 0:
            queryset = queryset.filter(tags__slug__in=tags).distinct()
        author = request.query_params.get('author')
        if author is not None:
            queryset = queryset.filter(author__id=author)
        if request.query_params.get('is_favorited'):
            queryset = queryset.filter(is_favorited=True)
        if request.query_params.get('is_in_shopping_cart'):
            queryset = queryset.filter(is_in_shopping_cart=True)
        return queryset


class IngredientSearchFilter(filters.SearchFilter):
    search_param = 'name'
