import discord
from discord.ext import commands
from pymongo import MongoClient
import creds
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np

intents = discord.Intents.all()

client = commands.Bot(command_prefix = '!',intents=intents)
clientMongo = MongoClient(creds.MONGO_URI) 

try:
    # The ismaster command is cheap and does not require authentication
    clientMongo.admin.command('ismaster')
    print("Connection to MongoDB successful!")
except Exception as e:
    print("Error connecting to MongoDB:", str(e))


@client.event
async def on_ready():
    
    print("The bot is ready for use!")
    print("--------------------------")

#the name of this function should be what user will type in the command.
@client.command()
async def hello(ctx):
    await ctx.send("Hello, I am the Discord bot for DATA225 Term Project, I provide insights on valorant esports tournament data\nThese are insights I can provide\n1. Assists per Round vs Kills per round -> !APRvKPR <tournament_id>\n2. Performance Stats -> !Performance_Stats <tournament_id>\n3. Map Win Stats -> !Map_Win_Stats <tournament_id>\n4. Player comparision Radar plot based on Shooting stats -> !shooting_stats  <tournament_id> <player1> <player2>\n5. Player comparision Radar plot based on Other features -> !gg_stats <tournament_id> <player1> <player2>\n6. Top Agent Picks on all map -> !Map_Agent_Picks <tournament_id>\n7. Average Kill Death ratio of all teams -> !Team_Stats_KD <tournament_id>\n8. Total Kills by each team in the Tournament -> !Team_Stats_Kills <tournament_id>\n9. Headshot percentage by each team  -> !Team_Stats_HS <tournament_id>")
    #await ctx.send(file=discord.File('hello.png'))

@client.command()
async def APRvKPR(ctx, t_id):
    
    database = clientMongo.TermProj
    c_name = str(t_id)
    collection = database[c_name]

    # # Define your query (replace "your_field" and "your_value" with the actual field and value)
    # query = {"your_field": "your_value"}

    cursor = collection.find()

    documents_list = list(cursor)
    df = pd.DataFrame(documents_list)
    # Retrieve a single document that matches the query
    # result = collection.find_one(query)
    # for document in cursor:
    #     print(document)
    # if result:
    #     print(result)
    # else:
    #     print("Document not found.")
    a = list(documents_list[0].keys())[1:]
    d = {}
    for i in a:
        d[i] = documents_list[0][i]
    df = pd.DataFrame.from_dict(d, orient='index')
    df['CL%'] = df['CL%'].str.replace('%', '')

    # Convert the column to numeric
    df['CL%'] = pd.to_numeric(df['CL%'], errors='coerce')

    # Replace NaN with 0
    df['CL%'] = df['CL%'].fillna(0)

    # Assuming 'CL%' column contains strings with '%' symbol
    df['HS%'] = df['HS%'].str.replace('%', '')

    # Convert the column to numeric
    df['HS%'] = pd.to_numeric(df['HS%'], errors='coerce')

    # Replace NaN with 0
    df['HS%'] = df['HS%'].fillna(0)

    # Assuming 'CL%' column contains strings with '%' symbol
    df['KAST'] = df['KAST'].str.replace('%', '')

    # Convert the column to numeric
    df['KAST'] = pd.to_numeric(df['KAST'], errors='coerce')

    # Replace NaN with 0
    df['KAST'] = df['KAST'].fillna(0)
    # Assuming 'df' is your DataFrame
    columns_to_convert = df.columns.difference(['Player',"CL"])  # Exclude 'name' column

    df[columns_to_convert] = df[columns_to_convert].apply(pd.to_numeric, errors='coerce')
    df['CL'] = df['CL'].apply(lambda x: eval(x) if '/' in x else float(x))
    df['Team'] = df["Player"].apply(lambda x:x.split("\n")[1])
    df['Player'] = df['Player'].apply(lambda x:x.split("\n")[0])
    plt.figure()
    plt.scatter(df['KPR'].astype("float"), df['APR'].astype("float"))
    plt.ylabel('Assists per Round (APR)')
    plt.xlabel('Kills per Round (KPR)')
    plt.title('Assists per Round vs Kills per Round')
    # Annotate specific points
    
    plt.axvline(df['KPR'].mean(), color='red', linestyle='dashed', linewidth=2, label='Mean KPR')
    plt.axhline(df['APR'].mean(), color='blue', linestyle='dashed', linewidth=2, label='Mean APR')

    # Annotate highest kills
    annotations = {
    'highest_kills': df.loc[df['KPR'].idxmax(), 'Player'],
    'highest_assists': df.loc[df['APR'].idxmax(), 'Player'],
    'highest_kills_assists': df.loc[(df['KPR'] + df['APR']).idxmax(), 'Player'],
    'lowest_kills': df.loc[df['KPR'].idxmin(), 'Player'],
    'lowest_assists': df.loc[df['APR'].idxmin(), 'Player'],
    'lowest_kills_assists': df.loc[(df['KPR'] + df['APR']).idxmin(), 'Player']
    }

# Annotate points
    for label, player_name in annotations.items():
        x = df.loc[df['Player'] == player_name, 'KPR'].values[0]
        y = df.loc[df['Player'] == player_name, 'APR'].values[0]
        plt.annotate(f'{player_name}', (x, y), textcoords="offset points", xytext=(0, -15), ha='center')

    plt.savefig('scatter_plot.png')
    
    await ctx.send(file=discord.File('scatter_plot.png'))

    file_to_delete = 'scatter_plot.png'  # Replace with your file name

    # Get the current working directory where the notebook is saved
    current_directory = os.getcwd()

    # Specify the full path to the file
    file_path = os.path.join(current_directory, file_to_delete)

    # Check if the file exists before attempting to delete
    if os.path.exists(file_path):
        # Delete the file
        os.remove(file_path)
        print(f"The file '{file_to_delete}' has been deleted.")
    else:
        print(f"The file '{file_to_delete}' does not exist.")

@client.command()
async def Performance_Stats(ctx , t_id):
    
    
    database = clientMongo.TermProj
    c_name = str(t_id)
    collection = database[c_name]

   
    cursor = collection.find()

    documents_list = list(cursor)
    
       
    a = list(documents_list[0].keys())[1:]
    d = {}
    for i in a:
        d[i] = documents_list[0][i]
    df = pd.DataFrame.from_dict(d, orient='index')

      
    x = df['HS%'].str.rstrip('%').astype('float')
    y = df['K'].astype('float')
    z = df['ADR'].astype("float")  # This will be our color variable

        # Random size values for each data point
    sizes = df["A"].astype('int')
    plt.figure()
        # Plotting the scatterplot with diamond markers, different sizes, and colors based on 'z'
    plt.scatter(x, y, s=sizes,c=z, cmap='viridis', marker='o')
    plt.title("Performance Analysis Scatterplot: Kills, Headshot Percentage, Average Damage/round and Assists")
    plt.xlabel("Headshot percentage")
    plt.ylabel("Number of Kills")
    # plt.xticks(range(0, 100, 20))
    #plt.yticks(range(0, 400, 10))
    plt.legend(['Size = no. of Assists'], bbox_to_anchor=(1.20, 1), loc='upper left')
        # Add a colorbar to the plot to represent the 'z' variable
    plt.colorbar(label='Average Damage per round')
    plt.savefig('temp_viz2.png',bbox_inches = 'tight')

    await ctx.send(file=discord.File('temp_viz2.png'))
        
        
    file_to_delete = 'temp_viz2.png'  # Replace with your file name

        # Get the current working directory where the notebook is saved
    current_directory = os.getcwd()

        # Specify the full path to the file
    file_path = os.path.join(current_directory, file_to_delete)

        # Check if the file exists before attempting to delete
    if os.path.exists(file_path):
            # Delete the file
            os.remove(file_path)
            print(f"The file '{file_to_delete}' has been deleted.")
    else:
            print(f"The file '{file_to_delete}' does not exist.")

@client.command()
async def Map_Win_Stats(ctx, t_id):
    databaseMap = clientMongo.TermProjMap
    c_name = str(t_id) + "Map"
    collection = databaseMap[c_name]

    # # Define your query (replace "your_field" and "your_value" with the actual field and value)
    # query = {"your_field": "your_value"}

    cursor = collection.find()

    documents_list = list(cursor)
    a = list(documents_list[0].keys())[1:]
    d = {}
    for i in a:
        d[i] = documents_list[0][i]
        df = pd.DataFrame.from_dict(d, orient='index')
    
    df["Map"] = df["Map"].apply(lambda x : x.split("\t")[-1])
    df['Map'] = df['Map'].replace("","All")

    columns_to_process = ['ATK WIN','DEF WIN','killjoy', 'skye', 'raze', 'viper', 'jett', 'omen', 'astra', 'sova', 'brimstone', 'breach', 'kayo', 'fade', 'harbor', 'chamber', 'cypher', 'yoru', 'neon', 'gekko', 'phoenix', 'reyna', 'sage', 'iso', 'deadlock']

    # Remove '%' symbol and convert to numeric
    df[columns_to_process] = df[columns_to_process].replace('%', '', regex=True).apply(pd.to_numeric, errors='coerce')
    plt.figure()
    fig, ax = plt.subplots(figsize=(10, 6))
    df.set_index('Map', inplace=True)
    # Bar width
    bar_width = 0.35

    # Bar positions
    bar_positions_atk = range(len(df))
    bar_positions_def = [pos + bar_width for pos in bar_positions_atk]
    ax.set_facecolor('black')
    # Bar plots
    ax.bar(bar_positions_atk, df['ATK WIN'], width=bar_width, label='ATK WIN', color='turquoise', alpha=1)
    ax.bar(bar_positions_def, df['DEF WIN'], width=bar_width, label='DEF WIN', color='teal', alpha=1)

    # Set x-axis ticks and labels
    ax.set_xticks([pos + bar_width / 2 for pos in bar_positions_atk])
    ax.set_xticklabels(df.index)

    # Set labels and title
    ax.set_ylabel('Win Percentage %')
    ax.set_xlabel('Map')
    ax.set_title('ATK vs DEF Wins on Different Maps')

    # Add legend
    ax.legend()

    # Show the plot
    # plt.show()
    plt.savefig('temp_viz3')

    await ctx.send(file=discord.File('temp_viz3.png'))

    file_to_delete = 'temp_viz3.png'  # Replace with your file name

    # Get the current working directory where the notebook is saved
    current_directory = os.getcwd()

    # Specify the full path to the file
    file_path = os.path.join(current_directory, file_to_delete)

    # Check if the file exists before attempting to delete
    if os.path.exists(file_path):
        # Delete the file
        os.remove(file_path)
        print(f"The file '{file_to_delete}' has been deleted.")
    else:
        print(f"The file '{file_to_delete}' does not exist.")
    
@client.command()
async def shooting_stats(ctx,t_id,p1,p2):
    
    
    database = clientMongo.TermProj
    c_name = str(t_id)
    collection = database[c_name]

    

    cursor = collection.find()

    documents_list = list(cursor)
   
# Retrieve a single document that matches the query
# result = collection.find_one(query)
# for document in cursor:
#     print(document)
# if result:
#     print(result)
# else:
#     print("Document not found.")
    a = list(documents_list[0].keys())[1:]
    d = {}
    for i in a:
        d[i] = documents_list[0][i]
    df1 = pd.DataFrame.from_dict(d, orient='index')
    df1["Player"] = df1["Player"].apply(lambda x : x.split("\n")[0])
    df1['CL%'] = df1['CL%'].str.replace('%', '')

    # Convert the column to numeric
    df1['CL%'] = pd.to_numeric(df1['CL%'], errors='coerce')

    # Replace NaN with 0
    df1['CL%'] = df1['CL%'].fillna(0)

    # Assuming 'CL%' column contains strings with '%' symbol
    df1['HS%'] = df1['HS%'].str.replace('%', '')

    # Convert the column to numeric
    df1['HS%'] = pd.to_numeric(df1['HS%'], errors='coerce')

    # Replace NaN with 0
    df1['HS%'] = df1['HS%'].fillna(0)

    # Assuming 'CL%' column contains strings with '%' symbol
    df1['KAST'] = df1['KAST'].str.replace('%', '')

    # Convert the column to numeric
    df1['KAST'] = pd.to_numeric(df1['KAST'], errors='coerce')

    # Replace NaN with 0
    df1['KAST'] = df1['KAST'].fillna(0)
    # Assuming 'df' is your DataFrame
    columns_to_convert = df1.columns.difference(['Player',"CL"])  # Exclude 'name' column

    df1[columns_to_convert] = df1[columns_to_convert].apply(pd.to_numeric, errors='coerce')
    df1['CL'] = df1['CL'].apply(lambda x: eval(x) if '/' in x else float(x))
    player_names = [p1,p2]
    attribute_labels = ['ACS', 'ADR', 'CL%', 'HS%', 'KAST']
    player1_data = df1.loc[df1['Player'] == player_names[0], attribute_labels].values.tolist()
    player2_data = df1.loc[df1['Player'] == player_names[1], attribute_labels].values.tolist()
    plt.figure()
    player_values = [player1_data[0], player2_data[0]]
    attribute_labels = ['ACS', 'ADR', 'CL%', 'HS%', 'KAST']
    scale = "log"

    num_attributes = len(attribute_labels)
    angles = np.linspace(0, 2 * np.pi, num_attributes, endpoint=False).tolist()

    # The plot is circular, so we need to close the plot loop
    angles += [angles[0]]

    # Create the radar plot with a black background
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True, facecolor='black'))
    ax.set_facecolor('black')

    # Plot each player's data with custom colors
    colors = ['purple', 'green']
    for i in range(len(player_names)):
        values = player_values[i] + [player_values[i][0]]
        if scale == 'log':
            values = np.log1p(values)  # Apply log scaling
        elif scale == 'minmax':
            values = (values - np.min(values)) / (np.max(values) - np.min(values))  # Apply min-max scaling
        ax.plot(angles, values, label=player_names[i], color=colors[i], linewidth=2.5)

    # Fill the area inside the plots
    for i in range(len(player_names)):
        values = player_values[i] + [player_values[i][0]]
        if scale == 'log':
            values = np.log1p(values)  # Apply log scaling
        elif scale == 'minmax':
            values = (values - np.min(values)) / (np.max(values) - np.min(values))  # Apply min-max scaling
        ax.fill(angles, values, alpha=0.25, color=colors[i])

    # Set y-axis labels to empty
    ax.set_yticklabels([])

    # Set x-axis labels and adjust their position
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(attribute_labels, color='black', fontsize=16, ha='center', va='bottom')

    # Set legend color to white
    legend = ax.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1), fontsize=16)
    for text in legend.get_texts():
        text.set_color('black')

    # Set the linewidth for the radial grid lines
    ax.grid(alpha=0.5, linewidth=1.2)

    # Increase the size of the dot at the intersection
    for i in range(len(player_names)):
        values = player_values[i] + [player_values[i][0]]
        if scale == 'log':
            values = np.log1p(values)  # Apply log scaling
        elif scale == 'minmax':
            values = (values - np.min(values)) / (np.max(values) - np.min(values))  # Apply min-max scaling
        ax.plot(angles, values, 'o', markersize=8, color=colors[i])
    plt.savefig('radar_1.png')

    await ctx.send(file=discord.File('radar_1.png'))

    file_to_delete = 'radar1.png'  # Replace with your file name

    # Get the current working directory where the notebook is saved
    current_directory = os.getcwd()

    # Specify the full path to the file
    file_path = os.path.join(current_directory, file_to_delete)

    # Check if the file exists before attempting to delete
    if os.path.exists(file_path):
        # Delete the file
        os.remove(file_path)
        print(f"The file '{file_to_delete}' has been deleted.")
    else:
        print(f"The file '{file_to_delete}' does not exist.")
    
@client.command()    
async def gg_stats(ctx,t_id,p1,p2):
    
    
    database = clientMongo.TermProj
    c_name = str(t_id)
    collection = database[c_name]

    

    cursor = collection.find()

    documents_list = list(cursor)
   
# Retrieve a single document that matches the query
# result = collection.find_one(query)
# for document in cursor:
#     print(document)
# if result:
#     print(result)
# else:
#     print("Document not found.")
    a = list(documents_list[0].keys())[1:]
    d = {}
    for i in a:
        d[i] = documents_list[0][i]
    df1 = pd.DataFrame.from_dict(d, orient='index')
    df1["Player"] = df1["Player"].apply(lambda x : x.split("\n")[0])
    df1['CL%'] = df1['CL%'].str.replace('%', '')

    # Convert the column to numeric
    df1['CL%'] = pd.to_numeric(df1['CL%'], errors='coerce')

    # Replace NaN with 0
    df1['CL%'] = df1['CL%'].fillna(0)

    # Assuming 'CL%' column contains strings with '%' symbol
    df1['HS%'] = df1['HS%'].str.replace('%', '')

    # Convert the column to numeric
    df1['HS%'] = pd.to_numeric(df1['HS%'], errors='coerce')

    # Replace NaN with 0
    df1['HS%'] = df1['HS%'].fillna(0)

    # Assuming 'CL%' column contains strings with '%' symbol
    df1['KAST'] = df1['KAST'].str.replace('%', '')

    # Convert the column to numeric
    df1['KAST'] = pd.to_numeric(df1['KAST'], errors='coerce')

    # Replace NaN with 0
    df1['KAST'] = df1['KAST'].fillna(0)
    # Assuming 'df' is your DataFrame
    columns_to_convert = df1.columns.difference(['Player',"CL"])  # Exclude 'name' column

    df1[columns_to_convert] = df1[columns_to_convert].apply(pd.to_numeric, errors='coerce')
    df1['CL'] = df1['CL'].apply(lambda x: eval(x) if '/' in x else float(x))
    player_names = [p1,p2]
    attribute_labels = ['K:D','KPR','APR']
    player1_data = df1.loc[df1['Player'] == player_names[0], attribute_labels].values.tolist()
    player2_data = df1.loc[df1['Player'] == player_names[1], attribute_labels].values.tolist()
    plt.figure()
    player_values = [player1_data[0], player2_data[0]]
    
    scale = "log"

    num_attributes = len(attribute_labels)
    angles = np.linspace(0, 2 * np.pi, num_attributes, endpoint=False).tolist()

    # The plot is circular, so we need to close the plot loop
    angles += [angles[0]]

    # Create the radar plot with a black background
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True, facecolor='black'))
    ax.set_facecolor('black')

    # Plot each player's data with custom colors
    colors = ['purple', 'green']
    for i in range(len(player_names)):
        values = player_values[i] + [player_values[i][0]]
        if scale == 'log':
            values = np.log1p(values)  # Apply log scaling
        elif scale == 'minmax':
            values = (values - np.min(values)) / (np.max(values) - np.min(values))  # Apply min-max scaling
        ax.plot(angles, values, label=player_names[i], color=colors[i], linewidth=2.5)

    # Fill the area inside the plots
    for i in range(len(player_names)):
        values = player_values[i] + [player_values[i][0]]
        if scale == 'log':
            values = np.log1p(values)  # Apply log scaling
        elif scale == 'minmax':
            values = (values - np.min(values)) / (np.max(values) - np.min(values))  # Apply min-max scaling
        ax.fill(angles, values, alpha=0.25, color=colors[i])

    # Set y-axis labels to empty
    ax.set_yticklabels([])

    # Set x-axis labels and adjust their position
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(attribute_labels, color='black', fontsize=16, ha='center', va='bottom')

    # Set legend color to white
    legend = ax.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1), fontsize=16)
    for text in legend.get_texts():
        text.set_color('black')

    # Set the linewidth for the radial grid lines
    ax.grid(alpha=0.5, linewidth=1.2)

    # Increase the size of the dot at the intersection
    for i in range(len(player_names)):
        values = player_values[i] + [player_values[i][0]]
        if scale == 'log':
            values = np.log1p(values)  # Apply log scaling
        elif scale == 'minmax':
            values = (values - np.min(values)) / (np.max(values) - np.min(values))  # Apply min-max scaling
        ax.plot(angles, values, 'o', markersize=8, color=colors[i])
    plt.savefig('radar_1.png')

    await ctx.send(file=discord.File('radar_1.png'))

    file_to_delete = 'radar1.png'  # Replace with your file name

    # Get the current working directory where the notebook is saved
    current_directory = os.getcwd()

    # Specify the full path to the file
    file_path = os.path.join(current_directory, file_to_delete)

    # Check if the file exists before attempting to delete
    if os.path.exists(file_path):
        # Delete the file
        os.remove(file_path)
        print(f"The file '{file_to_delete}' has been deleted.")
    else:
        print(f"The file '{file_to_delete}' does not exist.")
    
@client.command()
async def Map_Agent_Picks(ctx, t_id):
    databaseMap = clientMongo.TermProjMap
    c_name = str(t_id) + "Map"
    collection = databaseMap[c_name]
    

    # # Define your query (replace "your_field" and "your_value" with the actual field and value)
    # query = {"your_field": "your_value"}

    cursor = collection.find()

    documents_list = list(cursor)
    a = list(documents_list[0].keys())[1:]
    d = {}
    for i in a:
        d[i] = documents_list[0][i]
        df = pd.DataFrame.from_dict(d, orient='index')
    
    df["Map"] = df["Map"].apply(lambda x : x.split("\t")[-1])
    df['Map'] = df['Map'].replace("","All")

    columns_to_process = ['ATK WIN','DEF WIN','killjoy', 'skye', 'raze', 'viper', 'jett', 'omen', 'astra', 'sova', 'brimstone', 'breach', 'kayo', 'fade', 'harbor', 'chamber', 'cypher', 'yoru', 'neon', 'gekko', 'phoenix', 'reyna', 'sage', 'iso', 'deadlock']

    # Remove '%' symbol and convert to numeric
    df[columns_to_process] = df[columns_to_process].replace('%', '', regex=True).apply(pd.to_numeric, errors='coerce')
    # fig, ax = plt.subplots(figsize=(10, 6))
    #df.set_index('Map', inplace=True)
    # Bar width
    
    # Top 5 for each map excluding the first column
    for map_name in df['Map'].unique():
        map_df = df[df['Map'] == map_name]
        map_top_5 = map_df.iloc[:, 4:].mean().nlargest(3).to_dict()
        await ctx.send(f"\n\nTop 3 Most Picked Agents on {map_name}:")
        # print(map_top_5)

        for agent,pick_rate in map_top_5.items():
            await ctx.send(f" -{agent}:{pick_rate}")

@client.command()
async def Team_Stats_KD(ctx,t_id):
    database = clientMongo.TermProj
    c_name = str(t_id)
    collection = database[c_name]

    

    cursor = collection.find()

    documents_list = list(cursor)
   
# Retrieve a single document that matches the query
# result = collection.find_one(query)
# for document in cursor:
#     print(document)
# if result:
#     print(result)
# else:
#     print("Document not found.")
    a = list(documents_list[0].keys())[1:]
    d = {}
    for i in a:
        d[i] = documents_list[0][i]
    df1 = pd.DataFrame.from_dict(d, orient='index')
    # df1["Player"] = df1["Player"].apply(lambda x : x.split("\n")[0])
    df1['CL%'] = df1['CL%'].str.replace('%', '')

    # Convert the column to numeric
    df1['CL%'] = pd.to_numeric(df1['CL%'], errors='coerce')

    # Replace NaN with 0
    df1['CL%'] = df1['CL%'].fillna(0)

    # Assuming 'CL%' column contains strings with '%' symbol
    df1['HS%'] = df1['HS%'].str.replace('%', '')

    # Convert the column to numeric
    df1['HS%'] = pd.to_numeric(df1['HS%'], errors='coerce')

    # Replace NaN with 0
    df1['HS%'] = df1['HS%'].fillna(0)

    # Assuming 'CL%' column contains strings with '%' symbol
    df1['KAST'] = df1['KAST'].str.replace('%', '')

    # Convert the column to numeric
    df1['KAST'] = pd.to_numeric(df1['KAST'], errors='coerce')

    # Replace NaN with 0
    df1['KAST'] = df1['KAST'].fillna(0)
    # Assuming 'df' is your DataFrame
    columns_to_convert = df1.columns.difference(['Player',"CL"])  # Exclude 'name' column

    df1[columns_to_convert] = df1[columns_to_convert].apply(pd.to_numeric, errors='coerce')
    df1['CL'] = df1['CL'].apply(lambda x: eval(x) if '/' in x else float(x))
    df1['Team'] = df1["Player"].apply(lambda x:x.split("\n")[1])
    df1['Player'] = df1['Player'].apply(lambda x:x.split("\n")[0])
    temp = df1.groupby("Team")["K:D"].mean()
    # Extracting data from the DataFrame
    x_values = temp.index
    y_values = temp.values.flatten()
    plt.figure()
    # Creating a bar plot using Matplotlib
    plt.bar(x_values, y_values,width =0.6)

    # Adding labels and title
    plt.xlabel('Teams')
    plt.ylabel('Mean K:D')
    #plt.title('Bar Plot')
    plt.xticks(rotation=45, ha="right")  # Rotate x-axis labels for better readability
    # Display the plot
    # plt.show()
    plt.savefig('team_mean_kd.png')

    await ctx.send(file=discord.File('team_mean_kd.png'))

    file_to_delete = 'team_mean_kd.png'  # Replace with your file name

    # Get the current working directory where the notebook is saved
    current_directory = os.getcwd()

    # Specify the full path to the file
    file_path = os.path.join(current_directory, file_to_delete)

    # Check if the file exists before attempting to delete
    if os.path.exists(file_path):
        # Delete the file
        os.remove(file_path)
        print(f"The file '{file_to_delete}' has been deleted.")
    else:
        print(f"The file '{file_to_delete}' does not exist.")

@client.command()
async def Team_Stats_Kills(ctx,t_id):
    database = clientMongo.TermProj
    c_name = str(t_id)
    collection = database[c_name]

    

    cursor = collection.find()

    documents_list = list(cursor)
   
# Retrieve a single document that matches the query
# result = collection.find_one(query)
# for document in cursor:
#     print(document)
# if result:
#     print(result)
# else:
#     print("Document not found.")
    a = list(documents_list[0].keys())[1:]
    d = {}
    for i in a:
        d[i] = documents_list[0][i]
    df1 = pd.DataFrame.from_dict(d, orient='index')
    # df1["Player"] = df1["Player"].apply(lambda x : x.split("\n")[0])
    df1['CL%'] = df1['CL%'].str.replace('%', '')

    # Convert the column to numeric
    df1['CL%'] = pd.to_numeric(df1['CL%'], errors='coerce')

    # Replace NaN with 0
    df1['CL%'] = df1['CL%'].fillna(0)

    # Assuming 'CL%' column contains strings with '%' symbol
    df1['HS%'] = df1['HS%'].str.replace('%', '')

    # Convert the column to numeric
    df1['HS%'] = pd.to_numeric(df1['HS%'], errors='coerce')

    # Replace NaN with 0
    df1['HS%'] = df1['HS%'].fillna(0)

    # Assuming 'CL%' column contains strings with '%' symbol
    df1['KAST'] = df1['KAST'].str.replace('%', '')

    # Convert the column to numeric
    df1['KAST'] = pd.to_numeric(df1['KAST'], errors='coerce')

    # Replace NaN with 0
    df1['KAST'] = df1['KAST'].fillna(0)
    # Assuming 'df' is your DataFrame
    columns_to_convert = df1.columns.difference(['Player',"CL"])  # Exclude 'name' column

    df1[columns_to_convert] = df1[columns_to_convert].apply(pd.to_numeric, errors='coerce')
    df1['CL'] = df1['CL'].apply(lambda x: eval(x) if '/' in x else float(x))
    df1['Team'] = df1["Player"].apply(lambda x:x.split("\n")[1])
    df1['Player'] = df1['Player'].apply(lambda x:x.split("\n")[0])
    temp = df1.groupby("Team")["K"].sum()
    # Extracting data from the DataFrame
    x_values = temp.index
    y_values = temp.values.flatten()
    plt.figure()
    # Creating a bar plot using Matplotlib
    plt.bar(x_values, y_values,width =0.6)

    # Adding labels and title
    plt.xlabel('Teams')
    plt.ylabel('Total Kills')
    #plt.title('Bar Plot')
    plt.xticks(rotation=45, ha="right")  # Rotate x-axis labels for better readability
    # Display the plot
    # plt.show()
    plt.savefig('team_mean_kd.png')

    await ctx.send(file=discord.File('team_mean_kd.png'))

    file_to_delete = 'team_mean_kd.png'  # Replace with your file name

    # Get the current working directory where the notebook is saved
    current_directory = os.getcwd()

    # Specify the full path to the file
    file_path = os.path.join(current_directory, file_to_delete)

    # Check if the file exists before attempting to delete
    if os.path.exists(file_path):
        # Delete the file
        os.remove(file_path)
        print(f"The file '{file_to_delete}' has been deleted.")
    else:
        print(f"The file '{file_to_delete}' does not exist.")    

@client.command()
async def Team_Stats_HS(ctx,t_id):
    database = clientMongo.TermProj
    c_name = str(t_id)
    collection = database[c_name]

    

    cursor = collection.find()

    documents_list = list(cursor)
   
# Retrieve a single document that matches the query
# result = collection.find_one(query)
# for document in cursor:
#     print(document)
# if result:
#     print(result)
# else:
#     print("Document not found.")
    a = list(documents_list[0].keys())[1:]
    d = {}
    for i in a:
        d[i] = documents_list[0][i]
    df1 = pd.DataFrame.from_dict(d, orient='index')
    # df1["Player"] = df1["Player"].apply(lambda x : x.split("\n")[0])
    df1['CL%'] = df1['CL%'].str.replace('%', '')

    # Convert the column to numeric
    df1['CL%'] = pd.to_numeric(df1['CL%'], errors='coerce')

    # Replace NaN with 0
    df1['CL%'] = df1['CL%'].fillna(0)

    # Assuming 'CL%' column contains strings with '%' symbol
    df1['HS%'] = df1['HS%'].str.replace('%', '')

    # Convert the column to numeric
    df1['HS%'] = pd.to_numeric(df1['HS%'], errors='coerce')

    # Replace NaN with 0
    df1['HS%'] = df1['HS%'].fillna(0)

    # Assuming 'CL%' column contains strings with '%' symbol
    df1['KAST'] = df1['KAST'].str.replace('%', '')

    # Convert the column to numeric
    df1['KAST'] = pd.to_numeric(df1['KAST'], errors='coerce')

    # Replace NaN with 0
    df1['KAST'] = df1['KAST'].fillna(0)
    # Assuming 'df' is your DataFrame
    columns_to_convert = df1.columns.difference(['Player',"CL"])  # Exclude 'name' column

    df1[columns_to_convert] = df1[columns_to_convert].apply(pd.to_numeric, errors='coerce')
    df1['CL'] = df1['CL'].apply(lambda x: eval(x) if '/' in x else float(x))
    df1['Team'] = df1["Player"].apply(lambda x:x.split("\n")[1])
    df1['Player'] = df1['Player'].apply(lambda x:x.split("\n")[0])
    temp = df1.groupby("Team")["HS%"].mean()
    # Extracting data from the DataFrame
    x_values = temp.index
    y_values = temp.values.flatten()
    plt.figure()
    # Creating a bar plot using Matplotlib
    plt.bar(x_values, y_values,width =0.6)

    # Adding labels and title
    plt.xlabel('Teams')
    plt.ylabel('HS%')
    #plt.title('Bar Plot')
    plt.xticks(rotation=45, ha="right")  # Rotate x-axis labels for better readability
    # Display the plot
    # plt.show()
    plt.savefig('team_mean_kd.png')

    await ctx.send(file=discord.File('team_mean_kd.png'))

    file_to_delete = 'team_mean_kd.png'  # Replace with your file name

    # Get the current working directory where the notebook is saved
    current_directory = os.getcwd()

    # Specify the full path to the file
    file_path = os.path.join(current_directory, file_to_delete)

    # Check if the file exists before attempting to delete
    if os.path.exists(file_path):
        # Delete the file
        os.remove(file_path)
        print(f"The file '{file_to_delete}' has been deleted.")
    else:
        print(f"The file '{file_to_delete}' does not exist.")    


client.run(creds.DISCORD_TOKEN)

