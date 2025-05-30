import Amazon
import Flipcart
import Myntra
import concurrent.futures

"""
    URL formats for direct search page :

f'https://flipkart.com/search?q={query}'
f'https://www.amazon.in/s?k={query}'
f'https://www.myntra.com/{query}?rawQuery={query}'

# fetch methode of Amazon, Flipkart, Myntra can have url= and/or Query= {except amazon with additional pc = pincode}
# if not provided, it asks on console _ viz Not recommended.
"""

def whatosearch():
    q = input("Which Product to compre (bulk search as of now) : ").strip()
    if q == '' or q == None or q == '0':
        q1 = input("What to Search on AMazon   : ").strip()
        q2 = input("What to Search on Flipkart : ").strip()
        q3 = input("What to Search on Myntra   : ").strip()
    else :
        q1 = q2 = q3 = q
    if all([q1, q2, q3]) :
        asign(q1=q1, q2=q2, q3=q3)
    else :
        raise ValueError("1 or more query was found Empty.")

def run_fetch(func, args, kwargs):
    return func(*args, **kwargs)

def asign(q1, q2, q3) -> None:
    global jobs
    jobs = [
        (Amazon.fetch, (), {'Query':f'{q1}'}), 
        (Flipcart.fetch, (), {'Query':f'{q2}'}),
        (Myntra.fetch, (), {'Query':f'{q3}'})
    ]
    run_parallel(jobs)

def run_parallel(jobs) :
    res = []
    with concurrent.futures.ProcessPoolExecutor() as executor :
        futures = [executor.submit(run_fetch, func, args, kwargs) for func, args, kwargs in jobs]
        for future in concurrent.futures.as_completed(futures):
            res.append(future.result())
    print(*res, sep='\n\n\n\n *********** \n\n\n\n')
    return

if __name__ == '__main__' :
    whatosearch()