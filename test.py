def bestof(candidates, valuation_func, filter_func = lambda x:True):
    return(max([(x, valuation_func(x)) for x in filter(filter_func, candidates)],key=lambda y: y[1])[0])



