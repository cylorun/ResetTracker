from stats import *

with open("data/palette.json","r") as f:
    guiColors = json.load(f)

# class methods for creating graphs
class Graphs:
    # makes a histogram of a distribution of datapoints
    @classmethod
    def graph1(cls, dist, title, smoothness=0.4, removeX=0, kde=True, min2=0, max2=3600):
        try:
            mean = np.mean(dist)
            new_dist = dist
            if removeX != 0:
                new_dist = Logistics.remove_top_X_percent(dist, removeX)
            new_mean = np.mean(new_dist)
            max1 = max(new_dist)

            if min2 != -1:
                minX = max(min(dist), min2)
            else:
                minX = min(dist)
            if max2 != -1:
                maxX = min(max(dist), max2)
            else:
                maxX = max(dist)
            rangeX = [minX * 0.95, maxX * 1.05]

            dist = [d for d in dist if d >= minX * 0.95 and d <= maxX * 1.05]

            # Set seaborn style

            # Create figure and axis objects
            fig, ax = plt.subplots(figsize=(4, 4))

            ax.set_facecolor(guiColors['background'])
            fig.set_facecolor(guiColors['background'])

            # Plot the KDE distribution
            if kde:
                sns.kdeplot(data=dist, ax=ax, bw_adjust=smoothness, color=guiColors['primary'])
            else:
                n, bins, patches = plt.hist(dist, bins=30, range=rangeX, density=False, color=guiColors['secondary'])
                maxN = max(n)
                sns.despine()

            plt.axvline(mean, color='orange', linestyle='--', ymin=0.15)
            plt.axvline(mean, color='orange', linestyle='--', ymax=0.07)
            ax.text(mean, ax.get_ylim()[1]*0.1, f'μ: {mean:.2f}', ha='left', va='center', color='orange')
            if removeX != 0:
                plt.axvline(new_mean, color='red', linestyle='--', ymin=0.25)
                plt.axvline(new_mean, color='red', linestyle='--', ymax=0.17)
                ax.text(new_mean, ax.get_ylim()[1] * 0.2, f'μ`: {new_mean:.2f}', ha='right', va='center', color='red')
                plt.axvline(max1, color='green', linestyle='--', ymin=0.35)
                plt.axvline(max1, color='green', linestyle='--', ymax=0.27)
                ax.text(max1, ax.get_ylim()[1] * 0.3, f'{(1 - removeX) * 100}th pctl: {max1:.2f}', ha='center', va='center', color='green')

            # Add labels and title
            ax.set_xlabel(title)
            ax.set_title('Distribution of ' + title)

            # Set x-axis limits
            plt.xlim(rangeX)

            return fig
        except Exception as e:
            print(1)
            print(e)
            return 1

    # makes a pie chart given a list of strings
    @classmethod
    def graph2(cls, items):
        try:
            data = {}
            for item in items:
                if item not in data.keys():
                    data[item] = 1
                else:
                    data[item] += 1

            # Set the color scheme
            colors = ['#7fc97f', '#beaed4', '#fdc086', '#ffff99', '#386cb0', '#f0027f']

            # Create a figure and axis object
            fig, ax = plt.subplots(figsize=(4, 3))

            ax.set_facecolor(guiColors['background'])
            fig.set_facecolor(guiColors['background'])

            # Create the pie chart with custom colors and explode values
            wedges, labels, _ = ax.pie(data.values(), colors=colors, explode=[0.05] * len(data), autopct='%1.1f%%',
                                       textprops={'fontsize': 10}, center=(-1, 0))

            # Adjust the center position of the pie chart
            ax.set_xlim(-1.5, 1.5)
            ax.set_ylim(-1.5, 1.5)

            # Add a shadow effect to the wedges
            for wedge in wedges:
                wedge.set_edgecolor('white')
                wedge.set_linewidth(1)
                wedge.set_alpha(0.8)

            # Set the font size for the labels and legend
            plt.setp(labels, fontsize=10)
            plt.legend(data.keys(), loc='center left', bbox_to_anchor=(0.5, 0.5), fontsize=9, framealpha=0.5)

            return fig
        except Exception as e:
            print(2)
            print(e)
            return 1


    # makes a 2-way table showing the frequency of each combination of iron source and entry method
    @classmethod
    def graph4(cls, enters, settings):
        try:
            color1 = 'rgb(120, 205, 255)'
            ironSourceList = []
            entryMethodList = []
            validSourceList = []
            for source in ['Buried Treasure w/ tnt', 'Buried Treasure', 'Full Shipwreck', 'Half Shipwreck', 'Village']:
                if settings['playstyle cont.'][source] == 1:
                    validSourceList.append(source)
            for enter in enters:
                if enter['type'] in validSourceList:
                    ironSourceList.append(enter['type'])
                else:
                    ironSourceList.append('Other')
                entryMethodList.append(enter['method'])
            ironSourceOptionsAll = ['Buried Treasure w/ tnt', 'Buried Treasure', 'Full Shipwreck', 'Half Shipwreck', 'Village', 'Other']
            ironSourceOptionsValid = []
            for i in range(len(ironSourceOptionsAll) - 1):
                if settings['playstyle cont.'][ironSourceOptionsAll[i]] == 1:
                    ironSourceOptionsValid.append(ironSourceOptionsAll[i])
            ironSourceOptionsValid.append('other')
            entryTypeOptions = ['Magma Ravine', 'Lava Pool', 'Obsidian', 'Bucketless']
            colors = n_colors(lowcolor='rgb(255, 200, 200)', highcolor='rgb(200, 0, 0)', n_colors=len(ironSourceList) + 1, colortype='rgb')
            data = []
            fill_color = []

            for i1 in range(len(ironSourceOptionsValid)):
                data.append([])
                fill_color.append([])
                for i2 in range(len(entryTypeOptions)):
                    data[i1].append(0)
                    fill_color[i1].append(0)
            for i in range(len(ironSourceList)):
                ironSource = ironSourceList[i]
                entryMethod = entryMethodList[i]
                index1 = len(ironSourceOptionsValid) - 1
                if ironSource in ironSourceOptionsValid:
                    index1 = ironSourceOptionsValid.index(ironSource)
                index2 = entryTypeOptions.index(entryMethod)
                data[index1][index2] += round(1/len(ironSourceList), 3)

            for i1 in range(len(fill_color)):
                for i2 in range(len(fill_color[i1])):
                    fill_color[i1][i2] = colors[round(data[i1][i2] * len(ironSourceList))]

            for i1 in range(len(data)):
                for i2 in range(len(data[i1])):
                    data[i1][i2] = Logistics.formatValue(data[i1][i2], isPercent=True)

            for i1 in range(len(data)):
                data[i1].insert(0, ironSourceOptionsValid[i1])
                fill_color[i1].insert(0, color1)

            data.insert(0, [''] + entryTypeOptions)
            fill_color.insert(0, ['rgb(100, 100, 100)'] + n_colors(lowcolor=color1, highcolor=color1, n_colors=len(entryTypeOptions), colortype='rgb'))
            fig = go.Figure(data=[go.Table(
                cells=dict(
                    values=data,
                    line_color=fill_color,
                    fill_color=fill_color,
                    align='center', font=dict(color='white', size=11)
                ))
            ])
            fig.update_layout(
                width=400,
                height=400,
                margin=dict(l=20, r=20, t=30, b=20),
                plot_bgcolor=guiColors['background'],
                paper_bgcolor=guiColors['background']
            )
            return fig
        except Exception as e:
            print(4)
            print(e)
            return 1

    # table displaying info about a specific split
    @classmethod
    def graph5(cls, splitData):
        try:
            headers = ['Count', 'Avg', 'Rate', 'Stdev', 'XPH']
            values = [[f"<b>{Logistics.formatValue(splitData['Count'])}</b>"],
                        [f"<b>{Logistics.formatValue(splitData['Cumulative Average'], moe=Logistics.t_int_moe(splitData['Count'], splitData['Cumulative Stdev'], 0.95), isTime=True)}</b>", f"<b>{Logistics.formatValue(splitData['Relative Average'], moe=Logistics.t_int_moe(splitData['Count'], splitData['Relative Stdev'], 0.95), isTime=True)}</b>"],
                        [f"<b>{Logistics.formatValue(splitData['Cumulative Conversion'], isPercent=True)}</b>", f"<b>{Logistics.formatValue(splitData['Relative Conversion'], moe=Logistics.z_int_moe(splitData['Count']/splitData['Relative Conversion'], splitData['Count'], 0.95), isPercent=True)}</b>"],
                        [f"<b>{Logistics.formatValue(splitData['Cumulative Stdev'], isTime=True)}</b>", f"<b>{Logistics.formatValue(splitData['Relative Stdev'], isTime=True)}</b>"],
                        [f"<b>{Logistics.formatValue(splitData['xph'])}</b>"]]
            colors = []
            for i1 in range(len(values)):
                colors.append([])
                for i2 in range(len(values[i1])):
                    color = 'black'
                    if i2 == 1:
                        color = '#5c5c5c'
                    colors[i1].append(color)

            fig = go.Figure(data=[go.Table(
                header=dict(
                    values=headers,
                    line_color='black',
                    fill_color=guiColors['secondary'],  # Use blue for header background color
                    align='center',
                    font=dict(color='white', size=14)
                ),
                cells=dict(
                    values=values,
                    line_color='black',
                    fill_color=guiColors['background'],
                    align='center',
                    font=dict(color=colors, size=12)
                ))
            ])
            fig.update_layout(
                margin=dict(l=20, r=20, t=30, b=20),  # Add some margin around the table
                height=180,
                width=400,
                plot_bgcolor=guiColors['background'],
                paper_bgcolor=guiColors['background']
            )
            return fig
        except Exception as e:
            print(5)
            print(e)
            return 1

    # table display split stats of current session
    @classmethod
    def graph6(cls, currentSession):
        try:
            # Define headers and values for the table
            headers = ['', 'Iron', 'Wood', 'Iron Pickaxe', 'Nether', 'Structure 1', 'Structure 2', 'Nether Exit',
                       'Stronghold', 'End']
            values = [['Count', 'Average', 'Average Split', 'Conversion']
                      ]
            for split in headers[1:]:
                values.append([
                    Logistics.formatValue(currentSession['splits stats'][split]['Count']),
                    Logistics.formatValue(currentSession['splits stats'][split]['Cumulative Average'], isTime=True),
                    Logistics.formatValue(currentSession['splits stats'][split]['Relative Average'], isTime=True),
                    Logistics.formatValue(currentSession['splits stats'][split]['Relative Conversion'], isPercent=True)

                    # Logistics.formatValue(currentSession['splits stats'][split]['Cumulative Average'], moe=Logistics.t_int_moe(currentSession['splits stats'][split]['Count'], currentSession['splits stats'][split]['Cumulative Stdev'], 0.95), isTime=True),
                    # Logistics.formatValue(currentSession['splits stats'][split]['Relative Average'], moe=Logistics.t_int_moe(currentSession['splits stats'][split]['Count'], currentSession['splits stats'][split]['Relative Stdev'], 0.95), isTime=True),
                    # Logistics.formatValue(currentSession['splits stats'][split]['Relative Conversion'], moe=Logistics.z_int_moe(currentSession['splits stats'][split]['Count']/currentSession['splits stats'][split]['Relative Conversion'], currentSession['splits stats'][split]['Count'], 0.95), isPercent=True)
                ])

            # Create the plot
            fig = go.Figure(data=[go.Table(
                header=dict(
                    values=headers,
                    line_color='black',
                    fill_color=guiColors['secondary'],
                    align='center',
                    font=dict(color='white', size=12)
                ),
                cells=dict(
                    values=values,
                    line_color='black',
                    fill_color=guiColors['background'],
                    align='center',
                    font=dict(color=guiColors['secondary'], size=11)
                ))
            ])

            fig.update_layout(
                margin=dict(l=20, r=20, t=20, b=20),
                height=300,
                width=800,
                font=dict(size=12),
                hovermode='closest',
                plot_bgcolor=guiColors['background'],
                paper_bgcolor=guiColors['background']
            )

            return fig
        except Exception as e:
            print(6)
            print(e)
            return 1

    # table displaying general stats of the current session
    @classmethod
    def graph7(cls, currentSession):
        try:
            headers = ['rnph', '% played', 'rpe', 'resets', 'playtime']
            values = [[Logistics.formatValue(currentSession['general stats']['rnph'])],
                        [Logistics.formatValue(currentSession['general stats']['% played'], isPercent=True)],
                        [Logistics.formatValue(currentSession['general stats']['rpe'])],
                        [Logistics.formatValue(currentSession['general stats']['total wall resets'] + currentSession['general stats']['total played'])],
                        [Logistics.formatValue(currentSession['general stats']['total RTA'] + currentSession['general stats']['total wall time'], isTime=True, includeHours=True)]]
            fig = go.Figure(data=[go.Table(
                header=dict(
                    values=headers,
                    fill_color=guiColors['secondary'],  # Use blue for header background color
                    line_color='black',
                    align='center',
                    font=dict(color=guiColors['white'], size=14)
                ),
                cells=dict(
                    values=values,
                    fill_color=guiColors['background'],  # Use white for cell background color
                    line_color='black',
                    align='center',
                    font=dict(color=guiColors['secondary'], size=12)
                ))
            ])
            fig.update_layout(
                margin=dict(l=20, r=20, t=30, b=20),  # Add some margin around the table
                height=150,
                width=400,
                plot_bgcolor=guiColors['background'],
                paper_bgcolor=guiColors['background']
            )
            return fig
        except Exception as e:
            print(7)
            print(e)
            return 1

    # pie chart from dict of numerical data
    @classmethod
    def graph8(cls, data):
        # Set the color scheme
        try:
            colors = ['#7fc97f', '#beaed4', '#fdc086', '#ffff99', '#386cb0', '#f0027f']

            # Create a figure and axis object
            fig, ax = plt.subplots(figsize=(4, 3))
            ax.set_facecolor(guiColors['background'])
            fig.set_facecolor(guiColors['background'])

            # Create the pie chart with custom colors and explode values
            wedges, labels, _ = ax.pie(data.values(), colors=colors, explode=[0.05] * len(data), autopct='%1.1f%%',
                                       textprops={'fontsize': 10}, center=(-1, 0))

            # Adjust the center position of the pie chart
            ax.set_xlim(-1.5, 1.5)
            ax.set_ylim(-1.5, 1.5)

            # Add a shadow effect to the wedges
            for wedge in wedges:
                wedge.set_edgecolor('white')
                wedge.set_linewidth(1)
                wedge.set_alpha(0.8)

            # Set the font size for the labels and legend
            plt.setp(labels, fontsize=10)
            plt.legend(data.keys(), loc='center left', bbox_to_anchor=(0.5, 0.5), fontsize=9, framealpha=0.5)

            return fig
        except Exception as e:
            print(8)
            print(e)
            return 1

    # scatterplot displaying nph and average enter, with a canvas based on efficiency score
    @classmethod
    def graph9(cls, sessions):
        try:
            nph_list = []
            avg_enter_list = []
            profile_list = []
            for i in range(len(sessions['sessions'])):
                if sessions['sessions'][i] != 'All' and 'Latest' not in sessions['sessions'][i]['string']:
                    nph_list.append(sessions['stats'][i]['general stats']['rnph'])
                    avg_enter_list.append(sessions['stats'][i]['splits stats']['Nether']['Cumulative Average'])
                    profile_list.append(sessions['stats'][i]['profile'])

            dict1 = {'nph': nph_list, 'avg_enter': avg_enter_list, 'profile': profile_list}

            fig, ax = plt.subplots(figsize=(6, 4))
            ax.set_facecolor(guiColors['background'])
            fig.set_facecolor(guiColors['background'])

            p2 = sns.scatterplot(x='nph', y='avg_enter', hue='profile', data=dict1, s=60, alpha=0.8, palette='Set1',
                                 edgecolor='none')
            ax.set_xlabel('NPH', fontsize=16)
            ax.set_ylabel('Average Enter', fontsize=16)
            ax.tick_params(axis='both', labelsize=14)
            ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1), title='Profile', fontsize=14, title_fontsize=14)
            plt.tight_layout()
            return fig
        except Exception as e:
            print(9)
            print(e)
            return 1

    # table displaying some nether stats for each enter type
    @classmethod
    def graph10(cls, exitSuccess):
        try:
            header = [''] + list(exitSuccess.keys())
            values = [['Conversion', 'Avg. Enter', 'Avg. Nether Split']]
            for key in exitSuccess.keys():
                row = []
                row.append(Logistics.formatValue(exitSuccess[key]['Exit Conversion'], isPercent=True))
                row.append(Logistics.formatValue(exitSuccess[key]['Average Enter'], isTime=True))
                row.append(Logistics.formatValue(exitSuccess[key]['Average Split'], isTime=True))
                values.append(row)

            fig = go.Figure(data=[go.Table(
                header=dict(
                    values=header,
                    line_color='black',
                    fill_color=guiColors['secondary'],
                    align='center',
                    font=dict(color='white', size=12)
                ),
                cells=dict(
                    values=values,
                    line_color='black',
                    fill_color=guiColors['background'],
                    align='center',
                    font=dict(color=guiColors['secondary'], size=11)
                ))
            ])

            fig.update_layout(
                margin=dict(l=20, r=20, t=20, b=20),
                height=200,
                width=600,
                font=dict(size=12),
                hovermode='closest',
                plot_bgcolor=guiColors['background'],
                paper_bgcolor=guiColors['background']
            )

            return fig
        except Exception as e:
            print(10)
            print(e)
            return 1

    # table displaying general stats of a session
    @classmethod
    def graph11(cls, generalData):
        try:
            headers = ['rnph', 'avg. enter', 'score']
            values = [[Logistics.formatValue(generalData['rnph'], moe=Logistics.xph_int_moe1(generalData['rnph'], len(generalData['enters']), 0.95), isNPH=True)],
                      [Logistics.formatValue(generalData['average enter'], isTime=True)],
                      [Logistics.formatValue(generalData['efficiency score'])]]

            fig = go.Figure(data=[go.Table(
                header=dict(
                    values=headers,
                    line_color='black',
                    fill_color=guiColors['secondary'],  # Use blue for header background color
                    align='center',
                    font=dict(color='white', size=14)
                ),
                cells=dict(
                    values=values,
                    line_color='black',
                    fill_color=guiColors['background'],
                    align='center',
                    font=dict(color=guiColors['secondary'], size=12)
                ))
            ])
            fig.update_layout(
                margin=dict(l=20, r=20, t=30, b=20),  # Add some margin around the table
                height=100,
                width=400,
                plot_bgcolor=guiColors['background'],
                paper_bgcolor=guiColors['background']
            )
            return fig
        except Exception as e:
            print(11)
            print(e)
            return 1

    # table displaying general stats of a session
    @classmethod
    def graph12(cls, generalData):
        try:
            values = [Logistics.formatValue(generalData['total resets']),
                      Logistics.formatValue(generalData['total RTA'] + generalData['total wall time'], isTime=True, includeHours=True),
                      Logistics.formatValue(generalData['% played'], isPercent=True),
                      Logistics.formatValue(generalData['rpe'])]
            headers = ['Resets', 'Playtime', '% played', 'rpe']

            fig = go.Figure(data=[go.Table(
                header=dict(
                    values=headers,
                    line_color='black',
                    fill_color=guiColors['secondary'],  # Use blue for header background color
                    align='center',
                    font=dict(color='white', size=14)
                ),
                cells=dict(
                    values=values,
                    line_color='black',
                    fill_color=guiColors['background'],  # Use white for cell background color
                    align='center',
                    font=dict(color=guiColors['secondary'], size=12)
                ))
            ])
            fig.update_layout(
                margin=dict(l=20, r=20, t=30, b=20),  # Add some margin around the table
                height=100,
                width=400,
                plot_bgcolor=guiColors['background'],
                paper_bgcolor=guiColors['background']
            )
            return fig
        except Exception as e:
            print(12)
            print(e)
            return 1

    # makes a histogram distribution of rta colour coded based on the current split during reset
    @classmethod
    def graph13(cls, igtDist, latestSplits):
        try:
            mappings = {'None': '#D3D3D3', 'Iron': '#000000', 'Wood': '#FF0000', 'Iron Pickaxe': '#00FF00',
                        'Nether': '#0000FF', 'Structure 1': '#FFFF00', 'Structure 2': '#FF00FF', 'Nether Exit': '#00FFFF',
                        'Stronghold': '#C0C0C0', 'End': '#808080'}
            values = list(mappings.values())
            keys = list(mappings.keys())

            data = [[], [], [], [], [], [], [], [], [], []]

            for i in range(len(igtDist)):
                data[keys.index(latestSplits[i])].append(igtDist[i])

            fig, ax = plt.subplots(figsize=(4, 4))
            ax.set_facecolor(guiColors['background'])
            fig.set_facecolor(guiColors['background'])

            plt.hist(data, color=values, stacked=True,
                     bins=np.linspace(0, round(math.sqrt(max(igtDist))) + 1, round(math.sqrt(max(igtDist))) + 2) ** 2)

            # Add labels and title
            plt.xlabel("Value")
            plt.ylabel("Frequency")
            plt.title("Stacked Histogram")
            plt.yscale('log', base=10, subs=range(100))

            # Add legend
            patches = [mpatches.Patch(color=color, label=label) for label, color in mappings.items()]
            plt.legend(handles=patches, loc='upper right')

            return fig
        except Exception as e:
            print(13)
            print(e)
            return 1

    # heatmap or 2d histogram for split showing density of split-to-reset and start-to-split distribution
    @classmethod
    def graph14(cls, data, split):
        try:
            splits = ['Iron', 'Wood', 'Iron Pickaxe', 'Nether', 'Structure 1', 'Structure 2', 'Nether Exit', 'Stronghold',
                      'End']
            splitDist = data['splits stats'][Logistics.get_previous_item(splits, split)]['Cumulative Distribution']
            index = -1
            x = []
            y = []
            for i in range(len(data['general stats']['RTA Distribution'])):
                if data['general stats']['latest split list'][i] in splits[splits.index(split):]:
                    index += 1
                    if data['general stats']['latest split list'][i] == split:
                        split1 = splitDist[index]
                        x.append(split1)
                        y.append(data['general stats']['RTA Distribution'][i] - split1)

            fig, ax = plt.subplots(figsize=(4, 4))

            bins = np.histogram2d(x, y, bins=5)[0]
            sns.heatmap(bins, cmap='Blues')
            plt.xlabel('List 2')
            plt.ylabel('List 1')

            return fig
        except Exception as e:
            print(14)
            print(e)
            return 1

    # table display split stats of selected session
    @classmethod
    def graph15(cls, session):
        try:
            # Define headers and values for the table
            headers = ['', 'Iron', 'Wood', 'Iron Pickaxe', 'Nether', 'Structure 1', 'Structure 2', 'Nether Exit',
                       'Stronghold', 'End']
            values = [['Count', 'Average', 'Average Split', 'Conversion']
                      ]
            for split in headers[1:]:
                values.append([
                    Logistics.formatValue(session['splits stats'][split]['Count']),
                    Logistics.formatValue(session['splits stats'][split]['Cumulative Average'], isTime=True),
                    Logistics.formatValue(session['splits stats'][split]['Relative Average'], isTime=True),
                    Logistics.formatValue(session['splits stats'][split]['Relative Conversion'], isPercent=True)
                ])

            # Create the plot
            fig = go.Figure(data=[go.Table(
                header=dict(
                    values=headers,
                    line_color='black',
                    fill_color=guiColors['secondary'],
                    align='center',
                    font=dict(color='white', size=12)
                ),
                cells=dict(
                    values=values,
                    line_color='black',
                    fill_color=guiColors['background'],
                    align='center',
                    font=dict(color=guiColors['secondary'], size=11)
                ))
            ])

            fig.update_layout(
                margin=dict(l=20, r=20, t=20, b=20),
                height=300,
                width=800,
                font=dict(size=12),
                hovermode='closest',
                plot_bgcolor=guiColors['background'],
                paper_bgcolor=guiColors['background']
            )

            return fig
        except Exception as e:
            print(15)
            print(e)
            return 1

    # plots inverted nph to session timestamp
    @classmethod
    def graph16(cls, date_time, nether):
        try:

            x_list = []
            y_list = []
            start = datetime.strptime(date_time[0], '%Y-%m-%d %H:%M:%S.%f')
            prev = start
            for i in range(len(nether)):
                if nether[i] != '':

                    value = datetime.strptime(date_time[i], '%Y-%m-%d %H:%M:%S.%f')
                    x_list.append((value-start)/timedelta(seconds=1))
                    y_list.append((value-prev)/timedelta(seconds=1))
                    prev = value
            dict1 = {'time since start': x_list, 'time since prev': y_list}

            fig, ax = plt.subplots(figsize=(6, 4))
            ax.set_facecolor(guiColors['background'])
            fig.set_facecolor(guiColors['background'])

            p2 = sns.scatterplot(x='time since start', y='time since prev', data=dict1, s=60, alpha=0.8, palette='Set1',
                                 edgecolor='none')
            ax.set_xlabel('session timeline', fontsize=16)
            ax.set_ylabel('time since last enter', fontsize=16)
            ax.tick_params(axis='both', labelsize=14)
            plt.tight_layout()
            # Calculate slope and margin of error
            confidence_level = 0.95
            slope, margin_of_error = Logistics.slope_int_moe(x_list, y_list, confidence_level)

            # Format the slope and margin of error values
            slope_formatted = '{:.2f}'.format(slope)
            margin_of_error_formatted = '{:.2f}'.format(margin_of_error)

            # Add text with slope and margin of error to the graph
            plt.text(0.5, 0.1, f'Slope: {slope_formatted}\nMargin of Error: {margin_of_error_formatted}',
                     fontsize=12, ha='center', transform=ax.transAxes)
            return fig
        except Exception as e:
            print(e)
            return 1

    # plots slope of subsets from x/y var against z_var
    @classmethod
    def graph17(cls, x_var, y_var, z_var, x_quantity="variable", y_quanity="slope", p_positive=True):
        try:
            slope_list = []
            error_list = []
            p_list = []

            if not(len(x_var) == len(y_var) == len(z_var)):
                raise ValueError

            for x, y, z in zip(x_var, y_var, z_var):
                slope, se = Logistics.slope_int_moe(x, y, 0.95, returnStandard=True)
                _, _, _, p, _ = stats.linregress(x, y)
                if slope < 0 ^ p_positive:
                    p_prime = p/2
                else:
                    p_prime = 1 - p/2

                slope_list.append(slope)
                error_list.append(se)
                p_list.append(p_prime)

            x_list = z_var
            if y_quanity == "slope":
                y_list = slope_list
            elif y_quanity == "p":
                y_list = p_list

            if y_quanity == "slope":
                x1 = sm.add_constant(z_var)
                y1 = y_list
                wls_model = sm.WLS(y1, x1, weights=[1/error for error in error_list])
                results = wls_model.fit()
                p_value = results.pvalues[1]
            elif y_quanity == "p":
                _, _, _, p_value, _ = stats.linregress(x_list, y_list)

            dict1 = {x_quantity: x_list, y_quanity: y_list}

            fig, ax = plt.subplots(figsize=(6, 4))
            ax.set_facecolor(guiColors['background'])
            fig.set_facecolor(guiColors['background'])

            p2 = sns.scatterplot(x=x_quantity, y=y_quanity, data=dict1, s=60, alpha=0.8, palette='Set1',
                                 edgecolor='none')
            ax.set_xlabel(x_quantity, fontsize=16)
            ax.set_ylabel(y_quanity, fontsize=16)
            ax.tick_params(axis='both', labelsize=14)
            plt.tight_layout()
            # Calculate slope and margin of error

            # Format the slope and margin of error values
            p_value_formatted = '{:.3f}'.format(p_value)

            if y_quanity == "slope":
                plt.errorbar(z_var, slope_list, yerr=error_list, fmt='o', capsize=3)

            # Add text with slope and margin of error to the graph
            plt.text(0.5, 0.1, f'p-value: {p_value_formatted}',
                     fontsize=12, ha='center', transform=ax.transAxes)
            return fig
        except Exception as e:
            print(e)
            return 1
