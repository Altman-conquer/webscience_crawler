import os.path

import pandas as pd

meetings_set = None

def get_all_ccfa_meetings():
    global meetings_set
    if meetings_set is not None:
        return meetings_set

    if os.path.exists('ccf/ccf_meetings.xlsx') is True:
        meetings = pd.read_excel('ccf/ccf_meetings.xlsx')
    elif os.path.exists('ccf_meetings.xlsx') is True:
        meetings = pd.read_excel('ccf_meetings.xlsx')
    else:
        raise FileNotFoundError('ccf_meetings.xlsx not found')

    names = [str(i).lower() for i in meetings['全称'].tolist()]
    if meetings_set is None:
        meetings_set = set(names)
    return meetings_set

def main():
    names = get_all_ccfa_meetings()

    with open('./input.txt', 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if line.lower() in names:
                print('CCF A')

if __name__ == '__main__':
    main()