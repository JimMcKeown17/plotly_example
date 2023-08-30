#!/usr/bin/env python
# coding: utf-8

# # Notes to Self
# - Improvement by Metric created below allowing filtering for different grades
# 
# ## Future things to add
# - Session analysis (per center or per LC)
# - Perhaps tables w/ low performers (be it # of sessions, attendance, kids results, etc)

# In[1]:


import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import dash

# import plotly
import plotly.graph_objects as go
import plotly.express as px

from jupyter_dash import JupyterDash
from dash import dcc, html, Input, Output

from dash.dependencies import Output, Input
from dash.exceptions import PreventUpdate

G3_colour = "#6DA9E4"
G2_colour = "#F7D060"
G1_colour = "#917FB3"
GR_colour = "#98D8AA"
ECD_colour = "#FF6D60"


# In[2]:


# uni = pd.read_csv("20230401 - Masi University Main Sheet.csv")
# tl = pd.read_csv("2023 Top Learner  High School - Main -20230120 - NMB High Schools.csv")
children = pd.read_csv("Results By Year/All22.csv").assign(
    full_sessions = lambda x: x["Total Sessions"] > 30
)


# In[3]:


children.columns


# In[4]:


children["Jan - Sounds and Phonics"] =  children["Jan - Sounds First Letter"] + children["Jan - Phonics"]
children["Nov - Sounds and Phonics"] =  children["Nov - Sounds First Letter"] + children["Nov - Phonics"]
children["Sounds and Phonics Improvement"] = children["Nov - Sounds and Phonics"] - children["Jan - Sounds and Phonics"]
children["Jan - Setence Total"] = children["Jan - Sentence 1"] + children["Jan - Sentence 2"]
children["Nov - Sentence Total"] = children["Nov - Sentence 1"] + children["Nov - Sentence 2"]
children["First Sounds Improvement"] = children["Nov - Sounds First Letter"] - children["Jan - Sounds First Letter"]
children["Phonics Improvement"] = children["Nov - Phonics"] - children["Jan - Phonics"]
children["Sight Words Improvement"] = children["Nov - Sight Words"] - children["Jan - Sight Words"]
children["Letters Improvement"] = children["Nov - Letters Correct"] - children["Jan - Letters Correct"]
children["CVCs Improvement"] = children["Nov - CVCs Written"] - children["Jan - CVCs Written"]
children["Sentence Improvement"] = children["Nov - Sentence Total"] - children["Jan - Setence Total"]
children["Writing a Story"] = children["Nov - Writing a Story"] - children["Jan - Writing a Story"]
children["Total Improvement"] = children["Nov - Total"] - children["Jan - Total"]
children['Ever On Programme w Grads'] = children['Ever On Programme'].apply(lambda x: 'Yes' if x == 'Yes' or x == 'Graduated' else 'No')

improvement_columns = ["First Sounds Improvement","Phonics Improvement","Sight Words Improvement", "Letters Improvement", "Sentence Improvement", "Total Improvement" ]


# In[5]:


# We are excluding our graduates from all of these
on_programme_primary = children[(children['On The Programme EOY'] == "Yes") & (children['Grade'] != "PreR") & (children['Ever On Programme'] != "Graduated")]
on_primary = on_programme_primary.groupby("Schools")
not_programme_primary = children[(children['On The Programme EOY'] == "No") & (children['Centre Type'] != "ECD") & (children['Ever On Programme'] != "Graduated")]
not_primary = on_programme_primary.groupby("Schools")
on_programme_ecd = children[(children['On The Programme EOY'] == "Yes") & (children['Grade'] == "PreR")]
on_ecd = on_programme_ecd.groupby("Schools")
not_programme_ecd = children[(children['On The Programme EOY'] == "No") & (children['Grade'] == "PreR") & (children['Ever On Programme'] != "Graduated")]
not_ecd = on_programme_ecd.groupby("Schools")
on_programme_R = children[(children['On The Programme EOY'] == "Yes") & (children['Grade'] == "Grade R")]
on_R = on_programme_R.groupby("Schools")
not_programme_R = children[(children['On The Programme EOY'] == "No") & (children['Grade'] == "Grade R") & (children['Ever On Programme'] != "Graduated")]
not_R = not_programme_R.groupby("Schools")
on_programme_1 = children[(children['On The Programme EOY'] == "Yes") & (children['Grade'] == "Grade 1")]
on_1 = on_programme_1.groupby("Schools")
not_programme_1 = children[(children['On The Programme EOY'] == "No") & (children['Grade'] == "Grade 1") & (children['Ever On Programme'] != "Graduated")]
not_1 = not_programme_1.groupby("Schools")
on_programme_2 = children[(children['On The Programme EOY'] == "Yes") & (children['Grade'] == "Grade 2")]
on_2 = on_programme_2.groupby("Schools")
not_programme_2 = children[(children['On The Programme EOY'] == "No") & (children['Grade'] == "Grade 2") & (children['Ever On Programme'] != "Graduated")]
not_2 = not_programme_2.groupby("Schools")
on_programme_3 = children[(children['On The Programme EOY'] == "Yes") & (children['Grade'] == "Grade 3")]
on_3 = on_programme_3.groupby("Schools")
not_programme_3 = children[(children['On The Programme EOY'] == "No") & (children['Grade'] == "Grade 3") & (children['Ever On Programme'] != "Graduated")]
not_3 = not_programme_3.groupby("Schools")
all_ECD = children[children['Grade'] == "PreR"]
all_Primary = children[(children['Grade'] != "PreR") & (children['Ever On Programme'] != "Graduated")]
all_Primary_all = children[(children['Grade'] != "PreR")]


#graduates included below. When we are comparing total scores for kids on the programme vs graduated out of the programme, we want to include our grads.
all_R = children[children['Grade'] == "Grade R"]
all_1 = children[children['Grade'] == "Grade 1"]
all_2 = children[children['Grade'] == "Grade 2"]
all_3 = children[children['Grade'] == "Grade 3"]
all_ECD_R = pd.concat([all_ECD, all_R])
on_programme_primary_grads = children[(children['On The Programme EOY'] == "Yes") & (children['Grade'] != "PreR")]
on_primary_grads = on_programme_primary_grads.groupby("Schools")


# In[6]:


app = JupyterDash(__name__)

app.layout = html.Div([
    dcc.Dropdown(
    id="stat",
    options=["Phonics Improvement","Sight Words Improvement", "Letters Improvement", "Total Improvement"],
    value="Total Improvement"
    ),
    dcc.Graph(id="Graph")
])

@app.callback(
    Output("Graph", "figure"),
    Input("stat", "value")
)

def stat_picker(stat):
    
    # Figuring out who is on the programme for ECD
    on_programme_ecd = children[(children['On The Programme EOY'] == "Yes") & (children['Grade'] == "PreR")]

    # Calculate the average 'Total Improvement' per 'Schools'
    avg_improvement = on_programme_ecd.groupby('Schools', as_index=False)[stat].mean()
    avg_improvement = avg_improvement.sort_values(by=stat, ascending=False)

    # Create the bar plot
    fig = px.bar(avg_improvement, 
                 x="Schools", 
                 y=f"{stat}", 
                 title=f"Average Progress of ECD Children by {stat}",
                color="Schools")

    # Set x-axis title
    fig.update_xaxes(title_text="Schools")

    # Set y-axis title
    fig.update_yaxes(title_text=f"{stat}")

    # Update layout properties
    fig.update_layout(autosize=False, width=900, height=600)
    return fig

if __name__ == '__main__':
    app.run_server(mode="inline")



# In[7]:


app = JupyterDash(__name__)

app.layout = html.Div([
    dcc.Dropdown(
    id="stat",
    options=["First Sounds Improvement","Phonics Improvement","Sight Words Improvement", "Letters Improvement", "CVCs Improvement", "Total Improvement"],
    value="Total Improvement"
    ),
    dcc.Graph(id="Graph")
])

@app.callback(
    Output("Graph", "figure"),
    Input("stat", "value")
)

def stat_picker(stat):
    
    # Figuring out who is on the programme for Grades R & 1
    on_programme_primary = children[(children['On The Programme EOY'] == "Yes") & (children['Grade'].isin(["Grade R", "Grade 1"]))]

    # Calculate the average 'Total Improvement' per 'Schools'
    avg_improvement = on_programme_primary.groupby('Schools', as_index=False)[stat].mean()
    avg_improvement = avg_improvement.sort_values(by=stat, ascending=False)

    # Create the bar plot
    fig = px.bar(avg_improvement, 
                 x="Schools", 
                 y=f"{stat}", 
                 title=f"Average Progress of Grades R & 1 Children by {stat}",
                color="Schools")

    # Set x-axis title
    fig.update_xaxes(title_text="Schools")

    # Set y-axis title
    fig.update_yaxes(title_text=f"{stat}")

    # Update layout properties
    fig.update_layout(autosize=False, width=900, height=600)
    return fig

if __name__ == '__main__':
    app.run_server(mode="inline")



# In[25]:


app = JupyterDash(__name__)

app.layout = html.Div([
    dcc.Dropdown(
    id="stat",
    options=["Sight Words Improvement", "Letters Improvement", "CVCs Improvement", "Sentence Improvement", "Writing a Story", "Total Improvement"],
    value="Total Improvement"
    ),
    dcc.Graph(id="Graph")
])

@app.callback(
    Output("Graph", "figure"),
    Input("stat", "value")
)

def stat_picker(stat):
    
    # Figuring out who is on the programme for Grades 2 & 3
    on_programme_primary = children[(children['On The Programme EOY'] == "Yes") & (children['Grade'].isin(["Grade 2", "Grade 3"]))]

    # Calculate the average 'Total Improvement' per 'Schools'
    avg_improvement = on_programme_primary.groupby('Schools', as_index=False)[stat].mean()
    avg_improvement = avg_improvement.sort_values(by=stat, ascending=False)

    # Create the bar plot
    fig = px.bar(avg_improvement, 
                 x="Schools", 
                 y=f"{stat}", 
                 title=f"Average Progress of Grades 2 & 3 Children by {stat}",
                color="Schools")

    # Set x-axis title
    fig.update_xaxes(title_text="Schools")

    # Set y-axis title
    fig.update_yaxes(title_text=f"{stat}")

    # Update layout properties
    fig.update_layout(autosize=False, width=900, height=600)
    return fig

if __name__ == '__main__':
    app.run_server(mode="inline")



# In[ ]:




