import threading

ranges = [
    [10, 20],
    [1, 5],
    [70, 80],
    [27, 92],
    [0, 16]
]
n = len(ranges)

result = [0] * n

threads = []

def runner(thread_id, start, end, result):
    r = range(start, end+1)
    s = sum(r)
    result[thread_id] = s


for i in range(n):
    (start, end) = ranges[i]
    t = threading.Thread(target = runner, args = (i, start, end, result))
    t.start()
    threads.append(t)


for t in threads:
    t.join()

print(result)
print(sum(result))
