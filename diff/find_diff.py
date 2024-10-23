import pandas as pd


def read(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read().splitlines()

    return set(data)

def diff(set_a, set_b):
    return set_a - set_b

def main():
    df = pd.read_excel('../output/SINet_A_Scale_Insensitive_Convolutional_Neural_Network_for_Fast_Vehicle_Detection.xlsx', header=None)
    a = set(df.iloc[:, 0].to_list())
    # a = read('1.txt')
    b = read('2.txt')
    diff_result = diff(a, b)
    print(diff_result)

    remove_index = []
    for index, row in df.iterrows():
        if row[0] in diff_result:
            remove_index.append(index)

    df.drop(remove_index, inplace=True)
    df.to_excel('../output/result.xlsx', header=None, index=None)

def test():
    for i in range(24):
        print(i + 1)

if __name__ == '__main__':
    # main()
    test()