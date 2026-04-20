import synapseclient
syn = synapseclient.Synapse()
syn.login(authToken="")
import streamlit as st
import pandas as pd
import plotly.express as px #ottimo per i grafici interattivi
