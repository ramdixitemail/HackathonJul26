class RetrievalAgent:
    def contains_nodes(self, rows):

        for row in rows:

            for value in row.values():

                if hasattr(value, "labels"):
                    return True

        return False

    def rows_to_text(self, rows):

        result = []

        for row in rows:

            d = {}

            for key, value in row.items():

                try:
                    d[key] = dict(value)
                except Exception:
                    d[key] = value

            result.append(d)

        return str(result)

    def to_context(self, rows):

        context = []

        for row in rows:

            d = {}

            for key,value in row.items():

                # Neo4j Node
                if hasattr(value,"labels"):

                    d[key]=dict(value)

                # Neo4j Relationship
                elif hasattr(value,"type"):

                    d[key]=dict(value)

                else:

                    d[key]=value

            context.append(d)

        return str(context)