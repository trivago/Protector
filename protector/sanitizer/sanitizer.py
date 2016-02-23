import urllib


class Sanitizer(object):
    @staticmethod
    def sanitize(query):
        """
        Prepared raw query for parsing
        :param query: The query to sanitize
        """
        query = urllib.unquote(query).decode('string_escape')
        return query.lower()
