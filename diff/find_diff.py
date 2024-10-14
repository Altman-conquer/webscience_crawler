def read(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read().splitlines()

    return set(data)

def diff(set_a, set_b):
    return set_a - set_b

def main():
    a = read('1.txt')
    b = read('2.txt')
    print(diff(a, b))

if __name__ == '__main__':
    main()