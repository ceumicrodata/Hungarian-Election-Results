import unicodecsv
import sys

OUTPUT_FIELDS = 'name,party,year,county,city,votes,win,round'.split(',')
OUTPUT_FILE = sys.stdout

writer = unicodecsv.DictWriter(OUTPUT_FILE, OUTPUT_FIELDS)
writer.writeheader()

year2evktet_file = dict([('1990', 'evktet.txt'),
                         ('1994', 'oevk_jkv_tetel.txt'),
                         ('1998', 'evktet.txt'),
                         ('2002', 'egy_ert.txt'),
                         ('2006', 'egy_ert.txt'),
                         ('2010', 'egy_ert.txt'),
                         ])

year2szkf_file = dict([('1990', 'szkf.txt'),
                       ('1994', 'szkf.txt'),
                       ('1998', 'szkf.txt')
                       ])


def read_rows_from_raw_election_file(filename):
    with open(filename, 'rb') as file:
        rows = []
        for row in file:
            row = row.decode('utf-8')
            rows.append(map(lambda x: ' '.join(x.split()), row.split('|')))
    return rows


def normalize_name(string):
    pass


def code2winner_1990_1998_sooborsa(evktet):
    code2winner = [{}, {}, {}]
    for row in evktet:
        r = int(row[0])
        key = '+'.join([row[1], row[3]])
        value = ' '.join(row[6].split()) + '\t' + row[7]
        if key in code2winner[r]:
            if int(code2winner[r][key].split('\t')[1]) < int(row[7]):
                code2winner[r][key] = value
        else:
            code2winner[r][key] = value
    return code2winner


def code2city_1990_1998_sooborsa(szkf):
    code2city = {}
    for line in szkf:
        if not line[0].startswith('Egy'):
            continue
        key = '+'.join([line[2], line[7]])
        value = [line[5], line[6]]
        code2city[key] = value
    code2city['01+01'][1] = code2city['01+01'][1].replace('II', 'I')
    return code2city


def write_rows_1990_1998(year, evktet, code2winner, code2city, writer):
    for row in evktet:
        key = '+'.join([row[1], row[3]])
        won = '0'
        if key in code2winner[2]:
            if row[0] <> '1':
                if code2winner[2][key].split('\t')[0] == ' '.join(row[6].split()):
                    won = '1'
        else:
            if code2winner[1][key].split('\t')[0] == ' '.join(row[6].split()):
                won = '1'
        outrow = dict()
        name = ' '.join(' '.join([row[5], row[6]]).split())
        outrow['name'] = name.title()
        outrow['party'] = row[8]
        outrow['year'] = year
        outrow['county'] = code2city[key][0]
        outrow['city'] = code2city[key][1]
        outrow['votes'] = int(row[7])
        outrow['win'] = won
        outrow['round'] = row[0]
        writer.writerow(outrow)


def code2winner_2002_2010_sooborsa(egy_erf):
    egy_erf_eredmenyes = filter(lambda x: 's eredm' in x[17], egy_erf)
    code2winner = dict()
    for row in egy_erf_eredmenyes:
        key = '+'.join([row[0], row[1]])
        name = ' '.join(' '.join(row[20:23]).split())
        code2winner[key] = name.title()
    return code2winner


def write_rows_2002_2010(year, evktet, code2winner, code2city, writer, round):
    for row in evktet:
        key = '+'.join([row[0], row[1]])
        name = ' '.join(' '.join(row[3:6]).split()).title()
        won = '0'
        if key in code2winner:
            if code2winner[key] == name:
                won = '1'
        outrow = dict()
        outrow['name'] = name
        outrow['party'] = row[8]
        outrow['year'] = year
        outrow['county'] = code2city[key][0]
        outrow['city'] = code2city[key][1]
        outrow['votes'] = int(row[6])
        outrow['win'] = won
        outrow['round'] = round
        writer.writerow(outrow)


for year in '1990,1994,1998'.split(','):
    szkf_file = '{}/{}/{}'.format('parliamentary', year, 'szkf.txt')
    szkf = read_rows_from_raw_election_file(szkf_file)
    evktet_file = '{}/{}/{}'.format('parliamentary', year, year2evktet_file[year])
    evktet = read_rows_from_raw_election_file(evktet_file)
    if year == '1998':
        evktet = map(lambda x: x[:5] + [''] + x[5:], evktet)
    if year == '1990':
        evktet = map(lambda x: x[:4] + [''] + x[4:], evktet)
        evktet = map(lambda x: x[:5] + [''] + x[6:], evktet)  # remove Dr.
    code2winner = code2winner_1990_1998_sooborsa(evktet)
    code2city = code2city_1990_1998_sooborsa(szkf)
    write_rows_1990_1998(year, evktet, code2winner, code2city, writer)


for year in '2002,2006,2010'.split(','):
    for round in '1,2'.split(','):
        egy_erf_file = '{}/{}/txt_{}ford/{}'.format('parliamentary', year, round, 'egy_erf.txt')
        egy_erf = read_rows_from_raw_election_file(egy_erf_file)
        if year == '2010':
            egy_erf = map(lambda x: x[:9] + [''] + x[9:13] + [''] + x[13:], egy_erf)
        if year == '2002':
            egy_erf = map(lambda x: x[:14] + ['', '', ''] + x[14:] + [''], egy_erf)

        code2city = dict(map(lambda x: ('+'.join([x[0], x[1]]), (x[2], x[3])), egy_erf))
        code2winner = code2winner_2002_2010_sooborsa(egy_erf)

        evktet_file = '{}/{}/txt_{}ford/{}'.format('parliamentary', year, round, year2evktet_file[year])
        evktet = read_rows_from_raw_election_file(evktet_file)
        if year == '2002':
            evktet = map(lambda x: x[:5] + [''] + x[5:], evktet)

        write_rows_2002_2010(year, evktet, code2winner, code2city, writer, round)