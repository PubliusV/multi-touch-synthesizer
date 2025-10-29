# Multi-Touch Attribution Synthesizer

An interactive Streamlit application for generating synthetic customer journey data and comparing multi-touch attribution (MTA) models. This tool helps marketers and analysts understand how different attribution methodologies allocate credit across marketing channels.

## Overview

Marketing attribution is complex. When a customer interacts with multiple channels before converting (Paid Social → Email → Paid Search → Purchase), how do you credit each touchpoint? This project demonstrates the impact of different attribution models on the same user journey data.

The application has two components:
1. **Data Synthesizer**: Generate (sufficiently) realistic synthetic user journeys with configurable channel parameters based on some statistical assumptions
2. **Attribution Dashboard**: Compare attribution models (First-Touch, Last-Touch, Linear, and Markov Chain) side-by-side

## Features

### Data Synthesis
- **Configurable channel parameters**: Set conversion rates, relative frequency, average order value, and AOV standard deviation for each marketing channel
- **Realistic user journeys**: Uses Poisson distribution to model touchpoint counts and weighted random sampling for channel selection
- **Conversion modeling**: Cumulative conversion probability across touchpoints with normally-distributed order values
- **Export functionality**: Download synthetic data as CSV or pickle for external analysis

### Attribution Models
The dashboard implements four standard attribution models:
- **First-Touch**: 100% credit to the first touchpoint in the journey
- **Last-Touch**: 100% credit to the final touchpoint before conversion
- **Linear**: Equal credit distributed across all touchpoints
- **Markov Chain**: Probabilistic model that calculates each channel's removal effect on conversion probability

### Visualizations
- Attributed conversions by channel and model
- Attributed revenue by channel and model
- Conversion rate (CVR) comparison across models
- Return on Ad Spend (ROAS) analysis with configurable CPC inputs

## Installation

```bash
pip install -r requirements.txt
```

### Dependencies
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `scipy` - Statistical distributions (Poisson)
- `streamlit` - Web application framework
- `plotly` - Interactive visualizations
- `ChannelAttribution` - Markov chain attribution modeling

## Usage

Launch the application:
```bash
streamlit run mta_data_synthesizer.py
```

The app has two pages accessible via the Streamlit sidebar:

### Page 1: Data Synthesizer (Homepage)

Configure your simulation:
1. Set the number of users to simulate (50 - 10M | pragmatic range (that won't take forever to simulate): 50 - 5,000)
2. Define expected touchpoints per user (Poisson lambda parameter - this also impacts simulation time)
   An increase in lambda creates a significant increase in simulation complexity, since the expected number of touchpoints for _each_ customer increases.
4. Customize channel parameters in the interactive table:
   - **Channel CVR**: Conversion rate for that channel
   - **Relative Frequency**: How often this channel appears in journeys
   - **AOV**: Average order value when converting through this channel
   - **Standard Deviation**: Variance in order values

Click "Generate Simulated Data" to create synthetic user journeys. This may take some time, depending on your simulated parameters. The app automatically saves a `synthetic_touchpoints.pkl` file for the attribution dashboard.

### Page 2: Attribution Dashboard

Navigate to the attribution dashboard using the sidebar. The dashboard automatically loads your synthetic data and displays:
- Summary metrics (total orders, revenue, sessions)
- Interactive comparison charts across attribution models
- Configurable CPC inputs for ROAS calculations
- Full model comparison table with all metrics

**Workflow**: Generate data on the homepage first, then switch to the attribution dashboard to analyze results. You can iterate by returning to the homepage to adjust parameters and regenerate data.

## How It Works

### Synthetic Data Generation

The synthesizer creates realistic user journeys through a multi-step process:

1. **User Journey Length**: For each user, draw touchpoint count from Poisson(λ) distribution
2. **Channel Selection**: At each touchpoint, randomly select a channel weighted by relative frequency
3. **Conversion Logic**: 
   - Accumulate CVR contributions from each touchpoint
   - On final touchpoint, convert probabilistically based on cumulative CVR
   - If conversion occurs, draw order value from Normal(μ=AOV, σ=stdev)

This approach models realistic customer behavior: multiple touchpoints influence conversion, and different channels have different performance characteristics.

### Attribution Modeling

**Heuristic Models** (First-Touch, Last-Touch, Linear):
- Simple rule-based credit assignment
- Fast to compute, easy to explain
- Ignore interaction effects between channels

**Markov Chain Model**:
- Calculates each channel's incremental contribution to conversion probability
- Models the customer journey as a state transition graph
- Accounts for channel sequencing and interaction effects
- More computationally expensive but theoretically rigorous

The dashboard shows how dramatically different models can produce different results from the same underlying data.

## Example Simulation Parameters

**Default Configuration**:
- Paid Social: 2% CVR, 20% frequency, $95 AOV
- Paid Search: 2% CVR, 10% frequency, $90 AOV  
- Display Network: 2.5% CVR, 30% frequency, $100 AOV
- Affiliate: 4% CVR, 30% frequency, $120 AOV
- Email: 5% CVR, 10% frequency, $130 AOV

**Note**: Relative frequencies must total 100%

With 1,000 users and average 10 touchpoints, this generates sufficiently realistic multi-touch journeys for attribution analysis.

## Limitations & Future Enhancements

**Limitations**:
- Synthetic data only (not connected to real marketing data sources, which is fine for our purposes, but makes the system unrealistically 'idealistic')
- Assumes independent channel selection (doesn't model sequential dependencies, e.g. customers who click through paid social might be more likely to visit through paid search next rather than visit from email.)
- Simple conversion logic (real customers are more complex; we're not really introducing noise. Which is fine for our theoretical example, but might make for more fun and realistic analysis.)
- No time-decay modeling for touchpoint recency

**Potential Enhancements**:
- Add time-decay attribution model
- Shapley value attribution (a game-theory approach)
- Could add a cohort layer to simulations, or a simple RFM model across multiple simulation runs.
- Model channel interaction effects more realistically

## Project Context

This project was built as a portfolio piece to demonstrate:
- Marketing analytics domain expertise (attribution modeling, customer journey analysis)
- Statistical modeling (Poisson distributions, Markov chains)
- Data visualization and dashboard development
- Streamlit application development
- Python data science stack proficiency

It reflects the type of attribution analysis I've conducted professionally, simplified into an interactive tool that makes attribution concepts accessible and tangible. But please keep in mind this is functionally a project I designed to generate what is ultimately a toy dataset.
