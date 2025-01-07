import numpy as np


class SemanticRouter():
    def __init__(self, embedding, routes):
        self.routes = routes
        self.embedding = embedding
        self.routesEmbedding = {}

        for route in self.routes:
            self.routesEmbedding[
                route.name
            ] = self.embedding.encode(route.samples)

    def get_routes(self):
        return self.routes

    def guide(self, query):
        queryEmbedding = self.embedding.encode([query])
        queryEmbedding = queryEmbedding / np.linalg.norm(queryEmbedding)
        scores = []

        # Calculate the cosine similarity of the query embedding with the sample embeddings of the router.

        for route in self.routes:
            routesEmbedding = self.routesEmbedding[route.name] / np.linalg.norm(self.routesEmbedding[route.name])
            score = np.mean(np.dot(routesEmbedding, queryEmbedding.T).flatten())
            scores.append((score, route.name))

        scores.sort(reverse=True)
        return scores[0]
    
if __name__ == "__main__":
    import sys
    sys.path.append('../../../demo-5')

    from modules.embeddings import STEmbedding
    from modules.routers import Route
    from modules.routers import specials, chitchats


    modelEmbeding = STEmbedding()
    specialRoute = Route(name='specials', samples=specials)
    chitchatRoute = Route(name='chitchats', samples=chitchats)
    semanticRouter = SemanticRouter(modelEmbeding, routes=[specialRoute, chitchatRoute])

    query = 'Bạn tên là gì?'

    guidedRoute = semanticRouter.guide(query)[1]
    if guidedRoute == 'specials':
        print("Guide to RAGs")
    else:
        print("Guide to LLMs")