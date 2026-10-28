import numpy as np
import matplotlib.pyplot as plt

# Parameters for different hydrogen production technologies
ELECTROLYZER_DATA = {
    'PEM': {'efficiency': 0.70, 'capex_per_kW': 1100},
    'SOEC': {'efficiency': 0.85, 'capex_per_kW': 1300},
    'AEC': {'efficiency': 0.65, 'capex_per_kW': 900}
}

HHV_H2_KWH_PER_KG = 39.4  # Higher Heating Value of hydrogen

def get_dynamic_split(hour):
    # More H₂ production at night (22:00 to 6:00)
    if 22 <= hour or hour < 6:
        return 0.7
    else:
        return 0.3

hourly_prices = [0.04]*8 + [0.08]*8 + [0.02]*8  # high price midday

#def get_dynamic_split(hour):
#   if hourly_prices[hour % 24] > 0.05:
#        return 0.2  # sell more to grid
#    else:
#        return 0.7  # produce H₂ when grid prices are low

def simulate_hybrid_nuclear_plant(
    hourly_total_output_kW,
    hydrogen_split_fraction=0.3,
    method='SOEC',
    electricity_price_per_kWh=0.03,
    run_days=1,
    fixed_OM_per_kW_per_year=30
):
    """
    Simulate a hybrid nuclear-H2 plant with output split between grid and H2 production.
    """
    data = ELECTROLYZER_DATA[method]
    efficiency = data['efficiency']
    capex_per_kW = data['capex_per_kW']

    total_h2_kg = 0
    total_energy_input_H2_kWh = 0
    hourly_h2 = []
    hourly_grid = []

    profile = hourly_total_output_kW * run_days

    for power in profile:
        h2_split = get_dynamic_split(12)
        h2_power = power * h2_split
        grid_power = power - h2_power

        h2_kg = h2_power * efficiency / HHV_H2_KWH_PER_KG
        hourly_h2.append(h2_kg)
        hourly_grid.append(grid_power)

        total_h2_kg += h2_kg
        total_energy_input_H2_kWh += h2_power

    capex = capex_per_kW * max(hourly_total_output_kW)
    om_cost = fixed_OM_per_kW_per_year * max(hourly_total_output_kW) * run_days / 365
    elec_cost = total_energy_input_H2_kWh * electricity_price_per_kWh

    total_cost = capex + om_cost + elec_cost
    cost_per_kg = total_cost / total_h2_kg if total_h2_kg else float('inf')

    return {
        'Hourly_H2_kg': hourly_h2,
        'Hourly_Grid_kW': hourly_grid,
        'Total_H2_kg': total_h2_kg,
        'Grid_Energy_Sent_kWh': sum(hourly_grid),
        'Energy_Used_for_H2_kWh': total_energy_input_H2_kWh,
        'Cost_per_kg_H2_$': cost_per_kg,
        'Capex_$': capex,
        'Electricity_Cost_$': elec_cost,
        'O&M_$': om_cost,
        'Split_%': hydrogen_split_fraction
    }

# -------------------------------
# Example: Hybrid 150 MWe Reactor
# -------------------------------
if __name__ == "__main__":
    hourly_output = [150_000] * 24  # 150 MWe base load for 24h
    split_ratio = 0.4  # 40% to hydrogen, 60% to grid

    result = simulate_hybrid_nuclear_plant(
        hourly_total_output_kW=hourly_output,
        hydrogen_split_fraction=split_ratio,
        method='SOEC',
        electricity_price_per_kWh=0.02,
        run_days=2
    )

    # Output
    print(f"\n--- Hybrid Nuclear-Hydrogen Plant Simulation ---")
    for k, v in result.items():
        if not isinstance(v, list):
            print(f"{k}: {v:,.2f}")

    # Plot
    hours = list(range(len(result['Hourly_H2_kg'])))
    plt.figure(figsize=(10, 5))
    plt.plot(hours, result['Hourly_H2_kg'], label='H₂ Production (kg/hr)', color='blue')
    plt.plot(hours, result['Hourly_Grid_kW'], label='Electricity to Grid (kW)', color='orange', linestyle='--')
    plt.title("Hybrid Reactor Output: H₂ vs Grid")
    plt.xlabel("Hour")
    plt.ylabel("Output")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()