from rest_framework.pagination import PageNumberPagination


class LimitPagination(PageNumberPagination):
    """
    Пагинация для API по 10 элементов на страницу через limit
    """
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 100