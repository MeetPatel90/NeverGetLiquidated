import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import requests
import time
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Binance Futures Cross Margin Calculator",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Binance Futures Cross Margin Calculator")
st.markdown("Calculate liquidation prices, PnL, and visualize your cross margin positions with **LIVE PRICES**")

# Live Price Functions
@st.cache_data(ttl=30)  # Cache for 30 seconds
def get_binance_prices():
    """Fetch live prices from Binance API (completely free, no API key needed)"""
    try:
        url = "https://fapi.binance.com/fapi/v1/ticker/price"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            prices = {}
            for item in data:
                symbol = item['symbol']
                if symbol.endswith('USDT'):
                    prices[symbol] = float(item['price'])
            return prices, True
        else:
            return {}, False
    except Exception as e:
        st.error(f"Error fetching live prices: {str(e)}")
        return {}, False

def get_live_prices():
    """Get live prices from Binance API"""
    prices, success = get_binance_prices()

    if not success or not prices:
        # Return default prices as fallback
        st.error("Binance API unavailable, using default prices")
        return {
            "BTCUSDT": 50000.0,
            "ETHUSDT": 3000.0,
            "ADAUSDT": 0.50,
            "SOLUSDT": 100.0,
            "DOGEUSDT": 0.08,
            "XRPUSDT": 0.60,
            "LTCUSDT": 80.0,
            "AVAXUSDT": 35.0,
            "DOTUSDT": 7.0,
            "LINKUSDT": 15.0,
            "BANANAS31USDT": 0.01,
            "BROCCOLI714USDT": 0.01
        }

    return prices

# Initialize session state for positions
if 'positions' not in st.session_state:
    st.session_state.positions = []

if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = False

if 'last_update' not in st.session_state:
    st.session_state.last_update = time.time()

# Sidebar for wallet balance and live price settings
st.sidebar.header("💰 Wallet Settings")
wallet_balance = st.sidebar.number_input(
    "Starting Futures Wallet Balance (USDT)",
    min_value=1.0,
    value=1000.0,
    step=10.0
)

st.sidebar.header("📡 Live Price Settings")

# Auto-refresh toggle
auto_refresh = st.sidebar.checkbox("Auto-refresh prices", value=st.session_state.auto_refresh)
st.session_state.auto_refresh = auto_refresh

# Manual refresh button
if st.sidebar.button("🔄 Refresh Prices Now"):
    st.cache_data.clear()
    st.rerun()

# Get live prices
live_prices = get_live_prices()

# Display last update time
if live_prices:
    st.sidebar.success(f"✅ Live prices loaded")
    st.sidebar.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")

# Auto-refresh mechanism
if auto_refresh:
    if time.time() - st.session_state.last_update > 30:  # Refresh every 30 seconds
        st.session_state.last_update = time.time()
        st.rerun()

# Position input section
st.header("➕ Add Position")

col1, col2, col3, col4 = st.columns(4)

with col1:
    crypto = st.selectbox(
        "Cryptocurrency",
        ["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT", "DOGEUSDT", "XRPUSDT",
         "LTCUSDT", "AVAXUSDT", "DOTUSDT", "LINKUSDT", "BANANAS31USDT", "BROCCOLI714USDT"]
    )

with col2:
    position_type = st.selectbox("Position Type", ["LONG", "SHORT"])

with col3:
    # Use live price as default, with fallback to predefined defaults
    current_live_price = live_prices.get(crypto, 1.0)

    # Show live price indicator
    price_indicator = f"🟢 Live: ${current_live_price:,.6f}" if crypto in live_prices else "🔴 Offline"
    st.caption(price_indicator)

    entry_price = st.number_input(
        "Entry Price (USDT)",
        min_value=0.000001,
        value=current_live_price,
        step=0.000001,
        format="%.6f",
        key=f"entry_price_{crypto}"
    )

with col4:
    leverage = st.selectbox("Leverage", [1, 2, 3, 5, 10, 20, 25, 50, 75, 100, 125])

col5, col6 = st.columns(2)

with col5:
    position_size = st.number_input(
        "Position Size (USDT)",
        min_value=1.0,
        value=100.0,
        step=1.0
    )

with col6:
    maintenance_margin_rate = st.number_input(
        "Maintenance Margin Rate (%)",
        min_value=0.1,
        max_value=10.0,
        value=0.5,
        step=0.1
    ) / 100

# Add position button
if st.button("Add Position"):
    # Calculate correct margin and quantity
    margin_used = position_size / leverage  # This is correct: Position Size ÷ Leverage
    quantity = position_size / entry_price  # This is correct: Position Size ÷ Entry Price

    position = {
        'crypto': crypto,
        'type': position_type,
        'entry_price': entry_price,
        'leverage': leverage,
        'position_size': position_size,
        'maintenance_margin_rate': maintenance_margin_rate,
        'margin_used': margin_used,
        'quantity': quantity
    }
    st.session_state.positions.append(position)
    st.success(f"Added {position_type} position for {crypto} | Margin Used: ${margin_used:.2f} | Quantity: {quantity:.6f}")

# Display current positions
if st.session_state.positions:
    st.header("📊 Current Positions")

    # Create positions dataframe
    positions_df = pd.DataFrame(st.session_state.positions)

    # Display positions table
    display_positions_df = positions_df.copy()
    display_positions_df['entry_price'] = display_positions_df['entry_price'].apply(lambda x: f"${x:.6f}")
    display_positions_df['position_size'] = display_positions_df['position_size'].apply(lambda x: f"${x:.2f}")
    display_positions_df['margin_used'] = display_positions_df['margin_used'].apply(lambda x: f"${x:.2f}")
    display_positions_df['leverage'] = display_positions_df['leverage'].apply(lambda x: f"{x}x")

    st.dataframe(
        display_positions_df[['crypto', 'type', 'entry_price', 'leverage', 'position_size', 'margin_used']],
        use_container_width=True
    )

    # Clear positions button
    if st.button("Clear All Positions"):
        st.session_state.positions = []
        st.rerun()

    # Calculate total margin used
    total_margin_used = sum(pos['margin_used'] for pos in st.session_state.positions)
    available_balance = wallet_balance - total_margin_used

    st.sidebar.metric("Total Margin Used", f"${total_margin_used:.2f}")
    st.sidebar.metric("Available Balance", f"${available_balance:.2f}")

    # PnL Calculator Section
    st.header("💹 PnL Calculator & Liquidation Analysis")

    # Current price inputs with live prices
    st.subheader("📊 Current Prices (Live from Binance)")
    current_prices = {}

    unique_cryptos = list(set(pos['crypto'] for pos in st.session_state.positions))

    # Create columns for price display
    cols = st.columns(min(len(unique_cryptos), 4))
    for i, crypto in enumerate(unique_cryptos):
        with cols[i % 4]:
            # Get live price
            live_price = live_prices.get(crypto, 0)

            # Get entry price for reference
            entry_price = next(pos['entry_price'] for pos in st.session_state.positions if pos['crypto'] == crypto)

            # Calculate price change
            if live_price > 0:
                price_change = ((live_price - entry_price) / entry_price) * 100
                change_color = "🟢" if price_change > 0 else "🔴" if price_change < 0 else "⚪"

                st.metric(
                    label=f"{crypto}",
                    value=f"${live_price:,.6f}",
                    delta=f"{price_change:+.2f}%"
                )
                current_prices[crypto] = live_price
            else:
                st.error(f"No live price for {crypto}")
                current_prices[crypto] = entry_price

    # Manual price override option
    st.subheader("🔧 Manual Price Override (Optional)")
    with st.expander("Override live prices for testing"):
        manual_overrides = {}
        for crypto in unique_cryptos:
            manual_price = st.number_input(
                f"Override {crypto} Price (leave 0 to use live price)",
                min_value=0.0,
                value=0.0,
                step=0.000001,
                format="%.6f",
                key=f"override_{crypto}"
            )
            if manual_price > 0:
                manual_overrides[crypto] = manual_price

        # Apply manual overrides
        for crypto, manual_price in manual_overrides.items():
            current_prices[crypto] = manual_price

    # Calculate PnL and liquidation prices
    total_pnl = 0
    total_maintenance_margin = 0
    liquidation_data = []

    for pos in st.session_state.positions:
        crypto = pos['crypto']
        current_price = current_prices.get(crypto, pos['entry_price'])

        # Calculate PnL
        if pos['type'] == 'LONG':
            pnl = (current_price - pos['entry_price']) * pos['quantity']
        else:  # SHORT
            pnl = (pos['entry_price'] - current_price) * pos['quantity']

        total_pnl += pnl

        # Calculate maintenance margin for this position
        maintenance_margin = pos['position_size'] * pos['maintenance_margin_rate']
        total_maintenance_margin += maintenance_margin

        liquidation_data.append({
            'crypto': crypto,
            'type': pos['type'],
            'entry_price': pos['entry_price'],
            'current_price': current_price,
            'pnl': pnl,
            'maintenance_margin': maintenance_margin,
            'leverage': pos['leverage'],
            'position_size': pos['position_size']
        })

    # Calculate cross margin liquidation
    # Liquidation occurs when: wallet_balance + total_pnl <= total_maintenance_margin
    # This means: total_pnl <= total_maintenance_margin - wallet_balance
    liquidation_pnl_threshold = total_maintenance_margin - wallet_balance

    # Display metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total PnL", f"${total_pnl:.2f}", f"{total_pnl:.2f}")

    with col2:
        st.metric("Total Maintenance Margin", f"${total_maintenance_margin:.2f}")

    with col3:
        current_balance = wallet_balance + total_pnl
        st.metric("Current Balance", f"${current_balance:.2f}")

    with col4:
        margin_ratio = (total_maintenance_margin / current_balance * 100) if current_balance > 0 else 100
        color = "normal" if margin_ratio < 80 else "inverse"
        st.metric("Margin Ratio", f"{margin_ratio:.1f}%", delta_color=color)

    # Liquidation warning
    if margin_ratio >= 100:
        st.error("⚠️ LIQUIDATION RISK! Your margin ratio is at or above 100%")
    elif margin_ratio >= 80:
        st.warning("⚠️ HIGH RISK! Your margin ratio is approaching liquidation levels")

    # PnL breakdown table
    st.subheader("Position Breakdown")
    pnl_df = pd.DataFrame(liquidation_data)
    pnl_df['pnl_formatted'] = pnl_df['pnl'].apply(lambda x: f"${x:.2f}")
    pnl_df['price_change_%'] = ((pnl_df['current_price'] - pnl_df['entry_price']) / pnl_df['entry_price'] * 100).round(2)

    st.dataframe(
        pnl_df[['crypto', 'type', 'entry_price', 'current_price', 'price_change_%', 'pnl_formatted', 'leverage']],
        use_container_width=True
    )

    # Visualization Section
    st.header("📈 Visualizations")

    tab1, tab2, tab3 = st.tabs(["Liquidation Analysis", "Price Sensitivity", "PnL Chart"])

    with tab3:
        # PnL by position chart
        fig_pnl = px.bar(
            pnl_df,
            x='crypto',
            y='pnl',
            color='type',
            title="PnL by Position",
            labels={'pnl': 'PnL (USDT)', 'crypto': 'Cryptocurrency'},
            color_discrete_map={'LONG': 'green', 'SHORT': 'red'}
        )
        fig_pnl.add_hline(y=0, line_dash="dash", line_color="gray")
        st.plotly_chart(fig_pnl, use_container_width=True)

    with tab2:
        # Price sensitivity analysis
        st.subheader("Price Sensitivity Analysis")

        selected_crypto = st.selectbox("Select Crypto for Analysis", unique_cryptos)

        # Get the position for selected crypto
        selected_pos = next(pos for pos in st.session_state.positions if pos['crypto'] == selected_crypto)
        current_price = current_prices[selected_crypto]

        # Create price range
        price_range = np.linspace(current_price * 0.5, current_price * 1.5, 100)
        pnl_range = []

        for price in price_range:
            if selected_pos['type'] == 'LONG':
                pnl = (price - selected_pos['entry_price']) * selected_pos['quantity']
            else:
                pnl = (selected_pos['entry_price'] - price) * selected_pos['quantity']
            pnl_range.append(pnl)

        fig_sensitivity = go.Figure()
        fig_sensitivity.add_trace(go.Scatter(
            x=price_range,
            y=pnl_range,
            mode='lines',
            name=f"{selected_crypto} PnL",
            line=dict(color='blue', width=2)
        ))

        # Add current price line
        fig_sensitivity.add_vline(
            x=current_price,
            line_dash="dash",
            line_color="orange",
            annotation_text="Current Price"
        )

        # Add break-even line
        fig_sensitivity.add_hline(
            y=0,
            line_dash="dash",
            line_color="gray",
            annotation_text="Break Even"
        )

        fig_sensitivity.update_layout(
            title=f"Price Sensitivity for {selected_crypto}",
            xaxis_title="Price (USDT)",
            yaxis_title="PnL (USDT)"
        )

        st.plotly_chart(fig_sensitivity, use_container_width=True)

    with tab1:
        # Liquidation analysis
        st.subheader("Cross Margin Liquidation Analysis")

        # Group positions by crypto and direction to show how Binance actually handles them
        grouped_positions = {}
        for pos in st.session_state.positions:
            key = f"{pos['crypto']}_{pos['type']}"
            if key not in grouped_positions:
                grouped_positions[key] = {
                    'crypto': pos['crypto'],
                    'type': pos['type'],
                    'total_size': 0,
                    'weighted_entry_price': 0,
                    'total_margin': 0,
                    'positions': []
                }

            grouped_positions[key]['total_size'] += pos['position_size']
            grouped_positions[key]['total_margin'] += pos['margin_used']
            grouped_positions[key]['positions'].append(pos)

        # Calculate weighted average entry prices for grouped positions
        for key, group in grouped_positions.items():
            total_quantity = 0
            weighted_price_sum = 0

            for pos in group['positions']:
                quantity = pos['quantity']
                total_quantity += quantity
                weighted_price_sum += pos['entry_price'] * quantity

            group['weighted_entry_price'] = weighted_price_sum / total_quantity if total_quantity > 0 else 0
            group['average_leverage'] = group['total_size'] / group['total_margin'] if group['total_margin'] > 0 else 1

        st.subheader("📊 Binance Position Grouping (How Binance Actually Sees Your Positions)")

        # Display grouped positions
        grouped_data = []
        for key, group in grouped_positions.items():
            # Calculate maintenance margin for the grouped position
            avg_mmr = sum(pos['maintenance_margin_rate'] for pos in group['positions']) / len(group['positions'])
            maintenance_margin = group['total_size'] * avg_mmr

            # Calculate Binance-style cross margin liquidation price
            # This considers the entire wallet balance and other positions' PnL

            # Calculate total unrealized PnL from ALL OTHER positions
            other_positions_pnl = 0
            for other_key, other_group in grouped_positions.items():
                if other_key != key:  # Exclude current position group
                    other_current_price = current_prices.get(other_group['crypto'], other_group['weighted_entry_price'])
                    other_total_quantity = sum(pos['quantity'] for pos in other_group['positions'])

                    if other_group['type'] == 'LONG':
                        other_pnl = (other_current_price - other_group['weighted_entry_price']) * other_total_quantity
                    else:
                        other_pnl = (other_group['weighted_entry_price'] - other_current_price) * other_total_quantity

                    other_positions_pnl += other_pnl

            # Calculate total maintenance margin from ALL OTHER positions
            other_maintenance_margin = 0
            for other_key, other_group in grouped_positions.items():
                if other_key != key:
                    other_avg_mmr = sum(pos['maintenance_margin_rate'] for pos in other_group['positions']) / len(other_group['positions'])
                    other_maintenance_margin += other_group['total_size'] * other_avg_mmr

            # Available balance for this position = wallet + other PnL - other maintenance margins
            available_balance = wallet_balance + other_positions_pnl - other_maintenance_margin

            # Position details
            position_quantity = sum(pos['quantity'] for pos in group['positions'])
            position_value = group['total_size']  # Position size in USDT

            # Binance cross margin liquidation price formula
            if group['type'] == 'LONG':
                # For LONG: Price falls to liquidation when unrealized loss + maintenance margin = available balance
                # Liquidation PnL = -(available_balance - maintenance_margin)
                # (liq_price - entry_price) * quantity = -(available_balance - maintenance_margin)
                # liq_price = entry_price - (available_balance - maintenance_margin) / quantity
                liq_price = group['weighted_entry_price'] - (available_balance - maintenance_margin) / position_quantity
            else:
                # For SHORT: Price rises to liquidation when unrealized loss + maintenance margin = available balance
                # Liquidation PnL = -(available_balance - maintenance_margin)
                # (entry_price - liq_price) * quantity = -(available_balance - maintenance_margin)
                # liq_price = entry_price + (available_balance - maintenance_margin) / quantity
                liq_price = group['weighted_entry_price'] + (available_balance - maintenance_margin) / position_quantity

            # Ensure liquidation price is positive and reasonable
            if liq_price <= 0:
                liq_price = group['weighted_entry_price'] * 0.01 if group['type'] == 'LONG' else group['weighted_entry_price'] * 100

            current_price = current_prices.get(group['crypto'], group['weighted_entry_price'])

            # Calculate current PnL for this grouped position
            total_quantity = sum(pos['quantity'] for pos in group['positions'])
            if group['type'] == 'LONG':
                group_pnl = (current_price - group['weighted_entry_price']) * total_quantity
            else:
                group_pnl = (group['weighted_entry_price'] - current_price) * total_quantity

            distance_to_liq = abs((liq_price - current_price) / current_price * 100)

            grouped_data.append({
                'crypto': group['crypto'],
                'type': group['type'],
                'positions_count': len(group['positions']),
                'total_size_usdt': group['total_size'],
                'weighted_avg_entry': group['weighted_entry_price'],
                'avg_leverage': group['average_leverage'],
                'current_price': current_price,
                'liquidation_price': liq_price,
                'distance_to_liq_%': distance_to_liq,
                'current_pnl': group_pnl,
                'maintenance_margin': maintenance_margin
            })

        grouped_df = pd.DataFrame(grouped_data)
        if not grouped_df.empty:
            # Format the dataframe for display
            display_df = grouped_df.copy()
            display_df['total_size_usdt'] = display_df['total_size_usdt'].apply(lambda x: f"${x:.2f}")
            display_df['weighted_avg_entry'] = display_df['weighted_avg_entry'].apply(lambda x: f"${x:.6f}")
            display_df['current_price'] = display_df['current_price'].apply(lambda x: f"${x:.6f}")
            display_df['liquidation_price'] = display_df['liquidation_price'].apply(lambda x: f"${x:.6f}")
            display_df['current_pnl'] = display_df['current_pnl'].apply(lambda x: f"${x:.2f}")
            display_df['avg_leverage'] = display_df['avg_leverage'].apply(lambda x: f"{x:.1f}x")
            display_df['distance_to_liq_%'] = display_df['distance_to_liq_%'].apply(lambda x: f"{x:.2f}%")

            st.dataframe(
                display_df[['crypto', 'type', 'positions_count', 'total_size_usdt', 'weighted_avg_entry',
                            'avg_leverage', 'current_price', 'liquidation_price', 'distance_to_liq_%', 'current_pnl']],
                use_container_width=True
            )

        # Cross Margin Liquidation Explanation
        st.subheader("🎯 Cross Margin Liquidation Process")

        # Calculate overall liquidation threshold
        total_maintenance_margin_grouped = sum(row['maintenance_margin'] for row in grouped_data) if grouped_data else 0
        liquidation_threshold_pnl = total_maintenance_margin_grouped - wallet_balance

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Maintenance Margin Required", f"${total_maintenance_margin_grouped:.2f}")
        with col2:
            st.metric("Liquidation PnL Threshold", f"${liquidation_threshold_pnl:.2f}")



        # Show how positions affect each other
        if len(grouped_positions) > 1:
            st.subheader("🔄 Cross Margin Position Interactions")
            st.markdown("**How your positions affect each other's liquidation prices:**")

            for key, group in grouped_positions.items():
                current_price = current_prices.get(group['crypto'], group['weighted_entry_price'])
                total_quantity = sum(pos['quantity'] for pos in group['positions'])

                if group['type'] == 'LONG':
                    group_pnl = (current_price - group['weighted_entry_price']) * total_quantity
                else:
                    group_pnl = (group['weighted_entry_price'] - current_price) * total_quantity

                pnl_status = "📈 Helping" if group_pnl > 0 else "📉 Hurting" if group_pnl < 0 else "➡️ Neutral"
                st.markdown(f"- **{group['crypto']} {group['type']}**: {pnl_status} other positions (PnL: ${group_pnl:.2f})")
        else:
            st.info("Add more positions to see cross margin interactions!")

        # Show liquidation sequence
        if grouped_data:
            st.subheader("🔴 Liquidation Risk Ranking")
            risk_df = grouped_df.copy()
            risk_df = risk_df.sort_values('distance_to_liq_%')

            st.markdown("**Positions ranked by liquidation risk (closest to liquidation first):**")
            for idx, row in risk_df.iterrows():
                risk_level = "🔴 HIGH" if row['distance_to_liq_%'] < 5 else "🟡 MEDIUM" if row['distance_to_liq_%'] < 15 else "🟢 LOW"
                st.markdown(f"**{risk_level}** - {row['crypto']} {row['type']}: {row['distance_to_liq_%']:.2f}% to liquidation")

        st.warning("""
        **⚠️ Important Notes:**
        - Liquidation prices shown are dynamic and change as market moves
        - Profitable positions can significantly extend liquidation prices of losing positions
        - In extreme market conditions, multiple positions may be liquidated simultaneously
        - Always maintain sufficient margin buffer for safety
        """)

        # Individual positions breakdown (for reference)
        st.subheader("📋 Individual Positions (Before Grouping)")
        individual_scenarios = []

        for i, pos in enumerate(st.session_state.positions):
            if pos['type'] == 'LONG':
                individual_liq_price = pos['entry_price'] * (1 - 1/pos['leverage'] + pos['maintenance_margin_rate'])
            else:
                individual_liq_price = pos['entry_price'] * (1 + 1/pos['leverage'] - pos['maintenance_margin_rate'])

            individual_scenarios.append({
                'position_id': i+1,
                'crypto': pos['crypto'],
                'type': pos['type'],
                'entry_price': f"${pos['entry_price']:.6f}",
                'leverage': f"{pos['leverage']}x",
                'size': f"${pos['position_size']:.2f}",
                'individual_liq_price': f"${individual_liq_price:.6f}",
                'margin_used': f"${pos['margin_used']:.2f}"
            })

        individual_df = pd.DataFrame(individual_scenarios)
        st.dataframe(individual_df, use_container_width=True)

else:
    st.info("Add some positions to start calculating PnL and liquidation prices!")

    # Example positions
    st.subheader("💡 Example Usage")
    st.markdown("""
    **Try adding these example positions:**
    
    1. **BTCUSDT LONG**: Entry price will default to live price, try 10x leverage, $500 position size
    2. **ETHUSDT SHORT**: Entry price will default to live price, try 5x leverage, $300 position size
    3. **ADAUSDT LONG**: Entry price will default to live price, try 20x leverage, $200 position size
    
    Then watch how your PnL changes in real-time with live market prices!
    """)

# Footer
st.markdown("---")
st.info(f"""
        **How Binance Cross Margin Liquidation Actually Works:**
        
        1️⃣ **Position Grouping**: Binance groups positions by crypto + direction (LONG/SHORT)
           - Multiple BTCUSDT LONG positions → 1 combined BTCUSDT LONG position
           - Entry price becomes weighted average based on position sizes
           
        2️⃣ **Dynamic Liquidation Prices**: Unlike isolated margin, liquidation prices change in real-time
           - Considers your entire wallet balance: ${wallet_balance:.2f}
           - Includes unrealized PnL from OTHER positions
           - Accounts for maintenance margins from ALL positions
           
        3️⃣ **Cross Margin Formula**: For each position group:
           - **LONG Liquidation** = Entry Price - (Available Balance - Maintenance Margin) ÷ Quantity
           - **SHORT Liquidation** = Entry Price + (Available Balance - Maintenance Margin) ÷ Quantity
           - Available Balance = Wallet + Other Positions PnL - Other Maintenance Margins
        
        4️⃣ **Liquidation Trigger**: When Total Account Balance ≤ Total Maintenance Margin
           - Current condition: ${wallet_balance + total_pnl:.2f} vs ${total_maintenance_margin_grouped:.2f} required
           - Margin Ratio: {margin_ratio:.1f}% (liquidation at 100%)
           
        5️⃣ **Key Insight**: Profitable positions extend liquidation prices of losing positions!
           - If you have a winning ETHUSDT position, your BTCUSDT liquidation price becomes more favorable
           - Losing positions make other positions' liquidation prices worse
        """)
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <small>⚠️ This calculator is for educational purposes only. Always verify calculations and understand the risks before trading futures.</small>
</div>
""", unsafe_allow_html=True)