from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from pathlib import Path


def _calc_divisional_range(filesize, chuck=10):
    step = filesize//chuck
    arr = list(range(0, filesize, step))
    result = []
    for i in range(len(arr)-1):
        s_pos, e_pos = arr[i], arr[i+1]-1
        result.append([s_pos, e_pos])
    result[-1][-1] = filesize-1
    return result


def _range_download(url, save_name, s_pos, e_pos):
    headers = {"Range": f"bytes={s_pos}-{e_pos}"}
    res = requests.get(url, headers=headers, stream=True)
    with open(save_name, "rb+") as f:
        f.seek(s_pos)
        for chunk in res.iter_content(chunk_size=1024*1024):
            if chunk:
                f.write(chunk)


def download(url, filename):
    res = requests.head(url)
    filesize = int(res.headers['Content-Length'])
    divisional_ranges = _calc_divisional_range(filesize)
    if isinstance(filename, str):
        output_file = Path(filename)
    elif isinstance(filename, Path):
        output_file = filename
    else:
        output_file = Path('./output')
    output_file.touch()
    with ThreadPoolExecutor() as p:
        futures = []
        for s_pos, e_pos in divisional_ranges:
            futures.append(p.submit(_range_download, url, filename, s_pos, e_pos))
        as_completed(futures)
    return output_file
