import tabula
import pandas as pd


# %%

def convert_to_csv(fpath, tt_start, tt_end, save_to='./timetable.csv'):
    pages = list(range(tt_start, tt_end + 1))
    tabula.convert_into(fpath, save_to, pages=pages)


def preprocess_csv(save_to='./timetable_mod.csv', fpath='./timetable.csv', nrows=None):
    df = pd.read_csv(fpath, nrows=nrows)
    # print(df)

    col_name = 'COM\rCOD'
    # [L, P, U] row is the 0th row
    rows_to_drop = [0]
    for idx, row in df.iterrows():
        if row[col_name] == col_name:
            rows_to_drop.append(idx)
            rows_to_drop.append(idx + 1)
            # print(idx)

    df_mod = df.drop(index=rows_to_drop)
    # print(df_mod)

    col_labels = ['COMCOD', 'COURSE_NO', 'COURSE_TITLE', 'CREDIT_L', 'CREDIT_P', 'CREDIT', 'SEC',
                  'INSTRUCTORS', 'ROOM', 'DAYS_&_HOURS', 'COMMON_HOUR', 'COMPRE_DATE_&_SESSION']

    df_mod.set_axis(col_labels, axis=1, inplace=True)

    cols_to_drop = ['CREDIT_L', 'CREDIT_P']
    df_mod = df_mod.drop(columns=cols_to_drop)

    for idx, rows in df.iterrows():
        for col in df.columns.tolist():
            if isinstance(rows[col], str):
                df.at[idx, col] = df.iloc[idx][col].replace('\r', '')

    df_mod.to_csv(save_to, index=False)


def create_course_table(txt_to='./tt_course.txt', csv_to='./tt_course.csv', fpath='./timetable_mod.csv',
                        nrows=None):
    df = pd.read_csv(fpath, nrows=nrows)
    # print(df)

    # creating course table dataframe
    columns_to_drop = ['SEC', 'INSTRUCTORS', 'ROOM', 'DAYS_&_HOURS', 'COMMON_HOUR']
    df.drop(columns=columns_to_drop, inplace=True)

    col_name = 'COMCOD'
    rows_to_drop = []
    for idx, rows in df.iterrows():
        if pd.isna(rows[col_name]):
            rows_to_drop.append(idx)
    # print(rows_to_drop)
    df.drop(index=rows_to_drop, inplace=True)
    # print(df)

    df.to_csv(csv_to, index=False)

    with open(txt_to, 'w') as f:
        cols = df.columns.tolist()
        for idx, rows in df.iterrows():
            if pd.isna(rows[-1]):
                print("({}, '{}', '{}', {}, NULL)".format(int(rows[cols[0]]), rows[cols[1]],
                                                          rows[cols[2]].replace('\r', ' '), int(rows[cols[3]])),
                      end='', file=f)
            else:
                print("({}, '{}', '{}', {}, '{}')".format(int(rows[cols[0]]), rows[cols[1]],
                                                          rows[cols[2]].replace('\r', ' '), int(rows[cols[3]]),
                                                          rows[cols[4]]), end='', file=f)
            if idx == df.index[-1]:
                print(';', file=f)
            else:
                print(',', file=f)


def create_schedule_table(txt_to='./tt_schedule.txt', csv_to='./tt_schedule.csv', fpath='./timetable_mod.csv',
                          nrows=None):
    df = pd.read_csv(fpath, nrows=nrows)
    # print(df)

    # creating schedule table dataframe
    columns_to_drop = ['COURSE_NO', 'COURSE_TITLE', 'CREDIT', 'INSTRUCTORS', 'COMMON_HOUR', 'COMPRE_DATE_&_SESSION']
    df.drop(columns=columns_to_drop, inplace=True)

    col_name = 'COMCOD'
    for idx, rows in df.iterrows():
        if pd.isna(rows[col_name]):
            df.at[idx, col_name] = df.iloc[idx - 1][col_name]
    # print(df)

    col_name = 'SEC'
    rows_to_drop = []
    for idx, rows in df.iterrows():
        if pd.isna(rows[col_name]):
            rows_to_drop.append(idx)
    # print(rows_to_drop)
    df.drop(index=rows_to_drop, inplace=True)
    # print(df)

    df.to_csv(csv_to, index=False)

    last_row_idx = df.index[-1]
    for val in reversed(df.index):
        if pd.notna(df.loc[val]['SEC']):
            last_row_idx = val
            break
    # print(last_row_idx, df.loc[last_row_idx])

    with open(txt_to, 'w') as f:
        cols = df.columns.tolist()
        for idx, rows in df.iterrows():
            if pd.isna(rows['SEC']):
                continue
            if pd.isna(rows['ROOM']) and pd.isna(rows['DAYS_&_HOURS']):
                print("({}, '{}', NULL, NULL)".format(int(rows[cols[0]]), rows[cols[1]]),
                      end='', file=f)
            elif pd.isna(rows['ROOM']):
                print("({}, '{}', NULL, '{}')".format(int(rows[cols[0]]), rows[cols[1]], rows[cols[3]]),
                      end='', file=f)
            elif pd.isna(rows['DAYS_&_HOURS']):
                print("({}, '{}', {}, NULL)".format(int(rows[cols[0]]), rows[cols[1]], int(rows[cols[2]])),
                      end='', file=f)
            else:
                print("({}, '{}', {}, '{}')".format(int(rows[cols[0]]), rows[cols[1]], int(rows[cols[2]]),
                                                    rows[cols[3]]), end='', file=f)

            if idx == last_row_idx:
                print(';', file=f)
            else:
                print(',', file=f)


def create_instructors_id(txt_to='./tt_instNames.txt', fpath='./timetable_mod.csv', nrows=None):
    df = pd.read_csv(fpath, nrows=nrows)
    instructors = df['INSTRUCTORS'].unique().tolist()
    instructors = sorted(instructors)

    instId = {}
    with open(txt_to, 'w') as f:
        for id in range(len(instructors)):
            inst = instructors[id]
            instId[inst] = id + 1
            print("({}, '{}')".format(id + 1, inst.replace('\r', '')), end='', file=f)
            if inst == instructors[-1]:
                print(';', file=f)
            else:
                print(',', file=f)

    return instId


def create_instructors_table(instId, txt_to='./tt_instructors.txt', csv_to='./tt_instructors.csv',
                             fpath='./timetable_mod.csv',
                             nrows=None):
    df = pd.read_csv(fpath, nrows=nrows)
    # print(df)

    # creating instructors table dataframe
    columns_to_drop = ['COURSE_NO', 'COURSE_TITLE', 'CREDIT', 'ROOM', 'DAYS_&_HOURS', 'COMMON_HOUR',
                       'COMPRE_DATE_&_SESSION']
    df.drop(columns=columns_to_drop, inplace=True)

    col_names = ['COMCOD', 'SEC']
    for idx, rows in df.iterrows():
        for col in col_names:
            if pd.isna(rows[col]):
                df.at[idx, col] = df.iloc[idx - 1][col]
    # print(df)

    df.to_csv(csv_to, index=False)

    with open(txt_to, 'w') as f:
        cols = df.columns.tolist()
        for idx, rows in df.iterrows():
            print("({}, '{}', {})".format(int(rows[cols[0]]), rows[cols[1]], instId[rows[cols[2]]]), end='', file=f)
            if idx == df.index[-1]:
                print(';', file=f)
            else:
                print(',', file=f)


def create_sql_script(mergedScript='./timetable_script.sql', schemaScript='./sql_schema_script.txt',
                      sqlEntries='./sql_entries.txt', tt_course='./tt_course.txt', tt_schedule='./tt_schedule.txt',
                      tt_instNames='./tt_instNames.txt', tt_instructors='./tt_instructors.txt'):

    # merging sql entries

    with open(tt_course, 'r') as f:
        with open(sqlEntries, 'w') as f1:
            print("insert  into `Course`(`comcod`,`courseName`,`courseTitle`,`credit`,`compreSch`) values", file=f1)
            for line in f:
                f1.write(line)
            print("\n", file=f1)

    with open(tt_schedule, 'r') as f:
        with open(sqlEntries, 'a') as f1:
            print("insert  into `Schedule`(`comcod`,`section`,`room`, `time`) values", file=f1)
            for line in f:
                f1.write(line)
            print("\n", file=f1)

    with open(tt_instNames, 'r') as f:
        with open(sqlEntries, 'a') as f1:
            print("insert  into `InstNames`(`insID`, `profName`) values", file=f1)
            for line in f:
                f1.write(line)
            print("\n", file=f1)

    with open(tt_instructors, 'r') as f:
        with open(sqlEntries, 'a') as f1:
            print("insert  into `Instructors`(`comcod`,`section`,`profId`) values", file=f1)
            for line in f:
                f1.write(line)
            print("\n", file=f1)

    # merging both sql and schema script

    with open(schemaScript, 'r') as f:
        with open(mergedScript, 'w') as f1:
            for line in f:
                f1.write(line)
            print("\n", file=f1)

    with open(sqlEntries, 'r') as f:
        with open(mergedScript, 'a') as f1:
            for line in f:
                f1.write(line)
            print("\n", file=f1)


# %%

# input parameters
ttfpath = './Timetable_06_Nov_2021.pdf'
tt_start = 12
tt_end = 70

# %%

convert_to_csv(ttfpath, tt_start, tt_end)
preprocess_csv()

# %%

create_course_table()
create_schedule_table()
instId = create_instructors_id()
create_instructors_table(instId)

# %%

create_sql_script()

