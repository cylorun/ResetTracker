import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from plotly.colors import n_colors
import matplotlib.patches as mpatches

from stats import *


# class methods for creating graphs
class Graphs:
    # makes a kde histogram of a distribution of datapoints
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
            sns.set_style("whitegrid")

            # Create figure and axis objects
            fig, ax = plt.subplots(figsize=(4, 4))

            # Plot the KDE distribution
            if kde:
                sns.kdeplot(data=dist, ax=ax, bw_adjust=smoothness, color='#FF1493')
            else:
                n, bins, patches = plt.hist(dist, bins=30, range=rangeX, density=False)
                maxN = max(n)
                sns.despine()

            plt.axvline(mean, color='orange', linestyle='--', ymin=0.15)
            plt.axvline(mean, color='orange', linestyle='--', ymax=0.07)
            ax.text(mean, ax.get_ylim()[1]*0.1, f'μ: {mean:.2f}', ha='left', va='center', color='#FFC68C')
            if removeX != 0:
                plt.axvline(new_mean, color='green', linestyle='--', ymin=0.25)
                plt.axvline(new_mean, color='green', linestyle='--', ymax=0.17)
                ax.text(new_mean, ax.get_ylim()[1] * 0.2, f'μ`: {new_mean:.2f}', ha='right', va='center', color='#90EE90')
                plt.axvline(max1, color='blue', linestyle='--', ymin=0.35)
                plt.axvline(max1, color='blue', linestyle='--', ymax=0.27)
                ax.text(max1, ax.get_ylim()[1] * 0.3, f'{(1 - removeX) * 100}th pctl: {max1:.2f}', ha='center', va='center', color='#ADD8E6')

            # Add labels and title
            ax.set_xlabel(title)
            ax.set_title('Distribution of ' + title)

            # Set x-axis limits
            plt.xlim(rangeX)

            return fig
        except Exception as e:
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
            fig, ax = plt.subplots(figsize=(3, 3))

            # Create the pie chart with custom colors and explode values
            wedges, labels, _ = ax.pie(data.values(), colors=colors, explode=[0.05] * len(data), autopct='%1.1f%%',
                                       textprops={'fontsize': 10})

            # Add a shadow effect to the wedges
            for wedge in wedges:
                wedge.set_edgecolor('white')
                wedge.set_linewidth(1)
                wedge.set_alpha(0.8)

            # Set the font size for the labels and legend
            plt.setp(labels, fontsize=10)
            plt.legend(data.keys(), loc=1, fontsize=10)

            return fig
        except Exception as e:
            print(e)
            return 1

    # makes a table for relevant information of a split
    @classmethod
    def graph3(cls, splitStats):
        try:
            header = dict(values=['Count', 'Avg.', 'Avg. Split', 'Rate'],
                          fill_color='#C2D4FF',
                          align=['center'],
                          font=dict(color='black', size=14),
                          height=40
                          )
            cells = dict(values=[[Logistics.formatValue(splitStats['Count'])],
                                 [Logistics.formatValue(splitStats['Cumulative Average'], isTime=True)],
                                 [Logistics.formatValue(splitStats['Relative Average'], isTime=True)],
                                 [Logistics.formatValue(splitStats['Relative Conversion'], isPercent=True)]
                                 ],
                         fill_color='#F2F2F2',
                         align=['center'],
                         font=dict(color='black', size=12),
                         height=30
                         )

            fig = go.Figure(data=[go.Table(header=header, cells=cells)])

            # Update layout with title and font
            fig.update_layout(
                title='Table Title',
                font=dict(size=14, family='Arial'),
                width=400,
                height=400
            )

            # Update table properties
            fig.update_traces(
                columnwidth=[50, 70, 70, 70],
                selector=dict(type='table')
            )

            return fig
        except Exception as e:
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
                paper_bgcolor='#F5F5F5'
            )
            return fig
        except Exception as e:
            print(e)
            return 1

    # table displaying info about a specific split
    @classmethod
    def graph5(cls, splitData):
        try:
            headers = ['Count', 'Avg', 'Rate', 'Stdev', 'XPH']
            values = [[f"<b>{Logistics.formatValue(splitData['Count'])}</b>"],
                        [f"<b>{Logistics.formatValue(splitData['Cumulative Average'], isTime=True)}</b>", f"<b>{Logistics.formatValue(splitData['Relative Average'], isTime=True)}</b>"],
                        [f"<b>{Logistics.formatValue(splitData['Cumulative Conversion'], isPercent=True)}</b>", f"<b>{Logistics.formatValue(splitData['Relative Conversion'], isPercent=True)}</b>"],
                        [f"<b>{Logistics.formatValue(splitData['Cumulative Stdev'], isTime=True)}</b>", f"<b>{Logistics.formatValue(splitData['Relative Stdev'], isTime=True)}</b>"],
                        [f"<b>{Logistics.formatValue(splitData['xph'])}</b>"]]
            colors = []
            for i1 in range(len(values)):
                colors.append([])
                for i2 in range(len(values[i1])):
                    color = 'black'
                    if i2 == 1:
                        color = '#8c8c8c'
                    colors[i1].append(color)

            fig = go.Figure(data=[go.Table(
                header=dict(
                    values=headers,
                    fill_color='#1f77b4',  # Use blue for header background color
                    align='center',
                    font=dict(color='white', size=14)
                ),
                cells=dict(
                    values=values,
                    fill_color='white',  # Use white for cell background color
                    align='center',
                    font=dict(color=colors, size=12)
                ))
            ])
            fig.update_layout(
                margin=dict(l=20, r=20, t=30, b=20),  # Add some margin around the table
                height=150,
                width=400
            )
            return fig
        except Exception as e:
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
                ])

            # Create the plot
            fig = go.Figure(data=[go.Table(
                header=dict(
                    values=headers,
                    line_color='#2E2E2E',
                    fill_color='#2E2E2E',
                    align='center',
                    font=dict(color='white', size=12)
                ),
                cells=dict(
                    values=values,
                    line_color='#2E2E2E',
                    fill_color='#FFFFFF',
                    align='center',
                    font=dict(color='#2E2E2E', size=11)
                ))
            ])

            fig.update_layout(
                margin=dict(l=20, r=20, t=20, b=20),
                height=300,
                width=800,
                font=dict(size=12),
                hovermode='closest',
                paper_bgcolor='#F2F2F2',
                plot_bgcolor='#F2F2F2'
            )

            return fig
        except Exception as e:
            print(e)
            return 1

    # table displaying general stats of the current session
    @classmethod
    def graph7(cls, currentSession):
        try:
            headers = ['rnph', '% played', 'rpe']
            values = [[Logistics.formatValue(currentSession['general stats']['rnph'])],
                        [Logistics.formatValue(currentSession['general stats']['% played'], isPercent=True)],
                        [Logistics.formatValue(currentSession['general stats']['rpe'])]]
            fig = go.Figure(data=[go.Table(
                header=dict(
                    values=headers,
                    fill_color='#1f77b4',  # Use blue for header background color
                    align='center',
                    font=dict(color='white', size=14)
                ),
                cells=dict(
                    values=values,
                    fill_color='white',  # Use white for cell background color
                    align='center',
                    font=dict(color='#1f77b4', size=12)
                ))
            ])
            fig.update_layout(
                margin=dict(l=20, r=20, t=30, b=20),  # Add some margin around the table
                height=150,
                width=400
            )
            return fig
        except Exception as e:
            print(e)
            return 1

    # pie chart from dict of numerical data
    @classmethod
    def graph8(cls, data):
        # Set the color scheme
        try:
            colors = ['#7fc97f', '#beaed4', '#fdc086', '#ffff99', '#386cb0', '#f0027f']

            # Create a figure and axis object
            fig, ax = plt.subplots(figsize=(3, 3))
            # Create the pie chart with custom colors and explode values
            wedges, labels, _ = ax.pie(data.values(), colors=colors, explode=[0.05] * len(data), autopct='%1.1f%%', textprops={'fontsize': 10})

            # Add a shadow effect to the wedges
            for wedge in wedges:
                wedge.set_edgecolor('white')
                wedge.set_linewidth(1)
                wedge.set_alpha(0.8)

            # Set the font size for the labels and legend
            plt.setp(labels, fontsize=10)
            plt.legend(data.keys(), loc=1, fontsize=10)

            return fig
        except Exception as e:
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
            p2 = sns.scatterplot(x='nph', y='avg_enter', hue='profile', data=dict1, s=60, alpha=0.8, palette='Set1',
                                 edgecolor='none')
            ax.set_xlabel('NPH', fontsize=16)
            ax.set_ylabel('Average Enter', fontsize=16)
            ax.tick_params(axis='both', labelsize=14)
            ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1), title='Profile', fontsize=14, title_fontsize=14)
            plt.tight_layout()
            return fig
        except Exception as e:
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
                    line_color='#2E2E2E',
                    fill_color='#2E2E2E',
                    align='center',
                    font=dict(color='white', size=12)
                ),
                cells=dict(
                    values=values,
                    line_color='#2E2E2E',
                    fill_color='#FFFFFF',
                    align='center',
                    font=dict(color='#2E2E2E', size=11)
                ))
            ])

            fig.update_layout(
                margin=dict(l=20, r=20, t=20, b=20),
                height=200,
                width=600,
                font=dict(size=12),
                hovermode='closest',
                paper_bgcolor='#F2F2F2',
                plot_bgcolor='#F2F2F2'
            )

            return fig
        except Exception as e:
            print(e)
            return 1

    # table displaying general stats of a session
    @classmethod
    def graph11(cls, generalData):
        try:
            headers = ['rnph', 'avg. enter', 'score']
            values = [[Logistics.formatValue(generalData['rnph'])],
                      [Logistics.formatValue(generalData['average enter'], isTime=True)],
                      [Logistics.formatValue(generalData['efficiency score'])]]

            fig = go.Figure(data=[go.Table(
                header=dict(
                    values=headers,
                    fill_color='#1f77b4',  # Use blue for header background color
                    align='center',
                    font=dict(color='white', size=14)
                ),
                cells=dict(
                    values=values,
                    fill_color='white',  # Use white for cell background color
                    align='center',
                    font=dict(color='#1f77b4', size=12)
                ))
            ])
            fig.update_layout(
                margin=dict(l=20, r=20, t=30, b=20),  # Add some margin around the table
                height=100,
                width=400
            )
            return fig
        except Exception as e:
            print(e)
            return 1

    # table displaying general stats of a session
    @classmethod
    def graph12(cls, generalData):
        try:
            values = [Logistics.formatValue(generalData['total resets']),
                      Logistics.formatValue(generalData['total time'] + generalData['total Walltime'], isTime=True),
                      Logistics.formatValue(generalData['percent played'], isPercent=True),
                      Logistics.formatValue(generalData['rpe'])]
            headers = ['Resets', 'Playtime', '% played', 'rpe']

            fig = go.Figure(data=[go.Table(
                header=dict(
                    values=headers,
                    fill_color='#1f77b4',  # Use blue for header background color
                    align='center',
                    font=dict(color='white', size=14)
                ),
                cells=dict(
                    values=values,
                    fill_color='white',  # Use white for cell background color
                    align='center',
                    font=dict(color='#1f77b4', size=12)
                ))
            ])
            fig.update_layout(
                margin=dict(l=20, r=20, t=30, b=20),  # Add some margin around the table
                height=100,
                width=400
            )
            return fig
        except Exception as e:
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
            print(e)
            return 1

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
            plt.show()

            return fig
        except Exception as e:
            print(e)
            return 1

    @classmethod
    def testGraphs(cls):
        fig = Graphs.graph5({"Relative Distribution": [28.0, 18.0, 25.0, 15.0, 16.0, 17.0, 15.0, 22.0, 53.0, 23.0, 31.0, 37.0, 28.0, 30.0], "Cumulative Distribution": [28.0, 18.0, 25.0, 15.0, 16.0, 17.0, 15.0, 22.0, 53.0, 23.0, 31.0, 37.0, 28.0, 30.0], "Relative Conversion": 0.020378457059679767, "Cumulative Conversion": 0.020378457059679767, "Relative Average": 25.571428571428573, "Cumulative Average": 25.571428571428573, "Count": 14, "xph": 16.600790513833992})


