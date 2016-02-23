import sys
import grequests
from tqdm import tqdm

url = "http://protector:8888/"
NUM_PARALLEL_REQUESTS = 10


def batches(iterable, n=1):
    """
    From http://stackoverflow.com/a/8290508/270334
    :param n:
    :param iterable:
    """
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]


def exception_handler(request, exception):
    print("{} failed: {} ".format(request.kwargs, exception))


failed_requests = []
with open(sys.argv[1]) as f:
    lines = f.readlines()

for batch in tqdm(batches(lines, NUM_PARALLEL_REQUESTS)):
    request_set = set()
    for line in batch:
        query = line.strip()
        payload = {'q': query}
        r = grequests.get(url, params=payload)
        request_set.add(r)
    responses = grequests.map(request_set, exception_handler=exception_handler)
    for response in responses:
        # Yes, we really need to check for None here,
        # because a HTTP error 400 is also evaluated as False
        if response is None:
            continue
        if response.status_code != 200:
            failed_requests.append(response.text)

print("Request summary")
print("---------------")
for response in sorted(failed_requests):
    print(response)
