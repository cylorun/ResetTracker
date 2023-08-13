from utils import *

headerLabels = ['Date and Time', 'Iron Source', 'Enter Type', 'Gold Source', 'Spawn Biome', 'RTA', 'Wood',
                'Iron Pickaxe', 'Nether', 'Bastion', 'Fortress', 'Nether Exit', 'Stronghold', 'End', 'Retimed IGT',
                'IGT', 'Gold Dropped', 'Blaze Rods', 'Blazes', '', '', '', '', '', '', 'Iron', 'Wall Resets Since Prev',
                'Played Since Prev', 'RTA Since Prev', 'Break RTA Since Prev', 'Wall Time Since Prev', 'Session Marker',
                'RTA Distribution', 'seed', 'Diamond Pick', 'Pearls Thrown', 'Deaths',
                'Obsidian Placed', 'Diamond Sword', 'Blocks Mined']


class Stats:
    @classmethod
    def fixCSV(cls):
        file_path = 'data/stats.csv'
        temp_file_path = tempfile.NamedTemporaryFile(mode='w', delete=False).name
        with open(file_path, 'r') as file, open(temp_file_path, 'w', newline='') as temp_file:
            reader = csv.reader(file)
            writer = csv.writer(temp_file)
            flag = False
            for row in reader:
                output_row = []
                if not flag:
                    for value in row:
                        if re.match(r'^\d{2}:\d{2}:\d{2}$', value):
                            value += '.000000'
                        elif re.match(r'^\d{2}:\d{2}:\d{2}\.\d{6}$', value):
                            flag = True
                        output_row.append(value)
                else:
                    output_row = row
                if len(output_row) == 34:
                    output_row = output_row[:19] + [""] * 6 + output_row[25:] + output_row[19:25]
                writer.writerow(output_row)

        # Replace the original file with the modified one
        shutil.move(temp_file_path, file_path)

    @classmethod
    def fixSheet(cls, wks):
        try:
            length = wks.cols
            extra_cols = []
            if length == 33:
                extra_cols.append(['seed'] + [""] * (wks.rows - 1))
            if 33 <= length <= 34:
                for i in range(20, 26):
                    extra_cols.append(wks.get_col(i))
                    wks.update_col(i, [""] * wks.rows)
            for i in range(length, length + len(extra_cols)):
                wks.insert_cols(col=i, number=1, values=[extra_cols[i - length]], inherit=True)
        except Exception as e:
            print(e)
            return




