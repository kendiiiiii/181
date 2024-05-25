import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

# Set page configuration
st.set_page_config(page_title="Voltage Drop Calculator", page_icon="🔋", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Roboto', sans-serif;
    }

    .main {
        background-color: #f0f2f6;
        color: #0c0d0e;
    }
    .stButton>button {
        color: white;
        background-color: #0072c6;
        border-radius: 8px;
        padding: 0.5em;
    }
    .stNumberInput>div>input {
        background-color: #f0f2f6;
        border-radius: 8px;
        border: 1px solid #cccccc;
    }
    .stMarkdown {
        background-color: #ffffff;
        padding: 10px;
        border-radius: 8px;
    }
    .stSelectbox>div {
        background-color: #f0f2f6;
        border-radius: 8px;
    }
    .stTextInput input {
        background-color: #b2fab4 !important; /* Light green background */
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for navigation and chatbot
if 'page' not in st.session_state:
    st.session_state.page = 'home'

if 'catbot_history' not in st.session_state:
    st.session_state.catbot_history = []

def navigate_to_calculator():
    st.session_state.page = 'calculator'

def navigate_to_home():
    st.session_state.page = 'home'

def navigate_to_catbot():
    st.session_state.page = 'catbot'

def catbot_response(user_input):
    return ' '.join(['meow' * len(word) for word in user_input.split()])

# Function to calculate equivalent resistance of resistors in series
def series_resistance(resistors):
    return sum(resistors)

# Function to calculate equivalent resistance of resistors in parallel
def parallel_resistance(resistors):
    return 1 / sum([1 / r for r in resistors])

# Function to calculate voltage drop for series resistors
def calculate_voltage_drop(voltage, resistors):
    total_resistance = sum(resistors)
    voltage_drops = [voltage * (r / total_resistance) for r in resistors]
    return voltage_drops

# Sidebar for navigation
with st.sidebar:
    st.header("Navigation")
    option = st.radio("Go to", ["Home", "Calculate Voltage Drop", "CatBot"])

    if option == 'Home':
        navigate_to_home()
    elif option == 'Calculate Voltage Drop':
        navigate_to_calculator()
    elif option == 'CatBot':
        navigate_to_catbot()

# Home page
if st.session_state.page == 'home':
    st.title("🔋 Voltage Drop Calculator")
    st.markdown("### Created by Kendii Lam, student ID: 21076071")
    st.subheader("Welcome to the Voltage Drop Calculator App!")
    st.markdown("""
        This app helps you calculate the voltage drop in a circuit with both series and parallel resistors. 
        You can input the total voltage, the number of branches, and the resistance values for each resistor.
        The app will then calculate the voltage drop across each resistor and display the results in a visually appealing plot. Click the arrow at the top-left corner to navigate to the calculator tab.
    """)
    st.balloons()

# Calculator page
elif st.session_state.page == 'calculator':
    st.title("Voltage Drop Calculator")
    st.markdown("### Enter Circuit Parameters")
    with st.expander("⚙️ Enter Circuit Parameters"):
        st.markdown("#### Enter the total voltage and the number of branches.")
        voltage = st.slider("Enter the total voltage (V):", min_value=0.0, max_value=1000.0, step=0.1)
        num_branches = st.text_input("Enter the number of branches:", key="num_branches_input")
    
    if num_branches:
        try:
            num_branches = int(num_branches)
            branches = []

            st.markdown("### 📊 Branches and Resistor Values")
            branch_cols = st.columns(num_branches)
            for i, col in enumerate(branch_cols):
                with col:
                    st.subheader(f"Branch {i+1}")
                    num_resistors = st.number_input(f"Number of resistors in branch {i+1}:", min_value=1, step=1, key=f"num_resistors_{i}")
                    resistors = []
                    for j in range(num_resistors):
                        resistor_value = st.number_input(f"Value of resistor {j+1} (Ω) in branch {i+1}:", min_value=0.0, step=0.1, format="%.2f", key=f"resistor_{i}_{j}")
                        resistors.append(resistor_value)
                    branches.append(resistors)

            if st.button("Calculate Voltage Drop"):
                equivalent_resistances = []
                voltage_drops_per_branch = []

                for branch in branches:
                    equivalent_resistance = series_resistance(branch)
                    equivalent_resistances.append(equivalent_resistance)

                total_equivalent_resistance = parallel_resistance(equivalent_resistances)

                for branch in branches:
                    branch_voltage = voltage  # Voltage across each parallel branch is the same
                    voltage_drops = calculate_voltage_drop(branch_voltage, branch)
                    voltage_drops_per_branch.append(voltage_drops)

                st.markdown(f"### Equivalent Resistance: {total_equivalent_resistance:.2f} Ω")
                st.markdown("### Voltage Drops per Branch")
                for i, voltage_drops in enumerate(voltage_drops_per_branch):
                    st.markdown(f"**Branch {i+1}:** {voltage_drops}")

                # Plotting the voltage distribution in 2D using Matplotlib
                fig, ax = plt.subplots(figsize=(12, 6))
                norm = Normalize(vmin=min([min(branch) for branch in branches]), vmax=max([max(branch) for branch in branches]))
                cmap = plt.get_cmap("viridis")

                for i, (voltage_drops, branch) in enumerate(zip(voltage_drops_per_branch, branches)):
                    x = np.arange(1, len(voltage_drops) + 1)
                    color = cmap(norm(branch))
                    for j, (voltage_drop, resistor_value) in enumerate(zip(voltage_drops, branch)):
                        ax.plot(x[j], voltage_drop, marker='o', color=color[j], markersize=8)
                        if j == 0:
                            ax.plot(x, voltage_drops, color=color[0], label=f'Branch {i+1}')
                        else:
                            ax.plot(x, voltage_drops, color=color[0])

                ax.set_xlabel('Resistors in Branch')
                ax.set_ylabel('Voltage Drop (V)')
                ax.set_title('Voltage Distribution Across Branches')
                ax.legend()
                ax.grid(True)

                # Create colorbar as legend
                sm = ScalarMappable(cmap=cmap, norm=norm)
                sm.set_array([])
                fig.colorbar(sm, ax=ax, orientation='vertical', label='Resistance (Ω)')

                st.pyplot(fig)

        except ValueError:
            st.warning("Please enter a valid integer for the number of branches.")

# CatBot page
elif st.session_state.page == 'catbot':
    st.title("🐱 CatBot")
    st.markdown("### Talk to CatBot!")
    
    user_input = st.text_input("You: ", key="catbot_input")
    
    if st.button("Send"):
        response = catbot_response(user_input)
        st.session_state.catbot_history.append((user_input, response))
    
    if st.session_state.catbot_history:
        for user_input, response in st.session_state.catbot_history:
            st.markdown(f"**You:** {user_input}")
            st.markdown(f"**CatBot:** {response}")
