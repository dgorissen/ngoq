'''
Created on 3 Dec 2011

@author: dgorissen
'''
import functools

class Counter(dict):
    'Mapping where default values are zero'
    def __missing__(self, key):
        return 0


def lfu_cache(maxsize=100):
    '''Least-frequenty-used cache decorator.

    Arguments to the cached function must be hashable.
    Cache performance statistics stored in f.hits and f.misses.
    Clear the cache with f.clear().
    http://en.wikipedia.org/wiki/Least_Frequently_Used

    '''
    def decorating_function(user_function):
        cache = {}                      # mapping of args to results
        use_count = Counter()           # times each key has been accessed
        kwarg_mark = object()             # separate positional and keyword args

        @functools.wraps(user_function)
        def wrapper(*args, **kwargs):
            key = args
            if kwargs:
                key += (kwarg_mark,) + tuple(sorted(kwargs.items()))

            # get cache entry or compute if not found
            try:
                result = cache[key]
                use_count[key] += 1
                wrapper.hits += 1
            except KeyError:
                # need to add something to the cache, make room if necessary
                if len(cache) == maxsize:
                    for k, _ in nsmallest(maxsize // 10 or 1,
                                            use_count.iteritems(),
                                            key=itemgetter(1)):
                        del cache[k], use_count[k]
                cache[key] = user_function(*args, **kwargs)
                result = cache[key]
                use_count[key] += 1
                wrapper.misses += 1
            return result

        def clear():
            cache.clear()
            use_count.clear()
            wrapper.hits = wrapper.misses = 0

        wrapper.hits = wrapper.misses = 0
        wrapper.clear = clear
        wrapper.cache = cache
        return wrapper
    return decorating_function


if __name__ == '__main__':
    pass