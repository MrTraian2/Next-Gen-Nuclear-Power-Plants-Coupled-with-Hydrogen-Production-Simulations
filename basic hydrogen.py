# hydrogen_simulator.py

def hydrogen_output_kWh_to_kg(electricity_input_kWh, electrolyzer_type='PEM', efficiency=0.7):
    """
    Convert electricity in kWh to hydrogen output in kg.
    Args:
        electricity_input_kWh: Electric energy input in kilowatt-hours.
        electrolyzer_type: 'PEM' or 'SOEC'
        efficiency: fraction (e.g., 0.7 for 70% efficiency)
    Returns:
        Hydrogen produced in kilograms.
    """
    hhv_hydrogen_kWh_per_kg = 39.4  # Higher Heating Value of hydrogen in kWh/kg
    output_kg = electricity_input_kWh * efficiency / hhv_hydrogen_kWh_per_kg
    return output_kg


def simulate_hydrogen_system(
    electric_power_MW=100,
    hours_per_day=24,
    electrolyzer_type='PEM',
    efficiency=None,
    system_cost_per_kW=1100,
    days=1
):
    """
    Simulate hydrogen production for a simple system.

    Returns:
        A dictionary with hydrogen produced, cost, and energy metrics.
    """
    if efficiency is None:
        # Default efficiencies
        efficiency = 0.7 if electrolyzer_type == 'PEM' else 0.85

    total_energy_kWh = electric_power_MW * 1000 * hours_per_day * days
    hydrogen_kg = hydrogen_output_kWh_to_kg(total_energy_kWh, electrolyzer_type, efficiency)

    # Capital cost
    capital_cost = system_cost_per_kW * electric_power_MW * 1000
    cost_per_kg = capital_cost / (hydrogen_kg if hydrogen_kg else 1)

    return {
        'Hydrogen_kg': hydrogen_kg,
        'Energy_kWh': total_energy_kWh,
        'Efficiency': efficiency,
        'Capital_Cost_$': capital_cost,
        'Cost_per_kg_H2_$': cost_per_kg
    }


# Example usage:
if __name__ == "__main__":
    results = simulate_hydrogen_system(
        electric_power_MW=100,
        hours_per_day=24,
        electrolyzer_type='PEM',
        efficiency=None,   # Will auto-select based on type
        system_cost_per_kW=1100,
        days=1
    )

    for key, val in results.items():
        print(f"{key}: {val:,.2f}")
        
import matplotlib.pyplot as plt

power_range = range(10, 201, 10)
h2_outputs = []
for p in power_range:
    r = simulate_hydrogen_system(electric_power_MW=p)
    h2_outputs.append(r['Hydrogen_kg'])

plt.plot(power_range, h2_outputs)
plt.xlabel('Power Input (MW)')
plt.ylabel('Hydrogen Output (kg/day)')
plt.title('Hydrogen Output vs Power Input')
plt.grid(True)
plt.show()