def chunkify(data: list, num_chunks: int) -> list[list]:
    k, m = divmod(len(data), num_chunks)
    return [data[i*k + min(i, m):(i+1)*k + min(i+1, m)] for i in range(num_chunks)]