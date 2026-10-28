import numpy as np
import matplotlib.pyplot as plt

# Define performance and cost parameters for each hydrogen production method
ELECTROLYZER_DATA = {
    'PEM': {'efficiency': 0.70, 'capex_per_kW': 1100},
    'SOEC': {'efficiency': 0.85, 'capex_per_kW': 1300},
    'AEC': {'efficiency': 0.65, 'capex_per_kW': 900},
    'SMR': {'efficiency': 0.75, 'capex_per_kW': 700, 'fuel_cost_per_kg': 1.2},
    'Thermochemical': {'efficiency': 0.45, 'capex_per_kW': 1800}
}

HHV_H2_KWH_PER_KG = 39.4  # Higher Heating Value of hydrogen (kWh/kg)

def hydrogen_output_from_profile(
    hourly_power_kW: list,
    method='PEM',
    electricity_cost_per_kWh=0.03,
    run_days=1,
    fixed_OM_per_kW_per_year=30,
    save_csv=False
):
    """
    Simulate hydrogen production over a given period from hourly power data.
    """
    data = ELECTROLYZER_DATA[method]
    efficiency = data['efficiency']
    capex_per_kW = data['capex_per_kW']

    results = []
    total_energy_kWh = 0
    total_hydrogen_kg = 0

    # Repeat the profile for multiple days
    full_profile = hourly_power_kW * run_days

    for hour, power in enumerate(full_profile):
        energy = power  # already in kWh for each hour
        if method != 'SMR':
            h2 = energy * efficiency / HHV_H2_KWH_PER_KG
        else:
            h2 = energy * efficiency / HHV_H2_KWH_PER_KG  # same for SMR, but different cost
        results.append(h2)
        total_energy_kWh += energy
        total_hydrogen_kg += h2

    capex = capex_per_kW * max(hourly_power_kW)
    O_and_M = fixed_OM_per_kW_per_year * max(hourly_power_kW) * run_days / 365
    electricity_cost = total_energy_kWh * electricity_cost_per_kWh

    # SMR has fuel cost
    fuel_cost = 0
    if method == 'SMR':
        fuel_cost = total_hydrogen_kg * data['fuel_cost_per_kg']

    total_cost = capex + O_and_M + electricity_cost + fuel_cost
    cost_per_kg = total_cost / total_hydrogen_kg if total_hydrogen_kg else float('inf')

    # Optional CSV export
    if save_csv:
        import csv
        with open('hydrogen_output.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Hour', 'Hydrogen_kg'])
            for i, val in enumerate(results):
                writer.writerow([i, val])

    return {
        'Hydrogen_kg_total': total_hydrogen_kg,
        'Hourly_H2_kg': results,
        'Energy_input_kWh': total_energy_kWh,
        'Capital_Cost_$': capex,
        'Electricity_Cost_$': electricity_cost,
        'Fixed_OM_$': O_and_M,
        'Fuel_Cost_$': fuel_cost,
        'Cost_per_kg_H2_$': cost_per_kg,
        'Hourly_Power_kW': full_profile
    }

# -----------------------------
# EXAMPLE USE CASE BELOW
# -----------------------------
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    # Example: 24-hour hybrid power profile (100 MW base + 20 MW solar boost in daytime)
    hourly_power_profile = [
        100_000 if h < 6 or h > 18 else 120_000 for h in range(24)
    ]  # in kW

    # Simulate over 3 days using SOEC electrolyzer
    sim_result = hydrogen_output_from_profile(
        hourly_power_kW=hourly_power_profile,
        method='SOEC',
        electricity_cost_per_kWh=0.02,
        run_days=3,
        save_csv=False  # Change to True if you want a CSV
    )

    # Print summary
    print("\n--- Summary Results ---")
    for k, v in sim_result.items():
        if not isinstance(v, list):
            print(f"{k}: {v:,.2f}")

    # -----------------------------
    # PLOTTING
    # -----------------------------
    hours = list(range(len(sim_result['Hourly_H2_kg'])))
    h2_output = sim_result['Hourly_H2_kg']
    power_profile = sim_result['Hourly_Power_kW']

    fig, ax1 = plt.subplots(figsize=(10, 5))

    ax1.set_xlabel("Hour")
    ax1.set_ylabel("H2 Produced (kg/hr)", color='tab:blue')
    ax1.plot(hours, h2_output, color='tab:blue', label='Hydrogen Output')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    ax2 = ax1.twinx()
    ax2.set_ylabel("Power Input (kW)", color='tab:orange')
    ax2.plot(hours, power_profile, color='tab:orange', linestyle='--', label='Power Input')
    ax2.tick_params(axis='y', labelcolor='tab:orange')

    plt.title("Hydrogen Output vs Power Input (SOEC, 3 Days)")
    fig.tight_layout()
    plt.grid(True)
    plt.show()