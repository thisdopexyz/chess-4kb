#!/usr/bin/env python3
import os, sys

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'engine.py')
    path = os.path.abspath(path)
    if not os.path.exists(path):
        print(f'MISSING: {path}')
        return 1
    n = os.path.getsize(path)
    limit = 4096
    status = 'OK' if n <= limit else 'OVER'
    print(f'{path}: {n} bytes [{status}] (limit {limit})')
    return 0 if n <= limit else 2

if __name__ == '__main__':
    raise SystemExit(main())
