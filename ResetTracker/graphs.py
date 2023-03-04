import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from plotly.colors import n_colors

from stats import *


# class methods for creating graphs
class Graphs:
    # makes a kde histogram of a distribution of datapoints
    @classmethod
    def graph1(cls, dist, smoothness):
        mean = np.mean(dist)

        # Set seaborn style
        sns.set_style("whitegrid")

        # Create figure and axis objects
        fig, ax = plt.subplots(figsize=(4, 4))

        # Plot the KDE distribution
        sns.kdeplot(data=dist, ax=ax, bw_adjust=smoothness)

        plt.axvline(mean, color='red', linestyle='--')
        ax.text(mean, ax.get_ylim()[1]*0.1, f'Mean: {mean:.2f}', ha='center', va='center')

        # Add labels and title
        ax.set_xlabel('Distance')
        ax.set_ylabel('Density')
        ax.set_title('Distribution of Distances')

        # Set x-axis limits
        rangeX = [min(dist), max(dist)]
        ax.set_xlim(rangeX)

        # Remove top and right spines
        sns.despine()

        return fig

    # makes a pie chart given a list of strings
    @classmethod
    def graph2(cls, items):
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

    # makes a table for relevant information of a split
    @classmethod
    def graph3(cls, splitStats):
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

    # makes a 2-way table showing the frequency of each combination of iron source and entry method
    @classmethod
    def graph4(cls, enters, settings):
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

    # table displaying info about a specific split
    @classmethod
    def graph5(cls, splitData):
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

    # table display split stats of current session
    @classmethod
    def graph6(cls, currentSession):
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

    # table displaying general stats of the current session
    @classmethod
    def graph7(cls, currentSession):
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

    # pie chart from dict of numerical data
    @classmethod
    def graph8(cls, data):
        # Set the color scheme
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

    # scatterplot displaying nph and average enter, with a canvas based on efficiency score
    @classmethod
    def graph9(cls, sessions):
        nph_list = []
        avg_enter_list = []
        profile_list = []
        for i in range(len(sessions)):
            if sessions['sessions'][i] != 'All' and 'Latest' not in sessions['sessions'][i]['string']:
                nph_list.append(sessions['stats'][i]['general stats']['rnph'])
                avg_enter_list.append(sessions['stats'][i]['splits stats']['Nether']['Cumulative Average'])
                profile_list.append(sessions['stats'][i]['profile'])

        dict1 = {'nph': nph_list, 'avg_enter': avg_enter_list, 'profile': profile_list}

        x1 = np.linspace(6, 14.0, 60)
        x2 = np.linspace(90, 150, 80)
        x, y = np.meshgrid(x1, x2)
        cm = plt.cm.get_cmap('cividis')
        fig, ax = plt.subplots(figsize=(4, 4))
        p1 = ax.contourf(x, y, np.zeros_like(x), levels=1000, cmap=cm)
        p2 = sns.scatterplot(x='nph', y='avg_enter', hue='profile', data=dict1, s=60, alpha=0.8, palette='Set1',
                             edgecolor='none')
        ax.set_xlabel('Nether Portals per Hour', fontsize=16)
        ax.set_ylabel('Nether Entry Time (s)', fontsize=16)
        ax.tick_params(axis='both', labelsize=14)
        ax.legend(loc='best', title='Profile', fontsize=14, title_fontsize=14)
        plt.tight_layout()
        return fig

    # table displaying some nether stats for each enter type
    @classmethod
    def graph10(cls, exitSuccess):
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

    # table displaying general stats of a session
    @classmethod
    def graph11(cls, generalData):
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

    # table displaying general stats of a session
    @classmethod
    def graph12(cls, generalData):
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

    @classmethod
    def testGraphs(cls):
        fig = Graphs.graph5({"Relative Distribution": [28.0, 18.0, 25.0, 15.0, 16.0, 17.0, 15.0, 22.0, 53.0, 23.0, 31.0, 37.0, 28.0, 30.0], "Cumulative Distribution": [28.0, 18.0, 25.0, 15.0, 16.0, 17.0, 15.0, 22.0, 53.0, 23.0, 31.0, 37.0, 28.0, 30.0], "Relative Conversion": 0.020378457059679767, "Cumulative Conversion": 0.020378457059679767, "Relative Average": 25.571428571428573, "Cumulative Average": 25.571428571428573, "Count": 14, "xph": 16.600790513833992})


