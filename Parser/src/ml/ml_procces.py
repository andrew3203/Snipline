from concurrent.futures import ProcessPoolExecutor

def go(data: list[dict]) -> list[dict]:
    from src.ml.ml import parse
    return parse(data)

def run_ml(data: list[dict]) -> list[dict]:
    with ProcessPoolExecutor(max_workers=1) as executor:
        future = executor.submit(go, data)
        try:
            return future.result()
        except Exception as e:
            print(e)
    return []