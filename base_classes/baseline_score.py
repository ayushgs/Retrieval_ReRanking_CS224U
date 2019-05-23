class BaselineScorer(AScorer):
    def __init__(self, idf):
        super().__init__(idf)
    
    def get_sim_score(self, q, d):
        score = 0
        if d.body_hits is not None:
            for term in d.body_hits.keys():
                score += len(d.body_hits[term])
        return score
